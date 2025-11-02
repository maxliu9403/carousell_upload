from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

@dataclass
class ProductInfo:
    """商品信息数据类"""
    title: str
    price: str
    category: str = "others"
    brand: str = ""
    condition: str = "new"  # new, used
    gender: str = "unisex"  # male, female, unisex
    location: str = "All of Singapore"
    multi_quantity: bool = False

@dataclass
class UploadConfig:
    """上传配置数据类"""
    image_extensions: List[str]
    api_key: str
    api_port: int
    browser_type: str  # 当前选择的浏览器类型
    browser_config: dict  # 当前浏览器的配置
    all_browser_configs: dict  # 所有浏览器配置
    descriptions: List[str]
    male_sizes: List[str]
    female_sizes: List[str]
    meetup_locations: dict  # 改为字典，支持按地域分类
    domains: dict  # 地域域名配置
    categories: dict  # 商品类目配置
    navigation_timeouts: dict  # 页面导航超时配置

