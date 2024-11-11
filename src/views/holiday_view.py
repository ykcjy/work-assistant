import tkinter as tk
from tkinter import ttk
import logging
from datetime import datetime, timedelta
from ..controllers.tasks_controller import TasksController
import tkinter.messagebox as messagebox

class HolidayView(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.controller = TasksController(db)
        self.setup_logging()
        self.create_widgets()
        self.setup_layout()
        
        # 初始化日历显示
        self.current_date = datetime.now()
        self.load_calendar()

    def setup_logging(self):
        self.logger = logging.getLogger(__name__)

    def create_widgets(self):
        # 创建主框架
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill='both', expand=True)
        
        # 创建左侧控制区域
        control_frame = ttk.LabelFrame(self.main_frame, text="节假日设置")
        control_frame.pack(side='left', fill='y', padx=5, pady=5)
        
        # 添加初始化按钮
        self.init_btn = ttk.Button(control_frame, text="初始化法定节假日",
                                 command=self.init_holidays)
        self.init_btn.pack(fill='x', padx=5, pady=5)
        
        # 添加分隔线
        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', padx=5, pady=10)
        
        # 添加调休设置
        ttk.Label(control_frame, text="调休设置:").pack(padx=5, pady=2)
        
        self.holiday_type_var = tk.StringVar(value='holiday')
        self.holiday_radio = ttk.Radiobutton(control_frame, text="设为节假日", 
                                           variable=self.holiday_type_var, 
                                           value='holiday')
        self.holiday_radio.pack(padx=5, pady=2)
        
        self.workday_radio = ttk.Radiobutton(control_frame, text="设为调休上班", 
                                            variable=self.holiday_type_var, 
                                            value='workday')
        self.workday_radio.pack(padx=5, pady=2)
        
        # 添加图例说明
        legend_frame = ttk.LabelFrame(control_frame, text="图例")
        legend_frame.pack(fill='x', padx=5, pady=5)
        
        # 节假日图例
        holiday_frame = ttk.Frame(legend_frame)
        holiday_frame.pack(fill='x', padx=5, pady=2)
        holiday_color = tk.Label(holiday_frame, bg='pink', width=2)
        holiday_color.pack(side='left', padx=2)
        ttk.Label(holiday_frame, text="节假日").pack(side='left')
        
        # 调休图例
        workday_frame = ttk.Frame(legend_frame)
        workday_frame.pack(fill='x', padx=5, pady=2)
        workday_color = tk.Label(workday_frame, bg='lightblue', width=2)
        workday_color.pack(side='left', padx=2)
        ttk.Label(workday_frame, text="调休上班").pack(side='left')
        
        # 周末图例
        weekend_frame = ttk.Frame(legend_frame)
        weekend_frame.pack(fill='x', padx=5, pady=2)
        weekend_color = tk.Label(weekend_frame, bg='lightgray', width=2)
        weekend_color.pack(side='left', padx=2)
        ttk.Label(weekend_frame, text="周末").pack(side='left')
        
        # 创建右侧日历区域
        calendar_container = ttk.Frame(self.main_frame)  # 添加一个容器来居中日历
        calendar_container.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # 创建日历框架，并设置固定宽度
        self.calendar_frame = ttk.LabelFrame(calendar_container, text="节假日日历")
        self.calendar_frame.pack(anchor='n')  # 使用 anchor='n' 使其置顶
        
        # 创建月份导航
        nav_frame = ttk.Frame(self.calendar_frame)
        nav_frame.pack(fill='x', padx=5, pady=5)
        
        # 创建一个内部框架来容纳导航按钮和月份标签，使其居中对齐
        nav_inner_frame = ttk.Frame(nav_frame)
        nav_inner_frame.pack(expand=True)
        
        self.prev_month_btn = ttk.Button(nav_inner_frame, text="◀", width=2, 
                                       command=self.prev_month)
        self.prev_month_btn.pack(side='left')
        
        self.month_label = ttk.Label(nav_inner_frame, font=('Arial', 10, 'bold'),
                                   width=10)  # 设置固定宽度
        self.month_label.pack(side='left', padx=10)  # 添加左右间距
        
        self.next_month_btn = ttk.Button(nav_inner_frame, text="▶", width=2,
                                       command=self.next_month)
        self.next_month_btn.pack(side='left')
        
        # 创建日历网格
        calendar_grid = ttk.Frame(self.calendar_frame)
        calendar_grid.pack(padx=5, pady=5)  # 移除 fill 和 expand 参数
        
        # 创建星期标签
        weekdays = ['一', '二', '三', '四', '五', '六', '日']
        for i, day in enumerate(weekdays):
            label = ttk.Label(calendar_grid, text=day, width=3)  # 减小宽度
            label.grid(row=0, column=i, padx=1, pady=1)
        
        # 创建日期按钮网格
        self.day_buttons = []
        for row in range(6):
            button_row = []
            for col in range(7):
                btn = tk.Button(calendar_grid, width=3, height=1)  # 减小按钮大小
                btn.grid(row=row+1, column=col, padx=1, pady=1)
                button_row.append(btn)
            self.day_buttons.append(button_row)

    def init_holidays(self):
        """初始化当前年份的节假日"""
        try:
            year = self.current_date.year
            if messagebox.askyesno("确认", f"确定要初始化{year}年的法定节假日吗？\n这将清除已有的节假日设置。"):
                if self.controller.init_holidays(year):
                    self.load_calendar()  # 重新加载日历
                else:
                    messagebox.showerror("错误", "节假日初始化失败")
        except Exception as e:
            self.logger.error(f"Error initializing holidays: {e}")
            messagebox.showerror("错误", "节假日初始化失败")

    def setup_layout(self):
        # 使用pack布局管理器
        self.pack(fill='both', expand=True)

    def load_calendar(self):
        """加载日历数据"""
        year = self.current_date.year
        month = self.current_date.month
        
        # 更新月份标签
        self.month_label.config(text=f"{year}年{month}月")
        
        # 获取当月第一天是星期几
        first_day = datetime(year, month, 1)
        first_weekday = first_day.weekday()  # 0是星期一
        
        # 获取上个月的最后一天
        if month == 1:
            last_month = datetime(year-1, 12, 31)
        else:
            if month == 3:  # 处理2月份的特殊情况
                last_month = datetime(year, month-1, 28)
                if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                    last_month = datetime(year, month-1, 29)
            else:
                last_month = datetime(year, month-1, 1)
                while True:
                    try:
                        last_month = datetime(year, month, 1) - timedelta(days=1)
                        break
                    except ValueError:
                        month -= 1
        
        # 获取当月天数
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        days_in_month = (next_month - first_day).days
        
        # 获取节假日数据
        holidays = self.controller.get_holidays(year, month)
        
        # 更新按钮
        # 填充上个月的日期
        last_month_days = last_month.day
        for i in range(first_weekday):
            btn = self.day_buttons[0][i]
            day_num = last_month_days - first_weekday + i + 1
            btn.config(text=f"{day_num}", state='disabled', bg='#F0F0F0')  # 浅灰色
        
        # 填充当月日期
        current_row = 0
        current_col = first_weekday
        for day in range(1, days_in_month + 1):
            btn = self.day_buttons[current_row][current_col]
            date = datetime(year, month, day).date()
            btn.config(text=f"{day}", state='normal')
            
            # 设置按钮样式
            if date in holidays:
                if holidays[date]:  # 调休上班
                    btn.config(bg='lightblue')
                else:  # 节假日
                    btn.config(bg='pink')
            elif date.weekday() >= 5:  # 周末
                btn.config(bg='lightgray')
            else:  # 工作日
                btn.config(bg='white')
            
            # 绑定点击事件
            btn.config(command=lambda d=date: self.toggle_holiday(d))
            
            current_col += 1
            if current_col == 7:
                current_col = 0
                current_row += 1
        
        # 填充下个月的日期
        next_month_day = 1
        while current_row < 6:
            while current_col < 7:
                btn = self.day_buttons[current_row][current_col]
                btn.config(text=f"{next_month_day}", state='disabled', bg='#F0F0F0')  # 浅灰色
                next_month_day += 1
                current_col += 1
            current_col = 0
            current_row += 1
    
    def prev_month(self):
        """显示上个月"""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year-1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month-1)
        self.load_calendar()
    
    def next_month(self):
        """显示下个月"""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year+1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month+1)
        self.load_calendar()

    def toggle_holiday(self, date):
        """切换日期的节假日状态"""
        try:
            is_workday = self.holiday_type_var.get() == 'workday'
            
            # 获取当前日期的节假日状态
            cursor = self.db.conn.cursor()
            cursor.execute('SELECT id, is_workday FROM holidays WHERE date = ?', 
                         (date.strftime('%Y-%m-%d'),))
            current = cursor.fetchone()
            
            # 如果是周末
            if date.weekday() >= 5:
                if current:
                    # 如果已经有记录，删除记录恢复默认状态
                    cursor.execute('DELETE FROM holidays WHERE date = ?', 
                                 (date.strftime('%Y-%m-%d'),))
                else:
                    # 如果没有记录，添加调休记录
                    cursor.execute('''
                        INSERT INTO holidays (date, name, is_workday)
                        VALUES (?, ?, ?)
                    ''', (date.strftime('%Y-%m-%d'),
                         "调休" if is_workday else "节假日",
                         1 if is_workday else 0))
            else:
                # 非周末日期
                if current:
                    # 如果已有记录且状态相同，删除记录恢复默认状态
                    if current['is_workday'] == (1 if is_workday else 0):
                        cursor.execute('DELETE FROM holidays WHERE date = ?', 
                                     (date.strftime('%Y-%m-%d'),))
                    else:
                        # 更新状态
                        cursor.execute('''
                            UPDATE holidays 
                            SET is_workday = ?, name = ?
                            WHERE date = ?
                        ''', (1 if is_workday else 0, 
                             "调休" if is_workday else "节假日",
                             date.strftime('%Y-%m-%d')))
                else:
                    # 添加新记录
                    cursor.execute('''
                        INSERT INTO holidays (date, name, is_workday)
                        VALUES (?, ?, ?)
                    ''', (date.strftime('%Y-%m-%d'),
                         "调休" if is_workday else "节假日",
                         1 if is_workday else 0))
            
            self.db.conn.commit()
            self.load_calendar()  # 刷新日历显示
            
        except Exception as e:
            self.logger.error(f"Error toggling holiday: {e}")
            messagebox.showerror("错误", "设置节假日失败")

    # ... (其他方法与原来的节假日管理相关方法相同) 