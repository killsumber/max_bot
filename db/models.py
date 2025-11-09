from .connection import get_db_connection

def create_tables():
    """Создает все таблицы в БД"""
    """
    Описание таблиц:
    -users
    --id - индекс
    --max_id - id внутри приложение (уникальный индетификатор юзера)
    --username - имя
    --crated_at - первый заход в бота
    --utc - дельта по времени относительно utc
    """
    sql_scripts = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            max_id BIGINT UNIQUE NOT NULL,
            username VARCHAR(32),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            timezone VARCHAR(50) DEFAULT 'UTC',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY, --индекс
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, --id from max_id
            title VARCHAR(255) NOT NULL, 
            description TEXT,
            priority INT DEFAULT 0, --приоритет, 0 - низкий, 1 - средний, 2 - высокий
            status_in_work BOOLEAN DEFAULT TRUE, -- в работе/выполнено
            due_date TIMESTAMP, -- дата выполнения
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, --дата создания
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- дата обновления
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS utc(
        timezone VARCHAR(50),
        time_delta SMALLINT
        )
        """
    ]
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        for script in sql_scripts:
            cur.execute(script)
        conn.commit()
        print("✅ Все таблицы успешно созданы!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Ошибка при создании таблиц: {e}")
        raise
        
    finally:
        cur.close()
        conn.close()

def drop_tables():
    """Удаляет все таблицы (для тестов)"""
    tables = [
        "tasks",
        "users",
        'utc'
    ]
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        for table in tables:
            cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
        conn.commit()
        print("✅ Все таблицы удалены!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Ошибка при удалении таблиц: {e}")
        raise
        
    finally:
        cur.close()
        conn.close()