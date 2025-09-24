import yaml
from pathlib import Path
from typing import Dict, Any
from .models import UploadConfig
from .logger import logger

CONFIG_PATH = Path(__file__).parent.parent / "config" / "settings.yaml"

def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        logger.info("配置文件加载成功")
        return config
    except FileNotFoundError:
        logger.error(f"配置文件不存在: {CONFIG_PATH}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"配置文件格式错误: {e}")
        raise

def create_upload_config() -> UploadConfig:
    """创建上传配置对象"""
    config = load_config()
    
    # 获取当前选择的浏览器配置
    current_browser_type = config["browser"]["current_type"]
    current_browser_config = config["browser"]["browsers"][current_browser_type]
    
    return UploadConfig(
        image_extensions=config["upload"]["image_extensions"],
        api_key=current_browser_config["api_key"],
        api_port=current_browser_config["api_port"],
        browser_type=current_browser_type,
        browser_config=current_browser_config,
        all_browser_configs=config["browser"]["browsers"],
        descriptions=config["product"]["descriptions"],
        male_sizes=config["product"]["male_sizes"],
        female_sizes=config["product"]["female_sizes"],
        meetup_locations=config["product"]["meetup_locations"],
        domains=config["domains"],
        categories=config["product"]["categories"]
    )

# 保持向后兼容 - 移除模块级别的配置加载以避免重复日志
# config = load_config()
