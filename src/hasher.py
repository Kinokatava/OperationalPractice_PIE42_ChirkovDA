import os
import sqlite3
import db

def should_rehash(db_path: str, rel_path: str, current_size: int, current_mtime: float) -> bool:
    if not os.path.exists(db_path):
        return True
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT hash, size, modified_at FROM files WHERE relative_path = ?", 
        (rel_path,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row or not row[0]:
        return True
    
    db_size, db_mtime = row[1], row[2]
    if current_size != db_size or abs(current_mtime - db_mtime) > 1.0:
        return True
        
    return False

def process_files_for_hashes(root_path: str, db_path: str, files_list: list) -> dict:
    stats = {'calculated': 0, 'reused': 0, 'errors': 0}
    
    for file in files_list:
        rel_path = file['relative_path']
        abs_path = os.path.join(root_path, rel_path)
        
        if should_rehash(db_path, rel_path, file['size'], file['modified_at']):
            file_hash = db.get_file_hash(abs_path)
            if file_hash:
                db.update_file_hash(db_path, rel_path, file_hash)
                stats['calculated'] += 1
            else:
                stats['errors'] += 1
        else:
            stats['reused'] += 1
            
    return stats