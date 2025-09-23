"""
Carousell 自动上传工具

一个用于 Carousell 平台的自动化商品上传工具。
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# 导入主要模块
from core import create_upload_config, ProductInfo, UploadConfig, logger
from browser import start_browser, check_browser_api_health
from data import ExcelProductParser, SuccessRecordManager
from uploader import CarousellUploader, MultiAccountUploader
from cli import run, cli_main

__all__ = [
    'create_upload_config',
    'ProductInfo', 
    'UploadConfig',
    'logger',
    'start_browser',
    'check_browser_api_health',
    'ExcelProductParser',
    'SuccessRecordManager',
    'CarousellUploader',
    'MultiAccountUploader',
    'run',
    'cli_main'
]

