#!/usr/bin/env python3
"""
测试获取浏览器窗口信息的脚本
"""

from uploader.browser import fetch_all_browser_windows
from uploader.logger import logger

def test_fetch_browser_windows():
    """测试获取浏览器窗口信息"""
    try:
        # 从配置中获取端口和token
        api_port = 54347  # 根据您的配置调整
        token = "bba29e64820c4282ade6afc480b5c78e"  # 根据您的配置调整
        
        logger.info("开始测试获取浏览器窗口信息")
        
        # 调用接口获取所有浏览器窗口
        browser_windows = fetch_all_browser_windows(api_port, token)
        
        # 打印结果
        logger.info(f"获取到 {len(browser_windows)} 个浏览器窗口:")
        for seq, window_info in browser_windows.items():
            logger.info(f"  序号 {seq}: ID = {window_info['id']}")
        
        return browser_windows
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        raise

if __name__ == "__main__":
    test_fetch_browser_windows()
