from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

# SQLite database/backend
# store: gtid, timestamps, autolabel clock in/out, map gtid to name, 
# down the line: calculate hours based on clock in/out

#front end
# TA name, PFP, small pop up on scan