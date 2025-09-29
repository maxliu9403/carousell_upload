"""
上传功能模块
包含Carousell上传器和多账号上传器
"""

# 延迟导入，避免在模块级别导入时出现依赖问题
def get_uploaders():
    from .core.carousell_uploader import CarousellUploader
    from .multi.multi_account_uploader import MultiAccountUploader
    return CarousellUploader, MultiAccountUploader

def get_utils():
    from .utils import (
        get_random_description,
        get_random_size,
        get_random_meetup_location,
        enrich_product_info
    )
    return get_random_description, get_random_size, get_random_meetup_location, enrich_product_info

# 为了向后兼容，提供直接导入（如果依赖包可用）
try:
    from .core.carousell_uploader import CarousellUploader
    from .multi.multi_account_uploader import MultiAccountUploader
    from .utils import (
        get_random_description,
        get_random_size,
        get_random_meetup_location,
        enrich_product_info
    )
except ImportError:
    # 如果依赖包未安装，提供占位符
    CarousellUploader = None
    MultiAccountUploader = None
    get_random_description = None
    get_random_size = None
    get_random_meetup_location = None
    enrich_product_info = None

__all__ = [
    'get_uploaders',
    'get_utils',
    'CarousellUploader',
    'MultiAccountUploader',
    'get_random_description',
    'get_random_size',
    'get_random_meetup_location',
    'enrich_product_info'
]