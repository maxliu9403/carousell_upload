import logging
import logging.handlers
import sys
import os
import yaml
from datetime import datetime, timedelta
from pathlib import Path

def load_logging_config():
    """从配置文件加载日志配置"""
    try:
        # 获取配置文件路径
        config_path = Path(__file__).parent.parent / "config" / "settings.yaml"
        
        if not config_path.exists():
            # 如果配置文件不存在，使用默认配置
            return {
                "level": "INFO",
                "console_level": "INFO", 
                "file_level": "DEBUG",
                "enable_colors": True,
                "enable_file_logging": True,
                "log_rotation": {
                    "when": "midnight",
                    "interval": 1,
                    "backup_count": 5,
                    "days_to_keep": 5
                }
            }
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 获取日志配置，如果不存在则使用默认值
        logging_config = config.get('logging', {})
        
        return {
            "level": logging_config.get('level', 'INFO'),
            "console_level": logging_config.get('console_level', 'INFO'),
            "file_level": logging_config.get('file_level', 'DEBUG'),
            "enable_colors": logging_config.get('enable_colors', True),
            "enable_file_logging": logging_config.get('enable_file_logging', True),
            "log_rotation": logging_config.get('log_rotation', {
                "when": "midnight",
                "interval": 1,
                "backup_count": 5,
                "days_to_keep": 5
            })
        }
        
    except Exception as e:
        print(f"⚠️ 加载日志配置失败，使用默认配置: {e}")
        return {
            "level": "INFO",
            "console_level": "INFO",
            "file_level": "DEBUG", 
            "enable_colors": True,
            "enable_file_logging": True,
            "log_rotation": {
                "when": "midnight",
                "interval": 1,
                "backup_count": 5,
                "days_to_keep": 5
            }
        }

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

def cleanup_old_logs(log_dir: Path, days_to_keep: int = 5):
    """
    清理旧的日志文件，只保留指定天数的日志
    
    Args:
        log_dir: 日志目录
        days_to_keep: 保留的天数，默认5天
    """
    if not log_dir.exists():
        return
    
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    
    for log_file in log_dir.glob("carousell_*.log*"):
        try:
            # 从文件名提取日期
            if log_file.stem.startswith("carousell_"):
                date_str = log_file.stem.replace("carousell_", "")
                if len(date_str) == 8:  # YYYYMMDD格式
                    file_date = datetime.strptime(date_str, "%Y%m%d")
                    if file_date < cutoff_date:
                        log_file.unlink()
                        print(f"🗑️ 删除过期日志文件: {log_file.name}")
        except (ValueError, OSError) as e:
            # 如果无法解析日期或删除文件失败，跳过
            continue

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

def setup_logger(name: str = "carousell_uploader", level: int = None) -> logging.Logger:
    """
    设置日志记录器，支持从配置文件读取日志等级
    
    Args:
        name: 日志记录器名称
        level: 日志等级，如果为None则从配置文件读取
    """
    # 加载日志配置
    config = load_logging_config()
    
    # 如果未指定level，从配置文件读取
    if level is None:
        level_str = config.get('level', 'INFO')
        level = getattr(logging, level_str.upper(), logging.INFO)
    
    # 获取控制台和文件日志等级
    console_level_str = config.get('console_level', 'INFO')
    file_level_str = config.get('file_level', 'DEBUG')
    console_level = getattr(logging, console_level_str.upper(), logging.INFO)
    file_level = getattr(logging, file_level_str.upper(), logging.DEBUG)
    
    # 获取其他配置
    enable_colors = config.get('enable_colors', True)
    enable_file_logging = config.get('enable_file_logging', True)
    log_rotation = config.get('log_rotation', {})
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建格式器 - 包含文件名、行号和函数名
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d:%(funcName)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 彩色格式器 - 包含文件名、行号和函数名
    colored_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d:%(funcName)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    if enable_colors:
        console_handler.setFormatter(colored_formatter)
    else:
        console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器 - 支持外部日志目录和时间轮转
    if enable_file_logging:
        log_dir = get_log_directory()
        log_dir.mkdir(exist_ok=True)
        
        # 清理旧日志文件
        days_to_keep = log_rotation.get('days_to_keep', 5)
        cleanup_old_logs(log_dir, days_to_keep=days_to_keep)
        
        # 使用时间轮转文件处理器
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=log_dir / "carousell.log",
            when=log_rotation.get('when', 'midnight'),
            interval=log_rotation.get('interval', 1),
            backupCount=log_rotation.get('backup_count', 5),
            encoding='utf-8',
            utc=False
        )
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def log_error_with_traceback(logger, message: str, exc_info=None):
    """
    记录详细的错误信息，包含堆栈跟踪
    
    Args:
        logger: 日志记录器
        message: 错误消息
        exc_info: 异常信息，如果为None则自动获取当前异常
    """
    logger.error(f"❌ {message}", exc_info=exc_info)

def log_warning_with_context(logger, message: str, context: dict = None):
    """
    记录带上下文的警告信息
    
    Args:
        logger: 日志记录器
        message: 警告消息
        context: 上下文信息字典
    """
    if context:
        context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
        logger.warning(f"⚠️ {message} | 上下文: {context_str}")
    else:
        logger.warning(f"⚠️ {message}")

def log_info_with_context(logger, message: str, context: dict = None):
    """
    记录带上下文的信息
    
    Args:
        logger: 日志记录器
        message: 信息消息
        context: 上下文信息字典
    """
    if context:
        context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
        logger.info(f"ℹ️ {message} | 上下文: {context_str}")
    else:
        logger.info(f"ℹ️ {message}")

# 创建默认日志记录器
logger = setup_logger()

def reinitialize_logger():
    """重新初始化日志记录器，应用新的配置"""
    global logger
    
    # 清除现有的处理器
    if logger.handlers:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
    
    # 重新创建日志记录器
    logger = setup_logger()
    return logger

