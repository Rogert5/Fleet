from urllib.parse import urlparse
from flask import Flask, flash, redirect, render_template, request, session, jsonify, escape
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import psycopg2
from helpers import apology
from collections import defaultdict

# -----------------------------
# Application Configuration
# -----------------------------

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://u2uao60uo5rh2g:p67321ffebd10efb688c69c9231e5a4839c03d0e305f2d0a231391dc037f714eb@cb6h87c9erodfl.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/damd6vshgk9tdd'
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

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    van = db.Column(db.String(), nullable=False)
    body = db.Column(db.String(), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: convert_utc_to_cst(datetime.utcnow()))

class Note(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

# Create tables
with app.app_context():
    db.create_all()

# -----------------------------
# Route Handlers
# -----------------------------

@app.route("/", methods=["GET", "POST"])
def home():
    """Home page route"""
    if request.method == "POST":
        note_body = request.form.get("body")
        note = Note(body=note_body)
        db.session.add(note)
        db.session.commit()
        flash("Note added successfully")

    notes = Note.query.all()
    return render_template("home.html", notes=notes)

@app.route("/compose", methods=["GET", "POST"])
def compose():
    """Compose page route for adding new entries"""
    if request.method == "POST":
        van = request.form.get("van")
        body = request.form.get("body")

        if not van.isdigit() or not ((1 <= int(van) <= 23) or (52 <= int(van) <= 58)):
            return render_template("apology.html", top="Error", bottom="Sorry, only numbers between 1-23 and 52-58 are allowed. DO NOT ADD LETTER G")

        entry = Entry(van=van, body=body)
        db.session.add(entry)
        db.session.commit()

        flash("Entry Successful")
        return redirect("/inbox")

    return render_template("inbox.html")

@app.route("/inbox/delete-entry", methods=["POST"])
def delete_entry():
    """Delete an entry from the inbox"""
    entry_id = request.json.get("entryId")
    if entry_id:
        entry = Entry.query.get(entry_id)
        if entry:
            db.session.delete(entry)
            db.session.commit()
            return jsonify({'status': 'success'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Entry not found'}), 404
    return jsonify({'status': 'error', 'message': 'Invalid request'}), 400

@app.route("/inbox", methods=["GET", "POST"])
def inbox():
    """Inbox page route with optional ordering"""
    order_by = request.args.get("order_by", "timestamp")
    if order_by not in ["timestamp", "van"]:
        order_by = "timestamp"

    if order_by == "timestamp":
        entries = Entry.query.order_by(Entry.timestamp.desc())
    elif order_by == "van":
        entries = Entry.query.order_by(Entry.van.cast(db.Integer).asc())

    entry_list = [{"id": entry.id, "van": int(entry.van), "body": entry.body, "timestamp": entry.timestamp} for entry in entries]
    entry_list.sort(key=lambda x: (x['van'], x['timestamp'])) if order_by == "van" else entry_list.sort(key=lambda x: x['timestamp'], reverse=True)

    return render_template("inbox.html", entries=entry_list, order_by=order_by)

@app.route("/grid")
def grid():
    """Grid page route"""
    entries = Entry.query.all()
    return render_template("grid.html", entries=entries)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    """Admin page route"""
    return render_template("admin.html")

@app.route("/home/delete-note", methods=["POST"])
def delete_note():
    """Delete a note from the home page"""
    note_id = request.form.get("noteId")
    if note_id:
        note = Note.query.get(note_id)
        if note:
            db.session.delete(note)
            db.session.commit()
            flash("Note deleted successfully")
    return redirect("/")

# -----------------------------
# Utility Functions
# -----------------------------

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# -----------------------------
# Main Execution
# -----------------------------

if __name__ == "__main__":
    app.run(debug=True)
