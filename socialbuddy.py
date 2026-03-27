from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'socialbuddy_secret_2024'

import os
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# ── MODELS (Tables) ──
class User(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name  = db.Column(db.String(50), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    phone      = db.Column(db.String(15))
    password   = db.Column(db.String(200), nullable=False)
    plan       = db.Column(db.String(10), default='free')
    created_at = db.Column(db.DateTime, default=datetime)

class Contact(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100))
    email      = db.Column(db.String(120))
    phone      = db.Column(db.String(15))
    subject    = db.Column(db.String(200))
    message    = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime)

# ── ROUTES ──
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        new_msg = Contact(
            name    = request.form.get('name'),
            email   = request.form.get('email'),
            phone   = request.form.get('phone'),
            subject = request.form.get('subject'),
            message = request.form.get('message')
        )
        db.session.add(new_msg)
        db.session.commit()
        flash(f"Thanks {request.form.get('name')}! We'll get back to you soon.", 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Check if email exists
        existing = User.query.filter_by(email=request.form['email']).first()
        if existing:
            flash('This email is already registered! Please login.', 'error')
            return redirect(url_for('register'))

        # Hash password
        hashed_pw = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        new_user = User(
            first_name = request.form['first_name'],
            last_name  = request.form['last_name'],
            email      = request.form['email'],
            phone      = request.form.get('phone'),
            password   = hashed_pw,
            plan       = request.form.get('plan', 'free')
        )
        db.session.add(new_user)
        db.session.commit()

        flash(f'Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()

        if user and bcrypt.check_password_hash(user.password, request.form['password']):
            session['user_id']   = user.id
            session['user_name'] = user.first_name
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Wrong email or password. Try again!', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

# ── CREATE TABLES ──
with app.app_context():
    db.create_all()
    print("✅ Tables created!")

if __name__ == '__main__':
    app.run(debug=True)
