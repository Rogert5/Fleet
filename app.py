from datetime import datetime, timedelta
import os

from urllib.parse import urlparse
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from markupsafe import Markup
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import psycopg2
from helpers import apology
from collections import defaultdict
import json

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
    image_url = db.Column(db.String(255))
    
    # Define a function to get the default timestamp value in CST
    @staticmethod
    def default_cst_timestamp():
        # Get the current UTC time
        utc_now = datetime.utcnow()
        # Convert UTC time to CST
        cst_time = convert_utc_to_cst(utc_now)
        return cst_time

    # Define the timestamp column with the default value as CST time
    timestamp = db.Column(db.DateTime, nullable=False, default=default_cst_timestamp)



#Defines Note used in Admin page to send post it notes between management
class Note(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

# Define a function to convert UTC to CST
def convert_utc_to_cst(utc_time):
    # Calculate the time difference between UTC and CST (UTC-6 hours)
    cst_offset = timedelta(hours=-6)
    # Add the offset to the UTC time
    cst_time = utc_time + cst_offset
    return cst_time

# Create tables
with app.app_context():
    db.create_all()

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
        image_url = None
        if image_file and image_file.filename:
            filename = image_file.filename
            upload_folder = os.path.join("static", "uploads")
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, filename)
            image_file.save(image_path)
            image_url = f"/static/uploads/{filename}"

        # Create and save entry
        entry = Entry(van=van, body=body, image_url=image_url, timestamp=cst_time)
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



#admin user page makes it have the ability to post a note in notes through the POST method
@app.route("/admin", methods=["GET", "POST"])
def admin():

    # Pass notes to the template
    return render_template("admin.html")
    

    
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
        van = entry["van"].upper()
        prefix_order = {"": 0, "L": 1, "H": 2, "G": 3}
        for prefix in prefix_order:
            if van.startswith(prefix):
                try:
                    num = int(van[len(prefix):])
                    return (prefix_order[prefix], num, entry["timestamp"])
                except ValueError:
                    break
        return (999, float("inf"), entry["timestamp"])  # fallback

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