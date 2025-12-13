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

def smart_wait_for_element(page, selector: str, timeout: int = 30000, state: str = "visible"):
    """
    智能等待元素，支持多种状态
    
    Args:
        page: Playwright页面对象
        selector: CSS选择器
        timeout: 超时时间（毫秒）
        state: 等待状态 ("visible", "hidden", "attached", "detached")
    """
    logger.info(f"智能等待元素: {selector}, 状态: {state}, 超时: {timeout}ms")
    
    try:
        if state == "visible":
            page.wait_for_selector(selector, state="visible", timeout=timeout)
        elif state == "hidden":
            page.wait_for_selector(selector, state="hidden", timeout=timeout)
        elif state == "attached":
            page.wait_for_selector(selector, state="attached", timeout=timeout)
        elif state == "detached":
            page.wait_for_selector(selector, state="detached", timeout=timeout)
        else:
            raise ValueError(f"不支持的状态: {state}")
        
        logger.info(f"元素等待成功: {selector} -> {state}")
        return True
        
    except Exception as e:
        logger.error(f"元素等待失败: {selector} -> {state}, 错误: {e}")
        raise

def smart_wait_for_text(page, selector: str, expected_text: str, timeout: int = 30000):
    """
    智能等待元素包含指定文本
    
    Args:
        page: Playwright页面对象
        selector: CSS选择器
        expected_text: 期望的文本内容
        timeout: 超时时间（毫秒）
    """
    logger.info(f"智能等待文本: {selector} -> '{expected_text}', 超时: {timeout}ms")
    
    try:
        page.wait_for_function(
            f"""
            el => {{
                const text = el.textContent || el.innerText || '';
                return text.includes('{expected_text}');
            }}
            """,
            arg=page.locator(selector),
            timeout=timeout
        )
        
        logger.info(f"文本等待成功: {selector} -> '{expected_text}'")
        return True
        
    except Exception as e:
        logger.error(f"文本等待失败: {selector} -> '{expected_text}', 错误: {e}")
        raise

def smart_wait_for_url_change(page, current_url: str, timeout: int = 30000):
    """
    智能等待URL变化
    
    Args:
        page: Playwright页面对象
        current_url: 当前URL
        timeout: 超时时间（毫秒）
    """
    logger.info(f"智能等待URL变化: {current_url}, 超时: {timeout}ms")
    
    try:
        page.wait_for_function(
            f"""
            () => {{
                return window.location.href !== '{current_url}';
            }}
            """,
            timeout=timeout
        )
        
        new_url = page.url
        logger.info(f"URL变化成功: {current_url} -> {new_url}")
        return new_url
        
    except Exception as e:
        logger.error(f"URL变化等待失败: {current_url}, 错误: {e}")
        raise

def smart_wait_for_page_load(page, timeout: int = 30000):
    """
    智能等待页面加载完成
    
    Args:
        page: Playwright页面对象
        timeout: 超时时间（毫秒）
    """
    logger.info(f"智能等待页面加载, 超时: {timeout}ms")
    
    try:
        # 等待DOM内容加载
        page.wait_for_load_state("domcontentloaded", timeout=timeout)
        logger.info("DOM内容已加载")
        
        # 等待所有资源加载
        page.wait_for_load_state("load", timeout=timeout)
        logger.info("所有资源已加载")
        
        # 等待网络活动结束
        page.wait_for_load_state("networkidle", timeout=timeout)
        logger.info("网络活动已结束")
        
        # 额外等待确保页面稳定
        page.wait_for_timeout(1000)
        logger.info("页面加载完成")
        
        return True
        
    except Exception as e:
        logger.warning(f"页面加载等待超时: {e}")
        # 即使超时也继续执行
        page.wait_for_timeout(1000)
        return False

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

# ========= 路径处理辅助函数 =========
def validate_and_normalize_path(path: str) -> str:
    """
    验证和标准化路径，处理中文路径和编码问题
    
    Args:
        path: 原始路径字符串
        
    Returns:
        str: 标准化后的路径
        
    Raises:
        FileNotFoundError: 路径不存在
        ValueError: 路径格式无效
    """
    try:
        # 标准化路径
        normalized_path = os.path.normpath(path)
        
        # 检查路径是否存在
        if not os.path.exists(normalized_path):
            raise FileNotFoundError(f"路径不存在: {normalized_path}")
        
        # 检查是否为目录
        if not os.path.isdir(normalized_path):
            raise ValueError(f"路径不是目录: {normalized_path}")
        
        # 检查路径是否可读
        if not os.access(normalized_path, os.R_OK):
            raise ValueError(f"路径不可读: {normalized_path}")
        
        logger.info(f"路径验证成功: {normalized_path}")
        return normalized_path
        
    except Exception as e:
        logger.error(f"路径验证失败: {path}, 错误: {e}")
        raise

# ========= 文件上传 =========
def upload_folder_with_keyboard(folder_path: str, image_exts: set):
    """
    打开系统文件对话框后：
    - 选择 folder_path 下的所有指定后缀文件
    - 通过键盘粘贴路径并回车
    - 支持中文路径和特殊字符
    
    修复问题：
    - 明确聚焦到地址栏（Alt+D）后再粘贴路径
    - 进入文件夹后，明确聚焦到文件名输入框（Alt+N）后再粘贴文件名
    - 避免剪贴板内容和焦点位置混乱
    """
    # 验证和标准化路径
    normalized_path = validate_and_normalize_path(folder_path)
    logger.info(f"准备上传文件夹: {normalized_path}")
    
    # 等待文件对话框完全打开
    time.sleep(1 + random.random() * 0.5)
    
    # ========= 第一步：在地址栏中输入路径并进入文件夹 =========
    try:
        # 先点击空白处清除当前焦点（确保后续操作能够正确执行）
        pyautogui.click(10, 10)
        time.sleep(0.3 + random.random() * 0.2)
        logger.info("已点击空白处清除焦点")
        
        # 清空地址栏并直接输入路径（不使用剪贴板，避免编码问题）
        # 先聚焦到地址栏（Alt+D）
        pyautogui.hotkey('alt', 'd')
        time.sleep(0.2 + random.random() * 0.1)
        logger.info("已聚焦到地址栏")
        
        pyautogui.hotkey("ctrl", "a")  # 全选地址栏内容
        time.sleep(0.1)
        
        # 使用更慢的输入速度，确保路径完全输入
        # 根据路径长度计算输入时间，确保有足够时间完成输入
        input_interval = 0.15  # 增加输入间隔到0.15秒，确保每个字符都能正确输入
        pyautogui.write(normalized_path, interval=input_interval)
        logger.info(f"已在地址栏输入路径: {normalized_path}")
        
        # 根据路径长度计算等待时间，确保输入完全完成
        # 路径越长，需要的等待时间越长（每个字符0.15秒 + 额外缓冲时间）
        path_length = len(normalized_path)
        min_wait_time = 0.5  # 最小等待时间
        calculated_wait = path_length * input_interval * 1.5  # 路径长度 * 输入间隔 * 1.5倍安全系数
        wait_time = max(min_wait_time, calculated_wait) + random.uniform(0.2, 0.5)  # 加上随机延迟
        
        logger.info(f"等待路径输入完成（路径长度: {path_length}，等待时间: {wait_time:.2f}秒）...")
        time.sleep(wait_time)
        logger.info("准备按回车键进入文件夹...")
        
        # 尝试多种按回车的方法，确保能够进入文件夹
        enter_pressed = False
        enter_methods = [
            ("press_enter", lambda: pyautogui.press("enter")),
            ("hotkey_return", lambda: pyautogui.hotkey("return")),
            ("keyDown_Up", lambda: (pyautogui.keyDown("enter"), pyautogui.keyUp("enter"))),
        ]
        
        for method_name, method_func in enter_methods:
            try:
                method_func()
                time.sleep(0.3 + random.random() * 0.2)
                logger.info(f"已使用 {method_name} 按回车键")
                enter_pressed = True
                break
            except Exception as e:
                logger.debug(f"{method_name} 失败: {e}，尝试下一个方法")
                continue
        
        if not enter_pressed:
            logger.warning("所有按回车键的方法都失败")
        
        # 多次按回车键，确保能够进入（某些环境下可能需要多次按回车）
        for retry in range(3):
            try:
                pyautogui.press("enter")
                time.sleep(0.3 + random.random() * 0.2)
                logger.info(f"第{retry + 2}次按回车键（确保进入文件夹）")
            except Exception as e:
                logger.debug(f"第{retry + 2}次按回车键失败: {e}")
        
        # 等待文件夹加载完成（增加等待时间，确保真的进入了）
        wait_time = 1.0 + random.random() * 0.5
        logger.info(f"等待文件夹加载完成（{wait_time:.1f}秒）...")
        time.sleep(wait_time)
        logger.info("已尝试进入目标文件夹")
        
    except Exception as e:
        logger.error(f"地址栏输入路径或进入文件夹失败: {e}")
        raise RuntimeError(f"地址栏输入路径或进入文件夹失败: {e}")

    # ========= 第二步：过滤图片文件 =========
    files = [
        f for f in os.listdir(normalized_path)
        if os.path.isfile(os.path.join(normalized_path, f))
        and os.path.splitext(f)[1].lower() in image_exts
    ]
    if not files:
        raise RuntimeError(f"文件夹中没有可上传的图片: {normalized_path}")
    
    logger.info(f"找到 {len(files)} 个图片文件: {', '.join(files[:5])}{'...' if len(files) > 5 else ''}")

    # ========= 第三步：在文件名输入框中粘贴文件名列表 =========
    try:
        # 准备文件名列表（用引号包裹每个文件名）
        input_str = " ".join(f'"{name}"' for name in files)
        
        # 复制文件名列表到剪贴板（这会覆盖之前剪贴板中的路径，但此时路径已经使用完毕）
        pyperclip.copy(input_str)
        logger.info(f"已复制 {len(files)} 个文件名到剪贴板")
        time.sleep(0.2)
        
        # 明确聚焦到文件名输入框（Alt+N 是Windows文件对话框的快捷键）
        pyautogui.hotkey('alt', 'n')
        time.sleep(0.3 + random.random() * 0.2)
        logger.info("已聚焦到文件名输入框")
        
        # 清空文件名输入框并粘贴文件名列表
        pyautogui.hotkey("ctrl", "a")  # 全选
        time.sleep(0.1)
        pyautogui.press("delete")  # 删除现有内容（可能包含文件夹名）
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "v")  # 粘贴文件名列表
        time.sleep(0.3 + random.random() * 0.3)
        logger.info("已在文件名输入框粘贴文件名列表")
        
        # 按回车确认选择文件
        pyautogui.press("enter")
        time.sleep(0.3)
        logger.info(f"已选择文件夹中所有 {len(files)} 个文件上传")
        
    except Exception as e:
        logger.error(f"粘贴文件名列表失败: {e}")
        raise RuntimeError(f"粘贴文件名列表失败: {e}")

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
