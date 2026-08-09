from flask import Flask, request, render_template, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
application = app
app.secret_key = "hacktracker_super_secret_key_2026"

DB_NAME = "/tmp/hackathon.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS hackathons
                 (id INTEGER PRIMARY KEY, name TEXT, company TEXT, date TEXT, location TEXT)''')

    c.execute("SELECT COUNT(*) FROM hackathons")
    if c.fetchone()[0] == 0:
        sample = [
            ("HackTheNorth", "Google", "2026-09-15", "Bangalore"),
            ("CodeFest", "Microsoft", "2026-10-02", "Hyderabad"),
            ("Buildathon", "Amazon", "2026-11-10", "Pune"),
            ("DevJam", "TCS", "2026-12-05", "Chennai")
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
        conn = get_db()
        try:
            conn.execute("INSERT INTO users (name, email, password) VALUES (?,?,?)", (name, email, password))
            conn.commit()
            flash("Registration successful! Please login")
            return redirect(url_for('step2'))
        except:
            flash("Email already exists")
        finally:
            conn.close()
    return render_template("register.html")

@app.route("/api/login", methods=["POST"])
def login():
    email = request.form['email']
    password = request.form['password']
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password)).fetchone()
    conn.close()
    if user:
        session['user'] = email
        session['name'] = user['name']
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid email or password")
        return redirect(url_for('step2'))

@app.route("/dashboard")
def dashboard():
    if 'user' not in session:
        return redirect(url_for('step2'))
    return render_template("dashboard.html", name=session.get('name'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route("/step3")
def step3():
    conn = get_db()
    companies = conn.execute("SELECT DISTINCT company FROM hackathons").fetchall()
    conn.close()
    return render_template("step3.html", companies=companies)

@app.route("/step4", methods=["GET"])
def step4():
    query = request.args.get('q', '')
    conn = get_db()
    if query:
        results = conn.execute("SELECT * FROM hackathons WHERE location LIKE? OR company LIKE?", ('%'+query+'%', '%'+query+'%')).fetchall()
    else:
        results = conn.execute("SELECT * FROM hackathons").fetchall()
    conn.close()
    return render_template("step4.html", results=results, query=query)

@app.route("/step5")
def step5():
    conn = get_db()
    events = conn.execute("SELECT * FROM hackathons ORDER BY date").fetchall()
    conn.close()
    return render_template("step5.html", events=events)

if __name__ == "__main__":
    app.run(debug=True)
