import logging
import sys
import os
from datetime import datetime
from pathlib import Path

def get_log_directory():
    """获取日志目录，支持PyInstaller打包后的情况"""
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后的情况
        # 优先使用可执行文件同目录下的logs文件夹
        exe_dir = Path(sys.executable).parent
        external_log_dir = exe_dir / "logs"
        return external_log_dir
    else:
        # 开发环境
        return Path(__file__).parent.parent / "logs"

class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    # 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
        'RESET': '\033[0m'      # 重置
    }
    
    def format(self, record):
        # 检查是否支持颜色输出
        if self._supports_color():
            # 添加颜色
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
            record.name = f"\033[34m{record.name}\033[0m"  # 蓝色模块名
            record.msg = f"{color}{record.msg}{self.COLORS['RESET']}"
        
        return super().format(record)
    
    def _supports_color(self):
        """检查终端是否支持颜色"""
        # 检查环境变量
        if os.environ.get('NO_COLOR'):
            return False
        
        # 检查是否在Windows Git Bash中
        if os.name == 'nt' and 'TERM' in os.environ:
            term = os.environ['TERM'].lower()
            return 'xterm' in term or 'color' in term
        
        # 检查是否在Unix/Linux/macOS中
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            return True
        
        return False

def setup_logger(name: str = "carousell_uploader", level: int = logging.INFO) -> logging.Logger:
    """
    设置日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 彩色格式器
    colored_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(colored_formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器 - 支持外部日志目录
    log_dir = get_log_directory()
    log_dir.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(
        log_dir / f"carousell_{datetime.now().strftime('%Y%m%d')}.log",
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# 创建默认日志记录器
logger = setup_logger()

