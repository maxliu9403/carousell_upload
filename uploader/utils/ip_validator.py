"""
IP地域校验工具
用于验证指纹浏览器的IP地域是否与期望的地域一致
"""

from typing import Dict, Optional
from playwright.sync_api import Page  # pyright: ignore[reportMissingImports]
from core.logger import logger
import time


class IPValidator:
    """IP地域校验器"""
    
    # 地域代码映射表
    REGION_CODE_MAP = {
        'HK': ['HK', 'Hong Kong'],
        'SG': ['SG', 'Singapore'],
        'MY': ['MY', 'Malaysia'],
        'TW': ['TW', 'Taiwan'],
        'US': ['US', 'United States'],
        'UK': ['GB', 'United Kingdom'],
        'AU': ['AU', 'Australia'],
        'JP': ['JP', 'Japan'],
        'KR': ['KR', 'South Korea'],
    }
    
    # IP查询服务列表（按优先级排序）
    IP_SERVICES = [
        {
            'name': 'ipapi.co',
            'url': 'https://ipapi.co/json/',
            'country_key': 'country_code',
            'timeout': 5000
        },
        {
            'name': 'ip-api.com',
            'url': 'http://ip-api.com/json/',
            'country_key': 'countryCode',
            'timeout': 5000
        },
        {
            'name': 'ipinfo.io',
            'url': 'https://ipinfo.io/json',
            'country_key': 'country',
            'timeout': 5000
        }
    ]
    
    def __init__(self, page: Page, expected_region: str):
        """
        初始化IP校验器
        
        Args:
            page: Playwright页面对象
            expected_region: 期望的地域代码（如 'HK', 'SG'）
        """
        self.page = page
        self.expected_region = expected_region.upper()
    
    def validate_ip_region(self) -> tuple[bool, Optional[str], Optional[str]]:
        """
        校验当前浏览器的IP地域是否与期望一致
        
        Returns:
            tuple: (是否匹配, 实际地域代码, 实际IP地址)
        """
        logger.info(f"开始校验IP地域，期望地域: {self.expected_region}")
        
        # 尝试多个IP查询服务
        for service in self.IP_SERVICES:
            try:
                logger.info(f"尝试使用 {service['name']} 查询IP...")
                ip_info = self._fetch_ip_info(service)
                
                if ip_info:
                    actual_country = ip_info.get(service['country_key'], '').upper()
                    actual_ip = ip_info.get('ip', 'Unknown')
                    
                    logger.info(f"获取到IP信息 - IP: {actual_ip}, 地域: {actual_country}")
                    
                    # 判断地域是否匹配
                    is_match = self._is_region_match(actual_country)
                    
                    if is_match:
                        logger.info(f"✅ IP地域校验通过: {actual_country} 匹配 {self.expected_region}")
                    else:
                        logger.warning(f"❌ IP地域校验失败: {actual_country} 不匹配 {self.expected_region}")
                    
                    return is_match, actual_country, actual_ip
                    
            except Exception as e:
                logger.warning(f"使用 {service['name']} 查询IP失败: {e}")
                continue
        
        # 所有服务都失败
        logger.error("所有IP查询服务都失败，无法校验IP地域")
        return False, None, None
    
    def _fetch_ip_info(self, service: Dict) -> Optional[Dict]:
        """
        从指定服务获取IP信息
        
        Args:
            service: IP查询服务配置
            
        Returns:
            Dict: IP信息字典，失败返回None
        """
        try:
            # 访问IP查询API
            response = self.page.goto(
                service['url'],
                timeout=service['timeout'],
                wait_until='networkidle'
            )
            
            if not response or not response.ok:
                logger.warning(f"{service['name']} 返回错误状态: {response.status if response else 'None'}")
                return None
            
            # 获取页面文本内容
            content = self.page.content()
            
            # 提取JSON数据
            import re
            json_match = re.search(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
            else:
                json_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL)
                if json_match:
                    json_text = json_match.group(1)
                else:
                    json_text = content
            
            # 解析JSON
            import json
            json_text = json_text.strip()
            ip_info = json.loads(json_text)
            
            return ip_info
            
        except Exception as e:
            logger.warning(f"从 {service['name']} 获取IP信息失败: {e}")
            return None
    
    def _is_region_match(self, actual_country: str) -> bool:
        """
        判断实际地域是否与期望地域匹配
        
        Args:
            actual_country: 实际的国家/地区代码
            
        Returns:
            bool: 是否匹配
        """
        if not actual_country:
            return False
        
        # 获取期望地域的所有可能代码
        expected_codes = self.REGION_CODE_MAP.get(self.expected_region, [self.expected_region])
        
        # 检查是否匹配
        for code in expected_codes:
            if actual_country.upper() == code.upper():
                return True
        
        return False
    
    @staticmethod
    def quick_validate(page: Page, expected_region: str) -> tuple[bool, Optional[str], Optional[str]]:
        """
        快速校验IP地域（静态方法）
        
        Args:
            page: Playwright页面对象
            expected_region: 期望的地域代码
            
        Returns:
            tuple: (是否匹配, 实际地域代码, 实际IP地址)
        """
        validator = IPValidator(page, expected_region)
        return validator.validate_ip_region()

