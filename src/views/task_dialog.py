import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from tkcalendar import DateEntry
import os

class TaskDialog:
    def __init__(self, parent, title, task=None, task_id=None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.result = None
        self.task_data = None
        self.task_id = task_id
        
        # 定义有效的重要程度值
        self.valid_importance = ["普通", "重要", "紧急"]
        
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # 任务名称
        ttk.Label(main_frame, text="任务名称:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_entry = ttk.Entry(main_frame)
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # 到期日期
        ttk.Label(main_frame, text="到期日期:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.date_entry = DateEntry(main_frame, 
                                  width=20, 
                                  background='darkblue',
                                  foreground='white',
                                  borderwidth=2,
                                  date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # 重要程度
        ttk.Label(main_frame, text="重要程度:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.importance_combo = ttk.Combobox(main_frame, 
                                           values=self.valid_importance,
                                           state="readonly")
        self.importance_combo.set(self.valid_importance[0])
        self.importance_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # 文件路径
        ttk.Label(main_frame, text="文件路径:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.file_path_frame = ttk.Frame(main_frame)
        self.file_path_frame.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        
        self.file_path_entry = ttk.Entry(self.file_path_frame)
        self.file_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.browse_button = ttk.Button(self.file_path_frame, 
                                      text="浏览", 
                                      command=self.browse_file)
        self.browse_button.pack(side=tk.RIGHT, padx=(5, 0))

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        # 取消按钮
        ttk.Button(button_frame, 
                  text="取消", 
                  command=self.cancel
        ).pack(side=tk.LEFT, padx=5)
        
        # 确认按钮
        ttk.Button(button_frame, 
                  text="确认", 
                  command=self.confirm
        ).pack(side=tk.LEFT, padx=5)

        # 配置网格权重
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # 如果有任务数据，填充表单
        if task:
            self.name_entry.insert(0, task.get('name', ''))
            if 'due_date' in task:
                try:
                    date_obj = datetime.strptime(task['due_date'], '%Y-%m-%d')
                    self.date_entry.set_date(date_obj)
                except ValueError:
                    pass
            if 'importance' in task:
                importance = task['importance']
                if importance in self.valid_importance:
                    self.importance_combo.set(importance)
            if 'file_path' in task and task['file_path']:
                self.file_path_entry.insert(0, task['file_path'])

    def browse_file(self):
        """打开文件选择对话框"""
        file_path = filedialog.askopenfilename(
            title="选择文件",
            filetypes=[
                ("所有文件", "*.*"),
                ("文本文件", "*.txt"),
                ("Excel文件", "*.xlsx;*.xls"),
                ("Word文件", "*.docx;*.doc"),
                ("PDF文件", "*.pdf")
            ]
        )
        if file_path:
            # 更新文件路径
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, file_path)
            
            # 如果任务名称为空，自动填入文件名（不含扩展名）
            if not self.name_entry.get().strip():
                file_name = os.path.splitext(os.path.basename(file_path))[0]
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, file_name)

    def confirm(self):
        """确认按钮的回调函数"""
        if not self.name_entry.get().strip():
            messagebox.showwarning("警告", "请输入任务名称！")
            return

        try:
            importance = self.importance_combo.get()
            if importance not in self.valid_importance:
                messagebox.showerror("错误", f"无效的重要程度值。必须是: {', '.join(self.valid_importance)}")
                return

            self.task_data = {
                'id': self.task_id,
                'name': self.name_entry.get().strip(),
                'due_date': self.date_entry.get_date().strftime('%Y-%m-%d'),
                'importance': importance,
                'file_path': self.file_path_entry.get().strip() or None
            }
            
            self.result = self.task_data
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")

    def show(self):
        """显示对话框并等待用户响应"""
        self.dialog.grab_set()
        
        # 居中显示
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        self.dialog.wait_window()
        return self.result, self.task_data

    def cancel(self):
        """取消按钮的回调函数"""
        self.result = False
        self.task_data = None
        self.dialog.destroy()