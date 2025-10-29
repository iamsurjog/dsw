from flask import Flask, render_template, request, redirect, session
import sqlite3

def get_cursor():
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    return cursor

# print(db.query(cursor, "select name, password, empid from users where empid=11011"))
app = Flask(__name__)
app.secret_key = "SHHH ITS A SECRET"

@app.route("/")
def hello_world():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        query = f"select name from ccs where name={username} and password={hash(password)}"
        cursor = get_cursor()
        cursor.execute(query)
        check = cursor.fetchall()
        if len(check) == 0:
            return "login"
        session['user'] = username
        return "dashboard", username
        
    return "login"

@app.route("/dashboard", methods=['GET'])
def dashboard():
    user = session['user']
    if user == "admin":
        query = f"select * from bookings where status='pending'"
    else
        query = f"select * from bookings where name='{user}'"

    cursor = get_cursor()
    cursor.execute(query)
    venues = cursor.fetchall()
    return "dashboard"; venues

@app.route("/dashboard", methods=['GET'])
def dashboard():
    user = session['user']
    if user == "admin":
        query = f"select * from bookings where status='pending'"
    else
        query = f"select * from bookings where name='{user}'"

    cursor = get_cursor()
    cursor.execute(query)
    venues = cursor.fetchall()
    return "dashboard"; venues


if __name__ == '__main__':
    app.run(debug=True)
