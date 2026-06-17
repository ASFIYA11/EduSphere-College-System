import os
import sqlite3
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, Response
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'edusphere_secure_master_token_2026')
CORS(app)

# Persistent In-Memory Storage Core to prevent Render from freezing up
_db = sqlite3.connect(':memory:', check_same_thread=False)
_db.row_factory = sqlite3.Row

def init_original_database():
    cursor = _db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, password TEXT, role TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS students (roll_no TEXT PRIMARY KEY, name TEXT, attendance_pct REAL, backlogs INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS student_marks (id INTEGER PRIMARY KEY AUTOINCREMENT, roll_no TEXT, subject_name TEXT, marks_obtained INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS faculty (faculty_id TEXT PRIMARY KEY, name TEXT, salary REAL, attendance_pct REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS timetable (id INTEGER PRIMARY KEY AUTOINCREMENT, faculty_id TEXT, subject_name TEXT, class_time TEXT)")
    
    # Core Admin Profile Seeding
    cursor.execute("INSERT OR IGNORE INTO users VALUES ('admin', 'admin123', 'admin')")
    _db.commit()

init_original_database()

# Initialize Google GenAI Client
ai_client = genai.Client(api_key=os.getenv('GEMINI_API_KEY', 'MOCK_KEY'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/favicon.png')
def dynamic_favicon():
    """Generates the glowing cyan college shield tab icon dynamically out of thin air."""
    svg_icon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="128" height="128">
        <defs>
            <linearGradient id="shieldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#06b6d4" />
                <stop offset="100%" stop-color="#3b82f6" />
            </linearGradient>
        </defs>
        <path d="M64,8 L112,24 L112,64 C112,96 88,116 64,122 C40,116 16,96 16,64 L16,24 Z" fill="url(#shieldGrad)" />
        <path d="M64,16 L100,28 L100,64 C100,90 80,107 64,112 C48,107 28,90 28,64 L28,28 Z" fill="#0b1329" />
        <polygon points="64,36 92,48 64,60 36,48" fill="#06b6d4" />
        <polygon points="48,54 48,72 64,80 80,72 80,54 64,62" fill="#06b6d4" />
    </svg>"""
    return Response(svg_icon, mimetype='image/svg+xml')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json(silent=True) or request.form
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    selected_role = data.get('role', '').strip().lower()
    
    if not username or not password:
        return jsonify({"status": "error", "message": "Missing credentials."}), 400

    cursor = _db.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (username,))
    user = cursor.fetchone()
    
    # 🌟 OPEN ACCESS REGISTRATION INTERCEPTOR
    if not user:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (username, password, selected_role))
        if selected_role == 'student':
            cursor.execute("INSERT INTO students VALUES (?, ?, 84.5, 0)", (username, f"{username.capitalize()} (Student)"))
            cursor.execute("INSERT INTO student_marks (roll_no, subject_name, marks_obtained) VALUES (?, 'Data Structures', 85)", (username,))
            cursor.execute("INSERT INTO student_marks (roll_no, subject_name, marks_obtained) VALUES (?, 'Database Management', 90)", (username,))
        elif selected_role == 'faculty':
            cursor.execute("INSERT INTO faculty VALUES (?, ?, 72000.0, 94.0)", (username, f"Prof. {username.capitalize()}"))
            cursor.execute("INSERT INTO timetable (faculty_id, subject_name, class_time) VALUES (?, 'Advanced Programming', 'Mon 09:00 AM')", (username,))
        _db.commit()
        
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (username,))
        user = cursor.fetchone()

    if user and user['password'] == password:
        session['user_id'] = user['user_id']
        session['role'] = user['role']
        return jsonify({"status": "success", "role": user['role'], "user_id": user['user_id']})
        
    return jsonify({"status": "error", "message": "Invalid credentials."}), 401

@app.route('/api/dashboard/data')
def get_dashboard_data():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 403
        
    uid = session['user_id']
    role = session['role']
    cursor = _db.cursor()
    
    if role == 'student':
        profile = cursor.execute("SELECT * FROM students WHERE roll_no = ?", (uid,)).fetchone()
        marks = cursor.execute("SELECT subject_name, marks_obtained FROM student_marks WHERE roll_no = ?", (uid,)).fetchall()
        return jsonify({
            "role": "student",
            "profile": dict(profile) if profile else {},
            "marks": [dict(m) for m in marks]
        })
    elif role == 'faculty':
        profile = cursor.execute("SELECT * FROM faculty WHERE faculty_id = ?", (uid,)).fetchone()
        schedule = cursor.execute("SELECT subject_name, class_time FROM timetable WHERE faculty_id = ?", (uid,)).fetchall()
        return jsonify({
            "role": "faculty",
            "profile": dict(profile) if profile else {},
            "schedule": [dict(s) for s in schedule]
        })
    elif role == 'admin':
        total_users = cursor.execute("SELECT COUNT(*) as count FROM users").fetchone()['count']
        return jsonify({
            "role": "admin",
            "metrics": {"total_users": total_users, "status": "Active cloud matrix"}
        })

@app.route('/api/ai-assistant', methods=['POST'])
def ai_assistant():
    data = request.get_json(silent=True) or {}
    user_prompt = data.get('prompt', '').strip()
    
    if not user_prompt:
        return jsonify({"response": "Standing by..."})

    if os.getenv('GEMINI_API_KEY') and os.getenv('GEMINI_API_KEY') != 'MOCK_KEY':
        try:
            response = ai_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are a brilliant university computer science professor. Answer accurately using markdown formatting.",
                    temperature=0.3
                )
            )
            return jsonify({"response": response.text})
        except Exception as e:
            print(f"AI Error: {e}")

    return jsonify({"response": f"🤖 **Local Framework Echo:** Received '{user_prompt}' successfully."})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
