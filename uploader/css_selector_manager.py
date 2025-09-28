"""
CSS选择器管理器 - 支持热更新和用户交互式更新
"""

import os
import yaml
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
from core.logger import logger


class CSSSelectorManager:
    """CSS选择器管理器 - 支持热更新和用户交互"""
    
    def __init__(self, config_path: str = "config/css_selectors.yaml"):
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
                    self.config_data = yaml.safe_load(f) or {}
                self.last_modified = self.config_path.stat().st_mtime
                logger.info(f"✅ CSS选择器配置已加载: {self.config_path}")
            else:
                logger.warning(f"⚠️ CSS选择器配置文件不存在: {self.config_path}")
                self.config_data = {}
        except Exception as e:
            logger.error(f"❌ 加载CSS选择器配置失败: {e}")
            self.config_data = {}
    
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
            # 首先尝试地域特定的选择器
            if region and region != "all":
                # 构建地域特定的键名
                keys = element_key.split('.')
                if len(keys) >= 2:
                    # 例如: category_selection.service_category_option -> category_selection.service_category_option_sg
                    region_specific_key = f"{keys[0]}.{keys[1]}_{region.lower()}"
                    selector = self._get_selector_by_key(region_specific_key, selector_type, region)
                    if selector:
                        logger.debug(f"🎯 使用地域特定选择器: {region_specific_key} -> {selector}")
                        return selector
                else:
                    # 如果只有一个键，直接添加地域后缀
                    region_specific_key = f"{element_key}_{region.lower()}"
                    selector = self._get_selector_by_key(region_specific_key, selector_type, region)
                    if selector:
                        logger.debug(f"🎯 使用地域特定选择器: {region_specific_key} -> {selector}")
                        return selector
            
            # 尝试通用选择器
            selector = self._get_selector_by_key(element_key, selector_type, region)
            if selector:
                logger.debug(f"🎯 使用通用选择器: {element_key} -> {selector}")
                return selector
            
            logger.warning(f"⚠️ 找不到选择器配置: {element_key}")
            return None
                
        except Exception as e:
            logger.error(f"❌ 获取CSS选择器失败: {element_key}, 错误: {e}")
            return None
    
    def _get_selector_by_key(self, element_key: str, selector_type: str, region: str = None) -> Optional[str]:
        """
        根据键名获取选择器
        
        Args:
            element_key: 元素键名
            selector_type: 选择器类型
            region: 地域代码
            
        Returns:
            Optional[str]: CSS选择器字符串
        """
        try:
            # 解析嵌套路径
            keys = element_key.split('.')
            current_data = self.config_data
            
            for key in keys:
                if isinstance(current_data, dict) and key in current_data:
                    current_data = current_data[key]
                else:
                    return None
            
            # 如果是地域特定的选择器
            if isinstance(current_data, dict) and region and region in current_data:
                current_data = current_data[region]
            
            # 获取选择器
            if isinstance(current_data, dict):
                if selector_type in current_data:
                    selector = current_data[selector_type]
                    return selector
                else:
                    return None
            elif isinstance(current_data, str):
                # 直接是字符串选择器
                return current_data
            else:
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
        更新选择器配置，支持跨region更新
        
        Args:
            element_key: 元素键名
            selector_type: 选择器类型 (primary, fallback)
            new_selector: 新的选择器
            region: 地域代码
            
        Returns:
            bool: 是否更新成功
        """
        try:
            updated_count = 0
            
            # 如果指定了region，只更新该region
            if region:
                updated_count += self._update_single_region(element_key, selector_type, new_selector, region)
            else:
                # 如果没有指定region，更新所有匹配的选择器
                updated_count += self._update_all_matching_selectors(element_key, selector_type, new_selector)
            
            if updated_count > 0:
                # 更新元数据
                if "metadata" in self.config_data:
                    self.config_data["metadata"]["last_updated"] = datetime.now().isoformat()
                
                # 保存配置文件
                success = self._save_config()
                if success:
                    logger.info(f"✅ 成功更新 {updated_count} 个选择器: {element_key}")
                return success
            else:
                logger.warning(f"⚠️ 没有找到匹配的选择器进行更新: {element_key}")
                return False
            
        except Exception as e:
            logger.error(f"❌ 更新CSS选择器失败: {element_key}, 错误: {e}")
            return False
    
    def _update_single_region(self, element_key: str, selector_type: str, 
                             new_selector: str, region: str) -> int:
        """更新单个region的选择器"""
        try:
            # 解析嵌套路径
            keys = element_key.split('.')
            current_data = self.config_data
            
            # 导航到目标位置
            for key in keys[:-1]:
                if key not in current_data:
                    return 0
                current_data = current_data[key]
            
            target_key = keys[-1]
            
            # 如果是地域特定的选择器
            if isinstance(current_data.get(target_key), dict):
                if region in current_data[target_key]:
                    current_data = current_data[target_key][region]
                    if isinstance(current_data, dict) and selector_type in current_data:
                        current_data[selector_type] = new_selector
                        return 1
            else:
                if target_key in current_data:
                    current_data = current_data[target_key]
                    if isinstance(current_data, dict) and selector_type in current_data:
                        # 检查region字段
                        if current_data.get("region") == region or current_data.get("region") == "all":
                            current_data[selector_type] = new_selector
                            return 1
            
            return 0
            
        except Exception:
            return 0
    
    def _update_all_matching_selectors(self, element_key: str, selector_type: str, 
                                      new_selector: str) -> int:
        """更新所有匹配的选择器（跨region）"""
        try:
            updated_count = 0
            
            # 递归查找并更新所有匹配的选择器
            def update_recursive(data, path=""):
                nonlocal updated_count
                
                if isinstance(data, dict):
                    for key, value in data.items():
                        current_path = f"{path}.{key}" if path else key
                        
                        if current_path.endswith(element_key):
                            # 找到匹配的元素
                            if isinstance(value, dict) and selector_type in value:
                                # 检查是否有region字段
                                if "region" in value:
                                    value[selector_type] = new_selector
                                    updated_count += 1
                                    logger.debug(f"🔄 更新选择器: {current_path} -> {new_selector}")
                        else:
                            # 继续递归
                            update_recursive(value, current_path)
            
            update_recursive(self.config_data)
            return updated_count
            
        except Exception as e:
            logger.error(f"❌ 更新所有匹配选择器失败: {e}")
            return 0
    
    def _save_config(self) -> bool:
        """保存配置文件"""
        try:
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存配置文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False)
            
            # 更新最后修改时间
            self.last_modified = self.config_path.stat().st_mtime
            
            logger.info(f"✅ CSS选择器配置已保存: {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 保存CSS选择器配置失败: {e}")
            return False
    
    def add_new_element(self, element_key: str, primary_selector: str, 
                       fallback_selector: str = "", description: str = "") -> bool:
        """
        添加新的元素配置
        
        Args:
            element_key: 元素键名
            primary_selector: 主选择器
            fallback_selector: 备用选择器
            description: 元素描述
            
        Returns:
            bool: 是否添加成功
        """
        try:
            keys = element_key.split('.')
            current_data = self.config_data
            
            # 导航到目标位置，创建不存在的路径
            for key in keys[:-1]:
                if key not in current_data:
                    current_data[key] = {}
                current_data = current_data[key]
            
            target_key = keys[-1]
            
            # 创建新元素配置
            current_data[target_key] = {
                "primary": primary_selector,
                "fallback": fallback_selector,
                "description": description or element_key
            }
            
            # 更新元数据
            if "metadata" in self.config_data:
                self.config_data["metadata"]["last_updated"] = datetime.now().isoformat()
            
            # 保存配置文件
            return self._save_config()
            
        except Exception as e:
            logger.error(f"❌ 添加新元素配置失败: {element_key}, 错误: {e}")
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
        # 这里可以添加更复杂的验证逻辑
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
css_manager = CSSSelectorManager()


def get_css_manager() -> CSSSelectorManager:
    """获取CSS选择器管理器实例"""
    return css_manager
