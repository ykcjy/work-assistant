import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from ..controllers.files_controller import FilesController

class FilesView(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.controller = FilesController(db)
        self.setup_logging()
        self.create_widgets()
        self.setup_layout()
        self.load_files()

    def setup_logging(self):
        self.logger = logging.getLogger(__name__)

    def create_widgets(self):
        # 创建工具栏
        self.create_toolbar()
        
        # 创建文件列表
        self.create_files_list()

    def create_toolbar(self):
        self.toolbar = ttk.Frame(self)
        
        # 添加按钮
        self.add_btn = ttk.Button(self.toolbar, text="添加文件", 
                                 command=self.add_file)
        self.edit_btn = ttk.Button(self.toolbar, text="编辑", 
                                  command=self.edit_file)
        self.delete_btn = ttk.Button(self.toolbar, text="删除", 
                                    command=self.delete_file)

    def create_files_list(self):
        # 文件列表框架
        self.files_frame = ttk.LabelFrame(self, text="文件快捷方式")
        
        # 创建列表
        columns = ('文件名', '路径')
        self.files_list = ttk.Treeview(self.files_frame, columns=columns, 
                                      show='headings')
        
        # 设置列
        self.files_list.heading('文件名', text='文件名')
        self.files_list.heading('路径', text='路径')
        
        self.files_list.column('文件名', width=150)
        self.files_list.column('路径', width=350)
        
        # 添加滚动条
        self.scrollbar = ttk.Scrollbar(self.files_frame, orient="vertical", 
                                     command=self.files_list.yview)
        self.files_list.configure(yscrollcommand=self.scrollbar.set)
        
        # 绑定双击事件
        self.files_list.bind('<Double-1>', self.on_file_double_click)

    def setup_layout(self):
        # 配置主框架网格
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 布局工具栏
        self.toolbar.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        self.add_btn.pack(side='left', padx=2)
        self.edit_btn.pack(side='left', padx=2)
        self.delete_btn.pack(side='left', padx=2)
        
        # 布局文件列表
        self.files_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        self.files_list.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')

    def load_files(self):
        """加载文件列表"""
        try:
            # 清空现有数据
            self.files_list.delete(*self.files_list.get_children())
            
            # 加载文件数据
            files = self.controller.get_files()
            for file in files:
                self.files_list.insert('', 'end', iid=file['id'],
                                     values=(file['name'], file['file_path']))
        except Exception as e:
            self.logger.error(f"Error loading files: {e}")
            messagebox.showerror("错误", "加载文件列表失败")

    def add_file(self):
        """添加文件"""
        try:
            # 打开文件选择对话框
            file_path = filedialog.askopenfilename(title="选择文件")
            if file_path:
                # 调用控制器添加文件
                self.controller.add_file(file_path)
                self.load_files()  # 重新加载列表
                messagebox.showinfo("成功", "文件添加成功")
        except Exception as e:
            self.logger.error(f"Error adding file: {e}")
            messagebox.showerror("错误", "添加文件失败")

    def edit_file(self):
        """编辑文件路径"""
        selected = self.files_list.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要编辑的文件")
            return
        
        try:
            file_id = selected[0]
            current_path = self.files_list.item(file_id)['values'][1]
            
            # 打开文件选择对话框
            new_path = filedialog.askopenfilename(
                title="选择新文件",
                initialfile=current_path
            )
            
            if new_path:
                self.controller.update_file(file_id, new_path)
                self.load_files()
                messagebox.showinfo("成功", "文件路径更新成功")
        except Exception as e:
            self.logger.error(f"Error editing file: {e}")
            messagebox.showerror("错误", "编辑文件失败")

    def delete_file(self):
        """删除文件快捷方式"""
        selected = self.files_list.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的文件")
            return
        
        if messagebox.askyesno("确认", "确定要删除选中的文件快捷方式吗？"):
            try:
                file_id = selected[0]
                self.controller.delete_file(file_id)
                self.load_files()
                messagebox.showinfo("成功", "文件删除成功")
            except Exception as e:
                self.logger.error(f"Error deleting file: {e}")
                messagebox.showerror("错误", "删除文件失败")

    def on_file_double_click(self, event):
        """双击打开文件"""
        selected = self.files_list.selection()
        if selected:
            try:
                file_id = selected[0]
                file_path = self.files_list.item(file_id)['values'][1]
                self.controller.open_file(file_path)
            except Exception as e:
                self.logger.error(f"Error opening file: {e}")
                messagebox.showerror("错误", "打开文件失败") 