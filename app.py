from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
application = app # Vercel kosam
app.secret_key = "hacktracker_secret_123456"

DB_NAME = "/tmp/hackathon.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT)''')

    # Sample hackathons data
    c.execute('''CREATE TABLE IF NOT EXISTS hackathons
                 (id INTEGER PRIMARY KEY, name TEXT, company TEXT, date TEXT, location TEXT)''')

    # Check if data already exists
    c.execute("SELECT COUNT(*) FROM hackathons")
    if c.fetchone()[0] == 0:
        sample = [
            ("HackTheNorth", "Google", "2026-09-15", "Bangalore"),
            ("CodeFest", "Microsoft", "2026-10-02", "Hyderabad"),
            ("Buildathon", "Amazon", "2026-11-10", "Pune")
        ]
        c.executemany("INSERT INTO hackathons (name, company, date, location) VALUES (?,?,?,?)", sample)

    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/step2")
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
            c.execute("INSERT INTO users (name, email, password) VALUES (?,?,?)", (name, email, password))
            conn.commit()
            flash("Registration successful! Please login")
            return redirect(url_for('step2'))
        except:
            flash("Email already exists")
            return redirect(url_for('register'))
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
        flash("Invalid email or password")
        return redirect(url_for('step2'))

@app.route("/dashboard")
def dashboard():
    if 'user' in session:
        return render_template("dashboard.html")
    return redirect(url_for('step2'))

# Step 3,4,5 routes
@app.route("/step3")
def step3():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT DISTINCT company FROM hackathons")
    companies = [row[0] for row in c.fetchall()]
    conn.close()
    return render_template("step3.html", companies=companies)

@app.route("/step4")
def step4():
    query = request.args.get('q', '')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if query:
        c.execute("SELECT * FROM hackathons WHERE location LIKE? OR company LIKE?", ('%'+query+'%', '%'+query+'%'))
    else:
        c.execute("SELECT * FROM hackathons")
    results = c.fetchall()
    conn.close()
    return render_template("step4.html", results=results, query=query)

@app.route("/step5")
def step5():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM hackathons ORDER BY date")
    events = c.fetchall()
    conn.close()
    return render_template("step5.html", events=events)

if __name__ == "__main__":
    app.run(debug=True)
