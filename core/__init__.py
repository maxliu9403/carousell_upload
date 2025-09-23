"""
核心功能模块
包含配置管理、数据模型和日志系统
"""

# 延迟导入，避免在模块级别导入时出现依赖问题
def get_config():
    from .config import create_upload_config, load_config
    return create_upload_config, load_config

def get_models():
    from .models import ProductInfo, UploadConfig
    return ProductInfo, UploadConfig

def get_logger():
    from .logger import logger
    return logger

# 为了向后兼容，提供直接导入
try:
    from .models import ProductInfo, UploadConfig
    from .logger import logger
except ImportError:
    # 如果依赖包未安装，提供占位符
    ProductInfo = None
    UploadConfig = None
    logger = None

__all__ = [
    'get_config',
    'get_models', 
    'get_logger',
    'ProductInfo',
    'UploadConfig',
    'logger'
]
