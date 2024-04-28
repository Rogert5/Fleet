from datetime import datetime, timedelta
import os

from urllib.parse import urlparse
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from helpers import apology
from collections import defaultdict


# Configure application
app = Flask(__name__)

def create_app():
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

# Configure database
#{sgmm+VzG7VE@127.0.0.1:3306/fleet_db
#mysql+pymysql://mydb_root_user@localhost/fleet_db
<<<<<<< HEAD
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://u5jrt73t4bhb7a:p6e489bf1e00f874e5b60cecdc4ee2513987f0270a6470c095fb5983df1e1fd3f@cb6h87c9erodfl.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/der06trr78933f"
=======
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgres://u2uao60uo5rh2g:p67321ffebd10efb688c69c9231e5a4839c03d0e305f2d0a231391dc037f714eb@cb6h87c9erodfl.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/damd6vshgk9tdd'
>>>>>>> parent of 2b8184a (url changed , added import db, and added code from heroku to fix postgresql)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Create database object
db = SQLAlchemy(app)


# Define the Entry model used for inbox
class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    van = db.Column(db.String(2), nullable=False)
    body = db.Column(db.String(200), nullable=False)
    
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
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

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

#Delete entry from inbox
@app.route("/inbox/delete-entry", methods=["POST"])
def delete_entry():
    page = request.form.get("page")
    entry_id = request.form.get("entryId")
    if entry_id:
        entry = Entry.query.get(entry_id)
        if entry:
            db.session.delete(entry)
            db.session.commit()

    flash("Entry Deleted",)
    return redirect("/inbox")

# home page route
@app.route("/")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)