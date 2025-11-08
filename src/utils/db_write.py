# src/utils/db_write.py
import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2

# 🔑 Загружаем переменные из .env
# Ищем .env в корне проекта (рядом с src/, tests/)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# 📥 Читаем настройки БД из .env
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),  # ← должно быть "localhost"
    "port": int(os.getenv("POSTGRES_PORT", "6432")),  # ← должно быть 6432
    "database": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}

# Проверка: все ли обязательные переменные заданы?
required = ["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB"]
missing = [var for var in required if not os.getenv(var)]
if missing:
    raise EnvironmentError(f"❌ Не заданы переменные в .env: {', '.join(missing)}")

def create_table_and_insert():
    print("📡 Подключение к PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            done BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Таблица 'tasks' готова")

    cur.execute(
        "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id",
        ("Запись через .env!", False)
    )
    task_id = cur.fetchone()[0]
    conn.commit()

    print(f"✅ Запись создана! ID = {task_id}")

    cur.execute("SELECT id, title FROM tasks ORDER BY id DESC LIMIT 3")
    print("\n📋 Последние 3 записи:")
    for row in cur.fetchall():
        print(f"   #{row[0]}: {row[1]}")

    cur.close()
    conn.close()
    print("🔌 Соединение закрыто.")

if __name__ == "__main__":
    create_table_and_insert()