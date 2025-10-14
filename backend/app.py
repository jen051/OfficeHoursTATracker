from flask import Flask, jsonify, g, request
import sqlite3
from datetime import datetime
import csv
import os
from flask_cors import CORS  # pip install flask-cors (for dev)
import json
import random
import threading
#from endev import InputDevice, list_devices, ecodes
#from pynput import keyboard
import re

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
DB = "data/scans.db"

action_dictionary = {}
queue = []
i = 0

random_dict = {}

random_names = [
    "Anonymous Werewolf",
    "Anonymous Mummy",
    "Anonymous Skeleton",
    "Anonymous Saja Boy",
    "Anonymous Vampire",
    "Anonymous Zombie",
    "Anonymous Ghost",
    "Anonymous Witch",
    "Anonymous Goblin",
    "Anonymous Phantom",
    "Anonymous Troll",
    "Anonymous Banshee",
    "Anonymous Kraken",
    "Anonymous Elf",
    "Anonymous Warlock",
    "Anonymous Demon",
    "Anonymous Lich",
    "Anonymous Ogre",
    "Anonymous Specter",
    "Anonymous Harpy",
    "Anonymous Shade",
    "Anonymous Golem",
    "Anonymous Wraith",
    "Anonymous Reaper",
    "Anonymous Imp",
    "Anonymous Siren",
    "Anonymous Centaur",
    "Anonymous Chimera",
    "Anonymous Djinn",
    "Anonymous Basilisk"
]

# Scanning Process

# Getting names from csv file
name_dictionary = {}
base_dir = os.path.dirname("data/")  # directory of the script
file_path = os.path.join(base_dir, "names.csv")

with open(file_path, mode='r', encoding='utf-8-sig') as file:
    reader = csv.DictReader(file)
    name_dictionary = {row["GTID"]: (row["Name"], row["Instructor_Tag"]) for row in reader}

db_connect = sqlite3.connect(DB, check_same_thread=False)

cursor = db_connect.cursor()

# make query here

query = """
CREATE TABLE IF NOT EXISTS scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gtid TEXT NOT NULL,
    name TEXT NOT NULL,
    action TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    instructor_tag TEXT NOT NULL
)
"""

cursor.execute(query)

db_connect.commit()

def log_scan(gtid, name, action, timestamp, instructor_tag):
    cursor.execute("INSERT INTO scans (gtid, name, action, timestamp, instructor_tag) VALUES (?, ?, ?, ?, ?)", 
                (gtid, name, action, timestamp, instructor_tag))
    db_connect.commit()
    #maybe connect to front end and put out a popup when this is triggered

def read_from_scanner(gtid):
    gtid = gtid[6:15] if len(gtid) >= 15 else gtid # extract gtid from string

    # Normal GITD pattern
    pattern = r"^\d{9}$"
    if not re.match(pattern, gtid):
        return -1, -1, -1, -1, -1

    # student scan, add to queue
    if gtid not in name_dictionary:
        if gtid not in random_dict:
            random_dict[gtid] = random.choice(random_names)

        if random_dict[gtid] in queue:
            queue.pop(0)
            random_dict.pop(gtid)
        else:
            queue.append(random_dict[gtid])
        return -1, -1, -1, -1, -1
    else:
    #maybe split this into time and date
        time = datetime.now()
        time_str = time.strftime("%B %d, %Y at %I:%M %p")

        if gtid not in action_dictionary or action_dictionary[gtid] == "CLOCK OUT":
            action_dictionary[gtid] = "CLOCK IN"
        else:
            action_dictionary[gtid] = "CLOCK OUT"

        name = name_dictionary[gtid][0]
        instructor_tag = name_dictionary[gtid][1]

    return gtid, name, action_dictionary[gtid], time_str, instructor_tag

scan_buffer = []

# def on_press(key):
#     global scan_buffer
#     try:
#         # Normal key (letters, numbers, etc.)
#         scan_buffer.append(key.char)
#     except AttributeError:
#         # Special keys (Enter, Shift, etc.)
#         if key == keyboard.Key.enter:
#             gtid = ''.join(scan_buffer)  # join characters into a string
#             scan_buffer = []             # clear buffer for next scan
#             # Example: extract GTID portion
#             gtid, name, action, time_str, instructor_tag = read_from_scanner(gtid) 
#             if gtid != -1:
#                 log_scan(gtid, name, action, time_str, instructor_tag)

#listener = keyboard.Listener(on_press=on_press)
#listener.daemon = True
#listener.start()

# def main_loop():
#     while True:
#         try:
#             gtid, name, action, time_str, instructor_tag = read_from_scanner()
#             if gtid == -1:
#                 continue
#             log_scan(gtid, name, action, time_str, instructor_tag)
#         except KeyError: #CHANGE THIS INTERRUPT
#             #add logic to make popup on front end
#             continue

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

@app.route("/api/manual-scan", methods=["POST"])
def manual_scan():
    gtid = request.get_json()["gtid"]
    print("Received JSON:", gtid)
    gtid, name, action, time_str, instructor_tag = read_from_scanner(gtid) 
    if gtid != -1:
       log_scan(gtid, name, action, time_str, instructor_tag)
    print(jsonify({"status": "success"}))
    return jsonify({"status": "success"})


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
    clocked_in_tas = [r[0] for r in rows if r[1] == "CLOCK IN"]
    return jsonify(clocked_in_tas)

@app.get("/api/queue")
def get_queue():
    return jsonify(queue)

if __name__ == '__main__':
    #t = threading.Thread(target = main_loop, daemon = True)
    #t.start()
    port = int(os.environ.get("PORT", 8080))

    app.run(debug=True, use_reloader=False, host='0.0.0.0',port=port)

# SQLite database/backend
# store: gtid, timestamps, autolabel clock in/out, map gtid to name, 
# down the line: calculate hours based on clock in/out

#front end
# TA name, PFP, small pop up on scan