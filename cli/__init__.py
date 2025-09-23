"""
命令行接口模块
包含主程序入口和CLI接口
"""

# 延迟导入，避免在模块级别导入时出现依赖问题
def get_main():
    from .main import run
    return run

def get_cli():
    from .cli import main as cli_main
    return cli_main

# 为了向后兼容，提供直接导入（如果依赖包可用）
try:
    from .main import run
    from .cli import main as cli_main
except ImportError:
    # 如果依赖包未安装，提供占位符
    run = None
    cli_main = None

__all__ = [
    'get_main',
    'get_cli',
    'run',
    'cli_main'
]
