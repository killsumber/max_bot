# init_db.py
import sys
import os

# Добавляем корневую директорию в Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.connection import get_connection
from db.queries import TimezoneQueries, UserQueries


def reset_and_create_tables():
    """Полностью пересоздаёт таблицы — для dev-сборки"""
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Удаляем старые таблицы (CASCADE удаляет зависимости)
        cur.execute("DROP TABLE IF EXISTS tasks, users, timezones CASCADE")
        print("🗑️  Старые таблицы удалены.")

        # Создаём users
        cur.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                max_id BIGINT NOT NULL UNIQUE,
                username TEXT NOT NULL,
                timezone TEXT DEFAULT 'UTC+3',
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Создаём tasks (связь через max_id!)
        cur.execute("""
            CREATE TABLE tasks (
                id SERIAL PRIMARY KEY,
                max_id BIGINT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                priority INTEGER DEFAULT 0,
                status_in_work BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (max_id) REFERENCES users(max_id) ON DELETE CASCADE
            )
        """)

        # Создаём timezones
        cur.execute("""
            CREATE TABLE timezones (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                utc_offset INTEGER NOT NULL
            )
        """)

        conn.commit()
        print("✅ Таблицы users, tasks, timezones созданы.")

    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"❌ Ошибка создания таблиц: {e}") from e
    finally:
        cur.close()
        conn.close()


def initialize_database():
    """Инициализирует БД: таблицы → демо-данные"""
    print("🗃️  Инициализация базы данных...")
    
    try:
        # 1. Пересоздаём таблицы
        reset_and_create_tables()
        
        # 2. Демо-пользователь
        UserQueries.create_or_update_user(
            max_id=123456789,
            username="demo_user",
            timezone="UTC+3"
        )
        print("✅ Демо-пользователь (max_id=123456789) создан.")
        
        # 3. Временные зоны
        TimezoneQueries.populate_timezones()
        print("✅ Временные зоны добавлены!")
        
        print("🎉 База данных готова к работе!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
        return False


if __name__ == "__main__":
    initialize_database()