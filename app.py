from flask import Flask, render_template, request, redirect, session
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = "SHHH ITS A SECRET"

def get_db_connection():
    conn = sqlite3.connect('db.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def hello_world():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form['user_type']
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        if user_type == 'student':
            user = conn.execute('SELECT * FROM CCs WHERE name = ?', (username,)).fetchone()
        elif user_type == 'faculty':
            user = conn.execute('SELECT * FROM Faculty WHERE name = ?', (username,)).fetchone()
        else:
            return "Invalid user type", 400
        
        conn.close()

        if user and hashlib.sha256(password.encode()).hexdigest() == user['password']:
            session['user'] = username
            session['user_type'] = user_type
            if user_type == 'student':
                return redirect('/student/dashboard')
            elif user_type == 'faculty':
                return redirect('/faculty/dashboard')
        else:
            return "Invalid credentials", 401
        
    return render_template("login.html")

@app.route('/student/dashboard')
def student_dashboard():
    if 'user' not in session or session.get('user_type') != 'student':
        return redirect('/login')
    
    conn = get_db_connection()
    approved_events = conn.execute('SELECT * FROM Bookings WHERE Name = ? AND Status = ?', (session['user'], 'approved')).fetchall()
    pending_events = conn.execute('SELECT * FROM Bookings WHERE Name = ? AND Status = ?', (session['user'], 'pending')).fetchall()
    conn.close()
    
    return render_template('student_dashboard.html', approved_events=approved_events, pending_events=pending_events)

@app.route('/faculty/dashboard')
def faculty_dashboard():
    if 'user' not in session or session.get('user_type') != 'faculty':
        return redirect('/login')
    
    conn = get_db_connection()
    approved_events = conn.execute('SELECT * FROM Bookings WHERE Status = ?', ('approved',)).fetchall()
    pending_events = conn.execute('SELECT * FROM Bookings WHERE Status = ?', ('pending',)).fetchall()
    conn.close()
    
    return render_template('faculty_dashboard.html', approved_events=approved_events, pending_events=pending_events)

@app.route('/venue_availability', methods=['GET', 'POST'])
def venue_availability():
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        venue = request.form.get('venue', 'all')

        conn = get_db_connection()
        
        query = '''
            SELECT * FROM venues 
            WHERE name NOT IN (
                SELECT Venue FROM Bookings
                WHERE (
                    (Start_Date < ? AND End_Date > ?) OR
                    (Start_Date = ? AND Start_Time < ?) OR
                    (End_Date = ? AND End_Time > ?)
                )
            )
        '''

        params = [end_date, start_date, start_date, end_time, end_date, start_time]

        if venue != 'all':
            query += ' AND name = ?'
            params.append(venue)
            
        available_venues = conn.execute(query, tuple(params)).fetchall()
        conn.close()
        
        return render_template('venue_availability.html', venues=available_venues)
    
    return render_template('venue_availability.html', venues=[])

@app.route('/book_venue', methods=['GET', 'POST'])
def book_venue():
    if 'user' not in session or session.get('user_type') != 'student':
        return redirect('/login')
        
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        venue = request.form['venue']
        event_name = request.form['event_name']
        
        conn = get_db_connection()
        query = '''
            SELECT * FROM venues 
            WHERE name NOT IN (
                SELECT Venue FROM Bookings
                WHERE (
                    (Start_Date < ? AND End_Date > ?) OR
                    (Start_Date = ? AND Start_Time < ?) OR
                    (End_Date = ? AND End_Time > ?)
                )
            )
        '''

        params = [end_date, start_date, start_date, end_time, end_date, start_time]

        if venue != 'all':
            query += ' AND name = ?'
            params.append(venue)
            
        available_venues = conn.execute(query, tuple(params)).fetchall()
        if len(available_venues) == 0:
            conn.execute('INSERT INTO Bookings (Venue, Start_Time, Start_Date, End_Time, End_Date, Name, Status, Event_Name) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                         (venue, start_time, start_date, end_time, end_date, session['user'], 'pending', event_name))
            conn.commit()
            conn.close()
            
            return redirect('/student/dashboard')
        
        return render_template('book_venue.html', error=True)

    conn = get_db_connection()
    venues = conn.execute('SELECT name FROM venues').fetchall()
    previous_bookings = conn.execute('SELECT * FROM Bookings WHERE Name = ?', (session['user'],)).fetchall()
    conn.close()

    return render_template('book_venue.html', venues=venues, previous_bookings=previous_bookings)

@app.route('/approve_booking/<int:booking_id>', methods=['POST'])
def approve_booking(booking_id):
    if 'user' not in session or session.get('user_type') != 'faculty':
        return redirect('/login')
        
    conn = get_db_connection()
    conn.execute('UPDATE Bookings SET Status = ? WHERE Booking_ID = ?', ('approved', booking_id))
    conn.commit()
    conn.close()
    
    return redirect('/faculty/dashboard')

@app.route('/reject_booking/<int:booking_id>', methods=['POST'])
def reject_booking(booking_id):
    if 'user' not in session or session.get('user_type') != 'faculty':
        return redirect('/login')
        
    conn = get_db_connection()
    conn.execute('UPDATE Bookings SET Status = ? WHERE Booking_ID = ?', ('rejected', booking_id))
    conn.commit()
    conn.close()
    
    return redirect('/faculty/dashboard')

if __name__ == '__main__':
    app.run(debug=True)
