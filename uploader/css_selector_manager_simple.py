"""
简化版CSS选择器管理器 - 不依赖PyYAML
使用JSON格式存储配置
"""

import json
import os
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
from core.logger import logger


class SimpleCSSSelectorManager:
    """简化版CSS选择器管理器 - 支持热更新和用户交互"""
    
    def __init__(self, config_path: str = "config/css_selectors.json"):
        """
        初始化CSS选择器管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self.config_data = {}
        self.last_modified = 0
        self._load_config()
        
    def _load_config(self):
        """加载配置文件"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                self.last_modified = self.config_path.stat().st_mtime
                logger.info(f"✅ CSS选择器配置已加载: {self.config_path}")
            else:
                logger.warning(f"⚠️ CSS选择器配置文件不存在: {self.config_path}")
                self.config_data = self._get_default_config()
                self._save_config()
        except Exception as e:
            logger.error(f"❌ 加载CSS选择器配置失败: {e}")
            self.config_data = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "basic_elements": {
                "sell_button": {
                    "primary": "a.D__s",
                    "fallback": "a[href*='sell']",
                    "description": "Sell按钮"
                },
                "upload_images_button": {
                    "primary": "div.D_JY",
                    "fallback": "div[class*='upload']",
                    "description": "上传图片按钮"
                }
            },
            "category_selection": {
                "service_category_selector": {
                    "primary": "div.D_aFi",
                    "fallback": "div[class*='category']",
                    "description": "服务类目选择器"
                }
            },
            "product_info": {
                "title_input": {
                    "primary": "input#title",
                    "fallback": "input[name='title']",
                    "description": "商品标题输入框"
                },
                "price_input": {
                    "primary": "input#price",
                    "fallback": "input[name='price']",
                    "description": "商品价格输入框"
                }
            },
            "publishing": {
                "publish_button": {
                    "primary": "button.D_uG",
                    "fallback": "button[type='submit']",
                    "description": "发布按钮"
                }
            },
            "metadata": {
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "description": "CSS选择器配置文件，支持热更新"
            }
        }
    
    def check_and_reload(self) -> bool:
        """
        检查配置文件是否有更新，如果有则重新加载
        
        Returns:
            bool: 是否重新加载了配置
        """
        try:
            if not self.config_path.exists():
                return False
                
            current_modified = self.config_path.stat().st_mtime
            if current_modified > self.last_modified:
                logger.info("🔄 检测到CSS选择器配置更新，重新加载...")
                self._load_config()
                return True
            return False
        except Exception as e:
            logger.error(f"❌ 检查配置文件更新失败: {e}")
            return False
    
    def get_selector(self, element_key: str, region: str = None, 
                    selector_type: str = "primary") -> Optional[str]:
        """
        获取CSS选择器
        
        Args:
            element_key: 元素键名，支持嵌套路径如 "basic_elements.sell_button"
            region: 地域代码 (HK, SG, MY)
            selector_type: 选择器类型 (primary, fallback)
            
        Returns:
            str: CSS选择器字符串
        """
        # 检查并重新加载配置
        self.check_and_reload()
        
        try:
            # 解析嵌套路径
            keys = element_key.split('.')
            current_data = self.config_data
            
            for key in keys:
                if isinstance(current_data, dict) and key in current_data:
                    current_data = current_data[key]
                else:
                    logger.warning(f"⚠️ 找不到元素配置: {element_key}")
                    return None
            
            # 如果是地域特定的选择器
            if isinstance(current_data, dict) and region and region in current_data:
                current_data = current_data[region]
            
            # 获取选择器
            if isinstance(current_data, dict):
                if selector_type in current_data:
                    selector = current_data[selector_type]
                    logger.debug(f"🎯 获取CSS选择器: {element_key} -> {selector}")
                    return selector
                else:
                    logger.warning(f"⚠️ 找不到选择器类型 {selector_type}: {element_key}")
                    return None
            elif isinstance(current_data, str):
                # 直接是字符串选择器
                logger.debug(f"🎯 获取CSS选择器: {element_key} -> {current_data}")
                return current_data
            else:
                logger.warning(f"⚠️ 无效的选择器配置: {element_key}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 获取CSS选择器失败: {element_key}, 错误: {e}")
            return None
    
    def get_selector_with_fallback(self, element_key: str, region: str = None) -> Tuple[str, str]:
        """
        获取主选择器和备用选择器
        
        Args:
            element_key: 元素键名
            region: 地域代码
            
        Returns:
            Tuple[str, str]: (主选择器, 备用选择器)
        """
        primary = self.get_selector(element_key, region, "primary")
        fallback = self.get_selector(element_key, region, "fallback")
        
        if not primary:
            primary = fallback or ""
        if not fallback:
            fallback = primary or ""
            
        return primary, fallback
    
    def get_element_description(self, element_key: str) -> str:
        """
        获取元素描述
        
        Args:
            element_key: 元素键名
            
        Returns:
            str: 元素描述
        """
        try:
            keys = element_key.split('.')
            current_data = self.config_data
            
            for key in keys:
                if isinstance(current_data, dict) and key in current_data:
                    current_data = current_data[key]
                else:
                    return element_key
            
            if isinstance(current_data, dict) and "description" in current_data:
                return current_data["description"]
            else:
                return element_key
        except Exception:
            return element_key
    
    def update_selector(self, element_key: str, selector_type: str, 
                       new_selector: str, region: str = None) -> bool:
        """
        更新选择器配置
        
        Args:
            element_key: 元素键名
            selector_type: 选择器类型 (primary, fallback)
            new_selector: 新的选择器
            region: 地域代码
            
        Returns:
            bool: 是否更新成功
        """
        try:
            # 解析嵌套路径
            keys = element_key.split('.')
            current_data = self.config_data
            
            # 导航到目标位置
            for key in keys[:-1]:
                if key not in current_data:
                    current_data[key] = {}
                current_data = current_data[key]
            
            target_key = keys[-1]
            
            # 如果是地域特定的选择器
            if region and isinstance(current_data.get(target_key), dict):
                if region not in current_data[target_key]:
                    current_data[target_key][region] = {}
                current_data = current_data[target_key][region]
                target_key = selector_type
            else:
                if target_key not in current_data:
                    current_data[target_key] = {}
                current_data = current_data[target_key]
                if not isinstance(current_data, dict):
                    current_data = {"primary": current_data, "fallback": ""}
                target_key = selector_type
            
            # 更新选择器
            current_data[target_key] = new_selector
            
            # 更新元数据
            if "metadata" in self.config_data:
                self.config_data["metadata"]["last_updated"] = datetime.now().isoformat()
            
            # 保存配置文件
            return self._save_config()
            
        except Exception as e:
            logger.error(f"❌ 更新CSS选择器失败: {element_key}, 错误: {e}")
            return False
    
    def _save_config(self) -> bool:
        """保存配置文件"""
        try:
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存配置文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            
            # 更新最后修改时间
            self.last_modified = self.config_path.stat().st_mtime
            
            logger.info(f"✅ CSS选择器配置已保存: {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 保存CSS选择器配置失败: {e}")
            return False
    
    def get_all_elements(self) -> Dict[str, Any]:
        """获取所有元素配置"""
        self.check_and_reload()
        return self.config_data.copy()
    
    def validate_selector(self, selector: str) -> bool:
        """
        验证CSS选择器格式
        
        Args:
            selector: CSS选择器
            
        Returns:
            bool: 是否有效
        """
        if not selector or not isinstance(selector, str):
            return False
        
        # 基本的CSS选择器验证
        try:
            # 简单的语法检查
            if selector.startswith('.') or selector.startswith('#') or selector.startswith('['):
                return True
            if any(char in selector for char in ['.', '#', '[', ':', '>', ' ', '+', '~']):
                return True
            return False
        except Exception:
            return False


# 全局实例
simple_css_manager = SimpleCSSSelectorManager()


def get_simple_css_manager() -> SimpleCSSSelectorManager:
    """获取简化版CSS选择器管理器实例"""
    return simple_css_manager
