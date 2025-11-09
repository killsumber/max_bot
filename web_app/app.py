# web_app/app.py
import sys
import os

# Добавляем корневую директорию в Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

# Теперь импорты из db должны работать
try:
    from db.queries import UserQueries, TaskQueries, TimezoneQueries
except ImportError as e:
    print(f"Import error: {e}")
    print("Current Python path:")
    for path in sys.path:
        print(f"  {path}")
    raise

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Демо-пользователь
DEMO_USER_ID = 123456789

@app.before_request
def setup_demo_user():
    """Создает демо-пользователя при первом запросе"""
    user = UserQueries.get_user_by_max_id(DEMO_USER_ID)
    if not user:
        UserQueries.create_or_update_user(
            max_id=DEMO_USER_ID,
            username="demo_user",
            timezone="UTC+3"
        )
        # Заполняем временные зоны если нужно
        timezones = TimezoneQueries.get_all_timezones()
        if not timezones:
            TimezoneQueries.populate_timezones()

@app.route('/')
def index():
    """Главная страница со статистикой"""
    user = UserQueries.get_user_by_max_id(DEMO_USER_ID)
    tasks = TaskQueries.get_user_tasks(DEMO_USER_ID)
    
    # Простая статистика
    total_tasks = len(tasks)
    active_tasks = len([t for t in tasks if t['status_in_work']])
    completed_tasks = total_tasks - active_tasks
    
    return render_template('index.html', 
                         user=user,
                         total_tasks=total_tasks,
                         active_tasks=active_tasks,
                         completed_tasks=completed_tasks)

@app.route('/tasks')
def tasks():
    """Страница со списком задач"""
    status_filter = request.args.get('status', 'all')
    user = UserQueries.get_user_by_max_id(DEMO_USER_ID)
    
    if status_filter == 'active':
        tasks_list = TaskQueries.get_user_tasks(DEMO_USER_ID, status_in_work=True)
    elif status_filter == 'completed':
        tasks_list = TaskQueries.get_user_tasks(DEMO_USER_ID, status_in_work=False)
    else:
        tasks_list = TaskQueries.get_user_tasks(DEMO_USER_ID)
    
    return render_template('tasks.html', 
                         tasks=tasks_list, 
                         user=user,
                         status_filter=status_filter)

@app.route('/tasks/create', methods=['GET', 'POST'])
def create_task():
    """Создание новой задачи"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        priority = int(request.form.get('priority', 0))
        
        if title:
            task = TaskQueries.create_task(
                max_id=DEMO_USER_ID,
                title=title,
                description=description,
                priority=priority
            )
            flash('Задача успешно создана!', 'success')
            return redirect(url_for('tasks'))
        else:
            flash('Название задачи обязательно!', 'error')
    
    return render_template('create_task.html')

@app.route('/tasks/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    """Переключение статуса задачи"""
    task = TaskQueries.get_task_by_id(task_id)
    if task:
        new_status = not task['status_in_work']
        TaskQueries.update_task_status(task_id, new_status)
        flash('Статус задачи обновлен!', 'success')
    
    return redirect(url_for('tasks'))

@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    """Удаление задачи"""
    success = TaskQueries.delete_task(task_id)
    if success:
        flash('Задача удалена!', 'success')
    else:
        flash('Задача не найдена!', 'error')
    
    return redirect(url_for('tasks'))

@app.route('/tasks/<int:task_id>/update_priority', methods=['POST'])
def update_priority(task_id):
    """Обновление приоритета задачи"""
    priority = int(request.form.get('priority', 0))
    TaskQueries.update_task_priority(task_id, priority)
    flash('Приоритет обновлен!', 'success')
    return redirect(url_for('tasks'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)