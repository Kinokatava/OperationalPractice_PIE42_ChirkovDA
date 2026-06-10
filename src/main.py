import argparse
import sys
import os
import db
import scanner 

def main():
    parser = argparse.ArgumentParser(
        description="Консольный индексатор файловой системы."
    )
    
    parser.add_argument(
        "path", 
        type=str, 
        help="Путь к папке, которую нужно просканировать"
    )
    
    parser.add_argument(
        "--ext",
        nargs="*",
        help="Фильтр по расширениям (например: --ext .txt .py)"
    )
    
    args = parser.parse_args()
    target_path = args.path 
    
    if not os.path.exists(target_path):
        print(f"Ошибка: Путь '{target_path}' не существует.")
        sys.exit(1) 
        
    if not os.path.isdir(target_path):
        print(f"Ошибка: '{target_path}' является файлом, а не папкой.")
        sys.exit(1)
        
    print(f"Путь принят: '{target_path}'")
    
    allowed_exts = None
    if args.ext:
        allowed_exts = set()
        for e in args.ext:
            ext = e.lower()
            if not ext.startswith('.'):
                ext = '.' + ext
            allowed_exts.add(ext)
        print(f"Фильтр активен: только файлы {allowed_exts}")

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, 'data', 'index.db')
    
    try:
        db.init_db(db_path)
    except Exception as e:
        print(f"Ошибка БД: {e}")
        sys.exit(1)

    # сканирование
    print("Начинаем сканирование...")
    scanned_files = scanner.scan_directory(target_path, allowed_exts)
    
    # критерий: "список файлов выводится"
    print(f"\nНайдено файлов: {len(scanned_files)}")
    print("Список файлов")
    for f in scanned_files[:15]:
        print(f"📄 {f['relative_path']} | {f['size']} байт | {f['file_type']}")
    if len(scanned_files) > 15:
        print(f"... и еще {len(scanned_files) - 15} файлов (полный список сохранен в БД).")
    
    # синхронизация с бд
    added, updated, deleted = db.sync_db(db_path, scanned_files)
    
    print("Итоги синхронизации БД:")
    print(f"   Добавлено: {added}")
    print(f"   Обновлено: {updated}")
    print(f"   Удалено: {deleted}")

if __name__ == "__main__":
    main()