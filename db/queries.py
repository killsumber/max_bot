# db/queries.py

from db.connection import get_connection
from psycopg2.extras import RealDictCursor


class UserQueries:
    @staticmethod
    def get_user_by_max_id(max_id):
        with get_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT * FROM users WHERE max_id = %s", (max_id,))
            return cur.fetchone()

    @staticmethod
    def create_or_update_user(max_id, username, timezone="UTC+3"):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO users (max_id, username, timezone)
                VALUES (%s, %s, %s)
                ON CONFLICT (max_id) 
                DO UPDATE SET username = EXCLUDED.username, timezone = EXCLUDED.timezone
            """, (max_id, username, timezone))
            conn.commit()


class TaskQueries:
    @staticmethod
    def get_user_tasks(max_id, status_in_work=None):
        with get_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            if status_in_work is None:
                cur.execute("""
                    SELECT * FROM tasks 
                    WHERE max_id = %s 
                    ORDER BY priority DESC, created_at DESC
                """, (max_id,))
            else:
                cur.execute("""
                    SELECT * FROM tasks 
                    WHERE max_id = %s AND status_in_work = %s
                    ORDER BY priority DESC, created_at DESC
                """, (max_id, status_in_work))
            return cur.fetchall()

    @staticmethod
    def get_task_by_id(task_id):
        with get_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
            return cur.fetchone()

    @staticmethod
    def create_task(max_id, title, description=None, priority=0):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO tasks (max_id, title, description, priority)
                VALUES (%s, %s, %s, %s)
                RETURNING *
            """, (max_id, title, description, priority))
            task = cur.fetchone()
            conn.commit()
            return task

    @staticmethod
    def update_task_status(task_id, status_in_work):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE tasks 
                SET status_in_work = %s 
                WHERE id = %s
            """, (status_in_work, task_id))
            conn.commit()
            return cur.rowcount > 0

    @staticmethod
    def update_task_priority(task_id, priority):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE tasks 
                SET priority = %s 
                WHERE id = %s
            """, (priority, task_id))
            conn.commit()

    @staticmethod
    def delete_task(task_id):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            conn.commit()
            return cur.rowcount > 0


class TimezoneQueries:
    @staticmethod
    def populate_timezones():
        timezones = [
            ("UTC-12", -12), ("UTC-11", -11), ("UTC-10", -10),
            ("UTC-9", -9), ("UTC-8", -8), ("UTC-7", -7),
            ("UTC-6", -6), ("UTC-5", -5), ("UTC-4", -4),
            ("UTC-3", -3), ("UTC-2", -2), ("UTC-1", -1),
            ("UTC", 0),
            ("UTC+1", 1), ("UTC+2", 2), ("UTC+3", 3),
            ("UTC+4", 4), ("UTC+5", 5), ("UTC+6", 6),
            ("UTC+7", 7), ("UTC+8", 8), ("UTC+9", 9),
            ("UTC+10", 10), ("UTC+11", 11), ("UTC+12", 12),
            ("UTC+13", 13), ("UTC+14", 14),
        ]

        with get_connection() as conn:
            cur = conn.cursor()
            for name, offset in timezones:
                cur.execute("""
                    INSERT INTO timezones (name, utc_offset)
                    VALUES (%s, %s)
                    ON CONFLICT (name) DO NOTHING
                """, (name, offset))
            conn.commit()

    @staticmethod
    def get_all_timezones():
        with get_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT * FROM timezones ORDER BY utc_offset")
            return cur.fetchall()