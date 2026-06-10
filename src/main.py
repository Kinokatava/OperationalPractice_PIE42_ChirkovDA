import argparse
import sys
import os

from db import init_db

def main():
    parser = argparse.ArgumentParser(
        description="Консольный индексатор файловой системы."
    )
    
    parser.add_argument(
        "path", 
        type=str, 
        help="Путь к папке, которую нужно просканировать"
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
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, 'data', 'index.db')
    
    try:
        init_db(db_path)
        print(f"База данных успешно создана/подготовлена: {db_path}")
    except Exception as e:
        print(f"Критическая ошибка при работе с БД: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()