import os
import sqlite3

def init_db(db_path: str) -> None:
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        relative_path TEXT UNIQUE NOT NULL,
        size INTEGER,
        modified_at REAL,
        file_type TEXT,
        hash TEXT
    );
    """
    
    cursor.execute(create_table_query)
    
    conn.commit()
    conn.close()