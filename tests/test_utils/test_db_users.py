# tests/test_utils/test_db_users.py
import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from db.models import create_tables, drop_tables
from db.queries import UserQueries, TaskQueries, TimezoneQueries


@pytest.fixture(autouse=True)
def setup_database():
    """Создает таблицы перед каждым тестом и удаляет после"""
    create_tables()
    yield
    drop_tables()

def test_user_creation():
    """Тест создания пользователя"""
    user = UserQueries.create_or_update_user(
        max_id=123456789,
        username="test_user",
        timezone="UTC+3"
    )
    
    assert user is not None
    assert user['max_id'] == 123456789
    assert user['username'] == "test_user"
    assert user['timezone'] == "UTC+3"

def test_task_creation():
    """Тест создания задачи"""
    # Сначала создаем пользователя
    user = UserQueries.create_or_update_user(max_id=123456789)
    
    # Затем задачу
    task = TaskQueries.create_task(
        max_id=123456789,
        title="Test Task",
        description="Test Description",
        priority=2  # высокий приоритет
    )
    
    assert task is not None
    assert task['title'] == "Test Task"
    assert task['priority'] == 2
    assert task['status_in_work'] == True

def test_get_user_tasks():
    """Тест получения задач пользователя"""
    user = UserQueries.create_or_update_user(max_id=123456789)
    
    # Создаем несколько задач
    TaskQueries.create_task(max_id=123456789, title="Task 1", priority=0)
    TaskQueries.create_task(max_id=123456789, title="Task 2", priority=2)
    
    tasks = TaskQueries.get_user_tasks(max_id=123456789)
    assert len(tasks) == 2
    # Задачи должны быть отсортированы по приоритету (сначала высокие)
    assert tasks[0]['priority'] == 2

def test_timezone_operations():
    """Тест работы с временными зонами"""
    # Заполняем таблицу временных зон
    TimezoneQueries.populate_timezones()
    
    # Получаем все зоны
    timezones = TimezoneQueries.get_all_timezones()
    assert len(timezones) == 25  # от -12 до +12
    
    # Ищем конкретную зону
    utc_plus_3 = TimezoneQueries.get_timezone_by_delta(3)
    assert utc_plus_3['timezone'] == 'UTC+3'