import sqlite3
import logging
from datetime import datetime
from pathlib import Path

class Database:
    def __init__(self, db_path="workspace.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = None
        self.setup_logging()
        self.connect()
        self.create_tables()
        self.migrate_database()

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def connect(self):
        """Create database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.logger.info("Database connection established")
        except sqlite3.Error as e:
            self.logger.error(f"Database connection error: {e}")
            raise

    def create_tables(self):
        """Create all required tables if they don't exist"""
        try:
            cursor = self.conn.cursor()
            
            # Pending tasks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pending_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    file_path TEXT,
                    due_date TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    importance TEXT DEFAULT '普通',
                    created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
                    updated_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
                    completed_at TEXT
                )
            ''')

            # 添加节假日表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS holidays (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    name TEXT NOT NULL,
                    is_workday INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))
                )
            ''')

            # Categories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    order_index INTEGER NOT NULL,
                    created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))
                )
            ''')

            # Bookmarks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    browser TEXT NOT NULL,
                    order_index INTEGER NOT NULL,
                    created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            ''')

            # File shortcuts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_shortcuts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    file_path TEXT NOT NULL UNIQUE,
                    created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))
                )
            ''')

            self.conn.commit()
            self.logger.info("Tables created successfully")
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Error creating tables: {e}")
            return False

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.logger.info("Database connection closed")

    def migrate_database(self):
        """Migrate database to latest version"""
        try:
            cursor = self.conn.cursor()
            
            # 检查 bookmarks 表是否存在 username 列
            cursor.execute("PRAGMA table_info(bookmarks)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'username' not in columns:
                self.logger.info("Migrating database: Adding username column to bookmarks")
                cursor.execute('''
                    ALTER TABLE bookmarks 
                    ADD COLUMN username TEXT
                ''')
            
            self.conn.commit()
            self.logger.info("Database migration completed successfully")
        except sqlite3.Error as e:
            self.logger.error(f"Database migration error: {e}")
            raise 