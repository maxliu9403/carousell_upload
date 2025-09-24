"""
浏览器类型选择器
提供交互式浏览器类型选择功能
"""

from typing import Dict, Any
from core.logger import logger
from .browser_factory import BrowserFactory


def select_browser_type() -> str:
    """
    交互式选择浏览器类型
    
    Returns:
        str: 选择的浏览器类型
    """
    supported_browsers = BrowserFactory.get_supported_browsers()
    
    print("\n" + "="*50)
    print("🔧 浏览器类型选择")
    print("="*50)
    print("请选择您使用的指纹浏览器类型:")
    print()
    
    for i, browser_type in enumerate(supported_browsers, 1):
        browser_name = get_browser_display_name(browser_type)
        print(f"{i}. {browser_name} ({browser_type})")
    
    print()
    
    while True:
        try:
            choice = input("请输入选择 (1-{}): ".format(len(supported_browsers)))
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(supported_browsers):
                selected_browser = supported_browsers[choice_num - 1]
                browser_name = get_browser_display_name(selected_browser)
                print(f"✅ 已选择: {browser_name}")
                logger.info(f"用户选择浏览器类型: {selected_browser}")
                return selected_browser
            else:
                print(f"❌ 请输入 1-{len(supported_browsers)} 之间的数字")
        except ValueError:
            print("❌ 请输入有效的数字")
        except KeyboardInterrupt:
            print("\n❌ 用户取消选择")
            exit(1)


def get_browser_display_name(browser_type: str) -> str:
    """
    获取浏览器类型的显示名称
    
    Args:
        browser_type (str): 浏览器类型
        
    Returns:
        str: 显示名称
    """
    display_names = {
        "bitBrowser": "BitBrowser",
        "ixBrowser": "IxBrowser"
    }
    return display_names.get(browser_type, browser_type)


def update_config_with_browser_type(config: Dict[str, Any], browser_type: str) -> Dict[str, Any]:
    """
    更新配置中的浏览器类型
    
    Args:
        config (Dict[str, Any]): 原始配置
        browser_type (str): 选择的浏览器类型
        
    Returns:
        Dict[str, Any]: 更新后的配置
    """
    if "browser" not in config:
        config["browser"] = {}
    
    config["browser"]["type"] = browser_type
    logger.info(f"配置已更新，浏览器类型: {browser_type}")
    return config


def validate_browser_config(config: Dict[str, Any]) -> bool:
    """
    验证浏览器配置是否完整
    
    Args:
        config (Dict[str, Any]): 浏览器配置
        
    Returns:
        bool: True表示配置完整，False表示配置不完整
    """
    browser_config = config.get("browser", {})
    
    required_fields = ["type", "api_port", "api_key"]
    missing_fields = []
    
    for field in required_fields:
        if not browser_config.get(field):
            missing_fields.append(field)
    
    if missing_fields:
        logger.error(f"浏览器配置缺少字段: {', '.join(missing_fields)}")
        return False
    
    browser_type = browser_config.get("type")
    if not BrowserFactory.validate_browser_type(browser_type):
        logger.error(f"不支持的浏览器类型: {browser_type}")
        return False
    
    return True


def interactive_browser_setup() -> Dict[str, Any]:
    """
    交互式浏览器设置
    
    Returns:
        Dict[str, Any]: 完整的浏览器配置
    """
    print("\n" + "="*50)
    print("🚀 浏览器设置向导")
    print("="*50)
    
    # 选择浏览器类型
    browser_type = select_browser_type()
    
    # 获取API配置
    print(f"\n📋 配置 {get_browser_display_name(browser_type)} 连接信息:")
    
    # 获取API端口
    while True:
        try:
            api_port = input("请输入API端口 (默认54345): ").strip()
            if not api_port:
                api_port = 54345
            else:
                api_port = int(api_port)
            break
        except ValueError:
            print("❌ 请输入有效的端口号")
        except KeyboardInterrupt:
            print("\n❌ 用户取消设置")
            return None
    
    # 询问API密钥（可选）
    api_key = input("请输入API密钥 (可选，直接回车跳过): ").strip()
    if not api_key:
        api_key = None
        print("⚠️ 未配置API密钥，某些功能可能不可用")
    
    # 构建配置
    config = {
        "browser": {
            "type": browser_type,
            "api_port": api_port
        }
    }
    
    if api_key:
        config["browser"]["api_key"] = api_key
    
    # 验证配置
    if validate_browser_config(config["browser"]):
        print("✅ 浏览器配置验证通过")
        return config
    else:
        print("❌ 浏览器配置验证失败")
        return None
