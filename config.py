import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RESOURCE_DIR = BASE_DIR / "src" / "resources"

# Database
DATABASE = {
    "path": DATA_DIR / "workspace.db"
}

# Window settings
WINDOW = {
    "title": "工作助手",
    "width": 1024,
    "height": 768,
    "min_width": 800,
    "min_height": 600
}

# Browser paths - 根据实际安装路径修改
BROWSERS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "ie": r"C:\Program Files\Internet Explorer\iexplore.exe"
}

# Colors
COLORS = {
    "warning": "#FFE4E1",
    "normal": "#FFFFFF",
    "highlight": "#F0F8FF"
}

# Date format
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# 获取实际的浏览器路径
def get_browser_path(browser_name):
    """获取浏览器实际安装路径"""
    default_paths = BROWSERS.copy()
    
    # Chrome 其他可能的安装路径
    chrome_paths = [
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser("~") + r"\AppData\Local\Google\Chrome\Application\chrome.exe",
    ]
    
    # Edge 其他可能的安装路径
    edge_paths = [
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        os.path.expanduser("~") + r"\AppData\Local\Microsoft\Edge\Application\msedge.exe",
    ]
    
    if browser_name == "chrome":
        for path in chrome_paths:
            if os.path.exists(path):
                return path
    elif browser_name == "edge":
        for path in edge_paths:
            if os.path.exists(path):
                return path
    
    return default_paths.get(browser_name)