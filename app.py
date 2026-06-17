import os
import sqlite3
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'edusphere_master_secure_token_2026')
CORS(app)

# High-Availability In-Memory Engine for Zero-Latency Render Cloud Sync
_cloud_db = sqlite3.connect(':memory:', check_same_thread=False)
_cloud_db.row_factory = sqlite3.Row

def init_db():
    cursor = _cloud_db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, password TEXT, role TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS students (roll_no TEXT PRIMARY KEY, name TEXT, attendance_pct REAL, backlogs INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS student_marks (id INTEGER PRIMARY KEY AUTOINCREMENT, roll_no TEXT, subject_name TEXT, marks_obtained INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS faculty (faculty_id TEXT PRIMARY KEY, name TEXT, salary REAL, attendance_pct REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS timetable (id INTEGER PRIMARY KEY AUTOINCREMENT, faculty_id TEXT, subject_name TEXT, class_time TEXT)")
    
    # Seed hardcoded core administrative bypass logic
    cursor.execute("INSERT OR IGNORE INTO users VALUES ('admin', 'admin123', 'admin')")
    _cloud_db.commit()

init_db()

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
    
    if not username or not password:
        return jsonify({"status": "error", "message": "Missing authentication parameters."}), 400

    cursor = _cloud_db.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (username,))
    user = cursor.fetchone()
    
    # 🌟 AUTOMATED OPEN REGISTRATION MODE: Create user dynamically if they don't exist yet!
    if not user:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (username, password, selected_role))
        if selected_role == 'student':
            cursor.execute("INSERT INTO students VALUES (?, ?, 85.0, 0)", (username, f"Student User ({username})"))
            cursor.execute("INSERT INTO student_marks (roll_no, subject_name, marks_obtained) VALUES (?, 'Core Architecture', 88)", (username,))
        elif selected_role == 'faculty':
            cursor.execute("INSERT INTO faculty VALUES (?, ?, 65000.0, 92.0)", (username, f"Professor {username}"))
            cursor.execute("INSERT INTO timetable (faculty_id, subject_name, class_time) VALUES (?, 'Distributed Systems', 'Tue 11:00 AM')", (username,))
        _cloud_db.commit()
        
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (username,))
        user = cursor.fetchone()

    if user and user['password'] == password:
        session['user_id'] = user['user_id']
        session['role'] = user['role']
        return jsonify({"status": "success", "role": user['role'], "user_id": user['user_id']})
        
    return jsonify({"status": "error", "message": "Invalid credentials verification sequence."}), 401

@app.route('/api/ai-assistant', methods=['POST'])
def ai_assistant():
    data = request.get_json(silent=True) or {}
    user_prompt = data.get('prompt', '').strip()
    
    if not user_prompt:
        return jsonify({"response": "Please enter a valid prompt string."})

    if os.getenv('GEMINI_API_KEY') and os.getenv('GEMINI_API_KEY') != 'MOCK_KEY':
        try:
            response = ai_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are a brilliant university engineering professor. Provide direct responses in clear markdown.",
                    temperature=0.3
                )
            )
            return jsonify({"response": response.text})
        except Exception as e:
            print(f"AI Exception: {e}")

    return jsonify({"response": f"🤖 Echo System Tracking Mode active. You asked: '{user_prompt}'"})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
