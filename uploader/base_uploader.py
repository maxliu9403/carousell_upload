"""
基础上传器类 - 包含所有地域和类目的公共功能
保持原有的点击操作顺序和CSS选择器不变
"""
from typing import Optional
from playwright.sync_api import Page  # pyright: ignore[reportMissingImports]
from core.models import ProductInfo, UploadConfig
from browser.actions import (
    click_with_wait, 
    upload_folder_with_keyboard, 
    human_delay, 
    input_with_wait, 
    smart_goto
)
from core.logger import logger
from .utils import enrich_product_info

class CriticalOperationFailed(Exception):
    """关键操作失败异常，需要立即停止当前流程"""
    pass

def safe_click_with_wait(page: Page, selector: str, must_exist: bool = False, timeout: int = None, 
                        browser_id: str = None, sku: str = None, operation: str = "点击操作"):
    """安全的点击操作，must_exist=True时失败会抛出CriticalOperationFailed"""
    # 先提示正在执行的操作
    log_prefix = f"BrowserID: {browser_id}, SKU: {sku}, " if browser_id and sku else ""
    logger.info(f"{log_prefix}正在{operation}: {selector}")
    
    try:
        result = click_with_wait(page, selector, must_exist, timeout)
        logger.info(f"{log_prefix}{operation}成功: {selector}")
        return result
    except RuntimeError as e:
        if must_exist:
            error_msg = f"关键{operation}失败"
            if browser_id and sku:
                error_msg = f"BrowserID: {browser_id}, SKU: {sku}, {error_msg}"
            error_msg += f", CSS选择器: {selector}, 失败原因: {e}"
            logger.error(error_msg)
            raise CriticalOperationFailed(error_msg)
        else:
            logger.warning(f"{log_prefix}{operation}失败: {selector}, 原因: {e}")
        raise

def safe_click_with_fallback(page: Page, primary_selector: str, fallback_selector: str, 
                            must_exist: bool = False, timeout: int = None,
                            browser_id: str = None, sku: str = None, operation: str = "点击操作"):
    """
    支持备用选择器的安全点击操作
    先尝试主选择器，失败后尝试备用选择器
    
    Args:
        page: Playwright页面对象
        primary_selector: 主选择器
        fallback_selector: 备用选择器
        must_exist: 是否必须存在
        timeout: 超时时间
        browser_id: 浏览器ID
        sku: 商品SKU
        operation: 操作描述
    """
    log_prefix = f"BrowserID: {browser_id}, SKU: {sku}, " if browser_id and sku else ""
    
    # 先尝试主选择器
    try:
        logger.info(f"{log_prefix}正在{operation}: {primary_selector}")
        result = click_with_wait(page, primary_selector, must_exist, timeout)
        logger.info(f"{log_prefix}{operation}成功: {primary_selector}")
        return result
    except RuntimeError as e:
        logger.warning(f"{log_prefix}主选择器失败: {primary_selector}, 原因: {e}")
        
        # 尝试备用选择器
        try:
            logger.info(f"{log_prefix}尝试备用选择器: {fallback_selector}")
            result = click_with_wait(page, fallback_selector, must_exist, timeout)
            logger.info(f"{log_prefix}{operation}成功: {fallback_selector} (备用选择器)")
            return result
        except RuntimeError as fallback_e:
            if must_exist:
                error_msg = f"关键{operation}失败"
                if browser_id and sku:
                    error_msg = f"BrowserID: {browser_id}, SKU: {sku}, {error_msg}"
                error_msg += f", 主选择器: {primary_selector}, 备用选择器: {fallback_selector}, 失败原因: {e}, 备用失败原因: {fallback_e}"
                logger.error(error_msg)
                raise CriticalOperationFailed(error_msg)
            else:
                logger.warning(f"{log_prefix}主选择器和备用选择器都失败: {primary_selector}, {fallback_selector}, 原因: {e}, 备用失败原因: {fallback_e}")
            raise

def safe_input_with_wait(page: Page, selector: str, text: str, must_exist: bool = False, timeout: int = None,
                        browser_id: str = None, sku: str = None, operation: str = "输入操作"):
    """安全的输入操作，must_exist=True时失败会抛出CriticalOperationFailed"""
    # 先提示正在执行的操作
    log_prefix = f"BrowserID: {browser_id}, SKU: {sku}, " if browser_id and sku else ""
    logger.info(f"{log_prefix}正在{operation}: {selector}, 输入内容: '{text}'")
    
    try:
        result = input_with_wait(page, selector, text, must_exist, timeout)
        logger.info(f"{log_prefix}{operation}成功: {selector}")
        return result
    except RuntimeError as e:
        if must_exist:
            error_msg = f"关键{operation}失败"
            if browser_id and sku:
                error_msg = f"BrowserID: {browser_id}, SKU: {sku}, {error_msg}"
            error_msg += f", CSS选择器: {selector}, 输入内容: '{text}', 失败原因: {e}"
            logger.error(error_msg)
            raise CriticalOperationFailed(error_msg)
        else:
            logger.warning(f"{log_prefix}{operation}失败: {selector}, 输入内容: '{text}', 原因: {e}")
        raise

def safe_input_with_fallback(page: Page, primary_selector: str, fallback_selector: str, text: str, 
                            must_exist: bool = False, timeout: int = None,
                            browser_id: str = None, sku: str = None, operation: str = "输入操作"):
    """
    支持备用选择器的安全输入操作
    先尝试主选择器，失败后尝试备用选择器
    
    Args:
        page: Playwright页面对象
        primary_selector: 主选择器
        fallback_selector: 备用选择器
        text: 要输入的文本
        must_exist: 是否必须存在
        timeout: 超时时间
        browser_id: 浏览器ID
        sku: 商品SKU
        operation: 操作描述
    """
    log_prefix = f"BrowserID: {browser_id}, SKU: {sku}, " if browser_id and sku else ""
    
    # 先尝试主选择器
    try:
        logger.info(f"{log_prefix}正在{operation}: {primary_selector}, 输入内容: '{text}'")
        result = input_with_wait(page, primary_selector, text, must_exist, timeout)
        logger.info(f"{log_prefix}{operation}成功: {primary_selector}")
        return result
    except RuntimeError as e:
        logger.warning(f"{log_prefix}主选择器失败: {primary_selector}, 原因: {e}")
        
        # 尝试备用选择器
        try:
            logger.info(f"{log_prefix}尝试备用选择器: {fallback_selector}")
            result = input_with_wait(page, fallback_selector, text, must_exist, timeout)
            logger.info(f"{log_prefix}{operation}成功: {fallback_selector} (备用选择器)")
            return result
        except RuntimeError as fallback_e:
            if must_exist:
                error_msg = f"关键{operation}失败"
                if browser_id and sku:
                    error_msg = f"BrowserID: {browser_id}, SKU: {sku}, {error_msg}"
                error_msg += f", 主选择器: {primary_selector}, 备用选择器: {fallback_selector}, 输入内容: '{text}', 失败原因: {e}, 备用失败原因: {fallback_e}"
                logger.error(error_msg)
                raise CriticalOperationFailed(error_msg)
            else:
                logger.warning(f"{log_prefix}主选择器和备用选择器都失败: {primary_selector}, {fallback_selector}, 原因: {e}, 备用失败原因: {fallback_e}")
            raise

class BaseUploader:
    """基础上传器类 - 包含所有地域和类目的公共功能"""
    
    def __init__(self, page: Page, config: UploadConfig, region: str = "SG", browser_id: str = None, sku: str = None):
        self.page = page
        self.config = config
        self.region = region
        self.browser_id = browser_id
        self.sku = sku
        
    def _get_domain_by_region(self) -> str:
        """根据地域获取对应的域名"""
        if self.region not in self.config.domains:
            logger.warning(f"未找到地域 {self.region} 的域名配置，使用默认地域 SG")
            self.region = "SG"
        
        domain = self.config.domains[self.region]
        logger.info(f"使用 {self.region} 地域域名: {domain}")
        return domain
        
    def _enrich_product_info(self, product_info: ProductInfo) -> ProductInfo:
        """丰富商品信息"""
        return enrich_product_info(product_info, self.config, self.region)
        
    # ========= 公共方法：服务商品上传流程 =========
    def _upload_service_product(self, enriched_info: ProductInfo, folder_path: str):
        """
        上传服务商品，公共函数
        保持原有的点击操作顺序和CSS选择器不变
        """
        # 打开主页
        self._navigate_to_homepage()
        
        # 开始上传流程
        self._start_upload_flow(folder_path)
        
        # 选择服务类目
        self._select_service_category()
        
        # 填写基本信息
        self._fill_basic_info(enriched_info)

        if self.region == "HK":
            self._closewhatsapp()
            self._closemeetup()
            self._open_delivery()

        if self.region == "SG":
            # 选择地域相关设置
            self._select_location_by_region()
        
        # 发布商品
        self._publish_product()
        
        # 等待页面稳定
        self.page.wait_for_timeout(10000)
    
    # HK逻辑
    def _closewhatsapp(self):
        """关闭WhatsApp"""
        if self.page.query_selector("button.D_mk"):
            logger.info("关闭whatsapp")
            safe_click_with_wait(self.page, "rect.D_axg", must_exist=True,
                           browser_id=self.browser_id, sku=self.sku, operation="关闭WhatsApp")
    # HK逻辑
    def _closemeetup(self):
        """关闭meetup"""
        if self.page.query_selector("input.D_vI"):
            logger.info("关闭面交")
            safe_click_with_fallback(self.page, "#FieldSetField-Container-field_meetup > .D_IL", ".D_pZ > .D_mx", must_exist=True,
                               browser_id=self.browser_id, sku=self.sku, operation="输入产品描述")

    # HK开启送货
    def _open_delivery(self):
        """开启送货"""
        if not self.page.query_selector("#FieldSetField-Container-field_mailing_details .D_tk"):
            logger.info("开启送货")
            safe_click_with_fallback(self.page, ".D_agx > .D_mK", "#FieldSetField-Container-field_mailing .D_mx", must_exist=True,
                           browser_id=self.browser_id, sku=self.sku, operation="开启送货")
            
    # ========= 公共方法：页面导航 =========
    def _navigate_to_homepage(self):
        """导航到主页"""
        domain = self._get_domain_by_region()
        smart_goto(self.page, domain, wait_until="domcontentloaded", timeout=30000)
        logger.info("🌐 已打开主页")
        
    def _navigate_to_manage_page(self):
        """导航到管理页面"""
        domain = self._get_domain_by_region()
        smart_goto(self.page, f"{domain}/manage-listings/", wait_until="domcontentloaded", timeout=30000)
        logger.info("🌐 已打开目标页面")
        
    # ========= 公共方法：上传流程 =========
    def _start_upload_flow(self, folder_path: str):
        """开始上传流程"""
        # 点击sell按钮
        safe_click_with_wait(self.page, "a.D__s", must_exist=True, 
                           browser_id=self.browser_id, sku=self.sku, operation="点击sell按钮")
        
        # 点击上传图片
        safe_click_with_wait(self.page, "div.D_JY", must_exist=True,
                           browser_id=self.browser_id, sku=self.sku, operation="点击上传图片")
        # 上传图片
        if folder_path:
            upload_folder_with_keyboard(folder_path, self.config.image_extensions)
            human_delay(2, 3)
        else:
            raise ValueError("folder_path参数不能为空")
        
        # 新账号初次上品会出现（可选）
        if self.region == "SG":
            safe_click_with_wait(self.page, ".D_ayk > .D_oN > .D_oZ", must_exist=False)

        # 忽略AI编写文案
        safe_click_with_wait(self.page, ".D_oK > .D_oe", must_exist=False,
                           browser_id=self.browser_id, sku=self.sku, operation="取消AI编写文案")

    def _select_service_category(self):
        """选择服务类目"""
        # 选择类目
        safe_click_with_wait(self.page, "div.D_aFi", must_exist=True,
                           browser_id=self.browser_id, sku=self.sku, operation="选择服务类目")
        
        # 根据地域选择搜索关键词
        search_keyword = self._get_service_search_keyword()
        
        # 输入搜索关键词
        safe_input_with_wait(self.page, "input.D_Kr", search_keyword, must_exist=True,
                           browser_id=self.browser_id, sku=self.sku, operation=f"输入{search_keyword}搜索服务")
        
        # 等待出现搜索结果
        self.page.wait_for_timeout(2000)
        # 点击服务
        if self.region == "HK":
            self._safe_click_subcategory(".D_aFp:nth-child(5) > .D_aFx > .D_mx", "服務")
        elif self.region == "SG":
            self._safe_click_subcategory(".D_aEk:nth-child(2) > .D_aEs > .D_la", "服务")
        elif self.region == "MY":
            self._safe_click_subcategory(".D_aEk:nth-child(2) > .D_aEs > .D_la", "服务")
        else:
            self._safe_click_subcategory(".D_aEk:nth-child(2) > .D_aEs > .D_la", "服务")
        
    def _get_service_search_keyword(self) -> str:
        """
        根据地域获取服务类目搜索关键词
        
        Returns:
            str: 搜索关键词
        """
        service_keywords = {
            "SG": "others",    # 新加坡使用 "others"
            "HK": "其他",      # 香港使用 "其他"
            "MY": "others"     # 马来西亚使用 "others"
        }
        
        keyword = service_keywords.get(self.region, "others")
        logger.info(f"使用地域 {self.region} 的服务搜索关键词: {keyword}")
        return keyword
        
    def _fill_basic_info(self, enriched_info: ProductInfo):
        """填写基本信息"""
        # 输入产品标题
        safe_input_with_wait(self.page, "input#title", enriched_info.title, must_exist=True,
                           browser_id=self.browser_id, sku=self.sku, operation="输入产品标题")

        if self.region == "HK":
            safe_click_with_wait(self.page, "button.D_oo:nth-child(1)", must_exist=True,
                               browser_id=self.browser_id, sku=self.sku, operation="点击新旧")
      
        # 输入产品价格
        safe_input_with_wait(self.page, "input#price", enriched_info.price, must_exist=True,
                           browser_id=self.browser_id, sku=self.sku, operation="输入产品价格")

        if self.region == "HK":
            safe_input_with_fallback(self.page, "textarea.D_tk", "textarea.D_tk", enriched_info.description, must_exist=True,
                               browser_id=self.browser_id, sku=self.sku, operation="输入产品描述")
        else:
            safe_input_with_fallback(self.page, ".D_aAb .D_tk", "textarea.D_tk", enriched_info.description, must_exist=True,
                               browser_id=self.browser_id, sku=self.sku, operation="输入产品描述")

        
    def _select_location_by_region(self):
        """根据地域选择Location"""
        # 点击 选择 Location
        safe_click_with_wait(self.page, "input.D_tk", must_exist=False,
                           browser_id=self.browser_id, sku=self.sku, operation="点击选择Location")
        self.page.wait_for_timeout(2000)
        safe_click_with_wait(self.page, ".D_bMM:nth-child(2) > .D_la", must_exist=True,
                               browser_id=self.browser_id, sku=self.sku, operation="选择面交地点")
        
    def _publish_product(self):
        """发布商品"""
        # 点击发布
        safe_click_with_wait(self.page, "button.D_uG", must_exist=True,
                           browser_id=self.browser_id, sku=self.sku, operation="点击发布按钮")
        
    # ========= 公共方法：编辑模式 =========
    def _enter_edit_mode(self):
        """进入编辑模式"""
        # 点击 未活跃
        safe_click_with_wait(self.page, "button.D_bwN:nth-child(2)", must_exist=True,
                           browser_id=self.browser_id, sku=self.sku, operation="点击未活跃按钮")

        # 点击 未活跃第一个元素
        safe_click_with_wait(self.page, "div.D_bvK", must_exist=True,
                           browser_id=self.browser_id, sku=self.sku, operation="点击未活跃第一个元素") 
        self.page.wait_for_timeout(2000)
        # 编辑
        safe_click_with_wait(self.page, ".D_boX:nth-child(1) > .D_mx", must_exist=True,
                           browser_id=self.browser_id, sku=self.sku, operation="点击编辑按钮")
        
    def _activate_product(self):
        """激活商品"""
        # 导航到管理页面
        self._navigate_to_manage_page()
        
        # 点击 未活跃
        safe_click_with_wait(self.page, "button.D_bwN:nth-child(2)", must_exist=True,
                           browser_id=self.browser_id, sku=self.sku, operation="点击未活跃按钮")
        
        # 点击 激活
        safe_click_with_wait(self.page, "button.D_mo", must_exist=True,
                           browser_id=self.browser_id, sku=self.sku, operation="点击激活按钮")
        
        # 点击确认激活
        safe_click_with_wait(self.page, "button.D_me", must_exist=True,
                           browser_id=self.browser_id, sku=self.sku, operation="点击确认激活按钮")
        
        self.page.wait_for_timeout(5000)
        
    # ========= 公共方法：安全点击子类目 =========
    def _safe_click_subcategory(self, selector: str, category_name: str):
        """
        安全点击子类目，处理DOM分离问题
        保持原有的重试逻辑和CSS选择器不变
        """
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                safe_click_with_wait(self.page, selector, must_exist=True,
                                   browser_id=self.browser_id, sku=self.sku, operation=f"点击{category_name}子类目")
                return True
            except Exception as e:
                logger.warning(f"第{attempt + 1}次点击{category_name}失败: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"刷新页面后重试...")
                    self.page.reload(wait_until="domcontentloaded")
                    self.page.wait_for_timeout(2000)
                else:
                    logger.error(f"多次重试后仍失败，放弃点击{category_name}")
                    raise
    
    def _wait_for_element_to_disappear(self, selector: str, timeout: int = 60000):
        """
        等待元素消失
        
        Args:
            selector: CSS选择器
            timeout: 超时时间（毫秒），默认60秒
        """
        log_prefix = f"BrowserID: {self.browser_id}, SKU: {self.sku}, " if self.browser_id and self.sku else ""
        logger.info(f"{log_prefix}等待元素消失: {selector}, 超时时间: {timeout}ms")
        
        try:
            # 等待元素消失
            self.page.wait_for_selector(selector, state="detached", timeout=timeout)
            logger.info(f"{log_prefix}元素已消失: {selector}")
            return True
        except Exception as e:
            error_msg = f"等待元素消失超时: {selector}, 超时时间: {timeout}ms"
            if self.browser_id and self.sku:
                error_msg = f"BrowserID: {self.browser_id}, SKU: {self.sku}, {error_msg}"
            error_msg += f", 失败原因: {e}"
            logger.error(error_msg)
            raise CriticalOperationFailed(error_msg)
