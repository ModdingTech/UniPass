from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def init_db():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        
        # Drop existing tables if they exist
        cur.execute("DROP TABLE IF EXISTS pass_requests")
        cur.execute("DROP TABLE IF EXISTS users")
        
        # Create users table
        cur.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                age INTEGER,
                address TEXT,
                phone TEXT
            )
        ''')
        
        # Create pass_requests table
        cur.execute('''
            CREATE TABLE pass_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                from_place TEXT NOT NULL,
                to_place TEXT NOT NULL,
                via1 TEXT,
                via2 TEXT,
                status TEXT NOT NULL DEFAULT 'Processing',
                created_at TEXT NOT NULL,
                expiry_date TEXT,
                estimated_arrival TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not (email and password):
            flash("Please enter both email and password.", "danger")
            return redirect(url_for('login'))

        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, password FROM users WHERE email=?", (email,))
            user = cur.fetchone()

            if user and check_password_hash(user[1], password):
                session['user_id'] = user[0]
                flash("Logged in successfully!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid email or password.", "danger")
                return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        age = request.form.get('age', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()

        if not (name and email and password and phone):
            flash("Name, email, password, and phone number are required.", "danger")
            return render_template('register.html', name=name, email=email, age=age, address=address, phone=phone)

        if age and not age.isdigit():
            flash("Age must be a number.", "danger")
            return render_template('register.html', name=name, email=email, age=age, address=address, phone=phone)

        if not phone.isdigit() or len(phone) != 10:
            flash("Please enter a valid 10-digit phone number.", "danger")
            return render_template('register.html', name=name, email=email, age=age, address=address, phone=phone)

        hashed_password = generate_password_hash(password)

        try:
            with sqlite3.connect('database.db') as conn:
                cur = conn.cursor()
                cur.execute('''
                    INSERT INTO users (name, email, password, age, address, phone)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (name, email, hashed_password, int(age) if age else None, address, phone))
                conn.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Email already registered. Please login instead.", "danger")
            return render_template('register.html', name=name, email=email, age=age, address=address, phone=phone)

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT id, from_place, to_place, via1, via2, status, created_at, expiry_date, estimated_arrival 
            FROM pass_requests WHERE user_id=?
            ORDER BY created_at DESC
        ''', (user_id,))
        passes = cur.fetchall()

    return render_template('dashboard.html', passes=passes)

@app.route('/apply_pass', methods=['GET', 'POST'])
def apply_pass():
    if 'user_id' not in session:
        flash("Please login to apply for a pass.", "warning")
        return redirect(url_for('login'))

    if request.method == 'POST':
        from_place = request.form.get('from_place', '').strip()
        to_place = request.form.get('to_place', '').strip()
        via1 = request.form.get('via1', '').strip()
        via2 = request.form.get('via2', '').strip()

        if not (from_place and to_place):
            flash("From and To places are required.", "danger")
            return render_template('apply_pass.html', from_place=from_place, to_place=to_place, via1=via1, via2=via2)

        current_time = datetime.now()
        expiry_date = (current_time + timedelta(days=365)).strftime('%Y-%m-%d')
        estimated_arrival = (current_time + timedelta(days=3)).strftime('%Y-%m-%d')

        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO pass_requests (user_id, from_place, to_place, via1, via2, status, created_at, expiry_date, estimated_arrival)
                VALUES (?, ?, ?, ?, ?, 'Processing', ?, ?, ?)
            ''', (session['user_id'], from_place, to_place, via1, via2, 
                  current_time.strftime('%Y-%m-%d %H:%M:%S'), expiry_date, estimated_arrival))
            pass_id = cur.lastrowid
            conn.commit()

        flash(f"Pass application submitted! Your Pass ID: {pass_id}", "success")
        flash("We will notify you by SMS when your pass arrives at the nearest station.", "info")
        return redirect(url_for('dashboard'))

    return render_template('apply_pass.html')

@app.route('/track_pass')
def track_pass():
    if 'user_id' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('login'))

    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT id, from_place, to_place, via1, via2, status, created_at, expiry_date, estimated_arrival 
            FROM pass_requests WHERE user_id=?
            ORDER BY created_at DESC
        ''', (session['user_id'],))
        passes = cur.fetchall()

    return render_template('track_pass.html', passes=passes)

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/delete_pass/<int:pass_id>')
def delete_pass(pass_id):
    if 'user_id' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('login'))

    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT user_id FROM pass_requests WHERE id=?', (pass_id,))
        result = cur.fetchone()
        
        if not result or result[0] != session['user_id']:
            flash("Unauthorized access.", "danger")
            return redirect(url_for('track_pass'))
            
        cur.execute('DELETE FROM pass_requests WHERE id=?', (pass_id,))
        conn.commit()
        
    flash("Pass application deleted successfully.", "success")
    return redirect(url_for('track_pass'))



@app.before_request
def initialize_database():
    # Initialize database only once
    if not hasattr(app, 'db_initialized'):
        init_db()
        app.db_initialized = True

if __name__ == '__main__':
    app.run(debug=True)
