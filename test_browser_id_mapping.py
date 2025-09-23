#!/usr/bin/env python3
"""
测试BrowserID到profile_id映射功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import create_upload_config
from browser.browser import fetch_all_browser_windows, get_profile_id_by_browser_id
from core.logger import logger

def test_browser_mapping():
    """测试浏览器映射功能"""
    try:
        # 加载配置
        config = create_upload_config()
        logger.info("配置加载成功")
        
        # 测试获取所有浏览器窗口
        logger.info("正在获取所有浏览器窗口...")
        browser_windows = fetch_all_browser_windows(config.api_port, config.api_key)
        logger.info(f"获取到 {len(browser_windows)} 个浏览器窗口")
        
        # 显示所有可用的BrowserID
        if browser_windows:
            logger.info("可用的BrowserID:")
            for seq, window_info in browser_windows.items():
                logger.info(f"  BrowserID: {seq} -> profile_id: {window_info['id']}")
            
            # 测试第一个BrowserID的映射
            first_browser_id = str(list(browser_windows.keys())[0])
            logger.info(f"测试BrowserID {first_browser_id} 的映射...")
            
            profile_id = get_profile_id_by_browser_id(
                config.api_port, 
                config.api_key, 
                first_browser_id
            )
            logger.info(f"映射成功: BrowserID {first_browser_id} -> profile_id {profile_id}")
            
        else:
            logger.warning("没有找到任何浏览器窗口")
            
    except Exception as e:
        logger.error(f"测试失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("开始测试BrowserID到profile_id映射功能...")
    success = test_browser_mapping()
    if success:
        print("✅ 测试完成")
    else:
        print("❌ 测试失败")
        sys.exit(1)
