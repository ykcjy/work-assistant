import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import webbrowser
from ..controllers.bookmarks_controller import BookmarksController

class BookmarksView(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.controller = BookmarksController(db)
        self.setup_logging()
        self.create_widgets()
        self.setup_layout()
        
        # 直接加载数据，不再延迟
        self.load_bookmarks()
        
        # 添加一个标志来防止重复调整
        self.adjusting_height = False
        
        # 初始化完成后调整高度
        self.after(100, self.adjust_bookmarks_height)

    def setup_logging(self):
        self.logger = logging.getLogger(__name__)

    def create_widgets(self):
        """创建所有控件"""
        # 创建左侧分类树
        self.create_category_tree()
        
        # 创建右侧书签列表
        self.create_bookmarks_list()
        
        # 创建工具栏
        self.create_toolbar()

    def create_category_tree(self):
        # 分类树框架
        self.category_frame = ttk.LabelFrame(self, text="分类")
        
        # 分类树
        self.category_tree = ttk.Treeview(self.category_frame, selectmode='browse')
        self.category_tree.heading('#0', text='分类', anchor='w')
        
        # 滚动条
        self.category_scroll = ttk.Scrollbar(self.category_frame, orient="vertical", 
                                           command=self.category_tree.yview)
        self.category_tree.configure(yscrollcommand=self.category_scroll.set)
        
        # 绑定事件
        self.category_tree.bind('<<TreeviewSelect>>', self.on_category_select)

    def on_category_select(self, event):
        """分类选择事件处理"""
        selected = self.category_tree.selection()
        if selected:
            category_id = selected[0]
            try:
                # 加载该分类下的书签
                bookmarks = self.controller.get_bookmarks(category_id)
                # 清空当前书签列表
                self.bookmarks_list.delete(*self.bookmarks_list.get_children())
                # 添加书签到列表
                for bookmark in bookmarks:
                    # 使用索引访问，如果没有 username 则显示'abc'
                    username = bookmark['username'] if 'username' in bookmark.keys() else 'abc'
                    self.bookmarks_list.insert('', 'end', iid=bookmark['id'],
                        values=(bookmark['name'], username, bookmark['browser']))
                # 调整高度
                self.after(100, self.adjust_bookmarks_height)
            except Exception as e:
                self.logger.error(f"Error loading bookmarks for category: {e}")
                messagebox.showerror("错误", "加载书签失败")

    def add_category(self):
        """添加分类"""
        dialog = CategoryDialog(self, "添加分类")
        if dialog.result:
            try:
                self.controller.add_category(dialog.result['name'])
                self.load_bookmarks()
                messagebox.showinfo("成功", "分类添加成功")
            except Exception as e:
                self.logger.error(f"Error adding category: {e}")
                messagebox.showerror("错误", "添加分类失败")

    def edit_category(self):
        """编辑分类"""
        selected = self.category_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要编辑的分类")
            return
        
        category_id = selected[0]
        current_name = self.category_tree.item(category_id)['text']
        dialog = CategoryDialog(self, "编辑分类", {'name': current_name})
        
        if dialog.result:
            try:
                self.controller.update_category(category_id, dialog.result['name'])
                self.load_bookmarks()
                messagebox.showinfo("成功", "分类更新成功")
            except Exception as e:
                self.logger.error(f"Error updating category: {e}")
                messagebox.showerror("错", "更新分类失败")

    def delete_category(self):
        """删除分类"""
        selected = self.category_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的分类")
            return
        
        if messagebox.askyesno("确认", "删除分类将同时删除该分类下的所有书签，确定要继续吗？"):
            try:
                category_id = selected[0]
                self.controller.delete_category(category_id)
                self.load_bookmarks()
                messagebox.showinfo("成功", "分类删除成功")
            except Exception as e:
                self.logger.error(f"Error deleting category: {e}")
                messagebox.showerror("错误", "删除分类失败")

   

    def on_mouse_move(self, event):
        """处理鼠标移动事件"""
        try:
            # 获取鼠标位置对应的单元格
            item = self.bookmarks_list.identify_row(event.y)
            
            # 如果移动到新的项目上
            if item != self.current_hover_item:
                # 移除之前项目的高亮
                if self.current_hover_item:
                    self.bookmarks_list.item(self.current_hover_item, tags=())
                
                # 高亮当前项目
                if item:
                    self.bookmarks_list.item(item, tags=('hover',))
                    self.current_hover_item = item
                    
                    # 从数据库获取完整的书签信息
                    bookmark = self.controller.get_bookmark(item)
                    if bookmark and bookmark['url']:
                        # 更新悬停标签内容为URL
                        self.hover_label.configure(text=bookmark['url'])
                        
                        # 获取鼠标相对于屏幕的位置
                        x = event.x_root + 10  # 鼠标右侧10像素
                        y = event.y_root + 10  # 鼠标下方10像素
                        
                        # 显示悬停标签
                        self.hover_label.place(x=event.x + 10, y=event.y + 10)
                        self.hover_label.lift()  # 确保标签显示在最上层
                
        except Exception as e:
            self.logger.error(f"Error handling mouse move: {e}")

    def on_mouse_leave(self, event):
        """处理鼠标离开事件"""
        try:
            # 隐藏悬停标签
            self.hover_label.place_forget()
            
            # 移除高亮
            if self.current_hover_item:
                self.bookmarks_list.item(self.current_hover_item, tags=())
                self.current_hover_item = None
                
        except Exception as e:
            self.logger.error(f"Error handling mouse leave: {e}")

    def create_toolbar(self):
        """创建工具栏"""
        self.toolbar = ttk.Frame(self)
        
        # 分类按钮
        self.add_category_btn = ttk.Button(self.toolbar, text="添加分类", 
                                         command=self.add_category)
        self.edit_category_btn = ttk.Button(self.toolbar, text="编辑分类", 
                                          command=self.edit_category)
        self.del_category_btn = ttk.Button(self.toolbar, text="删除分类", 
                                         command=self.delete_category)
        
        # 书签按钮
        self.add_bookmark_btn = ttk.Button(self.toolbar, text="添加书签", 
                                         command=self.add_bookmark)
        self.edit_bookmark_btn = ttk.Button(self.toolbar, text="编辑书签", 
                                          command=self.edit_bookmark)
        self.del_bookmark_btn = ttk.Button(self.toolbar, text="删除书签", 
                                         command=self.delete_bookmark)

        # 添加批量导入按钮
        self.import_bookmark_btn = ttk.Button(
            self.toolbar,
            text="批量导入",
            command=self.on_import_bookmarks
        )

    def setup_layout(self):
        """设置布局"""
        # 配置框架网格权重
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 布局工具栏
        self.toolbar.grid(row=0, column=0, columnspan=2, sticky='ew', padx=5, pady=(2,2))
        self.add_category_btn.pack(side='left', padx=2)
        self.edit_category_btn.pack(side='left', padx=2)
        self.del_category_btn.pack(side='left', padx=2)
        ttk.Separator(self.toolbar, orient='vertical').pack(side='left', padx=5, fill='y')
        self.add_bookmark_btn.pack(side='left', padx=2)
        self.edit_bookmark_btn.pack(side='left', padx=2)
        self.del_bookmark_btn.pack(side='left', padx=2)
        self.import_bookmark_btn.pack(side='left', padx=2)  # 添加批量导入按钮
        
        # 布局分类树
        self.category_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=(2,0))
        self.category_tree.pack(side='left', fill='both', expand=True)
        self.category_scroll.pack(side='right', fill='y')
        
        # 布局书签列表
        self.bookmarks_frame.grid(row=1, column=1, sticky='nsew', padx=5, pady=(2,0))
        self.bookmarks_list.pack(side='left', fill='both', expand=True)
        
        # 禁用自动调整大小
        self.bookmarks_frame.pack_propagate(False)
        self.bookmarks_frame.grid_propagate(False)

    def adjust_bookmarks_height(self, event=None):
        """动态调整书签列表高度"""
        if self.adjusting_height:
            return
            
        try:
            self.adjusting_height = True
            
            # 设置固定高度
            self.bookmarks_frame.configure(height=520)
            
            # 强制更新布局
            self.bookmarks_frame.update_idletasks()
            
            # 获取主窗口高度
            main_window = self.winfo_toplevel()
            window_height = main_window.winfo_height()
            
            # 计算所需的窗口高度
            toolbar_height = 25
            padding = 10
            required_height = 520 + toolbar_height + padding
            
            # 调整窗口大小
            if required_height > window_height:
                current_width = main_window.winfo_width()
                main_window.geometry(f"{current_width}x{int(required_height)}")
                
        except Exception as e:
            self.logger.error(f"Error adjusting bookmarks height: {e}")
        finally:
            self.after(100, self.reset_adjusting_flag)

    def reset_adjusting_flag(self):
        """重置高度调整标"""
        self.adjusting_height = False

    def load_bookmarks(self):
        """加载书签数据"""
        try:
            # 清空现有数据
            self.category_tree.delete(*self.category_tree.get_children())
            self.bookmarks_list.delete(*self.bookmarks_list.get_children())
            
            # 加载分类
            categories = self.controller.get_categories()
            default_category_id = None
            first_category_id = None
            
            for category in categories:
                category_id = category['id']
                if first_category_id is None:
                    first_category_id = category_id
                
                self.category_tree.insert('', 'end', iid=category_id, 
                                        text=category['name'])
                # 如果找到"运营"分类，记录其ID
                if category['name'] == '运营':
                    default_category_id = category_id
            
            # 选择并加载默认分类的书签（优先选择运营分类，如果没有则选择第一个分类）
            selected_id = default_category_id or first_category_id
            if selected_id:
                self.category_tree.selection_set(selected_id)
                self.category_tree.focus(selected_id)
                self.category_tree.see(selected_id)
                
                # 加载选中分类的书签
                bookmarks = self.controller.get_bookmarks(selected_id)
                for bookmark in bookmarks:
                    # 使用索引访问，如果没有 username 则显示'abc'
                    username = bookmark['username'] if 'username' in bookmark.keys() else 'abc'
                    self.bookmarks_list.insert('', 'end', iid=bookmark['id'],
                        values=(bookmark['name'], 
                               username,  # 使用变量而不是 get 方法
                               bookmark['browser']))
                
                # 加完成后调整高度
                self.after(200, self.adjust_bookmarks_height)
                
        except Exception as e:
            self.logger.error(f"Error loading bookmarks: {e}")
            messagebox.showerror("错误", "加载书签数据失败")

    def add_bookmark(self):
        """添加书签"""
        selected = self.category_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个分类")
            return
        
        category_id = selected[0]
        dialog = BookmarkDialog(self, "添加书签")
        if dialog.result:
            try:
                self.controller.add_bookmark(
                    category_id=category_id,
                    name=dialog.result['name'],
                    url=dialog.result['url'],
                    browser=dialog.result['browser']
                )
                self.on_category_select(None)  # 刷新书签列表
                # 调整高度
                self.after(100, self.adjust_bookmarks_height)
                messagebox.showinfo("成功", "书签添加成功")
            except Exception as e:
                self.logger.error(f"Error adding bookmark: {e}")
                messagebox.showerror("错误", "添加书签失败")

    def edit_bookmark(self):
        """编辑书签"""
        selected = self.bookmarks_list.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要编辑的书签")
            return
        
        bookmark_id = selected[0]
        # 从数据库获取完整的书签信息
        bookmark = self.controller.get_bookmark(bookmark_id)
        if bookmark:
            dialog = BookmarkDialog(self, "编辑书签", bookmark)
            
            if dialog.result:
                try:
                    self.controller.update_bookmark(
                        bookmark_id=bookmark_id,
                        name=dialog.result['name'],
                        url=dialog.result['url'],
                        browser=dialog.result['browser']
                    )
                    self.on_category_select(None)  # 刷新书签列表
                    # 调整高度
                    self.after(100, self.adjust_bookmarks_height)
                    messagebox.showinfo("成功", "书签更新成功")
                except Exception as e:
                    self.logger.error(f"Error updating bookmark: {e}")
                    messagebox.showerror("错误", "更新书签失败")

    def delete_bookmark(self):
        """删除书签"""
        selected = self.bookmarks_list.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的书签")
            return
        
        if messagebox.askyesno("确认", "确定要删除选中的书签吗？"):
            try:
                bookmark_id = selected[0]
                self.controller.delete_bookmark(bookmark_id)
                self.on_category_select(None)  # 刷新书签列表
                # 调整高度
                self.after(100, self.adjust_bookmarks_height)
                messagebox.showinfo("成功", "书签删除成功")
            except Exception as e:
                self.logger.error(f"Error deleting bookmark: {e}")
                messagebox.showerror("错误", "删除书签失败")

    def on_bookmark_double_click(self, event):
        """双击打开书签"""
        selected = self.bookmarks_list.selection()
        if selected:
            try:
                bookmark_id = selected[0]
                # 从数据库获取完整的书签信息
                bookmark = self.controller.get_bookmark(bookmark_id)
                if bookmark:
                    url = bookmark['url']  # 使用数据库中存储的URL
                    browser = bookmark['browser']
                    self.controller.open_bookmark(url, browser)
            except Exception as e:
                self.logger.error(f"Error opening bookmark: {e}")
                messagebox.showerror("错误", "打开书签失败")

    def on_tab_selected(self, event):
        """处理标签页切换事件"""
        selected_tab = event.widget.select()
        if self.winfo_id() == self.nametowidget(selected_tab).winfo_id():
            # 如果当前选中的标签是书签管理，调整高度
            self.after(100, self.adjust_bookmarks_height)

    def get_category_id(self, category_name):
        """根据分类名称获取分类ID，如果不存在则创建新分类"""
        try:
            # 先查找是否存在该分类
            for item in self.category_tree.get_children():
                if self.category_tree.item(item)['text'] == category_name:
                    return item
                    
            # 如果不存在，创建新分类
            new_category_id = self.controller.add_category(category_name)
            # 刷新分类树，但不刷新整个界面
            self.refresh_categories()
            return new_category_id
            
        except Exception as e:
            self.logger.error(f"Error getting/creating category ID: {e}")
            raise

    def check_bookmark_exists(self, category_id, url):
        """检查指定分类下是否存在相同URL的书签"""
        try:
            bookmarks = self.controller.get_bookmarks(category_id)
            return any(bookmark['url'] == url for bookmark in bookmarks)
        except Exception as e:
            self.logger.error(f"Error checking bookmark existence: {e}")
            return False

    def refresh_categories(self):
        """只刷新分类树"""
        try:
            # 保存当前选中的分类
            selected = self.category_tree.selection()
            
            # 清空并重新加载分类
            self.category_tree.delete(*self.category_tree.get_children())
            categories = self.controller.get_categories()
            
            for category in categories:
                category_id = category['id']
                self.category_tree.insert('', 'end', iid=category_id, 
                                        text=category['name'])
            
            # 恢复选中状态
            if selected:
                self.category_tree.selection_set(selected)
                
        except Exception as e:
            self.logger.error(f"Error refreshing categories: {e}")
            raise

    def on_import_bookmarks(self):
        """处理批量导入"""
        file_path = filedialog.askopenfilename(
            title="选择导入文件",
            filetypes=[("CSV 文件", "*.csv"), ("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
            bookmarks_data = []
            skipped_count = 0  # 记录跳过的重复书签数量
            
            for line in lines:
                if line.strip():
                    category, name, url, username, browser = line.strip().split(',')
                    
                    # 获取分类ID（如果不存在会自动创建）
                    category_id = self.get_category_id(category.strip())
                    
                    # 检查URL是否已存在
                    if self.check_bookmark_exists(category_id, url.strip()):
                        skipped_count += 1
                        continue
                    
                    bookmarks_data.append({
                        'category_id': category_id,
                        'name': name.strip(),
                        'url': url.strip(),
                        'username': username.strip(),
                        'browser': browser.strip()
                    })
            
            if bookmarks_data:
                success_count = self.controller.import_bookmarks(bookmarks_data)
                message = f"成功导入 {success_count} 个书签"
                if skipped_count > 0:
                    message += f"\n跳过 {skipped_count} 个重复的书签"
                messagebox.showinfo("导入结果", message)
            else:
                if skipped_count > 0:
                    messagebox.showinfo("导入结果", f"所有 {skipped_count} 个书签都已存在，未导入任何新书签")
                else:
                    messagebox.showwarning("导入结果", "没有可导入的书签数据")
                
                self.refresh_bookmarks()  # 刷新列表
                
        except Exception as e:
            messagebox.showerror("导入失败", f"导入过程中出现错误：{str(e)}")

    def create_bookmarks_list(self):
        """创建书签列表"""
        # 书签列表框架
        self.bookmarks_frame = ttk.LabelFrame(self, text="书签列表")
        self.bookmarks_frame.pack_propagate(False)  # 禁止自动调整大小
        
        # 创建列表
        columns = ('名称', '用户名', '浏览器')
        self.bookmarks_list = ttk.Treeview(self.bookmarks_frame, columns=columns, 
                                         show='headings')
        
        # 设置列
        self.bookmarks_list.heading('名称', text='名称')
        self.bookmarks_list.heading('用户名', text='用户名')
        self.bookmarks_list.heading('浏览器', text='浏览器')
        
        self.bookmarks_list.column('名称', width=250)
        self.bookmarks_list.column('用户名', width=150)
        self.bookmarks_list.column('浏览器', width=100)
        
        # 创建悬停标签
        self.hover_label = tk.Label(self.bookmarks_frame, 
                                  bg='lightyellow',  # 浅黄色背景
                                  relief='solid',    # 实线边框
                                  borderwidth=1)     # 边框宽度
        
        # 创建高亮标签 - 使用更深的蓝色
        self.bookmarks_list.tag_configure('hover', background='#CCE1FF')  # 从 #E8F0FE 改为 #CCE1FF
        
        # 绑定鼠标事件
        self.bookmarks_list.bind('<Motion>', self.on_mouse_move)    # 鼠标移动
        self.bookmarks_list.bind('<Leave>', self.on_mouse_leave)    # 鼠标离开
        self.bookmarks_list.bind('<Double-1>', self.on_bookmark_double_click)  # 双击打开
        
        # 保存当前高亮的项目ID
        self.current_hover_item = None

    def refresh_bookmarks(self):
        """刷新书签列表"""
        try:
            selected = self.category_tree.selection()
            if selected:
                self.on_category_select(None)
        except Exception as e:
            self.logger.error(f"Error refreshing bookmarks: {e}")
            messagebox.showerror("错误", "刷新书签列表失败")


class CategoryDialog(tk.Toplevel):
    def __init__(self, parent, title, category=None):
        super().__init__(parent)
        self.title(title)
        self.result = None
        
        # 创建表单
        ttk.Label(self, text="分类名称:").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(self, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 如果是编辑模式，填充现有数据
        if category:
            self.name_entry.insert(0, category['name'])
        
        # 按
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="确定", command=self.ok).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="取消", command=self.cancel).pack(side='left', padx=5)
        
        # 设置对话框模态
        self.transient(parent)
        self.grab_set()
        self.wait_window()

    def ok(self):
        """确认按钮回调"""
        self.result = {
            'name': self.name_entry.get()
        }
        self.destroy()

    def cancel(self):
        """取消按钮回调"""
        self.destroy()

class BookmarkDialog(tk.Toplevel):
    def __init__(self, parent, title, bookmark=None):
        super().__init__(parent)
        self.title(title)
        self.result = None
        
        # 创建表单
        ttk.Label(self, text="名称:").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(self, width=40)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self, text="URL:").grid(row=1, column=0, padx=5, pady=5)
        self.url_entry = ttk.Entry(self, width=40)
        self.url_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self, text="用户名:").grid(row=2, column=0, padx=5, pady=5)
        self.username_entry = ttk.Entry(self, width=40)
        self.username_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(self, text="浏览器:").grid(row=3, column=0, padx=5, pady=5)
        self.browser_combobox = ttk.Combobox(self, values=['chrome', 'edge', 'ie'])
        self.browser_combobox.grid(row=3, column=1, padx=5, pady=5)
        
        # 如果是编辑模式，填充现有数据
        if bookmark:
            self.name_entry.insert(0, bookmark['name'])
            self.url_entry.insert(0, bookmark['url'])
            if 'username' in bookmark:
                self.username_entry.insert(0, bookmark['username'])
            self.browser_combobox.set(bookmark['browser'])
        else:
            self.browser_combobox.set('chrome')  # 默认浏览器
        
        # 按钮
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="确定", command=self.ok).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="取消", command=self.cancel).pack(side='left', padx=5)
        
        # 设置对话框模态
        self.transient(parent)
        self.grab_set()
        self.wait_window()

    def ok(self):
        """确认按钮回调"""
        self.result = {
            'name': self.name_entry.get(),
            'url': self.url_entry.get(),
            'username': self.username_entry.get(),
            'browser': self.browser_combobox.get()
        }
        self.destroy()

    def cancel(self):
        """取消按钮回调"""
        self.destroy()