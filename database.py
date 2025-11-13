import sqlite3
import pickle

DB_PATH = "faces.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS faces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            encoding BLOB NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_face_encoding(name, encoding):
    init_db()  # <-- гарантируем, что таблица существует
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO faces (name, encoding) VALUES (?, ?)", (name, pickle.dumps(encoding)))
    conn.commit()
    conn.close()

def load_all_encodings():
    init_db()  # <-- гарантируем, что таблица существует
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name, encoding FROM faces")
    rows = cur.fetchall()
    conn.close()

    encodings = {}
    for name, enc_blob in rows:
        encodings[name] = pickle.loads(enc_blob)
    return encodings

# Всегда инициализируем базу при импорте
init_db()
