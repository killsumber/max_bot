# tests/test_utils/test_db.py
import os
from pathlib import Path
import psycopg2
from dotenv import load_dotenv
import pytest

# 🔑 Загружаем .env один раз при запуске тестов
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

@pytest.fixture
def db_conn():
    """Фикстура: соединение с БД + изоляция через временную таблицу."""
    # Подключаемся к основной БД (myapp), но будем работать во временной таблице
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
    cur = conn.cursor()

    # Создаём временную таблицу (исчезнет при закрытии сессии)
    cur.execute("""
        CREATE TEMP TABLE test_tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN DEFAULT FALSE
        )
    """)
    conn.commit()

    yield cur  # передаём курсор в тест

    # После теста: закрываем соединение (временная таблица удаляется автоматически)
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

    print("✅ Тест пройден: запись и чтение работают!")