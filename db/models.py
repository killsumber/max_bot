# db/models.py

from db.connection import get_connection

def create_tables():
    """Создаёт таблицы users, tasks, timezones с колонкой max_id"""
    conn = get_connection()
    cur = conn.cursor()

    try:
        # 1. users — с max_id (BIGINT, UNIQUE, NOT NULL)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                max_id BIGINT NOT NULL UNIQUE,
                username TEXT NOT NULL,
                timezone TEXT DEFAULT 'UTC+3',
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. tasks — с max_id (FK на users.max_id)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
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

        # 3. timezones
        cur.execute("""
            CREATE TABLE IF NOT EXISTS timezones (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                utc_offset INTEGER NOT NULL
            )
        """)

        conn.commit()
        print("✅ Таблицы users, tasks, timezones созданы.")
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Ошибка создания таблиц: {e}") from e
    finally:
        cur.close()
        conn.close()