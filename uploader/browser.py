import requests  # pyright: ignore[reportMissingModuleSource]
from playwright.sync_api import sync_playwright  # pyright: ignore[reportMissingImports]
from typing import Dict, Any
from .logger import logger

def check_browser_api_health(api_port: int, api_key: str) -> bool:
    """
    检查浏览器API是否正常
    
    Args:
        api_port (int): 接口服务端口号
        api_key (str): API密钥
    
    Returns:
        bool: True表示API正常，False表示API异常
    
    Raises:
        Exception: 当API检查失败时抛出异常
    """
    try:
        # 构建健康检查URL
        health_url = f"http://127.0.0.1:{api_port}/health"
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }
        
        logger.info(f"正在检查浏览器API健康状态: {health_url}")
        
        # 发送健康检查请求
        response = requests.get(health_url, headers=headers, timeout=10)
        
        # 检查HTTP状态码
        if response.status_code == 200:
            logger.info("✅ 浏览器API健康检查通过")
            return True
        else:
            logger.error(f"❌ 浏览器API健康检查失败，HTTP状态码: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.error(f"❌ 无法连接到浏览器API服务 (端口: {api_port})")
        logger.error("请检查浏览器服务是否已启动")
        return False
    except requests.exceptions.Timeout:
        logger.error("❌ 浏览器API健康检查超时")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ 浏览器API健康检查请求失败: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 浏览器API健康检查发生未知错误: {e}")
        return False

def start_browser(api_url: str, api_key: str, profile_id: str):
    """启动指纹浏览器并返回 Playwright 对象"""
    try:
        headers = {"x-api-key": api_key}
        resp = requests.post(api_url, headers=headers, json={"id": profile_id, "args": []})
        resp.raise_for_status()  # 检查 HTTP 状态码
        
        data = resp.json()
        if not data.get("success"):
            raise RuntimeError(f"启动指纹浏览器失败: {data}")
        
        ws_endpoint = data["data"]["ws"]
        logger.info(f"指纹浏览器已启动，WebSocket: {ws_endpoint}")

        playwright = sync_playwright().start()
        browser = playwright.chromium.connect_over_cdp(ws_endpoint)
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.new_page()
        
        logger.info("浏览器连接成功")
        return playwright, browser, page
        
    except requests.RequestException as e:
        logger.error(f"请求指纹浏览器 API 失败: {e}")
        raise
    except Exception as e:
        logger.error(f"启动浏览器失败: {e}")
        raise


def fetch_all_browser_windows(api_port: int, token: str) -> Dict[int, Dict[str, str]]:
    """
    获取全部浏览器窗口信息
    
    分页获取接口 /browser/list 中的所有窗口数据，并将其映射为 {seq: {"id": id}} 的形式返回
    
    Args:
        api_port (int): 接口服务端口号，例如：54345
        token (str): 请求头token，x-api-key 的值
    
    Returns:
        Dict[int, Dict[str, str]]: 浏览器ID的映射表 {seq: {"id": id}}
    """
    # 构建请求基础信息
    url = f"http://127.0.0.1:{api_port}/browser/list"
    headers = {
        "x-api-key": token,
        "Content-Type": "application/json"
    }

    browser_window_map = {}

    # 第一次请求：用于获取 totalNum
    page = 0
    page_size = 100
    payload = {
        "page": page,
        "pageSize": page_size
    }

    logger.info("1. 发送第一页请求，获取总数量信息")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        json_data = response.json()

        # ✅ 判断接口是否成功
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

        # ✅ 判断是否需要继续分页请求
        if total_num <= page_size:
            logger.info("   d. 所有数据已包含在第一页中，跳过后续分页请求")
            return browser_window_map

        # 计算总页数（向上取整）
        total_pages = (total_num + page_size - 1) // page_size

        logger.info(f"   b. 开始分页请求，预计页数: {total_pages}")

        # 从第2页开始拉取
        for page in range(1, total_pages):
            payload = {
                "page": page,
                "pageSize": page_size
            }
            logger.info(f"   c. 请求第 {page + 1} 页数据")

            try:
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                response.raise_for_status()
                json_data = response.json()

                # ✅ 判断接口是否成功
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


def get_profile_id_by_browser_id(api_port: int, token: str, browser_id: str, browser_windows: Dict[int, Dict[str, str]] = None) -> str:
    """
    根据BrowserID获取对应的profile_id
    
    Args:
        api_port (int): 接口服务端口号
        token (str): 请求头token
        browser_id (str): Excel中的BrowserID（对应browser_window_map中的seq）
    
    Returns:
        str: 对应的profile_id（browser_window_map中的id）
    
    Raises:
        ValueError: 当找不到对应的BrowserID时
    """
    try:
        # 如果传入了browser_windows，直接使用；否则重新获取
        if browser_windows is not None:
            browser_window_map = browser_windows
        else:
            browser_window_map = fetch_all_browser_windows(api_port, token)
        
        # 将browser_id转换为整数（因为seq是整数）
        seq = int(browser_id)
        
        # 查找对应的profile_id
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
