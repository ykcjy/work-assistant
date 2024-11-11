import sqlite3
import logging

class FilesModel:
    def __init__(self, db):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def get_files(self):
        """获取所有文件快捷方式"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                SELECT id, name, file_path 
                FROM file_shortcuts 
                ORDER BY name
            ''')
            return cursor.fetchall()
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise

    def add_file(self, name, file_path):
        """添加文件快捷方式"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                INSERT INTO file_shortcuts (name, file_path)
                VALUES (?, ?)
            ''', (name, file_path))
            self.db.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise

    def update_file(self, file_id, name, file_path):
        """更新文件快捷方式"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                UPDATE file_shortcuts 
                SET name = ?, file_path = ? 
                WHERE id = ?
            ''', (name, file_path, file_id))
            self.db.conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise

    def delete_file(self, file_id):
        """删除文件快捷方式"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                DELETE FROM file_shortcuts 
                WHERE id = ?
            ''', (file_id,))
            self.db.conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise 