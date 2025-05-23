from flask import Blueprint, session, flash, redirect, url_for, render_template
from datetime import datetime

history_bp = Blueprint('history', __name__)

@history_bp.route('/pass_history')
def pass_history():
    if 'user_id' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('login'))

    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT id, from_place, to_place, status, created_at 
            FROM pass_requests WHERE user_id=?
            ORDER BY created_at DESC
        ''', (session['user_id'],))
        history = cur.fetchall()

    return render_template('pass_history.html', history=history)
