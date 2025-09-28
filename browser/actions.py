import os
import time
import random
import pyautogui
import pyperclip
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout  # pyright: ignore[reportMissingImports]
from core.logger import logger
from core.config import load_config

# ========= 从配置文件加载参数 =========
def _load_actions_config():
    """从配置文件加载actions相关参数"""
    try:
        config = load_config()
        actions_config = config.get("actions", {})
        return {
            "default_timeout": actions_config.get("default_timeout", 8000),
            "retry_times": actions_config.get("retry_times", 3),
            "retry_delay": actions_config.get("retry_delay", 1.0)
        }
    except Exception as e:
        logger.warning(f"加载actions配置失败，使用默认值: {e}")
        return {
            "default_timeout": 8000,
            "retry_times": 3,
            "retry_delay": 1.0
        }

# 加载配置参数
_actions_config = _load_actions_config()
DEFAULT_TIMEOUT = _actions_config["default_timeout"]
RETRY_TIMES = _actions_config["retry_times"]
RETRY_DELAY = _actions_config["retry_delay"]

# 输出配置到日志
logger.info(f"Actions配置已加载: 超时时间={DEFAULT_TIMEOUT}ms, 重试次数={RETRY_TIMES}, 重试间隔={RETRY_DELAY}s")

# ========= 工具函数 =========
def human_delay(a: float = 1.0, b: float = 2.0):
    """模拟真人随机延迟"""
    time.sleep(random.uniform(a, b))

def click_blank_area(page: Page, x: int = None, y: int = None):
    """
    点击页面空白处
    
    Args:
        page: Playwright页面对象
        x: 点击的X坐标，为None时使用随机位置
        y: 点击的Y坐标，为None时使用随机位置
    """
    try:
        # 获取页面尺寸
        viewport = page.viewport_size
        if not viewport:
            viewport = {"width": 1920, "height": 1080}
        
        # 如果没有指定坐标，使用页面中心附近的随机位置
        if x is None:
            x = random.randint(viewport["width"] // 4, viewport["width"] * 3 // 4)
        if y is None:
            y = random.randint(viewport["height"] // 4, viewport["height"] * 3 // 4)
        
        # 点击空白处
        page.mouse.click(x, y)
        logger.info(f"点击空白处: ({x}, {y})")
        
        # 添加短暂延迟
        human_delay(0.5, 1.0)
        
    except Exception as e:
        logger.error(f"点击空白处失败: {e}")
        raise

def click_center(page: Page):
    """
    点击当前屏幕中心点位置
    
    Args:
        page: Playwright页面对象
    """
    try:
        # 获取页面尺寸
        viewport = page.viewport_size
        if not viewport:
            viewport = {"width": 1920, "height": 1080}
        
        # 计算屏幕中心点坐标
        center_x = viewport["width"] // 2
        center_y = viewport["height"] // 2
        
        # 点击屏幕中心点
        page.mouse.click(center_x, center_y)
        logger.info(f"点击屏幕中心点: ({center_x}, {center_y})")
        
        # 添加短暂延迟
        human_delay(0.5, 1.0)
        
    except Exception as e:
        logger.error(f"点击屏幕中心点失败: {e}")
        raise

def retry_action(action, retries: int = RETRY_TIMES, delay: float = RETRY_DELAY):
    """
    通用重试封装
    - action: 需要执行的函数
    - retries: 最大重试次数
    - delay: 每次重试间隔
    """
    logger.debug(f"retry_action调用: retries={retries}, delay={delay}")
    for i in range(retries):
        try:
            return action()
        except Exception as e:
            logger.warning(f"第{i + 1}次失败: {e}")
            if i < retries - 1:  # 不是最后一次重试
                time.sleep(delay)
    raise RuntimeError("多次重试后仍失败")

def scroll_page(page: Page, y_offset: int = 100):
    """
    滚动整个页面
    - y_offset: 正值向下，负值向上
    """
    page.evaluate(f"window.scrollBy(0, {y_offset})")
    logger.info(f"页面滚动 {y_offset} 像素")
    time.sleep(random.uniform(0.3, 0.7))

def click_with_wait(
    page: Page,
    selector: str,
    must_exist: bool = False,
    timeout: int = DEFAULT_TIMEOUT
):
    """
    通用点击函数（优化版）
    1. 复选框：优先使用 Playwright 原生 check() / uncheck()，保证最终状态
    2. 其他元素：等待可见可点后正常 click()
    """

    try:
        # 找到元素（外部可套 retry_action）
        element = retry_action(
            lambda: page.wait_for_selector(selector, state="attached", timeout=timeout),
            retries=RETRY_TIMES,
            delay=RETRY_DELAY
        )

        # 获取标签和类型
        tag_name  = element.evaluate("el => el.tagName.toLowerCase()")
        input_type = element.evaluate("el => el.type?.toLowerCase?.()")

        # ✅ 原生复选框：使用 check()，保证最终为选中
        if tag_name == "input" and input_type == "checkbox":
            if element.is_checked():
                logger.info(f"复选框已选中: {selector}")
                return True

            human_delay()
            element.check()   # Playwright 会自动等待并保证 checked
            logger.info(f"复选框勾选成功: {selector}")
            return True

        # ✅ 其他元素：等待可见、可点击后再点
        page.wait_for_function(
            """
            el => {
                const s = window.getComputedStyle(el);
                return el && !el.disabled &&
                       el.offsetParent !== null &&
                       s.visibility !== 'hidden' &&
                       s.pointerEvents !== 'none';
            }
            """,
            arg=element,
            timeout=timeout
        )

        element.scroll_into_view_if_needed()
        human_delay()
        page.wait_for_timeout(150)   # 轻微延迟，防止动画干扰
        element.click()
        logger.info(f"点击成功: {selector}")
        
        # 点击成功后添加2-3秒随机等待时间
        success_delay = random.uniform(2.0, 3.0)
        logger.info(f"点击操作完成，等待 {success_delay:.1f}s 后继续...")
        time.sleep(success_delay)
        
        return True

    except PlaywrightTimeout:
        msg = f"超时未找到元素: {selector}"
        if must_exist:
            raise RuntimeError(msg)
        logger.warning(msg)
        return False
    except Exception as e:
        msg = f"点击失败: {selector}，原因: {e}"
        if must_exist:
            raise RuntimeError(msg)
        logger.warning(msg)
        return False

def input_with_wait(page: Page, selector: str, text: str,
                    must_exist: bool = False,
                    timeout: int = DEFAULT_TIMEOUT):
    """
    通用输入函数：
    - text: 要输入的文本
    - must_exist=True  : 必须出现，否则抛异常
    - must_exist=False : 不存在时打印警告并跳过
    """
    try:
        element = retry_action(
            lambda: page.wait_for_selector(selector, state="visible", timeout=timeout),
            retries=RETRY_TIMES,
            delay=RETRY_DELAY
        )
        # 确保是可编辑输入框
        page.wait_for_function(
            "el => (el.tagName==='INPUT'||el.tagName==='TEXTAREA'||el.isContentEditable) && !el.disabled",
            arg=element,
            timeout=timeout
        )
        human_delay()
        element.scroll_into_view_if_needed()
        page.wait_for_timeout(200)
        element.fill("")                        # 清空
        element.type(text, delay=50)             # 模拟人工输入，每字 50ms
        logger.info(f"输入成功: {selector} -> {text}")
        
        # 输入成功后添加2-3秒随机等待时间
        success_delay = random.uniform(2.0, 3.0)
        logger.info(f"输入操作完成，等待 {success_delay:.1f}s 后继续...")
        time.sleep(success_delay)
        
        return True
    except Exception as e:
        msg = f"输入失败: {selector}，原因: {e}"
        if must_exist:
            raise RuntimeError(msg)
        logger.warning(msg)
        return False

# ========= 文件上传 =========
def upload_folder_with_keyboard(folder_path: str, image_exts: set):
    """
    打开系统文件对话框后：
    - 选择 folder_path 下的所有指定后缀文件
    - 通过键盘粘贴路径并回车
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")

    # 进入文件夹
    time.sleep(1 + random.random() * 0.5)
    pyautogui.click(10, 10)
    time.sleep(0.4 + random.random() * 0.3)
    pyautogui.write(folder_path, interval=0.05)
    pyautogui.click(10, 10)
    time.sleep(0.3 + random.random() * 0.2)
    pyautogui.press("enter"); time.sleep(0.3); pyautogui.press("enter")
    time.sleep(0.8 + random.random() * 0.5)

    # 过滤图片文件
    files = [
        f for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
        and os.path.splitext(f)[1].lower() in image_exts
    ]
    if not files:
        raise RuntimeError(f"文件夹中没有可上传的图片: {folder_path}")

    # 复制文件名并粘贴
    input_str = " ".join(f'"{os.path.splitext(name)[0]}"' for name in files)
    pyperclip.copy(input_str)
    pyautogui.click(10, 10)
    time.sleep(0.2)
    pyautogui.hotkey("ctrl", "a"); time.sleep(0.1)
    pyautogui.press("delete"); time.sleep(0.2)
    pyautogui.hotkey("ctrl", "v"); time.sleep(0.3 + random.random() * 0.3)
    pyautogui.press("enter")
    logger.info(f"已选择文件夹中所有文件上传: {', '.join(files)}")

def smart_goto(page: Page, url: str, wait_until: str = "domcontentloaded", timeout: int = 15000, retry_times: int = 2):
    """
    智能页面导航，支持重试和多种等待策略
    
    Args:
        page: Playwright页面对象
        url: 目标URL
        wait_until: 等待条件 ("load", "domcontentloaded", "networkidle", "commit")
        timeout: 超时时间（毫秒）
        retry_times: 重试次数
    """
    for attempt in range(retry_times):
        try:
            logger.info(f"正在导航到: {url} (尝试 {attempt + 1}/{retry_times})")
            
            # 执行页面导航
            response = page.goto(url, wait_until=wait_until, timeout=timeout)
            
            # 检查响应状态
            if response and response.status >= 400:
                logger.warning(f"页面响应状态码: {response.status}")
                if attempt < retry_times - 1:
                    logger.info(f"等待 {2 ** attempt} 秒后重试...")
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
            
            logger.info(f"✅ 页面导航成功: {url}")
            return response
            
        except Exception as e:
            logger.error(f"页面导航失败 (尝试 {attempt + 1}/{retry_times}): {e}")
            if attempt < retry_times - 1:
                wait_time = 2 ** attempt
                logger.info(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                logger.error(f"页面导航最终失败: {url}")
                raise
