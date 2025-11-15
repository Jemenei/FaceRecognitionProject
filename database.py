import sqlite3
import pickle
from datetime import datetime

# ==================== БАЗА ДАННЫХ ПОЛЬЗОВАТЕЛЕЙ ====================

DB_USERS = "users_registry.db"

def init_db():
    """Инициализация базы данных пользователей"""
    conn = sqlite3.connect(DB_USERS)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            faculty TEXT NOT NULL,
            face_encoding BLOB,
            photo_path TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_face_encoding(student_id, first_name, last_name, faculty, encoding):
    """Сохранение пользователя с face encoding"""
    init_db()
    conn = sqlite3.connect(DB_USERS)
    cur = conn.cursor()
    try:
        cur.execute("""INSERT INTO users (student_id, first_name, last_name, faculty, face_encoding) 
                      VALUES (?, ?, ?, ?, ?)""",
                   (student_id, first_name, last_name, faculty, pickle.dumps(encoding)))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def load_all_encodings():
    """Загрузка всех face encodings с полной информацией пользователей"""
    init_db()
    conn = sqlite3.connect(DB_USERS)
    cur = conn.cursor()
    cur.execute("SELECT id, student_id, first_name, last_name, face_encoding FROM users WHERE face_encoding IS NOT NULL")
    rows = cur.fetchall()
    conn.close()
    
    users = {}
    for user_id, student_id, first_name, last_name, enc_blob in rows:
        full_name = f"{first_name} {last_name}"
        users[student_id] = {
            'id': user_id,
            'name': full_name,
            'encoding': pickle.loads(enc_blob)
        }
    return users

def get_all_users():
    """Получить список всех пользователей"""
    init_db()
    conn = sqlite3.connect(DB_USERS)
    cur = conn.cursor()
    cur.execute("SELECT id, student_id, first_name, last_name, faculty, registered_at FROM users ORDER BY id DESC")
    users = cur.fetchall()
    conn.close()
    return users

def get_user_by_student_id(student_id):
    """Получить информацию о пользователе по student_id"""
    conn = sqlite3.connect(DB_USERS)
    cur = conn.cursor()
    cur.execute("SELECT id, student_id, first_name, last_name, faculty FROM users WHERE student_id=?", (student_id,))
    user = cur.fetchone()
    conn.close()
    return user

def delete_user(user_id):
    """Удалить пользователя"""
    conn = sqlite3.connect(DB_USERS)
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

# ==================== БАЗА ДАННЫХ ЛОГОВ ДОСТУПА ====================

DB_LOGS = "access_logs.db"

def init_logs_db():
    """Инициализация базы данных логов"""
    conn = sqlite3.connect(DB_LOGS)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            student_id TEXT,
            full_name TEXT,
            action TEXT,
            location TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def log_access(user_id, student_id, full_name, action, location="Main Entrance"):
    """Записать лог доступа (Вход/Выход)"""
    init_logs_db()
    conn = sqlite3.connect(DB_LOGS)
    cur = conn.cursor()
    cur.execute("""INSERT INTO access_logs (user_id, student_id, full_name, action, location) 
                  VALUES (?, ?, ?, ?, ?)""",
               (user_id, student_id, full_name, action, location))
    conn.commit()
    conn.close()

def get_recent_logs(limit=100):
    """Получить последние логи"""
    init_logs_db()
    conn = sqlite3.connect(DB_LOGS)
    cur = conn.cursor()
    cur.execute("""SELECT id, student_id, full_name, action, location, timestamp 
                  FROM access_logs ORDER BY timestamp DESC LIMIT ?""", (limit,))
    logs = cur.fetchall()
    conn.close()
    return logs

# Инициализация баз данных при импорте
init_db()
init_logs_db()