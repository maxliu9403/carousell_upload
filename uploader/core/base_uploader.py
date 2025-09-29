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
    smart_goto,
    DEFAULT_TIMEOUT
)
from core.logger import logger
from ..utils.utils import enrich_product_info
from ..actions.enhanced_safe_actions import EnhancedSafeActions, CriticalOperationFailed, create_enhanced_safe_actions

def safe_click_with_wait(page: Page, selector: str, must_exist: bool = False, timeout: int = None, 
                        browser_id: str = None, sku: str = None, operation: str = "点击操作"):
    """安全的点击操作，must_exist=True时失败会抛出CriticalOperationFailed"""
    # 设置默认超时时间
    if timeout is None:
        timeout = DEFAULT_TIMEOUT
    
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
    # 设置默认超时时间
    if timeout is None:
        timeout = DEFAULT_TIMEOUT
    
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
    # 设置默认超时时间
    if timeout is None:
        timeout = DEFAULT_TIMEOUT
    
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
    # 设置默认超时时间
    if timeout is None:
        timeout = DEFAULT_TIMEOUT
    
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
    
    def __init__(self, page: Page, config: UploadConfig, region: str = "SG", browser_id: str = None, sku: str = None, category: str = "sneakers"):
        self.page = page
        self.config = config
        self.region = region
        self.category = category
        self.browser_id = browser_id
        self.sku = sku
        # 初始化日志前缀
        self.log_prefix = f"BrowserID: {browser_id}, SKU: {sku}, " if browser_id and sku else ""
        # 初始化增强安全操作
        self.safe_actions = create_enhanced_safe_actions(page, browser_id, sku, self.region, self.category)
        
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

        # 等待页面稳定
        self.page.wait_for_timeout(10000)

        # 发布商品
        self._publish_product()

        # 判断dialog消失 - 使用role="dialog"元素消失作为判断条件
        try:
            # 等待dialog元素消失
            dialog_element = self.page.locator('[role="dialog"]')
            
            # 检查dialog是否存在
            if dialog_element.count() > 0:
                logger.info(f"{self.log_prefix}检测到dialog元素，等待其消失...")
                # 等待dialog消失
                dialog_element.wait_for(state="hidden", timeout=30000)
                logger.info(f"{self.log_prefix}Dialog已消失，操作完成，继续执行后续流程")
            else:
                logger.info(f"{self.log_prefix}未检测到dialog元素，可能已经消失，继续执行后续流程")
                
        except Exception as e:
            logger.warning(f"{self.log_prefix}等待dialog消失时发生异常: {e}")
            # 即使出现异常，也继续执行，因为dialog可能已经消失
            logger.info(f"{self.log_prefix}继续执行后续流程")
    
    # HK逻辑
    def _closewhatsapp(self):
        """关闭WhatsApp - 简化检测版本"""
        logger.info(f"{self.log_prefix}开始检查WhatsApp弹窗")
        
        try:
            # 直接检测WhatsApp弹窗文字
            whatsapp_detected = self.page.locator("text=添加WhatsApp號碼").is_visible()
            
            if whatsapp_detected:
                logger.info(f"{self.log_prefix}检测到WhatsApp弹窗，准备关闭")
                self.safe_actions.safe_click_with_config(
                    "popups_and_settings.whatsapp_close", self.region, must_exist=True,
                    operation="关闭WhatsApp"
                )
            else:
                logger.info(f"{self.log_prefix}未检测到WhatsApp弹窗，跳过关闭操作")
                
        except Exception as e:
            logger.error(f"{self.log_prefix}检测WhatsApp弹窗异常: {e}")
            logger.info(f"{self.log_prefix}跳过WhatsApp关闭操作")
    
    # HK逻辑
    def _closemeetup(self):
        """关闭面交 - 简化检测版本"""
        logger.info(f"{self.log_prefix}开始检查面交状态")
        
        try:
            # 直接检测面交状态文字
            meetup_enabled = self.page.locator("text=添加地點").is_visible()
            
            if meetup_enabled:
                logger.info(f"{self.log_prefix}检测到面交已开启，准备关闭")
                self.safe_actions.safe_click_with_config(
                    "popups_and_settings.meetup_toggle", self.region, must_exist=True,
                    operation="关闭面交"
                )
            else:
                logger.info(f"{self.log_prefix}面交未开启，跳过关闭操作")
                
        except Exception as e:
            logger.error(f"{self.log_prefix}检测面交状态异常: {e}")
            logger.info(f"{self.log_prefix}跳见面交关闭操作")

    def _openmeetup(self):
        """开启面交"""
        logger.info(f"{self.log_prefix}开始检查面交状态")
        
        try:
            # 直接检测面交状态文字
            meetup_enabled = self.page.locator("text=添加地點").is_visible()
            
            if not meetup_enabled:
                logger.info(f"{self.log_prefix}检测到面交未开启，准备开启")
                self.safe_actions.safe_click_with_config(
                    "popups_and_settings.meetup_toggle", self.region, must_exist=True,
                    operation="开启面交"
                )
            else:
                logger.info(f"{self.log_prefix}面交已开启，跳过开启操作")
                
        except Exception as e:
            logger.error(f"{self.log_prefix}检测面交状态异常: {e}")
            logger.info(f"{self.log_prefix}跳见面交开启操作")

    def _close_delivery(self):
        """关闭送货"""
        logger.info(f"{self.log_prefix}开始检查送货状态")
        
        try:
            # 直接检测送货状态文字
            delivery_enabled = self.page.locator("text=仲有冇額外郵寄資料同埋更多選擇").is_visible()
            
            if delivery_enabled:
                logger.info(f"{self.log_prefix}检测到送货已开启，准备关闭")
                self.safe_actions.safe_click_with_config(
                    "popups_and_settings.delivery_toggle", self.region, must_exist=True,
                    operation="关闭送货"
                )
            else:
                logger.info(f"{self.log_prefix}送货未开启，跳过关闭操作")
                
        except Exception as e:
            logger.error(f"{self.log_prefix}检测送货状态异常: {e}")
            logger.info(f"{self.log_prefix}跳过送货关闭操作")

    # HK开启送货
    def _open_delivery(self):
        """开启送货 - 简化检测版本"""
        logger.info(f"{self.log_prefix}开始检查送货状态")
        
        try:
            # 直接检测送货状态 - 通过placeholder属性检测
            delivery_enabled = self.page.locator("textarea[placeholder='仲有冇額外郵寄資料同埋更多選擇']").is_visible()
            
            if not delivery_enabled:
                logger.info(f"{self.log_prefix}检测到送货未开启，准备开启")
                self.safe_actions.safe_click_with_config(
                    "popups_and_settings.delivery_toggle", self.region, must_exist=True,
                    operation="开启送货"
                )
            else:
                logger.info(f"{self.log_prefix}送货已开启，跳过开启操作")
                
        except Exception as e:
            logger.error(f"{self.log_prefix}检测送货状态异常: {e}")
            logger.info(f"{self.log_prefix}跳过送货开启操作")

    # 关闭收款
    def _close_buyer_protection(self):
        """关闭收款保障"""
        logger.info(f"{self.log_prefix}开始检查收款保障状态")
        
        try:
            # 直接检测收款保障状态文字
            buyer_protection_enabled = self.page.locator("text=所有透過「平台收款功能」成功交易的訂單將豁免所有費用").is_visible()
            
            if buyer_protection_enabled:
                logger.info(f"{self.log_prefix}检测到收款保障已开启，准备关闭")
                self.safe_actions.safe_click_with_config(
                    "popups_and_settings.buyer_protection_toggle", self.region, must_exist=True,
                    operation="关闭收款保障"
                )
                self.safe_actions.safe_click_with_config(
                    "popups_and_settings.buyer_protection_confirm", self.region, must_exist=True,
                    operation="确认关闭收款保障"
                )
            else:
                logger.info(f"{self.log_prefix}收款保障未开启，跳过关闭操作")
                
        except Exception as e:
            logger.error(f"{self.log_prefix}检测收款保障状态异常: {e}")
            logger.info(f"{self.log_prefix}跳过收款保障关闭操作")

        
    # ========= 公共方法：页面导航 =========
    def _navigate_to_homepage(self):
        """导航到主页"""
        domain = self._get_domain_by_region()
        smart_goto(self.page, domain, wait_until="domcontentloaded", timeout=20000)
        logger.info("🌐 已打开主页")
        
    def _navigate_to_manage_page(self):
        """导航到管理页面"""
        domain = self._get_domain_by_region()
        smart_goto(self.page, f"{domain}/manage-listings/", wait_until="domcontentloaded", timeout=20000)
        logger.info("🌐 已打开目标页面")
        
    # ========= 公共方法：上传流程 =========
    def _start_upload_flow(self, folder_path: str):
        """开始上传流程"""
        # 点击sell按钮
        self.safe_actions.safe_click_with_config(
            "basic_elements.sell_button", self.region, must_exist=True,
            operation="点击Sell按钮"
        )
        
        # 点击上传图片
        self.safe_actions.safe_click_with_config(
            "basic_elements.upload_images_button", self.region, must_exist=True,
            operation="点击上传图片按钮"
        )
        
        # 上传图片
        if folder_path:
            upload_folder_with_keyboard(folder_path, self.config.image_extensions)
            human_delay(2, 3)
        else:
            raise ValueError("folder_path参数不能为空")
        
        # 新账号初次上品会出现（可选）
        if self.region == "SG":
            self.safe_actions.safe_click_with_config(
                "basic_elements.new_account_popup_close", self.region, must_exist=False,
                operation="关闭新账号弹窗"
            )
        
        # 处理AI文案相关操作（使用图片匹配）
        self._handle_ai_writing_operations()

    def _select_service_category(self):
        """选择服务类目"""
        # 选择类目
        self.safe_actions.safe_click_with_config(
            "category_selection.service_category_selector", self.region, must_exist=True,
            operation="选择服务类目"
        )
        
        # 根据地域选择搜索关键词
        search_keyword = self._get_service_search_keyword()
        
        # 输入搜索关键词
        self.safe_actions.safe_input_with_config(
            "category_selection.category_search_input", search_keyword, self.region, must_exist=True,
            operation=f"输入{search_keyword}搜索服务"
        )
        
        # 等待出现搜索结果
        self.page.wait_for_timeout(2000)
        
        # 点击服务
        self.safe_actions.safe_click_with_config(
            "category_selection.service_category_option", self.region, must_exist=True,
            operation="选择服务类目选项"
        )
        
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
        self.safe_actions.safe_input_with_config(
            "product_info.title_input", enriched_info.title, self.region, must_exist=True,
            operation="输入产品标题"
        )

        if self.region == "HK":
            self.safe_actions.safe_click_with_config(
                "basic_elements.condition_new_used", self.region, must_exist=True,
                operation="点击新旧程度选择"
            )
      
        # 输入产品价格
        self.safe_actions.safe_input_with_config(
            "product_info.price_input", enriched_info.price, self.region, must_exist=True,
            operation="输入产品价格"
        )
        
        # 输入产品描述
        if self.region == "HK":
            self.safe_actions.safe_input_with_config(
                "product_info.description_input", enriched_info.description, self.region, must_exist=True,
                operation="输入产品描述")

    def _handle_ai_writing_operations(self):
        """处理AI文案相关操作 - 使用文字匹配点击"""
        logger.info(f"{self.log_prefix}开始处理AI文案相关操作")
        
        try:
            # 使用文字匹配点击 "改為手動填寫" 按钮
            self.safe_actions.safe_click_with_config(
                "basic_elements.ai_writing_cancel_button", 
                self.region, 
                must_exist=False,  # 非必需操作，如果不存在则跳过
                operation="点击AI文案取消按钮"
            )
            
            logger.info(f"{self.log_prefix}AI文案操作完成")
            
        except Exception as e:
            logger.error(f"{self.log_prefix}AI文案操作异常: {e}")
        
        logger.info(f"{self.log_prefix}AI文案操作跳过，继续执行后续流程")
        
    def _select_location_by_region(self):
        """根据地域选择Location"""
        # 点击 选择 Location
        self.safe_actions.safe_click_with_config(
            "basic_elements.location_selector", self.region, must_exist=False,
            operation="点击选择Location"
        )
        self.page.wait_for_timeout(2000)
        
        # 选择面交地点
        self.safe_actions.safe_click_with_config(
            "basic_elements.location_option", self.region, must_exist=True,
            operation="选择面交地点"
        )
        
    def _publish_product(self):
        """发布商品"""
        # 点击发布
        self.safe_actions.safe_click_with_config(
            "publishing.publish_button", self.region, must_exist=True,
            operation="点击发布按钮"
        )
        
    # ========= 公共方法：编辑模式 =========
    def _enter_edit_mode(self):
        """进入编辑模式"""
        # 点击 未活跃
        self.safe_actions.safe_click_with_config(
            "editing.inactive_tab", self.region, must_exist=True,
            operation="点击未活跃按钮"
        )

        # 点击 未活跃第一个元素
        self.safe_actions.safe_click_with_config(
            "editing.inactive_first_item", self.region, must_exist=True,
            operation="点击未活跃第一个元素"
        )
        self.page.wait_for_timeout(2000)
        
        # 编辑
        self.safe_actions.safe_click_with_config(
            "editing.edit_button", self.region, must_exist=True,
            operation="点击编辑按钮"
        )
        
    def _activate_product(self):
        """激活商品"""
        # 导航到管理页面
        self._navigate_to_manage_page()
        
        # 点击 未活跃
        self.safe_actions.safe_click_with_config(
            "editing.inactive_tab", self.region, must_exist=True,
            operation="点击未活跃按钮"
        )
        
        # 点击 激活
        self.safe_actions.safe_click_with_config(
            "editing.activate_button", self.region, must_exist=True,
            operation="点击激活按钮"
        )
        
        # 点击确认激活
        self.safe_actions.safe_click_with_config(
            "editing.confirm_activate", self.region, must_exist=True,
            operation="点击确认激活按钮"
        )
        
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
        logger.info(f"{self.log_prefix}等待元素消失: {selector}, 超时时间: {timeout}ms")
        
        try:
            # 等待元素消失
            self.page.wait_for_selector(selector, state="detached", timeout=timeout)
            logger.info(f"{self.log_prefix}元素已消失: {selector}")
            return True
        except Exception as e:
            error_msg = f"等待元素消失超时: {selector}, 超时时间: {timeout}ms"
            if self.browser_id and self.sku:
                error_msg = f"BrowserID: {self.browser_id}, SKU: {self.sku}, {error_msg}"
            error_msg += f", 失败原因: {e}"
            logger.error(error_msg)
            raise CriticalOperationFailed(error_msg)
