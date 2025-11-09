# database/queries.py
from .connection import get_db_cursor

class UserQueries:
    """Запросы для работы с пользователями"""
    
    @staticmethod
    def create_or_update_user(max_id, username=None, timezone='UTC'):
        """Создает или обновляет пользователя"""
        sql = """
            INSERT INTO users (max_id, username, timezone)
            VALUES (%(max_id)s, %(username)s, %(timezone)s)
            ON CONFLICT (max_id) 
            DO UPDATE SET 
                username = EXCLUDED.username,
                timezone = EXCLUDED.timezone,
                updated_at = CURRENT_TIMESTAMP
            RETURNING *
        """
        
        conn, cur = get_db_cursor()
        try:
            cur.execute(sql, {
                'max_id': max_id,
                'username': username,
                'timezone': timezone
            })
            result = cur.fetchone()
            conn.commit()
            return result
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_user_by_max_id(max_id):
        """Находит пользователя по max_id"""
        sql = "SELECT * FROM users WHERE max_id = %s"
        
        conn, cur = get_db_cursor()
        try:
            cur.execute(sql, (max_id,))
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_user_by_id(user_id):
        """Находит пользователя по id (SERIAL)"""
        sql = "SELECT * FROM users WHERE id = %s"
        
        conn, cur = get_db_cursor()
        try:
            cur.execute(sql, (user_id,))
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def update_user_timezone(max_id, timezone):
        """Обновляет временную зону пользователя"""
        sql = """
            UPDATE users 
            SET timezone = %s, updated_at = CURRENT_TIMESTAMP 
            WHERE max_id = %s 
            RETURNING *
        """
        
        conn, cur = get_db_cursor()
        try:
            cur.execute(sql, (timezone, max_id))
            result = cur.fetchone()
            conn.commit()
            return result
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_all_users():
        """Получает всех пользователей"""
        sql = "SELECT * FROM users ORDER BY created_at DESC"
        
        conn, cur = get_db_cursor()
        try:
            cur.execute(sql)
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def delete_user(max_id):
        """Удаляет пользователя"""
        sql = "DELETE FROM users WHERE max_id = %s"
        
        conn, cur = get_db_cursor()
        try:
            cur.execute(sql, (max_id,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            cur.close()
            conn.close()

class TaskQueries:
    """Запросы для работы с задачами"""
    
    @staticmethod
    def create_task(max_id, title, description=None, priority=0, 
                   status_in_work=True, due_date=None):
        """Создает новую задачу"""
        # Сначала получаем user_id по max_id
        user_sql = "SELECT id FROM users WHERE max_id = %s"
        conn, cur = get_db_cursor()
        
        try:
            cur.execute(user_sql, (max_id,))
            user = cur.fetchone()
            if not user:
                raise ValueError(f"Пользователь с max_id {max_id} не найден")
            
            user_id = user['id']
            
            sql = """
                INSERT INTO tasks (user_id, title, description, priority, status_in_work, due_date)
                VALUES (%(user_id)s, %(title)s, %(description)s, %(priority)s, %(status_in_work)s, %(due_date)s)
                RETURNING *
            """
            
            cur.execute(sql, {
                'user_id': user_id,
                'title': title,
                'description': description,
                'priority': priority,
                'status_in_work': status_in_work,
                'due_date': due_date
            })
            result = cur.fetchone()
            conn.commit()
            return result
            
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_user_tasks(max_id, status_in_work=None):
        """Получает задачи пользователя по max_id"""
        sql = """
            SELECT t.* 
            FROM tasks t
            JOIN users u ON t.user_id = u.id
            WHERE u.max_id = %s
        """
        params = [max_id]
        
        if status_in_work is not None:
            sql += " AND t.status_in_work = %s"
            params.append(status_in_work)
            
        sql += " ORDER BY t.priority DESC, t.created_at DESC"
        
        conn, cur = get_db_cursor()
        try:
            cur.execute(sql, params)
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_task_by_id(task_id):
        """Получает задачу по ID"""
        sql = "SELECT * FROM tasks WHERE id = %s"
        
        conn, cur = get_db_cursor()
        try:
            cur.execute(sql, (task_id,))
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def update_task_status(task_id, status_in_work):
        """Обновляет статус задачи (в работе/выполнено)"""
        sql = """
            UPDATE tasks 
            SET status_in_work = %s, updated_at = CURRENT_TIMESTAMP 
            WHERE id = %s 
            RETURNING *
        """
        
        conn, cur = get_db_cursor()
        try:
            cur.execute(sql, (status_in_work, task_id))
            result = cur.fetchone()
            conn.commit()
            return result
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def update_task_priority(task_id, priority):
        """Обновляет приоритет задачи"""
        sql = """
            UPDATE tasks 
            SET priority = %s, updated_at = CURRENT_TIMESTAMP 
            WHERE id = %s 
            RETURNING *
        """
        
        conn, cur = get_db_cursor()
        try:
            cur.execute(sql, (priority, task_id))
            result = cur.fetchone()
            conn.commit()
            return result
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def update_task(task_id, title=None, description=None, priority=None, due_date=None):
        """Обновляет задачу (частичное обновление)"""
        updates = []
        params = {}
        
        if title is not None:
            updates.append("title = %(title)s")
            params['title'] = title
        if description is not None:
            updates.append("description = %(description)s")
            params['description'] = description
        if priority is not None:
            updates.append("priority = %(priority)s")
            params['priority'] = priority
        if due_date is not None:
            updates.append("due_date = %(due_date)s")
            params['due_date'] = due_date
        
        if not updates:
            return None
            
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params['task_id'] = task_id
        
        sql = f"""
            UPDATE tasks 
            SET {', '.join(updates)}
            WHERE id = %(task_id)s 
            RETURNING *
        """
        
        conn, cur = get_db_cursor()
        try:
            cur.execute(sql, params)
            result = cur.fetchone()
            conn.commit()
            return result
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def delete_task(task_id):
        """Удаляет задачу"""
        sql = "DELETE FROM tasks WHERE id = %s"
        
        conn, cur = get_db_cursor()
        try:
            cur.execute(sql, (task_id,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_tasks_by_priority(max_id, priority):
        """Получает задачи пользователя по приоритету"""
        sql = """
            SELECT t.* 
            FROM tasks t
            JOIN users u ON t.user_id = u.id
            WHERE u.max_id = %s AND t.priority = %s
            ORDER BY t.created_at DESC
        """
        
        conn, cur = get_db_cursor()
        try:
            cur.execute(sql, (max_id, priority))
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_overdue_tasks(max_id):
        """Получает просроченные задачи пользователя"""
        sql = """
            SELECT t.* 
            FROM tasks t
            JOIN users u ON t.user_id = u.id
            WHERE u.max_id = %s 
            AND t.due_date < CURRENT_TIMESTAMP 
            AND t.status_in_work = TRUE
            ORDER BY t.due_date ASC
        """
        
        conn, cur = get_db_cursor()
        try:
            cur.execute(sql, (max_id,))
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()

class TimezoneQueries:
    """Запросы для работы с временными зонами"""
    
    @staticmethod
    def populate_timezones():
        """Заполняет таблицу utc стандартными временными зонами"""
        timezones = [
            ('UTC-12', -12), ('UTC-11', -11), ('UTC-10', -10),
            ('UTC-9', -9), ('UTC-8', -8), ('UTC-7', -7), ('UTC-6', -6),
            ('UTC-5', -5), ('UTC-4', -4), ('UTC-3', -3), ('UTC-2', -2),
            ('UTC-1', -1), ('UTC', 0), ('UTC+1', 1), ('UTC+2', 2),
            ('UTC+3', 3), ('UTC+4', 4), ('UTC+5', 5), ('UTC+6', 6),
            ('UTC+7', 7), ('UTC+8', 8), ('UTC+9', 9), ('UTC+10', 10),
            ('UTC+11', 11), ('UTC+12', 12)
        ]
        
        sql = "INSERT INTO utc (timezone, time_delta) VALUES (%s, %s)"
        
        conn, cur = get_db_cursor()
        try:
            for tz_name, delta in timezones:
                cur.execute(sql, (tz_name, delta))
            conn.commit()
            print(f"✅ Добавлено {len(timezones)} временных зон")
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_all_timezones():
        """Получает все временные зоны"""
        sql = "SELECT * FROM utc ORDER BY time_delta"
        
        conn, cur = get_db_cursor()
        try:
            cur.execute(sql)
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_timezone_by_delta(delta):
        """Находит временную зону по смещению"""
        sql = "SELECT * FROM utc WHERE time_delta = %s"
        
        conn, cur = get_db_cursor()
        try:
            cur.execute(sql, (delta,))
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_timezone_by_name(timezone_name):
        """Находит временную зону по названию"""
        sql = "SELECT * FROM utc WHERE timezone = %s"
        
        conn, cur = get_db_cursor()
        try:
            cur.execute(sql, (timezone_name,))
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

class StatsQueries:
    """Запросы для статистики"""
    
    @staticmethod
    def get_user_stats(max_id):
        """Получает статистику пользователя"""
        sql = """
            SELECT 
                COUNT(t.id) as total_tasks,
                COUNT(CASE WHEN t.status_in_work = TRUE THEN 1 END) as active_tasks,
                COUNT(CASE WHEN t.status_in_work = FALSE THEN 1 END) as completed_tasks,
                COUNT(CASE WHEN t.priority = 2 THEN 1 END) as high_priority_tasks,
                COUNT(CASE WHEN t.priority = 1 THEN 1 END) as medium_priority_tasks,
                COUNT(CASE WHEN t.priority = 0 THEN 1 END) as low_priority_tasks,
                COUNT(CASE WHEN t.due_date < CURRENT_TIMESTAMP AND t.status_in_work = TRUE THEN 1 END) as overdue_tasks
            FROM tasks t
            JOIN users u ON t.user_id = u.id
            WHERE u.max_id = %s
        """
        
        conn, cur = get_db_cursor()
        try:
            cur.execute(sql, (max_id,))
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_recent_tasks(max_id, limit=5):
        """Получает последние задачи пользователя"""
        sql = """
            SELECT t.* 
            FROM tasks t
            JOIN users u ON t.user_id = u.id
            WHERE u.max_id = %s
            ORDER BY t.created_at DESC
            LIMIT %s
        """
        
        conn, cur = get_db_cursor()
        try:
            cur.execute(sql, (max_id, limit))
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()