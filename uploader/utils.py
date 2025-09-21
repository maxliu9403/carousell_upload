import random
from typing import List
from .models import ProductInfo, UploadConfig
from .logger import logger

def get_random_description(config: UploadConfig) -> str:
    """从配置中随机选择一个商品描述"""
    description = random.choice(config.descriptions)
    logger.info(f"随机选择商品描述: {description}")
    return description

def get_random_size(config: UploadConfig, gender: str) -> str:
    """
    根据性别从配置中随机选择一个尺码
    - male: 从 male_sizes 中选择
    - female: 从 female_sizes 中选择
    - unisex: 从 male_sizes 中选择（默认）
    """
    if gender.lower() == "female" or gender.lower() == "women" or gender.lower() == "womens":
        size = random.choice(config.female_sizes)
        logger.info(f"随机选择女性尺码: {size}")
    elif gender.lower() == "male" or gender.lower() == "men" or gender.lower() == "mens":
        # male 或 unisex 都使用男性尺码
        size = random.choice(config.male_sizes)
        logger.info(f"随机选择男性尺码: {size}")
    else:
        # unisex 使用 40
        size = 40
        logger.info(f"随机选择尺码: {size}")
    return size

def get_random_meetup_location(config: UploadConfig) -> str:
    """从配置中随机选择一个面交地点"""
    location = random.choice(config.meetup_locations)
    logger.info(f"随机选择面交地点: {location}")
    return location

def enrich_product_info(product_info: ProductInfo, config: UploadConfig) -> ProductInfo:
    """
    为 ProductInfo 添加随机生成的值
    返回一个新的 ProductInfo 对象，包含 description、size、meetup_location
    """
    # 获取随机值
    description = get_random_description(config)
    size = get_random_size(config, product_info.gender)
    meetup_location = get_random_meetup_location(config)
    
    # 创建新的 ProductInfo 对象（由于 dataclass 不可变，我们需要创建新实例）
    enriched_info = ProductInfo(
        title=product_info.title,
        price=product_info.price,
        category=product_info.category,
        brand=product_info.brand,
        condition=product_info.condition,
        gender=product_info.gender,
        location=product_info.location,
        multi_quantity=product_info.multi_quantity
    )
    
    # 添加动态属性
    enriched_info.description = description
    enriched_info.size = size
    enriched_info.meetup_location = meetup_location
    
    logger.info(f"商品信息已丰富: 描述={description}, 尺码={size}, 面交地点={meetup_location}")
    return enriched_info
