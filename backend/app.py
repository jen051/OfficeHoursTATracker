from flask import Flask, jsonify, g
import sqlite3
from datetime import datetime
import csv
import os
from flask_cors import CORS  # pip install flask-cors (for dev)
# from scan_to_db import log_scan, read_from_scanner, db_connect, action_dictionary, queue
import json
import threading

app = Flask(__name__)
DB = "data/scans.db"

action_dictionary = {}
queue = []

# Scanning Process

# Getting names from csv file
name_dictionary = {}
base_dir = os.path.dirname("data/")  # directory of the script
file_path = os.path.join(base_dir, "names.csv")

with open(file_path, mode='r', encoding='utf-8-sig') as file:
    reader = csv.DictReader(file)
    name_dictionary = {row["GTID"]: row["Name"] for row in reader}

db_connect = sqlite3.connect(DB, check_same_thread=False)

cursor = db_connect.cursor()

# make query here

query = """
CREATE TABLE IF NOT EXISTS scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gtid TEXT NOT NULL,
    name TEXT NOT NULL,
    action TEXT NOT NULL,
    timestamp TEXT NOT NULL
)
"""

cursor.execute(query)

db_connect.commit()

def log_scan(gtid, name, action, timestamp):
    cursor.execute("INSERT INTO scans (gtid, name, action, timestamp) VALUES (?, ?, ?, ?)", 
                (gtid, name, action, timestamp))
    db_connect.commit()
    #maybe connect to front end and put out a popup when this is triggered

def read_from_scanner():
    gtid = input()
    gtid = gtid[6:15] # extract gtid from string

    # student scan, add to queue
    if gtid not in name_dictionary:
        cropped_gtid = gtid[-4:]
        if cropped_gtid in queue:
            queue.pop(0)
        else:
            queue.append(cropped_gtid)
        return -1, -1, -1, -1
    else:
    #maybe split this into time and date
        time = datetime.now()
        time_str = time.strftime("%B %d, %Y at %I:%M %p")

        if gtid not in action_dictionary or action_dictionary[gtid] == "CLOCK OUT":
            action_dictionary[gtid] = "CLOCK IN"
        else:
            action_dictionary[gtid] = "CLOCK OUT"

        name = name_dictionary[gtid]

    return gtid, name, action_dictionary[gtid], time_str

def main_loop():
    while True:
        try:
            gtid, name, action_dictionary[gtid], time_str = read_from_scanner()
            if gtid == -1:
                continue
            log_scan(gtid, name, action_dictionary[gtid], time_str)
        except KeyError: #CHANGE THIS INTERRUPT
            #add logic to make popup on front end
            continue



# Helpers

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row  # makes rows behave like dicts
    return g.db

def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.get("/api/scans")
def scans():
    db = get_db()
    # conn = sqlite3.connect("scans.db")
    # cursor = conn.cursor()
    # # Get the latest event for each user
    query = """
        SELECT name, action 
        FROM scans 
        WHERE id IN (
            SELECT MAX(id) FROM scans GROUP BY name
        )
    """
    rows = db.execute(query).fetchall()
    # print(rows[0])
    clocked_in_tas = [r[0] for r in rows if r[1] == "CLOCK IN"]
    return jsonify(clocked_in_tas)

@app.get("/api/queue")
def get_queue():
    return jsonify(queue)

if __name__ == '__main__':
    t = threading.Thread(target = main_loop, daemon = True)
    t.start()
    
    app.run(debug=True, use_reloader=False, host='0.0.0.0')

# SQLite database/backend
# store: gtid, timestamps, autolabel clock in/out, map gtid to name, 
# down the line: calculate hours based on clock in/out

#front end
# TA name, PFP, small pop up on scan