import sys
import logging
from pathlib import Path
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw
import PIL.ImageTk  # 改用这种方式导入
from src.models.database import Database
from src.views.main_window import MainWindow

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def ensure_data_directory():
    """Ensure data directory exists"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

def main():
    """Main application entry point"""
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("Starting application")

        # Ensure data directory exists
        ensure_data_directory()

        # Initialize database
        db = Database()

        # Create and run main window
        app = MainWindow(db)
        
        def on_closing():
            """处理窗口关闭事件"""
            try:
                response = messagebox.askokcancel(
                    "退出确认",
                    "确定要退出工作助手吗？",
                    parent=app    # 确保对话框与主窗口关联
                )
                
                if response:
                    logger.info("User confirmed exit")
                    app.quit()
                    app.destroy()
                    os._exit(0)  # 使用 os._exit() 替代 sys.exit()
            except Exception as e:
                logger.error(f"Error in on_closing: {e}")
                os._exit(1)

        def quit_app(icon=None):
            """处理系统托盘的退出事件"""
            try:
                if icon:
                    icon.stop()
                
                # 确保在主线程中运行对话框
                def show_confirm_dialog():
                    app.deiconify()  # 确保窗口可见以显示对话框
                    app.update()     # 强制更新窗口状态
                    app.lift()       # 将窗口提升到最前
                    app.focus_force()  # 强制获取焦点
                    
                    response = messagebox.askokcancel(
                        "退出确认",
                        "确定要退出工作助手吗？",
                        parent=app
                    )
                    
                    if response:
                        logger.info("User confirmed exit from tray")
                        app.after(100, lambda: os._exit(0))  # 延迟退出以确保对话框关闭
                    else:
                        # 如果用户取消退出，恢复系统托盘
                        if icon:
                            app.withdraw()
                            icon.run()
                
                # 确保在主线程中执行
                if app.winfo_exists():
                    app.after(0, show_confirm_dialog)
                else:
                    os._exit(0)
                
            except Exception as e:
                logger.error(f"Error in quit_app: {e}")
                os._exit(1)

        def restore_window(icon):
            """从系统托盘恢复窗口"""
            try:
                icon.stop()  # 停止系统托盘图标
                
                # 恢复窗口并确保显示在最前面
                app.deiconify()  # 恢复窗口
                app.state('normal')  # 确保窗口正常显示
                
                # 强制窗口显示在最前面
                app.attributes('-topmost', True)  # 设置为最顶层
                app.lift()  # 提升窗口
                app.focus_force()  # 强制获取焦点
                
                # 短暂延迟后取消最顶层设置
                def reset_topmost():
                    app.attributes('-topmost', False)
                    app.update()
                
                app.after(100, reset_topmost)  # 100ms后取消最顶层设置
                
                # 重新绑定关闭事件
                app.protocol("WM_DELETE_WINDOW", on_closing)
                
            except Exception as e:
                logger.error(f"Error in restore_window: {e}")

        def minimize_to_tray():
            """最小化到系统托盘"""
            try:
                import pystray
                from PIL import Image, ImageDraw
                
                # 创建一个醒目的默认图标
                def create_default_icon():
                    # 创建 64x64 的图像
                    img = Image.new('RGB', (64, 64), color='#FFFFFF')
                    draw = ImageDraw.Draw(img)
                    
                    # 绘制蓝色背景圆形
                    draw.ellipse([4, 4, 60, 60], fill='#2196F3')
                    
                    # 绘制白色的 "W" 字母（代表 "Work"）
                    draw.polygon([
                        (16, 16),   # 左上
                        (24, 16),   # 左上内
                        (32, 40),   # 中间下
                        (40, 16),   # 右上内
                        (48, 16),   # 右上
                        (38, 48),   # 右下
                        (32, 32),   # 中间
                        (26, 48)    # 左下
                    ], fill='white')
                    
                    return img
                
                # 尝试加载图标
                try:
                    icon_path = "logo.jfif"
                    if os.path.exists(icon_path):
                        image = Image.open(icon_path)
                        # 确保图标大小合适
                        image = image.resize((64, 64), Image.Resampling.LANCZOS)
                    else:
                        # 如果找不到图标文件，使用新的默认图标
                        image = create_default_icon()
                except Exception:
                    # 如果加载失败，使用新的默认图标
                    image = create_default_icon()
                
                menu = pystray.Menu(
                    pystray.MenuItem("显示", restore_window),
                    pystray.MenuItem("退出", quit_app)  # 简化 lambda
                )
                
                icon = pystray.Icon("name", image, "工作助手", menu)
                app.withdraw()  # 隐藏窗口
                icon.run()  # 运行系统托盘
                
            except Exception as e:
                logger.error(f"Error in minimize_to_tray: {e}")
                app.deiconify()  # 如果出错，恢复窗口显示

        # 绑定最小化事件
        def on_minimize():
            app.withdraw()  # 隐藏窗口
            minimize_to_tray()  # 最小化到系统托盘
        
        app.protocol("WM_DELETE_WINDOW", on_closing)
        app.bind("<Unmap>", lambda e: on_minimize() if app.state() == 'iconic' else None)
        
        # Set window icon
        try:
            icon_path = "logo.jfif"
            if os.path.exists(icon_path):
                icon = Image.open(icon_path)
                photo = PIL.ImageTk.PhotoImage(icon)  # 使用完整的命名空间
                app.iconphoto(True, photo)
        except Exception:
            logger.warning("Application icon not found")

        # Start main loop
        app.mainloop()

    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        raise
    finally:
        logger.info("Application shutdown")

if __name__ == "__main__":
    main() 