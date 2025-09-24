"""
浏览器工厂类
根据配置创建对应的浏览器接口实例
"""

from typing import Dict, Any
from .browser_interface import BrowserInterface, BitBrowserInterface, IxBrowserInterface
from core.logger import logger


class BrowserFactory:
    """浏览器工厂类"""
    
    # 支持的浏览器类型
    SUPPORTED_BROWSERS = {
        "bitBrowser": BitBrowserInterface,
        "ixBrowser": IxBrowserInterface
    }
    
    @classmethod
    def create_browser(cls, browser_type: str, api_port: int, api_key: str) -> BrowserInterface:
        """
        创建浏览器接口实例
        
        Args:
            browser_type (str): 浏览器类型 (bitBrowser, ixBrowser)
            api_port (int): API端口
            api_key (str): API密钥
            
        Returns:
            BrowserInterface: 浏览器接口实例
            
        Raises:
            ValueError: 当浏览器类型不支持时
        """
        if browser_type not in cls.SUPPORTED_BROWSERS:
            supported_types = ", ".join(cls.SUPPORTED_BROWSERS.keys())
            raise ValueError(f"不支持的浏览器类型: {browser_type}，支持的类型: {supported_types}")
        
        browser_class = cls.SUPPORTED_BROWSERS[browser_type]
        logger.info(f"创建{browser_type}浏览器接口实例")
        return browser_class(api_port, api_key)
    
    @classmethod
    def get_supported_browsers(cls) -> list:
        """
        获取支持的浏览器类型列表
        
        Returns:
            list: 支持的浏览器类型列表
        """
        return list(cls.SUPPORTED_BROWSERS.keys())
    
    @classmethod
    def validate_browser_type(cls, browser_type: str) -> bool:
        """
        验证浏览器类型是否支持
        
        Args:
            browser_type (str): 浏览器类型
            
        Returns:
            bool: True表示支持，False表示不支持
        """
        return browser_type in cls.SUPPORTED_BROWSERS


def get_browser_interface(config: Dict[str, Any]) -> BrowserInterface:
    """
    根据配置获取浏览器接口实例
    
    Args:
        config (Dict[str, Any]): 浏览器配置
        
    Returns:
        BrowserInterface: 浏览器接口实例
    """
    # 获取浏览器类型
    browser_type = config.get("type", "bitBrowser")
    api_port = config.get("api_port")
    api_key = config.get("api_key")
    
    if not api_port:
        raise ValueError(f"浏览器配置缺少api_port")
    
    # api_key是可选的
    if api_key is None:
        logger.warning(f"浏览器 '{browser_type}' 未配置api_key，某些功能可能不可用")
        api_key = ""  # 使用空字符串作为默认值
    
    return BrowserFactory.create_browser(browser_type, api_port, api_key)


def validate_browser_config(config: Dict[str, Any]) -> bool:
    """
    验证浏览器配置是否有效
    
    Args:
        config (Dict[str, Any]): 浏览器配置
        
    Returns:
        bool: True表示配置有效，False表示配置无效
    """
    try:
        browser_type = config.get("type", "bitBrowser")
        api_port = config.get("api_port")
        
        if not api_port:
            logger.error(f"浏览器配置缺少api_port")
            return False
        
        # 验证浏览器类型是否支持
        if not BrowserFactory.validate_browser_type(browser_type):
            logger.error(f"不支持的浏览器类型: {browser_type}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"验证浏览器配置失败: {e}")
        return False
