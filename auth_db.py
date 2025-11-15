import sqlite3
import bcrypt

DB = "admin.db"

def init_users():
    """Инициализация базы данных администраторов"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Создаем админа по умолчанию: admin / admin123
    try:
        default_password = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt())
        cur.execute("INSERT INTO admins (username, password_hash, full_name) VALUES (?, ?, ?)",
                   ("admin", default_password, "Главный администратор"))
    except sqlite3.IntegrityError:
        pass  # Админ уже существует
    
    conn.commit()
    conn.close()

def register_user(username, password, full_name=""):
    """Регистрация нового администратора"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        cur.execute("INSERT INTO admins (username, password_hash, full_name) VALUES (?, ?, ?)", 
                   (username, password_hash, full_name))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def login_user(username, password):
    """Проверка логина и пароля администратора"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT password_hash, full_name FROM admins WHERE username=?", (username,))
    user = cur.fetchone()
    conn.close()
    
    if user and bcrypt.checkpw(password.encode(), user[0]):
        return user[1]  # Возвращаем полное имя администратора
    return None

# Инициализируем БД при импорте
init_users()