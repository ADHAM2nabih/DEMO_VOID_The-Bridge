import sqlite3
import os

DB_PATH = "db/training.db"

def init_db():
    os.makedirs("db", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS trained_videos (
        video_name TEXT PRIMARY KEY,
        label TEXT
    )
    """)
    conn.commit()
    conn.close()

def is_trained(video_name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM trained_videos WHERE video_name=?", (video_name,))
    res = cur.fetchone()
    conn.close()
    return res is not None

def mark_trained(video_name, label):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO trained_videos VALUES (?,?)",
        (video_name, label)
    )
    conn.commit()
    conn.close()
