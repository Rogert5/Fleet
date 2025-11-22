from datetime import datetime, timedelta
import os
import uuid

from urllib.parse import urlparse
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from markupsafe import Markup
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import psycopg2
from helpers import apology
from collections import defaultdict
import json
from werkzeug.utils import secure_filename
from sqlalchemy import case, func, cast
from sqlalchemy.types import Integer

#MASTER BRANCH
# -----------------------------
# Application Configuration
# -----------------------------


# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

#uri = os.getenv("DATABASE_URL")  # or other relevant config var
#if uri.startswith("postgres://"):
#    uri = uri.replace("postgres://", "postgresql://", 1)

# Configure database
#postgresql://u2uao60uo5rh2g:p67321ffebd10efb688c69c9231e5a4839c03d0e305f2d0a231391dc037f714eb@cb6h87c9erodfl.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/damd6vshgk9tdd
#{sgmm+VzG7VE@127.0.0.1:3306/fleet_db (GODADDY CODE)
#mysql+pymysql://mydb_root_user@localhost/fleet_db (LOCAL CODE)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://u2uao60uo5rh2g:p67321ffebd10efb688c69c9231e5a4839c03d0e305f2d0a231391dc037f714eb@cb6h87c9erodfl.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/damd6vshgk9tdd'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Create database object
db = SQLAlchemy(app)



# Ensure this is somewhere near the top of your app.py
UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# -----------------------------
# Helper Functions
# -----------------------------

def convert_utc_to_cst(utc_time):
    """Convert UTC time to CST (UTC-6 hours)"""
    cst_offset = timedelta(hours=-6)
    return utc_time + cst_offset


# -----------------------------
# Model Definitions
# -----------------------------

# Define the Entry model used for inbox
class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    van = db.Column(db.String(), nullable=False)
    body = db.Column(db.String(), nullable=False)
    image_url = db.Column(db.String(), nullable=True)

    @staticmethod
    def default_cst_timestamp():
        # Get the current UTC time
        utc_now = datetime.utcnow()
        # Convert UTC time to CST
        cst_time = convert_utc_to_cst(utc_now)
        return cst_time

    # Define the timestamp column with the default value as CST time
    timestamp = db.Column(db.DateTime, nullable=False, default=default_cst_timestamp)


# Defines Note used in Admin page to send post it notes between management
class Note(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())


# Defines Van model for editing and deleting van/vins from Admin.html
class Van(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    van_code = db.Column(db.String(), nullable=False, unique=True)
    vin = db.Column(db.String(), nullable=False, unique=True)


# Create tables and seed vans
with app.app_context():
    db.create_all()

    # One-time seed – runs only if the table is empty
    if Van.query.count() == 0:
        seed_vans = [
            Van(van_code='G1',  vin='3C6URVJG8KE545204'),
            Van(van_code='G2',  vin='3C6URVJG0LE113112'),
            Van(van_code='G3',  vin='3C6MRVJG8ME541401'),
            Van(van_code='G4',  vin='3C6URVJG8LE117182'),
            Van(van_code='G5',  vin='3C6URVJG9LE113142'),
            Van(van_code='G6',  vin='3C6URVJG3KE551296'),
            Van(van_code='G7',  vin='3C6URVJG0LE144389'),
            Van(van_code='G8',  vin='1FTBR3X81LKB33385'),
            Van(van_code='G9',  vin='1FTBR3X80LKB28176'),
            Van(van_code='G10', vin='3C6URVJG9LE113156'),
            Van(van_code='G11', vin='3C6URVJG7KE545243'),
            Van(van_code='G12', vin='3C6URVJG6KE553303'),
            Van(van_code='G13', vin='3C6URVJG0KE551384'),
            Van(van_code='G14', vin='3C6URVJG1LE113135'),
            Van(van_code='G15', vin='3C6URVJGXLE113117'),
            Van(van_code='G52', vin='3C6LRVCG3PE582919'),
            Van(van_code='G53', vin='3C6LRVBG4NE139466'),
            Van(van_code='G54', vin='3C6LRVBG8NE139468'),
            Van(van_code='G55', vin='3C6LRVBG6NE139467'),
            Van(van_code='G56', vin='3C6TRVBG3LE134868'),
            Van(van_code='G57', vin='3C6TRVBG5LE134869'),
            Van(van_code='G58', vin='3C6URVJG5LE129743'),
        ]
        db.session.bulk_save_objects(seed_vans)
        db.session.commit()



# SECOND COPY (safe because models are already defined)
def convert_utc_to_cst(utc_time):
    cst_offset = timedelta(hours=-6)
    return utc_time + cst_offset

    
@app.route("/inbox/delete-entry", methods=["POST"])
def delete_entry():
    entry_id = request.json.get("entryId")
    if entry_id:
        entry = Entry.query.get(entry_id)
        if entry:
            db.session.delete(entry)
            db.session.commit()
            return jsonify({'status': 'success'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Entry not found'}), 404
    else:
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400

# home page route
@app.route("/", methods=["GET", "POST"])
def home():
        if request.method == "POST":
            # Get the note body from the form data
            note_body = request.form.get("body")

            # Insert the note into the database
            note = Note(body=note_body)
            db.session.add(note)
            db.session.commit()

        # Retrieve notes from the database
        notes = Note.query.all()

        return render_template("home.html", notes=notes)
        


# Compose route for entry in Inbox.html
@app.route("/compose", methods=["GET", "POST"])
def compose():
    if request.method == "POST":
        van = request.form.get("van", "").strip().upper()  # Force van to uppercase and trim spaces
        body = request.form.get("body", "").replace("\r", "")
        image_file = request.files.get("image")  # Handle uploaded image

        # Get the current UTC time
        utc_now = datetime.utcnow()
        cst_time = convert_utc_to_cst(utc_now)

        # Validate van number
        valid_prefixes = ["L", "H", "G"]
        image_url = None  # Default if no image is attached

        # Normalize casing
        van = van.upper()

        # If it's just digits, convert to G-prefixed
        if van.isdigit():
            van_num = int(van)
            if 1 <= van_num <= 58:
                van = f"G{van_num}"
            else:
                apology_message = "Only 1–58 or L1–L58, G1–G58, or H1–H58 are allowed."
                return render_template("apology.html", top="Error", bottom=apology_message)

        # If it's prefixed (L, G, H)
        elif any(van.startswith(prefix) and van[1:].isdigit() for prefix in valid_prefixes):
            van_num = int(van[1:])
            if not (1 <= van_num <= 58):
                apology_message = "Only 1–58 or L1–L58, G1–G58, or H1–H58 are allowed."
                return render_template("apology.html", top="Error", bottom=apology_message)

        else:
            # Invalid format
            apology_message = "Only 1–58 or L1–L58, G1–G58, or H1–H58 are allowed."
            return render_template("apology.html", top="Error", bottom=apology_message)

        # Handle image saving (if present)
        if image_file and image_file.filename and allowed_file(image_file.filename):
            unique_suffix = uuid.uuid4().hex
            ext = image_file.filename.rsplit('.', 1)[-1]
            filename = f"{secure_filename(van)}_{unique_suffix}.{ext}"
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(filepath)
            image_url = f"/static/uploads/{filename}"

        elif image_file:
            flash("Invalid file type. Please upload a PNG, JPG, JPEG, or GIF.")
            return redirect("inbox")


        # Create and save entry
        entry = Entry(van=van, body=body, timestamp=cst_time, image_url=image_url)
        db.session.add(entry)
        db.session.commit()

        flash("Entry Successful")
        return redirect("inbox")

    # If GET request, just render the compose form (inbox)
    return render_template("inbox.html")




# Add a new route for the grid page
@app.route("/grid")
def grid():
    # Fetch entries from the database
    entries = Entry.query.all()
    return render_template("grid.html", entries=entries)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        # Handle "Add Van" form submission
        van_code = request.form.get("van_code", "").strip().upper()
        vin = request.form.get("vin", "").strip().upper()

        # Basic validation
        if not van_code or not vin:
            flash("Van and VIN are required.")
            return redirect("/admin")

        # Only allow G/H/L + digits, like G1–G58, H1–H58, L1–L58
        valid_prefixes = ["G", "H", "L"]
        if not any(van_code.startswith(p) and van_code[len(p):].isdigit() for p in valid_prefixes):
            flash("Van must be like G1–G58, H1–H58, or L1–L58.")
            return redirect("/admin")

        # Check for duplicate van_code
        existing_code = Van.query.filter_by(van_code=van_code).first()
        if existing_code:
            flash(f"Van {van_code} already exists.")
            return redirect("/admin")

        # Check for duplicate VIN
        existing_vin = Van.query.filter_by(vin=vin).first()
        if existing_vin:
            flash(f"VIN {vin} is already assigned to another van.")
            return redirect("/admin")

        # Create and save new van
        new_van = Van(van_code=van_code, vin=vin)
        db.session.add(new_van)
        db.session.commit()

        flash(f"Van {van_code} added successfully.")
        return redirect("/admin")

    # GET request: show the admin page with sorted vans
    group_order = case(
        (Van.van_code.like('G%'), 1),
        (Van.van_code.like('H%'), 2),
        (Van.van_code.like('L%'), 3),
        else_=4
    )
    numeric_part = cast(func.substr(Van.van_code, 2), Integer)

    vans = Van.query.order_by(group_order, numeric_part).all()

    return render_template("admin.html", vans=vans)

@app.route("/vans/<int:van_id>/edit", methods=["POST"])
def edit_van(van_id):
    van = Van.query.get_or_404(van_id)

    new_code = request.form.get("van_code", "").strip().upper()
    new_vin = request.form.get("vin", "").strip().upper()

    if not new_code or not new_vin:
        flash("Van and VIN are required.")
        return redirect("/admin")

    # Only allow G/H/L + digits, like G1–G58, H1–H58, L1–L58
    valid_prefixes = ["G", "H", "L"]
    if not any(new_code.startswith(p) and new_code[len(p):].isdigit() for p in valid_prefixes):
        flash("Van must be like G1–G58, H1–H58, or L1–L58.")
        return redirect("/admin")

    # Check for duplicate van_code (exclude this van)
    existing_code = Van.query.filter(
        Van.id != van_id,
        Van.van_code == new_code
    ).first()
    if existing_code:
        flash(f"Van {new_code} already exists.")
        return redirect("/admin")

    # Check for duplicate VIN (exclude this van)
    existing_vin = Van.query.filter(
        Van.id != van_id,
        Van.vin == new_vin
    ).first()
    if existing_vin:
        flash(f"VIN {new_vin} is already assigned to another van.")
        return redirect("/admin")

    # Apply updates
    van.van_code = new_code
    van.vin = new_vin
    db.session.commit()

    flash(f"Van updated to {new_code}.")
    return redirect("/admin")

@app.route("/vans/<int:van_id>/delete", methods=["POST"])
def delete_van(van_id):
    van = Van.query.get_or_404(van_id)
    code = van.van_code

    db.session.delete(van)
    db.session.commit()

    flash(f"Van {code} deleted.")
    return redirect("/admin")

    

    
# Rearrange inbox entries by date (descending) or van (ascending)
@app.route("/inbox", methods=["GET", "POST"])
def inbox():
    order_by = request.args.get("order_by", "van")
    if order_by not in ["timestamp", "van"]:
        order_by = "timestamp"

    entries = Entry.query.all()

    entry_list = [{
        "id": entry.id,
        "van": entry.van,
        "body": entry.body,
        "timestamp": entry.timestamp,
        "image_url": getattr(entry, "image_url", None)  # fallback if field missing
    } for entry in entries]

    # Define custom sorting for vans with optional prefixes
    def custom_van_sort(entry):
        van = entry["van"].upper()  # normalize casing
        prefix_order = {"L": 0, "G": 1, "H": 2, "": 3}  # L first, then G, then H, then any leftover junk

        for prefix in prefix_order:
            if van.startswith(prefix):
                try:
                    num = int(van[len(prefix):])
                    return (prefix_order[prefix], num, entry["timestamp"])
                except ValueError:
                    break

        return (999, float("inf"), entry["timestamp"])  # fallback for malformed entries


    # Apply sorting
    if order_by == "timestamp":
        entry_list.sort(key=lambda x: x["timestamp"], reverse=True)
    elif order_by == "van":
        entry_list.sort(key=custom_van_sort)

    return render_template("inbox.html", entries=entry_list, order_by=order_by)





# Delete note from the databasegit a
@app.route("/home/delete-note", methods=["POST"])
def delete_note():
    note_id = request.form.get("noteId")
    if note_id:
        note = Note.query.get(note_id)
        if note:
            db.session.delete(note)
            db.session.commit()
    flash("Note deleted successfully")
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)