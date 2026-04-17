import sqlite3
import os
from hashids import Hashids

# ------------------ 配置 ------------------
DB_PATH = os.getenv("DB_PATH", "data.db")               # Docker 中会映射到 /app/data.db
HASH_SALT = os.getenv("HASH_SALT", "ai-content-cleaner-salt")
hashids = Hashids(salt=HASH_SALT, min_length=6)

# ------------------ 初始化 ------------------
if not os.path.exists("data.db"):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original TEXT,
        refined TEXT,
        prob_orig REAL,
        prob_refined REAL,
        safe INTEGER,
        token_usage INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()

def insert_task(original: str, refined: str, prob_orig: float,
                prob_refined: float, safe: bool, token_usage: int) -> int:
    """返回数据库自增的 task_id"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (original, refined, prob_orig, prob_refined, safe, token_usage) "
        "VALUES (?,?,?,?,?,?)",
        (original, refined, prob_orig, prob_refined, int(safe), token_usage),
    )
    task_id = cur.lastrowid
    conn.commit()
    conn.close()
    return task_id