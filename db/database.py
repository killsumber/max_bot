# tests/test_utils/test_db.py
import os
from pathlib import Path
import psycopg2
from dotenv import load_dotenv
import pytest

# 🔑 Загружаем .env
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def get_test_db_config():
    """Определяет конфигурацию БД для тестов."""
    # Если запущено в Docker - используем service name, иначе localhost
    host = "postgres" if os.getenv("DOCKER_ENV") else "localhost"
    
    return {
        "host": host,
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "database": os.getenv("POSTGRES_DB", "myapp"),
        "user": os.getenv("POSTGRES_USER", "app"),
        "password": os.getenv("POSTGRES_PASSWORD", "secret")
    }

@pytest.fixture
def db_conn():
    """Фикстура: соединение с БД + изоляция через временную таблицу."""
    config = get_test_db_config()
    
    try:
        conn = psycopg2.connect(**config)
    except psycopg2.OperationalError as e:
        pytest.skip(f"База данных недоступна: {e}")

    cur = conn.cursor()

    # Создаём временную таблицу
    cur.execute("""
        CREATE TEMP TABLE test_tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN DEFAULT FALSE
        )
    """)
    conn.commit()

    yield cur

    cur.close()
    conn.close()

def test_insert_and_select(db_conn):
    """Тест: запись → чтение → проверка."""
    # Запись
    db_conn.execute(
        "INSERT INTO test_tasks (title, done) VALUES (%s, %s)",
        ("Тестовая задача из pytest", True)
    )

    # Чтение
    db_conn.execute("SELECT title, done FROM test_tasks")
    result = db_conn.fetchone()

    # Проверки
    assert result is not None
    assert result[0] == "Тестовая задача из pytest"
    assert result[1] is True