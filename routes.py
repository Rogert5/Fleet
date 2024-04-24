from . import app, db
from flask import render_template

@app.route("/")
def home():
    return render_template("home.html")


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


#compose route for entry in Inbox.html
@app.route("/compose", methods=["GET", "POST"])
def compose():
    if request.method == "POST":
        van = request.form.get("van")
        body = request.form.get("body")

        # Get the current UTC time
        utc_now = datetime.utcnow()
        # Convert UTC time to CST
        cst_time = convert_utc_to_cst(utc_now)

        if not van.isdigit() or not ((1 <= int(van) <= 29) or (52 <= int(van) <= 58)):
            apology_message = "Sorry, only numbers between 1-29 and 52-58 are allowed. DO NOT ADD LETTER G"
            return render_template("apology.html", top="Error", bottom=apology_message)


        entry = Entry(van=van, body=body, timestamp=cst_time)  # Include timestamp parameter
        db.session.add(entry)
        db.session.commit()

        flash("Entry Successful")
        return redirect("inbox")

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

    if request.method == "POST":
        # Get the note body from the form data
        note_body = request.form.get("body")

        # Insert the note into the database
        note = Note(body=note_body)
        db.session.add(note)
        db.session.commit()

    # Retrieve notes from the database
    notes = Note.query.all()

    # Pass notes to the template
    return render_template("admin.html", notes=notes)
    

    
# Rearrange inbox entries by date (descending) and van (ascending)
@app.route("/inbox", methods=["GET", "POST"])
def inbox():
    order_by = request.args.get("order_by", "timestamp")  # Default to ordering by timestamp
    if order_by not in ["timestamp", "van"]:
        order_by = "timestamp"  # Default to timestamp if invalid order_by value(incase of errors)

    if order_by == "timestamp":
        entries = Entry.query.order_by(Entry.timestamp.desc())  # Order by date (descending)
        entry_list = [{"id": entry.id, "van": int(entry.van), "body": entry.body, "timestamp": entry.timestamp} for entry in entries]

        
        # Sort the entry list by date in descending order
        entry_list.sort(key=lambda x: x['timestamp'], reverse=True)
    elif order_by == "van":
        entries = Entry.query.order_by(Entry.van.cast(db.Integer).asc())  # Order by van (ascending) as integers
        entry_list = [{"id": entry.id, "van": int(entry.van), "body": entry.body, "timestamp": entry.timestamp} for entry in entries]
        entry_list.sort(key=lambda x: (x['van'], x['timestamp']))  # Sort by van and then timestamp

    return render_template("inbox.html", entries=entry_list, order_by=order_by)


# Edit button from inbox page for editing entries
@app.route("/update_entry/<int:entry_id>", methods=["POST"])
def update_entry(entry_id):
    # Retrieve the updated content from the request body
    data = request.get_json()
    new_body = data.get("body")

    # Fetch the specific entry from the database
    entry = Entry.query.get(entry_id)

    # If the entry is not found, return an error response
    if not entry:
        return jsonify({"status": "error", "message": "Entry not found."}), 404

    # Update the entry's body
    entry.body = new_body
    
    # Get the current UTC time
    utc_now = datetime.utcnow()
    # Convert UTC time to CST
    cst_time = convert_utc_to_cst(utc_now)
    # Update the entry's timestamp to CST time
    entry.timestamp = cst_time

    # Commit the changes to the database
    db.session.commit()
    
    return jsonify({"status": "success", "message": "Entry updated successfully."})




# Delete note from the databasegit a
@app.route("/admin/delete-note", methods=["POST"])
def delete_note():
    note_id = request.form.get("noteId")
    if note_id:
        note = Note.query.get(note_id)
        if note:
            db.session.delete(note)
            db.session.commit()
    flash("Note deleted successfully")
    return redirect("/admin")
