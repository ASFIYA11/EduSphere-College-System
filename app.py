import os
import sqlite3
from flask import Flask, request, jsonify, render_template, Response, session, redirect, url_for
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'edusphere_absolute_master_key_2026')
CORS(app)

# Persistent In-Memory Database for zero-latency execution on cloud servers
_db = sqlite3.connect(':memory:', check_same_thread=False)
_db.row_factory = sqlite3.Row

def init_production_database():
    cursor = _db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, password TEXT, role TEXT, avatar_url TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS students (roll_no TEXT PRIMARY KEY, name TEXT, attendance_pct REAL, backlogs INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS student_marks (id INTEGER PRIMARY KEY AUTOINCREMENT, roll_no TEXT, subject_name TEXT, marks_obtained INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS faculty (faculty_id TEXT PRIMARY KEY, name TEXT, salary REAL, attendance_pct REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS timetable (id INTEGER PRIMARY KEY AUTOINCREMENT, faculty_id TEXT, subject_name TEXT, class_time TEXT)")
    
    # Base Hardcoded Admin Bypass Profile Seeding
    cursor.execute("INSERT OR IGNORE INTO users VALUES ('admin', 'admin123', 'admin', 'https://images.unsplash.com/photo-1517841905240-472988babdf9')")
    _db.commit()

init_production_database()

# Initialize Google GenAI Core Client securely
ai_client = genai.Client(api_key=os.getenv('GEMINI_API_KEY', 'MOCK_KEY'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/static/favicon.png')
def dynamic_favicon():
    """Generates a high-res glowing indigo engineering crest on-the-fly for the browser tab."""
    svg_icon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="128" height="128">
        <defs>
            <linearGradient id="pGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#6366f1" />
                <stop offset="100%" stop-color="#d946ef" />
            </linearGradient>
        </defs>
        <path d="M64,8 L112,24 L112,64 C112,96 88,116 64,122 C40,116 16,96 16,64 L16,24 Z" fill="url(#pGrad)" />
        <path d="M64,16 L100,28 L100,64 C100,90 80,107 64,112 C48,107 28,90 28,64 L28,28 Z" fill="#0f172a" />
        <polygon points="64,36 92,48 64,60 36,48" fill="#6366f1" />
        <polygon points="48,54 48,72 64,80 80,72 80,54 64,62" fill="#d946ef" />
    </svg>"""
    return Response(svg_icon, mimetype='image/svg+xml')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json or request.form
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    selected_role = data.get('role', 'student').strip().lower()
    
    if not username or not password:
        return jsonify({"status": "error", "message": "Missing authentication tokens."}), 400

    cursor = _db.cursor()
    user = cursor.execute("SELECT * FROM users WHERE user_id = ?", (username,)).fetchone()
    
    # 🌟 OPEN ACCESS GLOBAL MODE: Auto-register user seamlessly on the fly if missing!
    if not user:
        default_avatar = "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde" if selected_role == 'student' else "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e"
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (username, password, selected_role, default_avatar))
        if selected_role == 'student':
            cursor.execute("INSERT INTO students VALUES (?, ?, 84.5, 0)", (username, f"{username.capitalize()} (Student Profile)"))
            cursor.execute("INSERT INTO student_marks (roll_no, subject_name, marks_obtained) VALUES (?, 'Data Structures', 85)", (username,))
            cursor.execute("INSERT INTO student_marks (roll_no, subject_name, marks_obtained) VALUES (?, 'Database Systems', 92)", (username,))
        elif selected_role == 'faculty':
            cursor.execute("INSERT INTO faculty VALUES (?, ?, 78000.0, 95.0)", (username, f"Dr. {username.capitalize()}"))
            cursor.execute("INSERT INTO timetable (faculty_id, subject_name, class_time) VALUES (?, 'Distributed Systems Core', 'Mon & Wed 10:00 AM')", (username,))
        _db.commit()
        user = cursor.execute("SELECT * FROM users WHERE user_id = ?", (username,)).fetchone()

    if user and user['password'] == password:
        session['user_id'] = user['user_id']
        session['role'] = user['role']
        return jsonify({"status": "success", "role": user['role'], "userId": user['user_id']})
        
    return jsonify({"status": "error", "message": "Access Keyphrase Mismatch."}), 401

@app.route('/api/dashboard/profile', methods=['GET', 'POST'])
def manage_dashboard_profile():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized session context"}), 403
        
    uid = session['user_id']
    role = session['role']
    cursor = _db.cursor()
    
    # 🌟 CUSTOM GOOGLE IMAGE URL UPDATE ENDPOINT
    if request.method == 'POST':
        new_url = request.json.get('avatar_url', '').strip()
        if new_url:
            cursor.execute("UPDATE users SET avatar_url = ? WHERE user_id = ?", (new_url, uid))
            _db.commit()
            return jsonify({"status": "success", "message": "Avatar mapping modified successfully!"})

    user_base = cursor.execute("SELECT avatar_url FROM users WHERE user_id = ?", (uid,)).fetchone()
    avatar = user_base['avatar_url'] if user_base else "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde"

    if role == 'student':
        profile = cursor.execute("SELECT * FROM students WHERE roll_no = ?", (uid,)).fetchone()
        marks = cursor.execute("SELECT subject_name, marks_obtained FROM student_marks WHERE roll_no = ?", (uid,)).fetchall()
        return jsonify({
            "role": "student", "userId": uid, "avatar_url": avatar,
            "profile": dict(profile) if profile else {}, "marks": [dict(m) for m in marks]
        })
    elif role == 'faculty':
        profile = cursor.execute("SELECT * FROM faculty WHERE faculty_id = ?", (uid,)).fetchone()
        schedule = cursor.execute("SELECT subject_name, class_time FROM timetable WHERE faculty_id = ?", (uid,)).fetchall()
        return jsonify({
            "role": "faculty", "userId": uid, "avatar_url": avatar,
            "profile": dict(profile) if profile else {}, "schedule": [dict(s) for s in schedule]
        })
    elif role == 'admin':
        total = cursor.execute("SELECT COUNT(*) as count FROM users").fetchone()['count']
        return jsonify({
            "role": "admin", "userId": uid, "avatar_url": avatar,
            "metrics": {"total_users": total, "status": "ONLINE NOMINAL (IN-MEMORY CACHE)"}
        })

@app.route('/api/ai-assistant', methods=['POST'])
def ai_assistant():
    data = request.get_json(silent=True) or {}
    user_query = data.get('query', '').lower().strip()
    
    if "search" in user_query or "pdf" in user_query or "notes" in user_query:
        return jsonify({
            "response": "I've successfully isolated your engineering reference syllabus framework text documentation down below! 🎯", 
            "type": "file_link"
        })

    if ai_client and os.environ.get("GEMINI_API_KEY") and os.environ.get("GEMINI_API_KEY") != 'MOCK_KEY':
        try:
            response = ai_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_query,
                config=types.GenerateContentConfig(
                    system_instruction="You are EduSphere AI, a brilliant computer science professor. Answer accurately in structural markdown bullet points."
                )
            )
            return jsonify({"response": response.text, "type": "text"})
        except Exception:
            pass

    return jsonify({"response": f"🤖 [System Offline Echo Matrix Active]: Received your query: '{user_query}' successfully.", "type": "text"})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
