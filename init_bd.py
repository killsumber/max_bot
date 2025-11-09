import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.models import create_tables
from db.queries import TimezoneQueries

def initialize_database():
    """Инициализирует базу данных: создает таблицы и заполняет данные"""
    print("🗃️  Инициализация базы данных...")
    
    try:
        # Создаем таблицы
        create_tables()
        print("✅ Таблицы созданы успешно!")
        
        # Заполняем временные зоны
        TimezoneQueries.populate_timezones()
        print("✅ Временные зоны добавлены!")
        
        print("🎉 База данных готова к работе!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
        return False

if __name__ == "__main__":
    initialize_database()