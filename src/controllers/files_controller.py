import logging
import os
import subprocess
from ..models.files_model import FilesModel

class FilesController:
    def __init__(self, db):
        self.db = db
        self.model = FilesModel(db)
        self.logger = logging.getLogger(__name__)

    def get_files(self):
        """获取所有文件快捷方式"""
        try:
            return self.model.get_files()
        except Exception as e:
            self.logger.error(f"Error getting files: {e}")
            raise

    def add_file(self, file_path):
        """添加文件快捷方式"""
        try:
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            return self.model.add_file(file_name, file_path)
        except Exception as e:
            self.logger.error(f"Error adding file '{file_path}': {e}")
            raise

    def update_file(self, file_id, new_path):
        """更新文件路径"""
        try:
            file_name = os.path.splitext(os.path.basename(new_path))[0]
            return self.model.update_file(file_id, file_name, new_path)
        except Exception as e:
            self.logger.error(f"Error updating file ID '{file_id}' to '{new_path}': {e}")
            raise

    def delete_file(self, file_id):
        """删除文件快捷方式"""
        try:
            return self.model.delete_file(file_id)
        except Exception as e:
            self.logger.error(f"Error deleting file ID '{file_id}': {e}")
            raise

    def open_file(self, file_path):
        """打开文件"""
        try:
            if os.path.exists(file_path):
                if os.name == 'nt':
                    os.startfile(file_path)
                else:
                    subprocess.run(['xdg-open', file_path])
            else:
                raise FileNotFoundError(f"File not found: {file_path}")
        except Exception as e:
            self.logger.error(f"Error opening file '{file_path}': {e}")
            raise

    def confirm_edit(self, file_id):
        """确认编辑任务"""
        try:
            self.logger.info(f"Edit confirmed for file ID: {file_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error confirming edit for file ID '{file_id}': {e}")
            raise

    def update_task(self, task_id, task_data):
        """更新任务信息"""
        try:
            self.logger.info(f"Updating task {task_id} with data: {task_data}")
            return self.model.update_task(task_id, task_data)
        except Exception as e:
            self.logger.error(f"Error updating task {task_id}: {e}")
            raise