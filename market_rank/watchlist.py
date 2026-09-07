import sqlite3

DB_PATH = "watchlist.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            added TEXT DEFAULT CURRENT_TIMESTAMP,
            watched INTEGER DEFAULT 0
        )
    """)
    return conn

def add_to_watchlist(title):
    conn = get_connection()
    conn.execute("INSERT INTO watchlist (title) VALUES (?)", (title,))
    conn.commit()
    conn.close()

def list_watchlist():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM watchlist ORDER BY added").fetchall()
    conn.close()
    return rows

def delete_from_watchlist(title):
    conn = get_connection()
    conn.execute("DELETE FROM watchlist WHERE title = ?", (title,))
    conn.commit()
    conn.close()