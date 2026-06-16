# database.py
import mysql.connector
from dotenv import load_dotenv
import os

# Explicitly load hidden environment variable matrix tracks
load_dotenv()

# Secure Database Routing Coordinates
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '20222026'
}

def get_raw_connection():
    """Establishes a base network driver connection to the local MySQL server instance."""
    return mysql.connector.connect(**db_config)

def initialize_database():
    """
    Core Relational Schema Compiler Layer.
    Automatically creates the system database and seeds all relational tracking 
    tables dynamically if they do not exist inside the target storage node.
    """
    print("🚀 Initializing system database relational architecture compilation...")
    conn = get_raw_connection()
    cursor = conn.cursor()
    
    # 1. Initialize Database Namespace Node
    cursor.execute("CREATE DATABASE IF NOT EXISTS college_db")
    cursor.execute("USE college_db")
    print("✅ Target node schema namespace 'college_db' verified.")
    
    # 2. Compile RBAC Identity Credential Access Directory Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id VARCHAR(50) PRIMARY KEY,
            password VARCHAR(255) NOT NULL,
            role ENUM('student', 'faculty', 'admin') NOT NULL
        )
    """)
    
    # 3. Compile Core Student Academic Demographic Metrics Ledger Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            roll_no VARCHAR(50) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            attendance_pct DECIMAL(5,2) DEFAULT 100.00,
            backlogs INT DEFAULT 0,
            FOREIGN KEY (roll_no) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    
    # 4. Compile Student Grade Registry Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_marks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            roll_no VARCHAR(50),
            subject_name VARCHAR(100) NOT NULL,
            marks_obtained INT NOT NULL,
            FOREIGN KEY (roll_no) REFERENCES students(roll_no) ON DELETE CASCADE
        )
    """)
    
    # 5. Compile Faculty Personnel Payroll Operations Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faculty (
            faculty_id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            salary DECIMAL(10,2) NOT NULL DEFAULT 60000.00,
            attendance_pct DECIMAL(5,2) DEFAULT 100.00,
            FOREIGN KEY (faculty_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    
    # 6. Compile Faculty Weekly Instructional Curriculum Scheduling Matrix Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS timetable (
            id INT AUTO_INCREMENT PRIMARY KEY,
            faculty_id VARCHAR(50),
            subject_name VARCHAR(100) NOT NULL,
            class_time VARCHAR(50) NOT NULL,
            FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE
        )
    """)
    
    # Seed default base Admin account safely if it doesn't exist
    cursor.execute("SELECT * FROM users WHERE user_id = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id, password, role) VALUES ('admin', 'admin123', 'admin')")
        print("⚙️ System Administrative terminal root security account seeded successfully.")
        
    conn.commit()
    cursor.close()
    conn.close()
    print("🎉 Relational Schema Architecture Compilation completed with zero exceptions!")

if __name__ == '__main__':
    # Allows direct structural database generation initialization via CLI script parsing execution
    initialize_database()
