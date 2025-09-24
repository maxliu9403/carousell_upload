"""
浏览器接口抽象类
支持多种指纹浏览器的统一接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional
from playwright.sync_api import sync_playwright
from core.logger import logger


class BrowserInterface(ABC):
    """浏览器接口抽象类"""
    
    def __init__(self, api_port: int, api_key: str):
        self.api_port = api_port
        self.api_key = api_key
    
    @abstractmethod
    def check_health(self) -> bool:
        """
        检查浏览器API是否正常
        
        Returns:
            bool: True表示API正常，False表示API异常
        """
        pass
    
    @abstractmethod
    def start_browser(self, profile_id: str) -> Tuple[Any, Any, Any]:
        """
        启动浏览器并返回 Playwright 对象
        
        Args:
            profile_id (str): 浏览器配置文件ID
            
        Returns:
            Tuple[Any, Any, Any]: (playwright, browser, page)
        """
        pass
    
    @abstractmethod
    def close_browser(self, profile_id: str) -> bool:
        """
        关闭浏览器窗口
        
        Args:
            profile_id (str): 浏览器配置文件ID
            
        Returns:
            bool: True表示关闭成功，False表示关闭失败
        """
        pass
    
    @abstractmethod
    def get_browser_windows(self) -> Optional[Dict[int, Dict[str, str]]]:
        """
        获取浏览器窗口列表（仅bitBrowser需要）
        
        Returns:
            Optional[Dict[int, Dict[str, str]]]: 浏览器窗口映射表，ixBrowser返回None
        """
        pass
    
    @abstractmethod
    def get_profile_id_by_browser_id(self, browser_id: str, browser_windows: Optional[Dict[int, Dict[str, str]]] = None) -> str:
        """
        根据BrowserID获取对应的profile_id
        
        Args:
            browser_id (str): Excel中的BrowserID
            browser_windows (Optional[Dict[int, Dict[str, str]]]): 浏览器窗口映射表
            
        Returns:
            str: 对应的profile_id
        """
        pass


class BitBrowserInterface(BrowserInterface):
    """BitBrowser接口实现"""
    
    def check_health(self) -> bool:
        """检查BitBrowser API健康状态"""
        try:
            import requests
            
            # 使用列表接口代替健康检查
            url = f"http://127.0.0.1:{self.api_port}/browser/list"
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            payload = {"page": 1, "pageSize": 1}
            
            logger.info(f"正在检查BitBrowser API健康状态: {url}")
            
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    logger.info("✅ BitBrowser API健康检查通过")
                    return True
                else:
                    logger.error("❌ BitBrowser API健康检查失败，success=False")
                    return False
            else:
                logger.error(f"❌ BitBrowser API健康检查失败，HTTP状态码: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ BitBrowser API健康检查发生错误: {e}")
            return False
    
    def start_browser(self, profile_id: str) -> Tuple[Any, Any, Any]:
        """启动BitBrowser"""
        try:
            import requests
            
            # 构建API URL
            api_url = f"http://127.0.0.1:{self.api_port}/browser/open"
            headers = {"x-api-key": self.api_key}
            resp = requests.post(api_url, headers=headers, json={"id": profile_id, "args": []})
            resp.raise_for_status()
            
            data = resp.json()
            if not data.get("success"):
                raise RuntimeError(f"启动BitBrowser失败: {data}")
            
            ws_endpoint = data["data"]["ws"]
            logger.info(f"BitBrowser已启动，WebSocket: {ws_endpoint}")

            playwright = sync_playwright().start()
            browser = playwright.chromium.connect_over_cdp(ws_endpoint)
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.new_page()
            
            logger.info("BitBrowser连接成功")
            return playwright, browser, page
            
        except Exception as e:
            logger.error(f"启动BitBrowser失败: {e}")
            raise
    
    def close_browser(self, profile_id: str) -> bool:
        """关闭BitBrowser"""
        try:
            import requests
            
            close_url = f"http://127.0.0.1:{self.api_port}/browser/close"
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            resp = requests.post(close_url, headers=headers, json={"id": profile_id})
            resp.raise_for_status()
            
            data = resp.json()
            if data.get("success"):
                logger.info(f"BitBrowser窗口关闭成功: id={profile_id}")
                return True
            else:
                logger.warning(f"BitBrowser窗口关闭失败: id={profile_id}, 响应: {data}")
                return False
                
        except Exception as e:
            logger.error(f"关闭BitBrowser失败: profile_id={profile_id}, 错误: {e}")
            return False
    
    def get_browser_windows(self) -> Dict[int, Dict[str, str]]:
        """获取BitBrowser窗口列表"""
        try:
            import requests
            
            url = f"http://127.0.0.1:{self.api_port}/browser/list"
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }

            browser_window_map = {}
            page = 0
            page_size = 100
            payload = {"page": page, "pageSize": page_size}

            logger.info("1. 发送第一页请求，获取总数量信息")
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            json_data = response.json()

            if not json_data.get("success"):
                raise Exception("接口返回失败，success=False")

            data = json_data.get("data", {})
            total_num = data.get("totalNum", 0)
            logger.info(f"   a. 当前页码: {page}, 总数: {total_num}")

            # 处理第一页数据
            for item in data.get("list", []):
                seq = item.get("seq")
                _id = item.get("id")
                if seq is not None and _id:
                    browser_window_map[seq] = {"id": _id}

            # 判断是否需要继续分页请求
            if total_num <= page_size:
                logger.info("   d. 所有数据已包含在第一页中，跳过后续分页请求")
                return browser_window_map

            # 计算总页数
            total_pages = (total_num + page_size - 1) // page_size
            logger.info(f"   b. 开始分页请求，预计页数: {total_pages}")

            # 从第2页开始拉取
            for page in range(1, total_pages):
                payload = {"page": page, "pageSize": page_size}
                logger.info(f"   c. 请求第 {page + 1} 页数据")

                try:
                    response = requests.post(url, json=payload, headers=headers, timeout=60)
                    response.raise_for_status()
                    json_data = response.json()

                    if not json_data.get("success"):
                        raise Exception(f"第 {page + 1} 页接口返回失败，success=False")

                    data = json_data.get("data", {})
                    for item in data.get("list", []):
                        seq = item.get("seq")
                        _id = item.get("id")
                        if seq is not None and _id:
                            browser_window_map[seq] = {"id": _id}

                except Exception as e:
                    logger.error(f"      ⚠️ 请求第 {page + 1} 页失败: {str(e)}")
                    raise

        except Exception as e:
            logger.error(f"   ❌ 请求接口失败: {str(e)}")
            raise

        logger.info(f"2. 数据收集完成，窗口总数: {len(browser_window_map)}")
        return browser_window_map
    
    def get_profile_id_by_browser_id(self, browser_id: str, browser_windows: Optional[Dict[int, Dict[str, str]]] = None) -> str:
        """根据BrowserID获取对应的profile_id（BitBrowser需要映射）"""
        try:
            if browser_windows is not None:
                browser_window_map = browser_windows
            else:
                browser_window_map = self.get_browser_windows()
            
            seq = int(browser_id)
            
            if seq in browser_window_map:
                profile_id = browser_window_map[seq]["id"]
                logger.info(f"找到BrowserID {browser_id} 对应的profile_id: {profile_id}")
                return profile_id
            else:
                available_seqs = list(browser_window_map.keys())
                raise ValueError(f"未找到BrowserID {browser_id} 对应的浏览器窗口")
                
        except ValueError as e:
            logger.error(f"BrowserID映射失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取profile_id时发生错误: {e}")
            raise


class IxBrowserInterface(BrowserInterface):
    """IxBrowser接口实现"""
    
    def check_health(self) -> bool:
        """检查IxBrowser API健康状态"""
        try:
            import requests
            
            # 使用列表接口代替健康检查
            url = f"http://127.0.0.1:{self.api_port}/api/v2/profile-list"
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            payload = {"page": 1, "limit": 1}
            
            logger.info(f"正在检查IxBrowser API健康状态: {url}")
            
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                error_info = data.get("error", {})
                if error_info.get("code") == 0:
                    logger.info("✅ IxBrowser API健康检查通过")
                    return True
                else:
                    logger.error(f"❌ IxBrowser API健康检查失败，code: {error_info.get('code')}")
                    return False
            else:
                logger.error(f"❌ IxBrowser API健康检查失败，HTTP状态码: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ IxBrowser API健康检查发生错误: {e}")
            return False
    
    def start_browser(self, profile_id: str) -> Tuple[Any, Any, Any]:
        """启动IxBrowser"""
        try:
            import requests
            
            # 构建API URL
            api_url = f"http://127.0.0.1:{self.api_port}/api/v2/profile-open"
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "profile_id": int(profile_id),
                "load_extensions": True,
                "load_profile_info_page": True
            }
            
            resp = requests.post(api_url, headers=headers, json=payload)
            resp.raise_for_status()
            
            data = resp.json()
            error_info = data.get("error", {})
            if error_info.get("code") != 0:
                raise RuntimeError(f"启动IxBrowser失败: {error_info}")
            
            ws_endpoint = data["data"]["ws"]
            logger.info(f"IxBrowser已启动，WebSocket: {ws_endpoint}")

            playwright = sync_playwright().start()
            browser = playwright.chromium.connect_over_cdp(ws_endpoint)
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.new_page()
            
            logger.info("IxBrowser连接成功")
            return playwright, browser, page
            
        except Exception as e:
            logger.error(f"启动IxBrowser失败: {e}")
            raise
    
    def close_browser(self, profile_id: str) -> bool:
        """关闭IxBrowser"""
        try:
            import requests
            
            close_url = f"http://127.0.0.1:{self.api_port}/api/v2/profile-close"
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            payload = {"profile_id": int(profile_id)}
            
            resp = requests.post(close_url, headers=headers, json=payload)
            resp.raise_for_status()
            
            data = resp.json()
            error_info = data.get("error", {})
            if error_info.get("code") == 0:
                logger.info(f"IxBrowser窗口关闭成功: id={profile_id}")
                return True
            else:
                logger.warning(f"IxBrowser窗口关闭失败: id={profile_id}, 响应: {error_info}")
                return False
                
        except Exception as e:
            logger.error(f"关闭IxBrowser失败: profile_id={profile_id}, 错误: {e}")
            return False
    
    def get_browser_windows(self) -> Optional[Dict[int, Dict[str, str]]]:
        """IxBrowser不需要窗口映射，直接返回None"""
        logger.info("IxBrowser不需要窗口映射")
        return None
    
    def get_profile_id_by_browser_id(self, browser_id: str, browser_windows: Optional[Dict[int, Dict[str, str]]] = None) -> str:
        """IxBrowser直接使用BrowserID作为profile_id"""
        logger.info(f"IxBrowser直接使用BrowserID作为profile_id: {browser_id}")
        return browser_id
