from datetime import datetime, timedelta
import os

from urllib.parse import urlparse
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import psycopg2
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


@app.route("/")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)