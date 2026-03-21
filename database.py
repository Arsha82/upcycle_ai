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
    inserted_id = c.lastrowid
    conn.commit()
    conn.close()
    return inserted_id

def delete_recipe(item_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM recipes WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()

def rename_recipe(item_id, new_name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('UPDATE recipes SET item_name = ? WHERE id = ?', (new_name, item_id))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM recipes ORDER BY timestamp DESC')
    rows = c.fetchall()
    conn.close()
    return rows
