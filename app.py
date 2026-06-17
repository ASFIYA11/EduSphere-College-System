import os
import sqlite3
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'edusphere_secure_master_matrix_9981')
CORS(app)

# Persistent In-Memory DB Node for Zero-Latency Cloud Tracking
_cloud_db = sqlite3.connect(':memory:', check_same_thread=False)
_cloud_db.row_factory = sqlite3.Row

def init_db():
    cursor = _cloud_db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, password TEXT, role TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS students (roll_no TEXT PRIMARY KEY, name TEXT, attendance_pct REAL, backlogs INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS student_marks (id INTEGER PRIMARY KEY AUTOINCREMENT, roll_no TEXT, subject_name TEXT, marks_obtained INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS faculty (faculty_id TEXT PRIMARY KEY, name TEXT, salary REAL, attendance_pct REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS timetable (id INTEGER PRIMARY KEY AUTOINCREMENT, faculty_id TEXT, subject_name TEXT, class_time TEXT)")
    
    # Core Admin Seed
    cursor.execute("INSERT OR IGNORE INTO users VALUES ('admin', 'admin123', 'admin')")
    _cloud_db.commit()

init_db()

# Initialize Google GenAI SDK
ai_client = genai.Client(api_key=os.getenv('GEMINI_API_KEY', 'MOCK_KEY'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json(silent=True) or request.form
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    selected_role = data.get('role', '').strip().lower()
    
    # 🌟 OPEN ACCESS FOR ANY NEW USER: If they don't exist, register them instantly!
    cursor = _cloud_db.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (username,))
    user = cursor.fetchone()
    
    if not user and username != "":
        # Auto-create profile dynamically for whoever is testing your app!
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (username, password, selected_role))
        if selected_role == 'student':
            cursor.execute("INSERT INTO students VALUES (?, ?, 85.0, 0)", (username, f"External User ({username})"))
            cursor.execute("INSERT INTO student_marks (roll_no, subject_name, marks_obtained) VALUES (?, 'Core Engineering', 90)", (username,))
        elif selected_role == 'faculty':
            cursor.execute("INSERT INTO faculty VALUES (?, ?, 60000.0, 95.0)", (username, f"Professor {username}"))
            cursor.execute("INSERT INTO timetable (faculty_id, subject_name, class_time) VALUES (?, 'Systems Design', 'Mon 10 AM')", (username,))
        _cloud_db.commit()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (username,))
        user = cursor.fetchone()

    if user and user['password'] == password:
        session['user_id'] = user['user_id']
        session['role'] = user['role']
        return jsonify({"status": "success", "role": user['role'], "user_id": user['user_id']})
        
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@app.route('/api/dashboard/student')
def get_student_dashboard():
    uid = session.get('user_id')
    cursor = _cloud_db.cursor()
    profile = cursor.execute("SELECT * FROM students WHERE roll_no = ?", (uid,)).fetchone()
    marks = cursor.execute("SELECT subject_name, marks_obtained FROM student_marks WHERE roll_no = ?", (uid,)).fetchall()
    return jsonify({
        "profile": dict(profile) if profile else {"roll_no": uid, "name": "Guest Student", "attendance_pct": 75.0, "backlogs": 0},
        "marks": [dict(m) for m in marks]
    })

@app.route('/api/dashboard/faculty')
def get_faculty_dashboard():
    uid = session.get('user_id')
    cursor = _cloud_db.cursor()
    profile = cursor.execute("SELECT * FROM faculty WHERE faculty_id = ?", (uid,)).fetchone()
    schedule = cursor.execute("SELECT subject_name, class_time FROM timetable WHERE faculty_id = ?", (uid,)).fetchall()
    return jsonify({
        "profile": dict(profile) if profile else {"faculty_id": uid, "name": "Guest Faculty", "salary": 50000, "attendance_pct": 90.0},
        "schedule": [dict(s) for s in schedule]
    })

@app.route('/api/ai-assistant', methods=['POST'])
def ai_assistant():
    data = request.get_json(silent=True) or {}
    user_prompt = data.get('prompt', '').strip()
    
    if not user_prompt:
        return jsonify({"response": "I am standing by. Please provide your input query structure."})

    if os.getenv('GEMINI_API_KEY') and os.getenv('GEMINI_API_KEY') != 'MOCK_KEY':
        try:
            response = ai_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are a brilliant, strictly structured university systems engineering professor. Answer questions precisely using markdown components.",
                    temperature=0.3
                )
            )
            return jsonify({"response": response.text})
        except Exception as ai_err:
            print(f"AI Error: {ai_err}")

    return jsonify({"response": f"🤖 Core Sync Echo Profile Mode activated. You asked: '{user_prompt}'"})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
