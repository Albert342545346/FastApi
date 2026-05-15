# verify_9_1.py
import sqlite3
import os

DB_PATH = "products.db"

if not os.path.exists(DB_PATH):
    print("Файл products.db не найден. Запустите: python -m alembic upgrade head")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. Проверяем колонки
cursor.execute("PRAGMA table_info(products);")
columns = [row[1] for row in cursor.fetchall()]
required = ["id", "title", "price", "count", "description"]

if all(col in columns for col in required):
    print("Структура таблицы верна:", columns)
else:
    print("Не хватает колонок! Ожидается:", required)

# 2. Проверяем записи
cursor.execute("SELECT COUNT(*) FROM products;")
count = cursor.fetchone()[0]
if count >= 2:
    print(f"В таблице {count} записей (требование: ≥2)")
    cursor.execute("SELECT * FROM products;")
    for row in cursor.fetchall():
        print(row)
else:
    print(f"Записей меньше 2 (найдено: {count}). Добавьте их вручную или через скрипт.")

conn.close()