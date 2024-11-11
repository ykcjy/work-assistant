import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from src.controllers.files_controller import FilesController

class TaskEditor:
    def __init__(self, master, files_controller):
        self.master = master
        self.files_controller = files_controller
        
        self.task_name_entry = tk.Entry(master)
        self.task_name_entry.pack()

        self.file_id_entry = tk.Entry(master)
        self.file_id_entry.pack()

        self.confirm_button = tk.Button(master, text="确认", command=self.confirm_task)
        self.confirm_button.pack()

        self.edit_button = tk.Button(master, text="编辑任务", command=self.open_edit_window)
        self.edit_button.pack()

    def open_edit_window(self):
        """打开编辑任务的弹窗"""
        edit_window = tk.Toplevel(self.master)
        edit_window.title("编辑任务")
        
        # 创建一个框架来容纳所有控件
        main_frame = tk.Frame(edit_window)
        main_frame.pack(padx=10, pady=10)

        # 任务名称输入区域
        tk.Label(main_frame, text="任务名称:").pack()
        task_name_entry = tk.Entry(main_frame)
        task_name_entry.pack()

        # 到期日期选择区域
        tk.Label(main_frame, text="到期日期:").pack()
        date_entry = tk.Entry(main_frame)
        # 设置默认日期为今天
        date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        date_entry.pack()

        # 重要程度选择区域
        tk.Label(main_frame, text="重要程度:").pack()
        importance_entry = tk.Entry(main_frame)
        importance_entry.pack()

        # 创建按钮框架
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)

        # 取消按钮
        cancel_button = tk.Button(
            button_frame, 
            text="取消",
            command=edit_window.destroy
        )
        cancel_button.pack(side=tk.LEFT, padx=5)

        # 确认按钮
        confirm_button = tk.Button(
            button_frame,
            text="确认",
            command=lambda: self.confirm_edit_task(
                task_name_entry.get(),
                date_entry.get(),
                importance_entry.get(),
                edit_window
            )
        )
        confirm_button.pack(side=tk.LEFT, padx=5)

    def confirm_edit_task(self, task_name, due_date, importance, window):
        """处理确认编辑任务的逻辑"""
        if not all([task_name, due_date, importance]):
            messagebox.showwarning("警告", "请填写所有字段！")
            return
        try:
            # 验证日期格式
            datetime.strptime(due_date, '%Y-%m-%d')
            
            # 这里添加保存任务的逻辑
            self.files_controller.confirm_edit(task_name)
            messagebox.showinfo("确认", "任务已确认！")
            window.destroy()  # 关闭编辑窗口
        except ValueError:
            messagebox.showerror("错误", "日期格式无效，请使用 YYYY-MM-DD 格式")
        except Exception as e:
            messagebox.showerror("错误", f"确认任务失败: {e}")

    def confirm_task(self):
        """处理确认任务的逻辑"""
        file_id = self.get_file_id()
        if file_id is None:
            messagebox.showwarning("警告", "未找到文件 ID！")
            return
        try:
            self.files_controller.confirm_edit(file_id)
            messagebox.showinfo("确认", "任务已确认！")
        except Exception as e:
            messagebox.showerror("错误", f"确认任务失败: {e}")

    def get_file_id(self):
        """获取待确认的文件 ID"""
        try:
            return int(self.file_id_entry.get())
        except ValueError:
            return None

if __name__ == "__main__":
    root = tk.Tk()
    db = ...  # 初始化数据库连接
    files_controller = FilesController(db)
    app = TaskEditor(root, files_controller)
    root.mainloop()