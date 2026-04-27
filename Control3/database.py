import sqlite3

DB_NAME = "todos.db"

def get_db():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def create_user(username, password):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def create_todo(title, description):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO todos (title, description) VALUES (?, ?)", (title, description))
    conn.commit()
    id = cursor.lastrowid
    conn.close()
    return id

def get_todo(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, completed FROM todos WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    return row

def update_todo(id, title=None, desc=None, completed=None):
    conn = get_db()
    cursor = conn.cursor()
    if title:
        cursor.execute("UPDATE todos SET title = ? WHERE id = ?", (title, id))
    if desc is not None:
        cursor.execute("UPDATE todos SET description = ? WHERE id = ?", (desc, id))
    if completed is not None:
        cursor.execute("UPDATE todos SET completed = ? WHERE id = ?", (1 if completed else 0, id))
    conn.commit()
    conn.close()

def delete_todo(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todos WHERE id = ?", (id,))
    conn.commit()
    conn.close()