import sqlite3
import logging
from datetime import datetime, timedelta

class TasksModel:
    def __init__(self, db):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def get_tasks(self, include_completed=False):
        """获取任务列表"""
        try:
            cursor = self.db.conn.cursor()
            if include_completed:
                cursor.execute('''
                    SELECT id, name, file_path, due_date, status, completed_at, importance 
                    FROM pending_tasks 
                    WHERE status = 'completed'
                    ORDER BY completed_at DESC
                ''')
            else:
                cursor.execute('''
                    SELECT id, name, file_path, due_date, status, importance 
                    FROM pending_tasks 
                    WHERE status != 'completed'
                    ORDER BY date(due_date) ASC
                ''')
            return cursor.fetchall()
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise

    def get_task(self, task_id):
        """获取单个任务详情"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                SELECT id, name, file_path, due_date, status, completed_at, importance 
                FROM pending_tasks 
                WHERE id = ?
            ''', (task_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise

    def add_task(self, name, due_date, file_path=None, importance='普通'):
        """添加任务"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                INSERT INTO pending_tasks (name, file_path, due_date, status, importance)
                VALUES (?, ?, ?, 'pending', ?)
            ''', (name, file_path, due_date, importance))
            self.db.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise

    def update_task(self, task_id, name, due_date, importance):
        """更新任务信息"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                UPDATE pending_tasks 
                SET name = ?, 
                    due_date = ?,
                    importance = ?
                WHERE id = ?
            ''', (name, due_date, importance, task_id))
            
            self.db.conn.commit()
            return True
        except Exception as e:
            self.db.conn.rollback()
            raise

    def complete_task(self, task_id):
        """完成任务"""
        try:
            cursor = self.db.conn.cursor()
            completed_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                UPDATE pending_tasks 
                SET status = 'completed', completed_at = ? 
                WHERE id = ?
            ''', (completed_at, task_id))
            self.db.conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise

    def cleanup_completed_tasks(self):
        """清理已完成超过5个工作日的任务"""
        try:
            cursor = self.db.conn.cursor()
            # 计算5个工作日前的日期
            current_date = datetime.now()
            workdays = 0
            cleanup_date = current_date
            while workdays < 5:
                cleanup_date -= timedelta(days=1)
                if cleanup_date.weekday() < 5:  # 0-4 表示周一到周五
                    workdays += 1
            
            cleanup_date_str = cleanup_date.strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
                DELETE FROM pending_tasks 
                WHERE status = 'completed' 
                AND completed_at < ?
            ''', (cleanup_date_str,))
            self.db.conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise

    def delete_task(self, task_id):
        """删除任务"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                DELETE FROM pending_tasks 
                WHERE id = ?
            ''', (task_id,))
            self.db.conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise

    def get_today_new_tasks_count(self):
        """获取今日新增的未完成任务数"""
        try:
            cursor = self.db.conn.cursor()
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT COUNT(*) 
                FROM pending_tasks 
                WHERE DATE(created_at) = ? 
                AND status != 'completed'
            ''', (today,))
            return cursor.fetchone()[0]
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise

    def get_pending_tasks_count(self):
        """获取未完成任务总数"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) 
                FROM pending_tasks 
                WHERE status != 'completed'
            ''')
            return cursor.fetchone()[0]
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise

    def restore_task(self, task_id):
        """恢复任务到未完成状态"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                UPDATE pending_tasks 
                SET status = 'pending', completed_at = NULL 
                WHERE id = ?
            ''', (task_id,))
            self.db.conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise