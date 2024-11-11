import tkinter as tk
from tkinter import ttk
from datetime import datetime
from lunar_python import Lunar
import logging
from tkinter import messagebox
import random
import os

from .bookmarks_view import BookmarksView
from .files_view import FilesView
from .tasks_view import TasksView
from .holiday_view import HolidayView

class MainWindow(tk.Tk):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_logging()
        self.setup_window()
        
        # 创建自定义样式
        self.style = ttk.Style()
        # 设置不同标签页的样式
        self.style.configure('Bookmarks.TFrame', background='#E8F5E9')  # 浅绿色
        self.style.configure('Files.TFrame', background='#E3F2FD')      # 浅蓝色
        self.style.configure('Tasks.TFrame', background='#FFF3E0')      # 浅橙色
        self.style.configure('Completed.TFrame', background='#F3E5F5')  # 浅紫色
        
        self.create_widgets()
        self.start_time_update()
        
        # 创建系统托盘图标
        self.create_tray_icon()
        
        # 绑定窗口事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind('<Unmap>', self.on_minimize)  # 绑定最小化事件
        
        # 保存窗口原始位置和大小
        self.normal_geometry = None
        self.minimized = False
        
        self.update_task_count()

    def setup_logging(self):
        """Setup logging configuration"""
        self.logger = logging.getLogger(__name__)

    def setup_window(self):
        """Configure main window properties"""
        self.title("工作助手")
        self.geometry("1000x650")
        self.minsize(800, 550)
        
        # Configure window grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def create_widgets(self):
        """Create main window widgets"""
        self.create_time_display()
        self.create_main_notebook()
        self.create_menu()

    def create_time_display(self):
        """Create time display frame"""
        # 顶部框架
        self.time_frame = ttk.Frame(self)
        self.time_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # 添加标题标签
        title_label = ttk.Label(self.time_frame, text="工作助手", 
                               font=("Arial", 16, "bold"))
        title_label.pack(side="left", padx=10)
        
        # 创建任务提醒标签态显示）
        self.task_count_label = tk.Label(self.time_frame, 
                                       text="",
                                       fg='red',
                                       font=('Arial', 12, 'bold'))
        self.task_count_label.pack(side="left", padx=10)
        
        # 时间显示标签
        self.time_label = ttk.Label(self.time_frame, font=("Arial", 12))
        self.time_label.pack(side="right", padx=10)

    def create_main_notebook(self):
        """Create notebook for main content"""
        # 创建水平分隔的框架
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.main_frame.grid_columnconfigure(0, weight=8)  # notebook占8份宽度
        self.main_frame.grid_columnconfigure(1, weight=2)  # 提醒区域占2份宽度
        
        # 设置样式
        self.style = ttk.Style()
        
        # 配置notebook的基本样式
        self.style.configure('Custom.TNotebook', 
            background='#f0f0f0',
            borderwidth=1,
            relief='solid'  # 添加边框效果
        )
        
        # 配置标签页的基样式
        self.style.configure('Custom.TNotebook.Tab', 
            padding=[20, 8],
            background='#e0e0e0',
            foreground='#666666',  # 未选中时使用灰色文字
            font=('Arial', 10),
            borderwidth=1,
            relief='raised'  # 添加凸起效果
        )
        
        # 配置标签页不同状态的样式
        self.style.map('Custom.TNotebook.Tab',
            background=[
                ('selected', '#333333'),      # 选中时使用深黑色背景
                ('active', '#444444'),        # 鼠标悬停时使用中灰色
                ('!selected', 'gray85')       # 未选中时使用浅灰色，带立体感
            ],
            foreground=[
                ('selected', '#FF4444'),      # 选中时文字为红色
                ('active', '#4444FF'),        # 鼠标停时文字为蓝色
                ('!selected', '#333333')      # 未选中时文字为深灰色
            ],
            font=[
                ('selected', ('Arial', 11, 'bold')),  # 选中时字体加粗且稍大
                ('active', ('Arial', 10, 'bold')),    # 悬停时字体加粗
                ('!selected', ('Arial', 10))          # 未选中时使用普通字体
            ],
            relief=[
                ('selected', 'sunken'),    # 选中时凹陷效果
                ('!selected', 'raised'),   # 未选中时凸起效果
                ('active', 'ridge')        # 悬停时脊状效果
            ],
            borderwidth=[
                ('selected', 2),           # 选中时边框加粗
                ('!selected', 1),          # 未选中时正常边框
                ('active', 1)              # 悬停时正常边框
            ]
        )

        # 创建notebook
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # 创建各个功能模块的标签页
        self.bookmarks_view = BookmarksView(self.notebook, self.db)
        self.files_view = FilesView(self.notebook, self.db)
        self.tasks_view = TasksView(self.notebook, self.db)
        self.completed_tasks_view = TasksView(self.notebook, self.db, show_completed=True)
        self.holiday_view = HolidayView(self.notebook, self.db)  # 添加节假日管理视图

        # 添加标签页到notebook
        self.notebook.add(self.bookmarks_view, text="  网址管理  ", padding=5)
        self.notebook.add(self.files_view, text="  文件管理  ", padding=5)
        self.notebook.add(self.tasks_view, text="  待办任务  ", padding=5)
        self.notebook.add(self.completed_tasks_view, text="  已办任务  ", padding=5)
        self.notebook.add(self.holiday_view, text="  节假日管理  ", padding=5)  # 添加节假日管理标签页

        # 绑定标签切换事件
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # 创建到期提醒区域
        self.create_due_reminder()

        # 立即更新任务计数
        self.after(100, self.update_task_count)

    def create_due_reminder(self):
        """创建到期提醒区域"""
        # 创建提醒区域框架
        self.reminder_frame = ttk.LabelFrame(self.main_frame, text="近期到期任务")
        self.reminder_frame.grid(row=0, column=1, sticky="nsew", padx=(5,0))
        
        # 创建文本显示区域
        self.reminder_text = tk.Text(self.reminder_frame, 
                                   wrap=tk.WORD,
                                   width=15,  # 减小宽度
                                   height=20,
                                   font=('Arial', 10),
                                   spacing1=2,  # 段落前空白
                                   spacing2=0,  # 段落间空白
                                   spacing3=2)  # 段落后空白
        self.reminder_text.pack(fill='both', expand=True, padx=3, pady=3)
        
        # 设置只读
        self.reminder_text.configure(state='disabled')
        
        # 绑定大小变化
        self.reminder_text.bind('<Configure>', lambda e: self.update_due_reminder())
        
        # 立即更新一次
        self.after(100, self.update_due_reminder)

    def update_due_reminder(self):
        """更新到期提醒"""
        try:
            # 获取未完成任务
            tasks = self.tasks_view.controller.get_tasks()
            due_tasks = {
                "需要今天完成": [],      # 节假日前需要完成的紧急任务，以及今明两天到期的紧急任务
                "今天到期": [],         # 今天到期的普通任务
                "明天到期": [],         # 明天到期的普通任务
                "后天到期": []          # 后天到期的任务
            }
            
            for task_row in tasks:
                # 将 sqlite3.Row 转换为字典
                task = dict(task_row)
                
                needs_reminder, message = self.tasks_view.controller.check_due_date(
                    task['due_date'], 
                    task_row
                )
                
                if needs_reminder:
                    # 获取任务的重要程度
                    importance = task.get('importance', '普通')
                    
                    # 如果是紧急任务且今明两天到期，或需要今天完成，都���在"需要今天完成"分类下
                    if importance == '紧急' and (
                        "需要今天完成" in message or 
                        "今天到期" in message or 
                        "明天到期" in message or
                        "需要提前完成" in message
                    ):
                        due_tasks["需要今天完成"].append(task)
                    elif "今天到期" in message and importance != '紧急':
                        due_tasks["今天到期"].append(task)
                    elif "明天到期" in message and importance != '紧急':
                        due_tasks["明天到期"].append(task)
                    elif "后天到期" in message:
                        due_tasks["后天到期"].append(task)
            
            # 更新显示
            self.reminder_text.configure(state='normal')
            self.reminder_text.delete('1.0', tk.END)
            
            # 创建标签样式
            self.reminder_text.tag_configure('header',
                                          foreground='#333333',
                                          font=('Arial', 10, 'bold'))
            self.reminder_text.tag_configure('task_name', 
                                          foreground='black',
                                          font=('Arial', 10))
            self.reminder_text.tag_configure('due_today', 
                                          foreground='red',
                                          font=('Arial', 10, 'bold'))
            self.reminder_text.tag_configure('due_urgent',  # 新增紧急任务样式
                                          foreground='#FF0000',
                                          font=('Arial', 10, 'bold'))
            self.reminder_text.tag_configure('due_tomorrow', 
                                          foreground='#FF6600',
                                          font=('Arial', 10))
            self.reminder_text.tag_configure('due_later', 
                                          foreground='#0066CC',
                                          font=('Arial', 10))
            self.reminder_text.tag_configure('separator',
                                          font=('Arial', 8))
            
            # 显示任务
            has_content = False
            # 按固定顺序显示分类
            categories = ["需要今天完成", "今天到期", "明天到期", "后天到期"]
            for category in categories:
                tasks_list = due_tasks[category]
                if tasks_list:
                    if has_content:
                        # 计算分隔线长度
                        text_width = self.reminder_text.winfo_width()
                        char_width = 8
                        separator_count = max(10, min(15, text_width // char_width))
                        self.reminder_text.insert(tk.END, "\n" + "─" * separator_count + "\n", 'separator')
                    
                    # 选择合适的标签
                    if category == "需要今天完成":
                        tag = 'due_today'
                    elif category == "今天到期":
                        tag = 'due_today'
                    elif category == "明天到期":
                        tag = 'due_tomorrow'
                    else:
                        tag = 'due_later'
                    
                    # 插入分类标题
                    self.reminder_text.insert(tk.END, f"{category}：\n", tag)
                    
                    # 插入任务列表
                    for task in tasks_list:
                        importance = task['importance'] if 'importance' in task else '普通'
                        importance_mark = '★' if importance == '紧急' else '•'
                        task_name = task['name']
                        # 添加到期日期显示（对于非今天到期的任务）
                        if category not in ["需要今天完成", "今天到期"]:
                            due_date = task['due_date']
                            task_text = f"{importance_mark} {task_name} ({due_date})\n"
                        else:
                            task_text = f"{importance_mark} {task_name}\n"
                        self.reminder_text.insert(tk.END, task_text, 'task_name')
                    
                    has_content = True
            
            if not has_content:
                self.reminder_text.insert(tk.END, "暂无近期到期任务", 'header')
            
            self.reminder_text.configure(state='disabled')
            
        except Exception as e:
            self.logger.error(f"Error updating due reminder: {str(e)}")
        finally:
            # 每分钟更新一次
            self.after(60000, self.update_due_reminder)

    def update_task_count(self):
        """更新务计数"""
        try:
            # 获取未完成任务总数
            pending_count = self.tasks_view.controller.get_pending_tasks_count()
            
            if pending_count > 0:
                # 更新计数提示文本
                text = f"★ 温馨提示：当前有 {pending_count} 个待办任务需要处理 ★"
                self.task_count_label.configure(text=text)
            else:
                # 隐藏标签
                self.task_count_label.configure(text="")
                
        except Exception as e:
            self.logger.error(f"Error updating task count: {e}")
        finally:
            # 每分钟更新一次
            self.after(60000, self.update_task_count)

    def create_menu(self):
        """Create main menu bar"""
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)

        # 文件菜单
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="刷新", command=self.refresh_current_view)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.quit)

        # 帮助菜单
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)

    def update_time(self):
        """Update time display"""
        now = datetime.now()
        lunar = Lunar.fromDate(now)
        time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        lunar_str = f"农历 {lunar.getYearInChinese()}年 {lunar.getMonthInChinese()}月 {lunar.getDayInChinese()}"
        self.time_label.config(text=f"{time_str} | {lunar_str}")
        self.after(1000, self.update_time)

    def start_time_update(self):
        """Start time update loop"""
        self.update_time()

    def on_tab_changed(self, event):
        """标签页切换事件处理"""
        current_tab = self.notebook.select()
        current_view = self.notebook.index(current_tab)
        
        # 记录当前选中的标签页
        self.logger.info(f"Tab changed to index: {current_view}")
        
        # 刷新当前视图
        if current_view == 0:  # 如果是书签管理标签
            self.logger.info("Switching to BookmarksView")
            self.bookmarks_view.on_tab_selected(event)
        elif current_view == 1:
            self.logger.info("Switching to FilesView")
            self.files_view.load_files()
        elif current_view == 2:
            self.logger.info("Switching to TasksView")
            self.tasks_view.load_tasks()
        elif current_view == 3:
            self.logger.info("Switching to CompletedTasksView")
            self.completed_tasks_view.load_tasks()
        elif current_view == 4:
            self.logger.info("Switching to HolidayView")
            self.holiday_view.load_calendar()

    def refresh_current_view(self):
        """刷新当前视图"""
        try:
            # 获取当前选中的标签页
            current_tab = self.notebook.select()
            if current_tab:
                current_index = self.notebook.index(current_tab)
                
                # 根据不同的标签页执行相应的刷新操作
                if current_index == 0:  # 网址管理
                    self.bookmarks_view.load_bookmarks()
                    self.logger.info("Refreshed BookmarksView")
                elif current_index == 1:  # 文件管理
                    self.files_view.load_files()
                    self.logger.info("Refreshed FilesView")
                elif current_index == 2:  # 待办任务
                    self.tasks_view.load_tasks()
                    self.logger.info("Refreshed TasksView")
                elif current_index == 3:  # 已办任务
                    self.completed_tasks_view.load_tasks()
                    self.logger.info("Refreshed CompletedTasksView")
                elif current_index == 4:  # 节假日管理
                    self.holiday_view.load_calendar()  # 修改为正确的方法名
                    self.logger.info("Refreshed HolidayView")
                
                # 更新任务计数和到期提醒
                self.update_task_count()
                self.update_due_reminder()
                
                # 显示刷新成功消息
                messagebox.showinfo("提示", "刷新成功")
                
        except Exception as e:
            self.logger.error(f"Error refreshing current view: {e}")
            messagebox.showerror("错误", f"刷新失败: {str(e)}")

    def show_about(self):
        """显示关于对话框"""
        about_text = """工作助手 v1.0

一个简单的工作辅助工具，包含：
- 常用网址管理
- 文件快捷方式
- 任务提醒功能

作者：铜碗豆"""
        tk.messagebox.showinfo("关于", about_text)

    def on_closing(self):
        """窗口关闭事件处理"""
        if messagebox.askyesno("确认", "确定退出程序吗？"):
            self.quit_app()

    def create_tray_icon(self):
        """创建系统托盘图标"""
        try:
            from PIL import Image, ImageDraw
            import pystray
            from pystray import MenuItem as item
            
            # 加载 logo.jfif 作为图标
            icon_path = "logo.jfif"
            if os.path.exists(icon_path):
                # 打开并调整图像大小
                image = Image.open(icon_path)
                # 确保图像是 RGBA 模式
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                # 调整为合适的大小
                image = image.resize((64, 64))
            else:
                # 如果找不到图标文件，创建一个简单的图标
                image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
                draw = ImageDraw.Draw(image)
                margin = 2
                draw.ellipse([margin, margin, 64-margin, 64-margin], 
                            fill='red')
            
            # 创建托盘菜单
            menu = (
                item('显示', self._show_window),
                item('退出', self.quit_app),
            )
            
            # 创建托盘图标
            self.tray_icon = pystray.Icon(
                "工作助手",
                icon=image,
                menu=menu
            )
            
        except Exception as e:
            self.logger.error(f"Error creating tray icon: {e}")
            self.tray_icon = None

    def _show_window(self, icon=None):
        """从托盘恢复窗口（内部方法）"""
        try:
            # 停止托盘图标
            if self.tray_icon and self.tray_icon.visible:
                self.tray_icon.stop()
            
            # 恢窗口
            self.deiconify()
            if self.normal_geometry:
                self.geometry(self.normal_geometry)
            
            # 将窗口置于最前（临时）
            self.lift()
            self.focus_force()
            self.attributes('-topmost', True)
            self.after(100, lambda: self.attributes('-topmost', False))  # 缩短置顶时间
            
            # 刷新当前视图
            self.refresh_current_view()
            
            self.minimized = False
            
        except Exception as e:
            self.logger.error(f"Error showing window: {e}")

    def on_minimize(self, event=None):
        """最小事件处理"""
        if not self.minimized and event.widget == self:
            # 保存当前窗口位置和大小
            self.normal_geometry = self.geometry()
            
            # 隐藏窗口
            self.withdraw()
            
            # 显示托盘图标
            if self.tray_icon and not self.tray_icon.visible:
                self.tray_icon.run()
            
            self.minimized = True

    def quit_app(self, icon=None):
        """退出应用程序"""
        try:
            # 停止托盘图标
            if self.tray_icon and self.tray_icon.visible:
                self.tray_icon.stop()
            
            # 关闭数据库连接
            self.db.close()
            
            # 退出程序
            self.quit()
        except Exception as e:
            self.logger.error(f"Error quitting application: {e}")
            self.quit()