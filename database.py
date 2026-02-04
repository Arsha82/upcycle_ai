import sqlite3
import datetime

DB_NAME = "upcycle.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT,
            item_name TEXT,
            api_response TEXT,
            timestamp DATETIME DEFAULT (datetime('now', 'localtime'))
        )
    ''')
    conn.commit()
    conn.close()

def save_recipe(item_name, api_response, image_path=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO recipes (item_name, api_response, image_path) VALUES (?, ?, ?)', 
              (item_name, api_response, image_path))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM recipes ORDER BY timestamp DESC')
    rows = c.fetchall()
    conn.close()
    return rows
