import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import logging
from datetime import datetime
import os
import subprocess
from ..controllers.tasks_controller import TasksController
from .task_dialog import TaskDialog

class TasksView(ttk.Frame):
    def __init__(self, parent, db, show_completed=False):
        super().__init__(parent)
        self.db = db
        self.controller = TasksController(db)
        self.show_completed = show_completed
        self.setup_logging()
        self.create_widgets()
        self.setup_layout()
        self.load_tasks()
        
        # 启动定时清理任务
        self.after(3600000, self.cleanup_tasks)  # 每小时检查一次

    def setup_logging(self):
        self.logger = logging.getLogger(__name__)

    def create_widgets(self):
        # 创建工具栏
        self.create_toolbar()
        
        # 创建任务列表区域
        self.create_tasks_area()

    def create_toolbar(self):
        self.toolbar = ttk.Frame(self)
        
        if not self.show_completed:
            # 未完成任务视图的工具栏
            self.add_btn = ttk.Button(self.toolbar, text="添加任务", 
                                    command=self.show_add_dialog)
            self.edit_btn = ttk.Button(self.toolbar, text="编辑", 
                                     command=self.edit_selected_task)
            self.complete_btn = ttk.Button(self.toolbar, text="标记完成", 
                                         command=self.mark_complete)
            self.delete_btn = ttk.Button(self.toolbar, text="删除", 
                                       command=self.delete_task)
            # 添加修复按钮
            self.repair_btn = ttk.Button(self.toolbar, text="修复数据", 
                                       command=self.repair_data)
            
            # 布局按钮
            self.add_btn.pack(side='left', padx=2)
            self.edit_btn.pack(side='left', padx=2)
            self.complete_btn.pack(side='left', padx=2)
            self.delete_btn.pack(side='left', padx=2)
            ttk.Separator(self.toolbar, orient='vertical').pack(side='left', padx=5, fill='y')
            self.repair_btn.pack(side='left', padx=2)
        else:
            # 已完成任务视图的工具栏
            self.restore_btn = ttk.Button(self.toolbar, text="恢复任务", 
                                        command=self.restore_task)
            self.delete_btn = ttk.Button(self.toolbar, text="删除", 
                                       command=self.delete_task)
            
            self.restore_btn.pack(side='left', padx=2)
            self.delete_btn.pack(side='left', padx=2)

    def create_tasks_area(self):
        """创建任务列表区域"""
        # 创建任务列表的列定义
        if self.show_completed:
            columns = ('任务名称', '截止日期', '重要程度', '完成时间')
            column_widths = {
                '任务名称': 400,  # 增加任务名称列的宽度
                '截止日期': 100,
                '重要程度': 100,
                '完成时间': 150
            }
        else:
            columns = ('任务名称', '截止日期', '重要程度', '状态')
            column_widths = {
                '任务名称': 400,  # 增加任务名称列的宽度
                '截止日期': 100,
                '重要程度': 100,
                '状态': 100
            }
        
        # 创建任务列表框架
        frame_text = "已完成任务" if self.show_completed else "未完成任务"
        self.tasks_frame = ttk.LabelFrame(self, text=frame_text)
        self.tasks_frame.pack_propagate(False)  # 禁止自动调整大小
        
        # 创建任务列表
        self.tasks_list = ttk.Treeview(self.tasks_frame, columns=columns, 
                                     show='headings')
        
        # 设置列
        for col in columns:
            self.tasks_list.heading(col, text=col)
            self.tasks_list.column(col, width=column_widths[col])
        
        # 添加滚动条
        self.scrollbar = ttk.Scrollbar(self.tasks_frame, orient="vertical", 
                                     command=self.tasks_list.yview)
        self.tasks_list.configure(yscrollcommand=self.scrollbar.set)
        
        # 绑定双击事件（打开文件）
        self.tasks_list.bind('<Double-1>', self.on_task_double_click)

    def setup_layout(self):
        """设置布局"""
        # 配置主框架网格
        self.grid_columnconfigure(0, weight=1)  # 任务列表区域可扩展
        self.grid_rowconfigure(1, weight=1)     # 第二行（列表区域）可扩展
        
        # 布局工具栏
        self.toolbar.grid(row=0, column=0, sticky='ew', padx=5, pady=(2,2))
        
        # 布局任务列表
        self.tasks_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=(2,0))
        self.tasks_list.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')

    def load_tasks(self):
        """载任务列表"""
        try:
            # 清空现有数据
            self.tasks_list.delete(*self.tasks_list.get_children())
            
            # 重要程度映射
            importance_map = {
                '普通': '★',
                '重要': '★★★',
                '紧急': '★★★★★'
            }
            
            # 加载任务
            tasks = self.controller.get_tasks(include_completed=self.show_completed)
            for task in tasks:
                # 将重要程度转换为星号显示
                importance_stars = importance_map.get(task['importance'], '★')
                
                # 准备显示的值
                values = [
                    task['name'],
                    task['due_date'],
                    importance_stars,
                    task['completed_at'] if self.show_completed else task['status']
                ]
                
                # 插入任务
                self.tasks_list.insert('', 'end', iid=task['id'],
                                     values=values)
                
            # 加载完成后调整高度
            self.after(100, self.adjust_tasks_height)
                
        except Exception as e:
            self.logger.error(f"Error loading tasks: {e}")
            messagebox.showerror("错误", "加载任务列表失败")

    def show_add_dialog(self):
        """显示添加任务对话框"""
        dialog = TaskDialog(self, "添加任务")
        result, task_data = dialog.show()  # 获取结果和任务数据
        
        if result:  # 如果有结果（用户点击了确认）
            try:
                self.controller.add_task(
                    name=result['name'],
                    due_date=result['due_date'],
                    file_path=result.get('file_path'),
                    importance=result['importance']
                )
                self.load_tasks()
                # 获取主窗口实例并更新计数
                main_window = self.winfo_toplevel()
                if hasattr(main_window, 'update_task_count'):
                    main_window.update_task_count()
                messagebox.showinfo("成功", "任务添加成功")
            except Exception as e:
                self.logger.error(f"Error adding task: {e}")
                messagebox.showerror("错误", f"添加任务失败: {str(e)}")

    def edit_selected_task(self):
        """处理编辑按钮点击事件"""
        selected = self.tasks_list.selection()
        if not selected:
            messagebox.showwarning("警告", "请选择要编辑的任务")
            return
        
        try:
            task_id = selected[0]
            # 获取任务数据
            task_row = self.controller.get_task(task_id)
            if task_row:
                # 将 sqlite3.Row 对象转换为字典
                task_data = dict(zip(task_row.keys(), task_row))  # 使用 keys() 方法获取列名
                
                # 确保所有必需的字段都存在
                task_data = {
                    'id': task_data.get('id'),
                    'name': task_data.get('name', ''),
                    'due_date': task_data.get('due_date', ''),
                    'importance': task_data.get('importance', '普通'),
                    'status': task_data.get('status', ''),
                    'file_path': task_data.get('file_path', '')
                }
                
                self.show_edit_dialog(task_id, task_data)
            else:
                messagebox.showerror("错误", "无法获取任务数据")
        except Exception as e:
            self.logger.error(f"Error editing task: {e}")
            messagebox.showerror("错误", f"编辑任务失败: {str(e)}")

    def show_edit_dialog(self, task_id, task_data):
        """显示编辑任务对话框"""
        dialog = TaskDialog(self, "编辑任务", task_data, task_id)
        result, updated_task_data = dialog.show()
        
        if result:  # 如果有结果（用户点击了确认）
            try:
                # 调用控制器更新任务
                self.controller.update_task(
                    task_id=task_id,
                    name=result['name'],
                    due_date=result['due_date'],
                    importance=result['importance']
                )
                # 刷新任务列表显示
                self.load_tasks()
                messagebox.showinfo("成功", "任务更新成功")
            except Exception as e:
                self.logger.error(f"Error updating task: {e}")
                messagebox.showerror("错误", f"更新任务失败: {str(e)}")

    def mark_complete(self):
        """标记任务为完成"""
        selected = self.tasks_list.selection()
        if not selected:
            messagebox.showwarning("警告", "请选择要标记的任务")
            return
        
        try:
            task_id = selected[0]
            self.controller.complete_task(task_id)
            self.load_tasks()
            messagebox.showinfo("成功", "任务已标记为完成")
        except Exception as e:
            self.logger.error(f"Error completing task: {e}")
            messagebox.showerror("错误", "标记任务失败")

    def delete_task(self):
        """删除任务"""
        selected = self.tasks_list.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的任务")
            return
        
        if messagebox.askyesno("确认", "确定要删除选中的任务吗？"):
            try:
                task_id = selected[0]
                self.controller.delete_task(task_id)
                self.load_tasks()
                messagebox.showinfo("成功", "任务删除功")
            except Exception as e:
                self.logger.error(f"Error deleting task: {e}")
                messagebox.showerror("错误", "删除任务失败")

    def cleanup_tasks(self):
        """清理已完成任务"""
        try:
            self.controller.cleanup_completed_tasks()
            self.load_tasks()
        except Exception as e:
            self.logger.error(f"Error cleaning up tasks: {e}")
        finally:
            # 继续定时清理
            self.after(3600000, self.cleanup_tasks)  # 每小时检查一

    def on_task_double_click(self, event):
        """双击打开任务关联的文件"""
        tree = event.widget
        selected = tree.selection()
        if selected:
            try:
                task_id = selected[0]
                # 从数据库获取完整的任务信息
                task = self.controller.get_task(task_id)
                if task and task['file_path']:  # 使用字典方式访问
                    if os.path.exists(task['file_path']):
                        if os.name == 'nt':  # Windows
                            os.startfile(task['file_path'])
                        else:  # Linux/Mac
                            subprocess.run(['xdg-open', task['file_path']])
                    else:
                        messagebox.showwarning("警告", "文件不存在")
            except Exception as e:
                self.logger.error(f"Error opening file: {e}")
                messagebox.showerror("错误", "打开文件失败")

    def restore_task(self):
        """恢复任务到未完成状态"""
        selected = self.tasks_list.selection()
        if not selected:
            messagebox.showwarning("警告", "请选择要恢复的任务")
            return
        
        try:
            task_id = selected[0]
            self.controller.restore_task(task_id)
            self.load_tasks()
            messagebox.showinfo("成功", "任务已恢复到未完成状态")
        except Exception as e:
            self.logger.error(f"Error restoring task: {e}")
            messagebox.showerror("错误", "恢复任务失败")

    def repair_data(self):
        """修复任务数据"""
        try:
            if self.controller.repair_tasks_data():
                self.load_tasks()
                messagebox.showinfo("成功", "任务数据已修复")
            else:
                messagebox.showerror("错误", "修复任务数据失败")
        except Exception as e:
            self.logger.error(f"Error repairing data: {e}")
            messagebox.showerror("错误", "修复任务数据失败")

    def adjust_tasks_height(self, event=None):
        """动态调整任务列表高度"""
        try:
            # 获取当前显示的任务数量
            items = self.tasks_list.get_children()
            items_count = len(items)
            
            if items_count == 0:
                # 如果没有任务，设置一个最小高度
                self.tasks_frame.configure(height=100)
                return
                
            # 获取单个项目的高度（通过第一项目）
            first_item = items[0]
            bbox = self.tasks_list.bbox(first_item)
            if not bbox:  # 如果获取不到边界框，返回
                return
                
            item_height = bbox[3]
            
            # 计算所需总高度（项目数 * 项目高度 + 标题栏高度）
            header_height = 25  # 标题栏高度
            total_height = (items_count * item_height) + header_height
            
            # 获取主窗口高度
            main_window = self.winfo_toplevel()
            window_height = main_window.winfo_height()
            
            # 计算可用高度（主窗口高度 - 工具栏高度 - 标题栏高度 - 边距）
            toolbar_height = 30  # 工具栏高度
            title_height = 20    # 标题栏高度
            padding = 5          # 减小边距
            available_height = window_height - toolbar_height - title_height - padding
            
            # 设置最终高度（不超过可用高度）
            final_height = min(total_height, available_height)
            
            # 设置框架高度
            self.tasks_frame.configure(height=final_height)
            
            # 如果内容高度大于可高度，调整主窗口大小
            if total_height > available_height:
                new_window_height = total_height + toolbar_height + title_height + padding
                current_width = main_window.winfo_width()
                # 设置最小和最大窗口高度
                min_height = 600  # 最小高度
                max_height = 900  # 增加最大高度
                new_window_height = max(min_height, min(max_height, int(new_window_height)))
                main_window.geometry(f"{current_width}x{new_window_height}")
                
        except Exception as e:
            self.logger.error(f"Error adjusting tasks height: {e}")