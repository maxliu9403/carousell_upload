"""
CSS选择器管理器 - 支持地域和类别特定的配置
统一管理所有CSS选择器配置，支持热更新和用户交互式更新
"""

import os
import yaml
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
from core.logger import logger
from .regional_config_loader import get_regional_config_loader, RegionalConfigLoader


class EnhancedCSSSelectorManager:
    """CSS选择器管理器 - 基于地域和类别特定的配置，支持热更新和用户交互"""
    
    def __init__(self):
        """初始化CSS选择器管理器"""
        self.regional_loader = get_regional_config_loader()
        logger.info("✅ CSS选择器管理器已初始化")
    
    def check_and_reload(self) -> bool:
        """
        检查配置文件是否有更新，如果有则重新加载
        
        Returns:
            bool: 是否重新加载了配置
        """
        # 清除缓存以强制重新加载
        self.regional_loader.clear_cache()
        return True
    
    def get_selector_with_fallback(self, element_key: str, region: str = None, category: str = "sneakers") -> Tuple[Optional[str], Optional[str]]:
        """
        获取选择器配置（主选择器和备用选择器）
        
        Args:
            element_key: 元素键名
            region: 地域代码
            category: 类别代码
            
        Returns:
            Tuple[Optional[str], Optional[str]]: (主选择器, 备用选择器)
        """
        if not region:
            logger.error(f"❌ 必须提供地域代码: {element_key}")
            return None, None
        
        try:
            primary = self.regional_loader.get_selector_value(region, category, element_key, "primary")
            fallback = self.regional_loader.get_selector_value(region, category, element_key, "fallback")
            
            if primary:
                logger.debug(f"✅ 使用地域特定配置: {region}-{category}-{element_key}")
                return primary, fallback
            else:
                logger.warning(f"⚠️ 找不到地域特定配置: {region}-{category}-{element_key}")
                return None, None
                
        except Exception as e:
            logger.error(f"❌ 获取地域特定配置失败: {region}-{category}-{element_key}, 错误: {e}")
            return None, None
    
    def get_selector(self, element_key: str, region: str = None, selector_type: str = "primary", category: str = "sneakers") -> Optional[str]:
        """
        获取指定类型的选择器值
        
        Args:
            element_key: 元素键名
            region: 地域代码
            selector_type: 选择器类型 (primary, fallback, description)
            category: 类别代码
            
        Returns:
            Optional[str]: 选择器值
        """
        if not region:
            logger.error(f"❌ 必须提供地域代码: {element_key}")
            return None
        
        try:
            selector_value = self.regional_loader.get_selector_value(region, category, element_key, selector_type)
            if selector_value:
                logger.debug(f"✅ 获取选择器成功: {region}-{category}-{element_key}.{selector_type}")
                return selector_value
            else:
                logger.warning(f"⚠️ 找不到选择器: {region}-{category}-{element_key}.{selector_type}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 获取选择器失败: {region}-{category}-{element_key}.{selector_type}, 错误: {e}")
            return None

    def get_element_description(self, element_key: str, region: str = None, category: str = "sneakers") -> str:
        """
        获取元素描述
        
        Args:
            element_key: 元素键名
            region: 地域代码
            category: 类别代码
            
        Returns:
            str: 元素描述
        """
        if not region:
            logger.warning(f"⚠️ 未提供地域代码，使用默认描述: {element_key}")
            return element_key
        
        try:
            description = self.regional_loader.get_selector_value(region, category, element_key, "description")
            if description:
                return description
            else:
                logger.warning(f"⚠️ 找不到元素描述: {region}-{category}-{element_key}")
                return element_key
                
        except Exception as e:
            logger.error(f"❌ 获取元素描述失败: {region}-{category}-{element_key}, 错误: {e}")
            return element_key
    
    def update_selector(self, element_key: str, selector_type: str, new_selector: str, region: str = None, category: str = "sneakers") -> bool:
        """
        更新选择器配置
        
        Args:
            element_key: 元素键名
            selector_type: 选择器类型 (primary, fallback)
            new_selector: 新的选择器
            region: 地域代码
            category: 类别代码
            
        Returns:
            bool: 是否更新成功
        """
        if not region:
            logger.error(f"❌ 必须提供地域代码: {element_key}")
            return False
        
        try:
            # 获取当前配置
            config = self.regional_loader.load_config(region, category)
            if not config:
                logger.error(f"❌ 无法加载配置: {region}-{category}")
                return False
            
            # 更新配置
            keys = element_key.split('.')
            current = config
            
            # 导航到目标位置
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # 更新选择器
            if keys[-1] not in current:
                current[keys[-1]] = {}
            
            current[keys[-1]][selector_type] = new_selector
            
            # 保存到文件
            config_path = self.regional_loader.base_path / region / category / "css_selectors.yaml"
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            # 清除缓存
            self.regional_loader.clear_cache()
            
            logger.info(f"✅ CSS选择器已更新: {region}-{category}-{element_key}.{selector_type} -> {new_selector}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 更新CSS选择器失败: {region}-{category}-{element_key}, 错误: {e}")
            return False
    
    def validate_selector(self, selector: str) -> bool:
        """
        验证选择器格式
        
        Args:
            selector: CSS选择器
            
        Returns:
            bool: 是否有效
        """
        if not selector or not isinstance(selector, str):
            return False
        
        # 基本验证
        if len(selector.strip()) == 0:
            return False
        
        # 检查常见的选择器格式
        valid_prefixes = ['.', '#', '[', 'button:', 'input:', 'div', 'span', 'a', '//']
        if not any(selector.startswith(prefix) for prefix in valid_prefixes):
            # 允许其他格式，但给出警告
            logger.warning(f"⚠️ 选择器格式可能不正确: {selector}")
        
        return True


# 全局实例管理
_enhanced_css_manager = None

def get_enhanced_css_manager() -> EnhancedCSSSelectorManager:
    """获取CSS选择器管理器实例"""
    global _enhanced_css_manager
    if _enhanced_css_manager is None:
        _enhanced_css_manager = EnhancedCSSSelectorManager()
    return _enhanced_css_manager
