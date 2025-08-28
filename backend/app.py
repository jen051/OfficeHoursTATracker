from flask import Flask, jsonify, g
import sqlite3
from flask_cors import CORS  # pip install flask-cors (for dev)
from scan_to_db import log_scan, read_from_scanner, db_connect, action_dictionary

app = Flask(__name__)
DB = "data/scans.db"

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
    print(clocked_in_tas)
    return jsonify(clocked_in_tas)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

# SQLite database/backend
# store: gtid, timestamps, autolabel clock in/out, map gtid to name, 
# down the line: calculate hours based on clock in/out

#front end
# TA name, PFP, small pop up on scan