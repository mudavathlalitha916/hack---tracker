from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
application = app # Vercel kosam idhi must
app.secret_key = "hacktracker_secret_key" # session kosam

# Vercel lo /tmp lo matrame write cheyyachu
DB_NAME = "/tmp/hackathon.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/step2")  # Sign in button kosam
def step2():
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
            conn.commit()
            return redirect(url_for('step2'))
        except:
            return "Email already exists"
        finally:
            conn.close()
    return render_template("register.html")

@app.route("/api/login", methods=["POST"])
def login():
    email = request.form['email']
    password = request.form['password']
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = c.fetchone()
    conn.close()
    if user:
        session['user'] = email
        return redirect(url_for('dashboard'))
    else:
        return "Invalid credentials"

@app.route("/dashboard")
def dashboard():
    if 'user' in session:
        return render_template("dashboard.html")
    return redirect(url_for('step2'))

if __name__ == "__main__":
    app.run(debug=True)
