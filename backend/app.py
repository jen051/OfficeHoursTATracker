from flask import Flask, jsonify, g, request
import sqlite3
from datetime import datetime
import csv
import os
from flask_cors import CORS
import json
import random
import threading
import heapq
import time
import hashlib
import socket
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

random_names = []
with open("data/random_names.txt", "r") as f:
    random_names = [line.strip() for line in f if line.strip()]

time_heap = []
THRESHOLD = 25 * 60 

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

# def check_ip():
#     hostname = socket.gethostname()
#     ip = socket.gethostbyname(hostname)
#     return ip == '130.207.113.218'

def log_scan(gtid, name, action, timestamp, instructor_tag):
    cursor.execute("INSERT INTO scans (gtid, name, action, timestamp, instructor_tag) VALUES (?, ?, ?, ?, ?)", 
                (gtid, name, action, timestamp, instructor_tag))
    db_connect.commit()
    #maybe connect to front end and put out a popup when this is triggered

def enqueue_no_id(device_id):
    if device_id not in random_dict:
        random_dict[device_id] = random.choice(random_names)

        random_name = random_dict[device_id]

        if random_name in queue:
            try:
                queue.remove(random_name)
            except ValueError:
                pass
            random_dict.pop(device_id, None)
            return -1, -1
        else:
            queue.append(random_name)
            heapq.heappush(time_heap, (datetime.now(), device_id))
            return random_name, device_id
    else:
        random_name = random_dict[device_id]
        return random_name, device_id

def read_from_scanner(gtid):
    gtid = gtid[6:15] if len(gtid) >= 15 else gtid # extract gtid from string

    # Normal GITD pattern
    pattern = r"^\d{9}$"
    if not re.match(pattern, gtid):
        return -1, -2, -1, -1, -1

    # student scan, add to queue
    if gtid not in name_dictionary:
        # if gtid not in random_dict:
        #     random_dict[gtid] = random.choice(random_names)

        # random_name = random_dict[gtid]

        # if random_name in queue:
        #     queue.pop(0)
        #     random_dict.pop(gtid)
        # else:
        #     queue.append(random_name)
        #     heapq.heappush(time_heap, (datetime.now(), random_name)) # heap fix
        #     return -1, random_name, -1, -1, -1
        return -1, -3, -1, -1, -1
    else:
    #maybe split this into time and date
        time = datetime.now()
        time_str = time.strftime("%B %d, %Y at %I:%M %p")

        if gtid not in action_dictionary or action_dictionary[gtid] == "CLOCK OUT":
            action_dictionary[gtid] = "CLOCK IN"
        else:
            action_dictionary[gtid] = "CLOCK OUT"
        instructor_tag = name_dictionary[gtid][1]
        name = f"{name_dictionary[gtid][0]} ({instructor_tag})"
        

    return gtid, name, action_dictionary[gtid], time_str, instructor_tag


def cleanup_queue():
    while time_heap and (datetime.now() - time_heap[0][0]).total_seconds() > THRESHOLD:
        _, device_id = heapq.heappop(time_heap)
        name = random_dict.pop(device_id, None)
        if name and name in queue:
            try:
                queue.remove(name)
            except ValueError:
                pass

def periodic_cleanup():
    while True:
        cleanup_queue()
        time.sleep(60)

#scan_buffer = []

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
    client_ip = request.remote_addr
    valid_ip = client_ip == '130.207.113.218'
    response = {"ta_name": -1, "valid_ip": False}
    gtid, name, action, time_str, instructor_tag = read_from_scanner(gtid) 
    if gtid != -1 and valid_ip:
       log_scan(gtid, name, action, time_str, instructor_tag)
       response["ta_name"] = name
       response["valid_ip"] = True
    return jsonify(response)

@app.route("/api/button-queue", methods=["POST"])
def button_queue():
    response = {"status": "success"}

    data = request.get_json()
    device_id = data.get("device_id")
    
    if not device_id:
        return jsonify({"status": "error", "message": "Missing device_id"}), 400

    name, device_id = enqueue_no_id(device_id)
    if name != 1:
        response["random_name"] = name
        response["device_id"] = device_id
    return jsonify(response)



@app.route("/api/in-queue-status", methods=["POST", "GET"])
def in_queue_status():
    if request.method == "GET":
        device_id = request.args.get("device_id")
    else:
        data = request.get_json(silent=True) or {}
        device_id = data.get("device_id")

    if not device_id:
        return jsonify({"in_queue": False, "random_name": -1})
        
    status = device_id in random_dict
    response = {}

    response["in_queue"] = status
    response["random_name"] = random_dict[device_id] if status else -1
    return jsonify(response)


@app.route("/api/dequeue", methods=["POST"])
def dequeue():
    data = request.get_json()
    device_id = data.get("device_id")

    if device_id in random_dict:
        name = random_dict.pop(device_id)
        if name in queue:
            queue.remove(name) 
        global time_heap
        time_heap = [t for t in time_heap if t[1] != device_id]
        return jsonify({"status": "success", "removed_name": name})
    return jsonify({"status": "error", "message": "Token not found"}), 404


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
    thread = threading.Thread(target=periodic_cleanup, daemon=True)
    thread.start()
    port = int(os.environ.get("PORT", 8080))

    app.run(debug=True, use_reloader=False, host='0.0.0.0',port=port)

# SQLite database/backend
# store: gtid, timestamps, autolabel clock in/out, map gtid to name, 
# down the line: calculate hours based on clock in/out

#front end
# TA name, PFP, small pop up on scan
