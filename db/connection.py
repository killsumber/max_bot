# db/connection.py

import os
import psycopg2
from dotenv import load_dotenv

# Загружаем переменные из .env (ищет .env в текущей и родительских папках)
load_dotenv()

def get_connection():
    # Обязательные переменные — если нет, выдаём понятную ошибку
    required_vars = [
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD"
    ]

    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise EnvironmentError(
            f"❌ Отсутствуют обязательные переменные в .env: {', '.join(missing)}\n"
            "Убедитесь, что файл .env существует и содержит все настройки подключения к БД."
        )

    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port = int(os.getenv("POSTGRES_PORT", "6432")),  # 5432 - стандартный порт PostgreSQ
        database=os.getenv("POSTGRES_DB", "postgres"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )