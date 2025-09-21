"""
Carousell 上传器模块

包含所有上传相关的功能模块。
"""

from .carousell_uploader import CarousellUploader
from .models import ProductInfo, UploadConfig
from .config import create_upload_config, load_config
from .browser import start_browser, fetch_all_browser_windows, get_profile_id_by_browser_id, check_browser_api_health
from .actions import (
    click_with_wait,
    input_with_wait,
    upload_folder_with_keyboard,
    human_delay,
    scroll_page
)
from .logger import logger
from .utils import (
    get_random_description,
    get_random_size,
    get_random_meetup_location,
    enrich_product_info
)
from .excel_parser import ExcelProductParser
from .multi_account_uploader import MultiAccountUploader
from .record_manager import SuccessRecordManager

__all__ = [
    "CarousellUploader",
    "ProductInfo", 
    "UploadConfig",
    "create_upload_config",
    "load_config",
    "start_browser",
    "fetch_all_browser_windows",
    "get_profile_id_by_browser_id",
    "check_browser_api_health",
    "click_with_wait",
    "input_with_wait", 
    "upload_folder_with_keyboard",
    "human_delay",
    "scroll_page",
    "logger",
    "get_random_description",
    "get_random_size",
    "get_random_meetup_location",
    "enrich_product_info",
    "ExcelProductParser",
    "MultiAccountUploader",
    "SuccessRecordManager"
]

