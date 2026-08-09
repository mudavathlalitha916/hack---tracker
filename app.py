from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)
application = app # Vercel kosam idhi must

DB_NAME = "hackathon.db"

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

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name, email FROM users WHERE email=? AND password=?", (email, password))
    user = c.fetchone()
    conn.close()
    
    if user:
        return jsonify({"message": "Login successful.", "user": {"name": user[0], "email": user[1]}})
    else:
        return jsonify({"error": "Invalid credentials"}), 401
application=app
if __name__ == '__main__':
    app.run(debug=True)
