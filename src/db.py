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

def sync_db(db_path: str, scanned_files: list) -> tuple:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT relative_path FROM files")
    old_paths = {row[0] for row in cursor.fetchall()}
    
    new_paths = {f['relative_path'] for f in scanned_files}
    
    paths_to_delete = old_paths - new_paths

    added = 0
    updated = 0

    for file in scanned_files:
        cursor.execute("SELECT id FROM files WHERE relative_path = ?", (file['relative_path'],))
        if cursor.fetchone():
            cursor.execute("""
                UPDATE files 
                SET size=?, modified_at=?, file_type=? 
                WHERE relative_path=?
            """, (file['size'], file['modified_at'], file['file_type'], file['relative_path']))
            updated += 1
        else:
            cursor.execute("""
                INSERT INTO files (relative_path, size, modified_at, file_type)
                VALUES (?, ?, ?, ?)
            """, (file['relative_path'], file['size'], file['modified_at'], file['file_type']))
            added += 1

    deleted = 0
    if paths_to_delete:
        cursor.executemany(
            "DELETE FROM files WHERE relative_path = ?", 
            [(p,) for p in paths_to_delete]
        )
        deleted = cursor.rowcount

    conn.commit()
    conn.close()
    
    return added, updated, deleted