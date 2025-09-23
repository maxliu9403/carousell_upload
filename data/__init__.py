"""
数据处理模块
包含Excel解析和记录管理
"""

# 延迟导入，避免在模块级别导入时出现依赖问题
def get_excel_parser():
    from .excel_parser import ExcelProductParser
    return ExcelProductParser

def get_record_manager():
    from .record_manager import SuccessRecordManager
    return SuccessRecordManager

# 为了向后兼容，提供直接导入（如果依赖包可用）
try:
    from .excel_parser import ExcelProductParser
    from .record_manager import SuccessRecordManager
except ImportError:
    # 如果依赖包未安装，提供占位符
    ExcelProductParser = None
    SuccessRecordManager = None

__all__ = [
    'get_excel_parser',
    'get_record_manager',
    'ExcelProductParser',
    'SuccessRecordManager'
]
