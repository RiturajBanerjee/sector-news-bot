import sqlite3
from datetime import datetime

DB_NAME = "news.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sector TEXT,
                    title TEXT,
                    link TEXT,
                    summary_raw TEXT,
                    summary TEXT,
                    published TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    conn.commit()
    conn.close()

def save_news(sector, title, link, summary, published):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO news (sector, title, link, summary_raw, published) VALUES (?, ?, ?, ?, ?)",
              (sector, title, link, summary, published))
    conn.commit()
    conn.close()
