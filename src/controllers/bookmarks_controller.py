import logging
import webbrowser
import os
import subprocess
from ..models.bookmarks_model import BookmarksModel

class BookmarksController:
    def __init__(self, db):
        self.db = db
        self.model = BookmarksModel(db)
        self.logger = logging.getLogger(__name__)
        self.setup_browsers()

    def setup_browsers(self):
        """配置浏览器"""
        try:
            # Chrome浏览器可能的安装路径
            chrome_paths = [
                r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
                os.path.expanduser('~') + r'\AppData\Local\Google\Chrome\Application\chrome.exe',
            ]
            
            # Edge浏览器可能的安装路径
            edge_paths = [
                r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
                r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
                os.path.expanduser('~') + r'\AppData\Local\Microsoft\Edge\Application\msedge.exe',
            ]
            
            # 注册Chrome浏览器
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    webbrowser.register('chrome', None,
                        webbrowser.BackgroundBrowser(chrome_path))
                    break
            
            # 注册Edge浏览器
            for edge_path in edge_paths:
                if os.path.exists(edge_path):
                    webbrowser.register('edge', None,
                        webbrowser.BackgroundBrowser(edge_path))
                    break
        except Exception as e:
            self.logger.error(f"Error setting up browsers: {e}")

    def get_categories(self):
        """获取所有分类"""
        try:
            return self.model.get_categories()
        except Exception as e:
            self.logger.error(f"Error getting categories: {e}")
            raise

    def add_category(self, name):
        """添加新分类"""
        try:
            return self.model.add_category(name)
        except Exception as e:
            self.logger.error(f"Error adding category: {e}")
            raise

    def update_category(self, category_id, name):
        """更新分类"""
        try:
            return self.model.update_category(category_id, name)
        except Exception as e:
            self.logger.error(f"Error updating category: {e}")
            raise

    def delete_category(self, category_id):
        """删除分类"""
        try:
            return self.model.delete_category(category_id)
        except Exception as e:
            self.logger.error(f"Error deleting category: {e}")
            raise

    def get_bookmarks(self, category_id=None):
        """获取书签"""
        try:
            return self.model.get_bookmarks(category_id)
        except Exception as e:
            self.logger.error(f"Error getting bookmarks: {e}")
            raise

    def add_bookmark(self, category_id, name, url, browser):
        """添加书签"""
        try:
            return self.model.add_bookmark(category_id, name, url, browser)
        except Exception as e:
            self.logger.error(f"Error adding bookmark: {e}")
            raise

    def update_bookmark(self, bookmark_id, name, url, browser):
        """更新书签"""
        try:
            return self.model.update_bookmark(bookmark_id, name, url, browser)
        except Exception as e:
            self.logger.error(f"Error updating bookmark: {e}")
            raise

    def delete_bookmark(self, bookmark_id):
        """删除书签"""
        try:
            return self.model.delete_bookmark(bookmark_id)
        except Exception as e:
            self.logger.error(f"Error deleting bookmark: {e}")
            raise

    def open_bookmark(self, url, browser):
        """打开书签"""
        try:
            if browser == 'chrome':
                # 使用命令行方式打开Chrome
                chrome_paths = [
                    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
                    os.path.expanduser('~') + r'\AppData\Local\Google\Chrome\Application\chrome.exe',
                ]
                
                for chrome_path in chrome_paths:
                    if os.path.exists(chrome_path):
                        subprocess.Popen([chrome_path, url])
                        return
                
                # 如果找不到Chrome，使用系统默认浏览器
                webbrowser.open(url)
            
            elif browser == 'edge':
                # 使用Edge打开
                edge_paths = [
                    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
                    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
                    os.path.expanduser('~') + r'\AppData\Local\Microsoft\Edge\Application\msedge.exe',
                ]
                
                for edge_path in edge_paths:
                    if os.path.exists(edge_path):
                        subprocess.Popen([edge_path, url])
                        return
                
                # 如果找不到Edge，使用系统默认浏览器
                webbrowser.open(url)
            
            else:
                # 使用系统默认浏览器
                webbrowser.open(url)
                
        except Exception as e:
            self.logger.error(f"Error opening bookmark: {e}")
            # 如果出错，尝试使用系统默认浏览器
            try:
                webbrowser.open(url)
            except Exception as e2:
                self.logger.error(f"Error opening with default browser: {e2}")
                raise

    def get_bookmark(self, bookmark_id):
        """获取单个书签的详细信息"""
        try:
            return self.model.get_bookmark(bookmark_id)
        except Exception as e:
            self.logger.error(f"Error getting bookmark: {e}")
            raise

    def import_bookmarks(self, bookmarks_data):
        """批量导入书签
        Args:
            bookmarks_data: 包含书签信息的列表，每个元素应该是一个字典，包含：
                          category_id, name, url, browser
        Returns:
            导入成功的书签数量
        """
        try:
            success_count = 0
            for bookmark in bookmarks_data:
                try:
                    self.model.add_bookmark(
                        category_id=bookmark['category_id'],
                        name=bookmark['name'],
                        url=bookmark['url'],
                        browser=bookmark['browser']
                    )
                    success_count += 1
                except Exception as e:
                    self.logger.error(f"Error importing bookmark {bookmark}: {e}")
                    continue
            
            return success_count
        except Exception as e:
            self.logger.error(f"Error in batch import: {e}")
            raise