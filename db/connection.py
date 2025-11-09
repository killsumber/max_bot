import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from pathlib import Path

# Загружаем .env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def get_db_connection():
    """Создает и возвращает соединение с БД"""
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "6432"),
        database=os.getenv("POSTGRES_DB", "myapp"),
        user=os.getenv("POSTGRES_USER", "app"),
        password=os.getenv("POSTGRES_PASSWORD", "secret"),
        cursor_factory=RealDictCursor  # Возвращает результаты как словари
    )

def get_db_cursor():
    """Создает соединение и курсор"""
    conn = get_db_connection()
    return conn, conn.cursor()