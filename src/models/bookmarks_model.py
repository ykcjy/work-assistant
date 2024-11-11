import sqlite3
import logging

class BookmarksModel:
    def __init__(self, db):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def get_categories(self):
        """获取所有分类"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                SELECT id, name, order_index 
                FROM categories 
                ORDER BY order_index
            ''')
            return cursor.fetchall()
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise

    def add_category(self, name):
        """添加新分类"""
        try:
            cursor = self.db.conn.cursor()
            # 获取最大的order_index
            cursor.execute('SELECT MAX(order_index) FROM categories')
            max_order = cursor.fetchone()[0] or 0
            
            cursor.execute('''
                INSERT INTO categories (name, order_index)
                VALUES (?, ?)
            ''', (name, max_order + 1))
            self.db.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise

    def update_category(self, category_id, name):
        """更新分类"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                UPDATE categories 
                SET name = ? 
                WHERE id = ?
            ''', (name, category_id))
            self.db.conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise

    def delete_category(self, category_id):
        """删除分类及其所有书签"""
        try:
            cursor = self.db.conn.cursor()
            # 首先删除该分类下的所有书签
            cursor.execute('''
                DELETE FROM bookmarks 
                WHERE category_id = ?
            ''', (category_id,))
            # 然后删除分类
            cursor.execute('''
                DELETE FROM categories 
                WHERE id = ?
            ''', (category_id,))
            self.db.conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise

    def get_bookmarks(self, category_id=None):
        """获取书签"""
        try:
            cursor = self.db.conn.cursor()
            if category_id:
                cursor.execute('''
                    SELECT id, name, url, browser, order_index 
                    FROM bookmarks 
                    WHERE category_id = ? 
                    ORDER BY order_index
                ''', (category_id,))
            else:
                cursor.execute('''
                    SELECT id, name, url, browser, order_index 
                    FROM bookmarks 
                    ORDER BY order_index
                ''')
            return cursor.fetchall()
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise

    def add_bookmark(self, category_id, name, url, browser):
        """添加书签"""
        try:
            cursor = self.db.conn.cursor()
            # 获取当前分类下最大的order_index
            cursor.execute('''
                SELECT MAX(order_index) 
                FROM bookmarks 
                WHERE category_id = ?
            ''', (category_id,))
            max_order = cursor.fetchone()[0] or 0
            
            cursor.execute('''
                INSERT INTO bookmarks (category_id, name, url, browser, order_index)
                VALUES (?, ?, ?, ?, ?)
            ''', (category_id, name, url, browser, max_order + 1))
            self.db.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise

    def update_bookmark(self, bookmark_id, name, url, browser):
        """更新书签"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                UPDATE bookmarks 
                SET name = ?, url = ?, browser = ? 
                WHERE id = ?
            ''', (name, url, browser, bookmark_id))
            self.db.conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise

    def delete_bookmark(self, bookmark_id):
        """删除书签"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                DELETE FROM bookmarks 
                WHERE id = ?
            ''', (bookmark_id,))
            self.db.conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise

    def update_bookmark_order(self, bookmark_id, new_order):
        """更新书签顺序"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                UPDATE bookmarks 
                SET order_index = ? 
                WHERE id = ?
            ''', (new_order, bookmark_id))
            self.db.conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise

    def get_bookmark(self, bookmark_id):
        """获取单个书签的详细信息"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                SELECT id, name, url, browser, username 
                FROM bookmarks 
                WHERE id = ?
            ''', (bookmark_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise

    def batch_add_bookmarks(self, bookmarks_data):
        """批量添加书签
        Args:
            bookmarks_data: 书签数据列表
        Returns:
            成功添加的数量
        """
        cursor = self.db.cursor()
        success_count = 0
        
        try:
            for bookmark in bookmarks_data:
                cursor.execute("""
                    INSERT INTO bookmarks (category_id, name, url, browser)
                    VALUES (?, ?, ?, ?)
                """, (
                    bookmark['category_id'],
                    bookmark['name'],
                    bookmark['url'],
                    bookmark['browser']
                ))
                success_count += 1
            
            self.db.commit()
            return success_count
        except Exception as e:
            self.db.rollback()
            raise e
        finally:
            cursor.close()