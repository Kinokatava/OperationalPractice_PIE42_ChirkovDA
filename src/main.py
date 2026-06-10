import argparse
import sys
import os
import db
import scanner
import hasher

def main():
    parser = argparse.ArgumentParser(
        description="Консольный индексатор файловой системы с поиском дубликатов."
    )
    
    parser.add_argument("path", type=str, help="Путь к папке для сканирования")
    parser.add_argument("--ext", nargs="*", help="Фильтр по расширениям (например: --ext .txt .py)")
    
    parser.add_argument(
        "--find-dupes", 
        action="store_true", 
        help="Найти и показать файлы с одинаковым содержимым (по хэшу)"
    )
    
    args = parser.parse_args()
    target_path = os.path.abspath(args.path)
    
    if not os.path.isdir(target_path):
        print(f"Ошибка: '{args.path}' не является папкой.")
        sys.exit(1)
        
    print(f"Путь: '{target_path}'")
    
    allowed_exts = None
    if args.ext:
        allowed_exts = set()
        for e in args.ext:
            ext = e.lower()
            if not ext.startswith('.'): ext = '.' + ext
            allowed_exts.add(ext)
        print(f"Фильтр: {allowed_exts}")

    # Инициализация БД
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, 'data', 'index.db')
    
    try:
        db.init_db(db_path)
    except Exception as e:
        print(f"Ошибка БД: {e}")
        sys.exit(1)

    # СКАНИРОВАНИЕ
    scanned_files = scanner.scan_directory(target_path, allowed_exts)
    print(f"Найдено файлов: {len(scanned_files)}")
    
    # СИНХРОНИЗАЦИЯ БД (базовая)
    added, updated, deleted = db.sync_db(db_path, scanned_files)
    print(f"БД: +{added} ~{updated} -{deleted}")
    
    # ХЭШИРОВАНИЕ И ПОИСК ДУБЛИКАТОВ 
    if args.find_dupes:
        hash_stats = hasher.process_files_for_hashes(target_path, db_path, scanned_files)
        print(f"Хэши: посчитано новых: {hash_stats['calculated']}, использовано старых: {hash_stats['reused']}")
        
        duplicates = db.find_duplicates(db_path)
        
        if not duplicates:
            print("Дубликаты не найдены. Все файлы уникальны!")
        else:
            print(f"Найдено групп дубликатов: {len(duplicates)}")
            for i, group in enumerate(duplicates, 1):
                print(f"\nГруппа #{i} ({len(group)} файлов с одинаковым содержимым):")
                for path in group:
                    print(f"   • {path}")
    else:
        if scanned_files:
            print("\nПримеры файлов (первые 10):")
            for f in scanned_files[:10]:
                print(f"   • {f['relative_path']} | {f['size']} B")

if __name__ == "__main__":
    main()