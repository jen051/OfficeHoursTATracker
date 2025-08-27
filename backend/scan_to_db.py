import sqlite3
import time
from datetime import datetime
import csv
import os

database_file = "scans.db"

action_dictionary = {}

# Getting names from csv file
name_dictionary = {}
base_dir = os.path.dirname(__file__)  # directory of the script
file_path = os.path.join(base_dir, "names.csv")

with open(file_path, mode='r', encoding='utf-8-sig') as file:
    reader = csv.DictReader(file)
    name_dictionary = {row["GTID"]: row["Name"] for row in reader}

db_connect = sqlite3.connect(database_file)

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
            log_scan(gtid, name, action_dictionary[gtid], time_str)
        except KeyboardInterrupt:
            db_connect.close()

if __name__ == "__main__":
    main_loop()






