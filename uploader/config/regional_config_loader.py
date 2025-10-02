"""
地域和类别特定的配置加载器
支持按地域和类别加载不同的CSS选择器配置
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from core.logger import logger


class RegionalConfigLoader:
    """地域和类别特定的配置加载器"""
    
    def __init__(self, base_path: str = "uploader/regions"):
        """
        初始化配置加载器
        
        Args:
            base_path: 配置文件基础路径
        """
        self.base_path = self._get_config_path(base_path)
        self._cache = {}  # 配置缓存
    
    def _get_config_path(self, base_path: str) -> Path:
        """获取配置文件路径，支持PyInstaller打包后的情况"""
        if getattr(sys, 'frozen', False):
            # PyInstaller打包后的情况
            # 优先查找可执行文件同目录下的uploader/regions文件夹
            exe_dir = Path(sys.executable).parent
            external_path = exe_dir / "uploader" / "regions"
            if external_path.exists():
                return external_path
            
            # 如果外部配置文件不存在，使用打包在内部的配置文件
            internal_path = Path(sys._MEIPASS) / "uploader" / "regions"
            return internal_path
        else:
            # 开发环境
            return Path(base_path)
    
    def _get_config_file_path(self, region: str, category: str) -> Optional[Path]:
        """获取配置文件路径，支持外部和内部配置"""
        if getattr(sys, 'frozen', False):
            # PyInstaller打包后的情况
            # 优先查找可执行文件同目录下的配置文件
            exe_dir = Path(sys.executable).parent
            external_config = exe_dir / "uploader" / "regions" / region / category / "css_selectors.yaml"
            if external_config.exists():
                logger.info(f"使用外部CSS选择器配置: {external_config}")
                return external_config
            
            # 如果外部配置文件不存在，使用打包在内部的配置文件
            internal_config = Path(sys._MEIPASS) / "uploader" / "regions" / region / category / "css_selectors.yaml"
            if internal_config.exists():
                logger.info(f"使用内部CSS选择器配置: {internal_config}")
                return internal_config
            
            logger.warning(f"未找到CSS选择器配置文件: {region}/{category}")
            return None
        else:
            # 开发环境
            config_path = self.base_path / region / category / "css_selectors.yaml"
            if config_path.exists():
                logger.info(f"使用开发环境CSS选择器配置: {config_path}")
                return config_path
            return None
        
    def load_config(self, region: str, category: str) -> Dict[str, Any]:
        """
        加载指定地域和类别的配置文件
        
        Args:
            region: 地域 (HK, SG, MY)
            category: 类别 (sneakers, bags, clothes)
            
        Returns:
            Dict[str, Any]: 配置字典
        """
        cache_key = f"{region}_{category}"
        
        # 检查缓存
        if cache_key in self._cache:
            logger.debug(f"从缓存加载配置: {cache_key}")
            return self._cache[cache_key]
        
        # 构建配置文件路径 - 支持外部和内部配置
        config_path = self._get_config_file_path(region, category)
        
        if not config_path or not config_path.exists():
            logger.error(f"配置文件不存在: {config_path}")
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 缓存配置
            self._cache[cache_key] = config
            logger.info(f"成功加载配置文件: {config_path}")
            return config
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {config_path}, 错误: {e}")
            return {}
    
    def get_selector(self, region: str, category: str, selector_path: str) -> Optional[Dict[str, str]]:
        """
        获取指定的CSS选择器配置
        
        Args:
            region: 地域
            category: 类别
            selector_path: 选择器路径，如 "basic_elements.sell_button"
            
        Returns:
            Optional[Dict[str, str]]: 选择器配置或None
        """
        config = self.load_config(region, category)
        
        if not config:
            return None
        
        # 按路径获取选择器
        keys = selector_path.split('.')
        current = config
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            logger.warning(f"未找到选择器配置: {selector_path}")
            return None
    
    def get_selector_value(self, region: str, category: str, selector_path: str, 
                          value_type: str = "primary") -> Optional[str]:
        """
        获取选择器的具体值
        
        Args:
            region: 地域
            category: 类别
            selector_path: 选择器路径
            value_type: 值类型 (primary, fallback, description)
            
        Returns:
            Optional[str]: 选择器值或None
        """
        selector_config = self.get_selector(region, category, selector_path)
        
        if not selector_config:
            return None
        
        return selector_config.get(value_type)
    
    def clear_cache(self):
        """清除配置缓存"""
        self._cache.clear()
        logger.info("配置缓存已清除")


# 全局配置加载器实例
_regional_config_loader = None

def get_regional_config_loader() -> RegionalConfigLoader:
    """获取全局地域配置加载器实例"""
    global _regional_config_loader
    if _regional_config_loader is None:
        _regional_config_loader = RegionalConfigLoader()
    return _regional_config_loader
