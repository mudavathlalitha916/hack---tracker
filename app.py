import json
import mysql.connector
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
TEMPLATES = ROOT / "templates"

DB_CONFIG = {
    "host": "localhost",
    "user": "hackathon_user",
    "password": "StrongPass123",
    "database": "hackathon_tracker",
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

DEFAULT_HACKATHONS = [
    {
        "name": "AI Builders Summit",
        "company": "Nexora Labs",
        "date": "2026-08-24",
        "time": "09:00",
        "duration": "36h",
        "location": "Remote",
        "fee": "Free",
        "category": "AI / Education",
        "details": "A 36-hour AI challenge focused on building copilots for education and launching a final demo."
    },
    {
        "name": "FinTech Challenge",
        "company": "LedgerPoint",
        "date": "2026-08-28",
        "time": "11:00",
        "duration": "24h",
        "location": "New York",
        "fee": "$25",
        "category": "Finance",
        "details": "A fintech sprint where teams design secure payment experiences and pitch to banking partners."
    },
    {
        "name": "HealthTech Sprint",
        "company": "Medverse",
        "date": "2026-09-02",
        "time": "08:30",
        "duration": "30h",
        "location": "London",
        "fee": "Sponsored",
        "category": "Healthcare",
        "details": "A healthcare innovation hackathon focused on patient support apps and data privacy."
    },
    {
        "name": "Web3 Product Jam",
        "company": "BlockForge",
        "date": "2026-09-10",
        "time": "13:00",
        "duration": "20h",
        "location": "Singapore",
        "fee": "$15",
        "category": "Web3",
        "details": "Build a web3 experience with smart contracts and a polished product demo."
    },
    {
        "name": "Climate Data Hack",
        "company": "GreenGrid",
        "date": "2026-09-14",
        "time": "10:00",
        "duration": "28h",
        "location": "Berlin",
        "fee": "Free",
        "category": "Sustainability",
        "details": "Solve sustainability problems with data dashboards and live climate simulations."
    },
    {
        "name": "Campus Connect Marathon",
        "company": "CodeWave",
        "date": "2026-09-18",
        "time": "10:00",
        "duration": "26h",
        "location": "San Francisco",
        "fee": "$10",
        "category": "Student",
        "details": "Campus teams build new student services, collaboration tools, and campus life products."
    },
    {
        "name": "Product Design Hack",
        "company": "PixelSprint",
        "date": "2026-09-22",
        "time": "12:00",
        "duration": "18h",
        "location": "Toronto",
        "fee": "$20",
        "category": "Design",
        "details": "A design-first hackathon for user experience and product innovation teams."
    },
    {
        "name": "Climate Tech Challenge",
        "company": "EcoPulse",
        "date": "2026-09-26",
        "time": "09:30",
        "duration": "24h",
        "location": "Austin",
        "fee": "Free",
        "category": "Environment",
        "details": "Build products that reduce waste, measure carbon, or improve energy efficiency."
    },
    {
        "name": "LaunchPad Sprint",
        "company": "InnoSpark",
        "date": "2026-09-30",
        "time": "10:00",
        "duration": "22h",
        "location": "Seattle",
        "fee": "$12",
        "category": "Startup",
        "details": "Early-stage founders create launch-ready prototypes and investor-ready demos."
    },
    {
        "name": "Bengaluru AI Clash",
        "company": "IndiaTech Labs",
        "date": "2026-09-05",
        "time": "09:00",
        "duration": "24h",
        "location": "Bangalore",
        "fee": "Free",
        "category": "AI",
        "details": "A local Bengaluru hackathon focused on AI assistants, automation, and smart campus solutions."
    },
    {
        "name": "Mumbai FinTech Fest",
        "company": "PayPulse",
        "date": "2026-09-12",
        "time": "10:30",
        "duration": "20h",
        "location": "Mumbai",
        "fee": "$15",
        "category": "Finance",
        "details": "Fintech teams create payment, savings, and budgeting platforms for Indian users."
    },
    {
        "name": "Delhi Civic Impact Jam",
        "company": "UrbanHack",
        "date": "2026-09-19",
        "time": "08:30",
        "duration": "26h",
        "location": "New Delhi",
        "fee": "Free",
        "category": "CivicTech",
        "details": "Build civic engagement tools, public services, and community insights for Delhi."
    },
    {
        "name": "Hyderabad CloudSprint",
        "company": "CloudOps India",
        "date": "2026-09-24",
        "time": "11:00",
        "duration": "18h",
        "location": "Hyderabad",
        "fee": "$20",
        "category": "Cloud",
        "details": "A developer hackathon centered on DevOps, cloud automation, and scalable services."
    },
    {
        "name": "Chennai EduHack",
        "company": "LearnLeap",
        "date": "2026-09-28",
        "time": "09:30",
        "duration": "22h",
        "location": "Chennai",
        "fee": "Free",
        "category": "Education",
        "details": "Create next-gen learning tools, student communities, and classroom support apps."
    }
]


def init_db():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS registers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NULL,
            email VARCHAR(255),
            success BOOLEAN NOT NULL,
            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES registers(id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS hackathons (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            company VARCHAR(255) NOT NULL,
            date DATE NOT NULL,
            time VARCHAR(10) NOT NULL,
            duration VARCHAR(20) NOT NULL,
            location VARCHAR(255) NOT NULL,
            fee VARCHAR(50) NOT NULL,
            category VARCHAR(255) NOT NULL,
            details TEXT NOT NULL
        )
        """
    )

    cursor.execute("SELECT COUNT(*) FROM hackathons")
    count = cursor.fetchone()[0]
    if count == 0:
        for event in DEFAULT_HACKATHONS:
            cursor.execute(
                "INSERT INTO hackathons (name, company, date, time, duration, location, fee, category, details) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                [
                    event["name"],
                    event["company"],
                    event["date"],
                    event["time"],
                    event["duration"],
                    event["location"],
                    event["fee"],
                    event["category"],
                    event["details"],
                ],
            )

    connection.commit()
    cursor.close()
    connection.close()


def query_hackathons():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM hackathons ORDER BY date, time")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows


def find_user(email):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM registers WHERE email = %s", (email,))
    row = cursor.fetchone()
    cursor.close()
    connection.close()
    return row


def create_user(name, email, password):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO registers (name, email, password) VALUES (%s, %s, %s)",
            (name, email, password),
        )
        connection.commit()
        return True
    except mysql.connector.IntegrityError:
        return False
    finally:
        cursor.close()
        connection.close()


def record_login_attempt(email, success, user_id=None):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO login_attempts (user_id, email, success) VALUES (%s, %s, %s)",
        (user_id, email, success),
    )
    connection.commit()
    cursor.close()
    connection.close()


def parse_json_request(self):
    length = int(self.headers.get("Content-Length", 0))
    body = self.rfile.read(length) if length else b""
    if not body:
        return {}
    return json.loads(body.decode("utf-8"))


def send_json_response(self, data, status=200):
    response = json.dumps(data).encode("utf-8")
    self.send_response(status)
    self.send_header("Content-Type", "application/json; charset=utf-8")
    self.send_header("Content-Length", str(len(response)))
    self.end_headers()
    self.wfile.write(response)


class TrackerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/hackathons":
            send_json_response(self, query_hackathons())
            return

        page_map = {
            "/": "index.html",
            "/signup": "signup.html",
            "/login": "login.html",
            "/dashboard": "dashboard.html",
            "/step1": "step1.html",
            "/step2": "step2.html",
            "/step3": "step3.html",
            "/step4": "step4.html",
            "/step5": "step5.html",
        }

        if path in page_map:
            file_path = TEMPLATES / page_map[path]
            content = file_path.read_text(encoding="utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content.encode("utf-8"))))
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
            return

        return super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        body = parse_json_request(self)

        if path == "/api/signup":
            name = body.get("name", "").strip()
            email = body.get("email", "").strip().lower()
            password = body.get("password", "").strip()

            if not name or not email or not password:
                send_json_response(self, {"error": "All fields are required."}, status=400)
                return

            if create_user(name, email, password):
                send_json_response(self, {"message": "Account created."})
            else:
                send_json_response(self, {"error": "Email already exists."}, status=409)
            return

        if path == "/api/login":
            email = body.get("email", "").strip().lower()
            password = body.get("password", "").strip()

            if not email or not password:
                send_json_response(self, {"error": "Email and password are required."}, status=400)
                return

            user = find_user(email)
            if not user:
                send_json_response(self, {"error": "No account found with that email."}, status=404)
                return

            if user["password"] != password:
                send_json_response(self, {"error": "Incorrect password."}, status=401)
                return

            send_json_response(self, {"message": "Login successful.", "user": {"name": user["name"], "email": user["email"]}})
            return

        self.send_error(404, "Not found")


if __name__ == "__main__":
    init_db()
    port = 8000
    server = ThreadingHTTPServer(("0.0.0.0", port), TrackerHandler)
    print(f"Hackathon Tracker is running at http://localhost:{port}")
    server.serve_forever()
