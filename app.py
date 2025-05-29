from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import re
import os

app = Flask(__name__)
app.secret_key = 'mopas_secret_key'

DB_NAME = 'database/mopas.db'

# Initialize database and tables
def init_db():
    if not os.path.exists('database'):
        os.makedirs('database')
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            second_name TEXT,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            group_no TEXT UNIQUE NOT NULL,
            contact TEXT NOT NULL,
            contribution INTEGER DEFAULT 0 CHECK(contribution BETWEEN 0 AND 100)
        )
    ''')
    conn.commit()
    conn.close()

# Home / Landing Page
@app.route('/')
def home():
    return render_template('index.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first = request.form['first_name'].strip()
        second = request.form.get('second_name', '').strip()
        last = request.form['last_name'].strip()
        email = request.form['email'].strip()
        group_no = request.form['group_no'].strip()
        contact = request.form['contact'].strip()

        # Validate group number format
        if not re.match(r'^mopas([5-9][0-9]{2,}|[1-9][0-9]{3,})J$', group_no):
            flash("Group No must be in format like mopas532J (number 500 or above).")
            return redirect(url_for('register'))

        # Validate email basic format
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            flash("Invalid email address.")
            return redirect(url_for('register'))

        # Save user to DB
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (first_name, second_name, last_name, email, group_no, contact)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (first, second, last, email, group_no, contact))
            conn.commit()
            conn.close()
            flash("Registration successful! Please login.")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Email or Group No already exists.")
            return redirect(url_for('register'))

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        group_no = request.form['group_no'].strip()

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND group_no = ?', (email, group_no))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or group number.")
            return redirect(url_for('login'))

    return render_template('login.html')

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please login first.")
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT first_name, contribution FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()

    if user:
        user_data = {
            'first_name': user[0],
            'contribution': user[1]
        }
        return render_template('dashboard.html', user=user_data)
    else:
        flash("User not found.")
        return redirect(url_for('login'))

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for('home'))

# Apply to lead intercessors route
@app.route('/apply-lead-intercessors', methods=['GET', 'POST'])
def apply_lead_intercessors():
    if request.method == 'POST':
        # Here you would process and send email or save application
        # For now, just flash success
        flash("Application to lead intercessors sent successfully!")
        return redirect(url_for('dashboard'))
    # Show form with info on days and times
    return render_template('apply_lead_intercessors.html')

# Apply to host mission route
@app.route('/apply-host-mission', methods=['GET', 'POST'])
def apply_host_mission():
    if request.method == 'POST':
        # Process form and send email or save data
        flash("Application to host mission sent successfully!")
        return redirect(url_for('dashboard'))
    return render_template('apply_host_mission.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
