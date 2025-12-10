"""
基础上传器类 - 包含所有地域和类目的公共功能
保持原有的点击操作顺序和CSS选择器不变
"""
import time
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

# safe_click_with_fallback 函数已废弃 - fallback选择器逻辑已移除

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

# safe_input_with_fallback 函数已废弃 - fallback选择器逻辑已移除

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
        
        # 初始化按钮文本捕获属性
        self.sell_button_text = None
        
    def _get_button_text(self, element_key: str, allow_user_input: bool = True) -> str:
        """
        获取按钮的innerText值
        
        Args:
            element_key: 元素键名
            allow_user_input: 是否允许用户输入CSS选择器
            
        Returns:
            str: 按钮的innerText值，如果获取失败返回None
        """
        try:
            # 检查并重新加载配置（支持热更新）
            self.safe_actions.css_manager.check_and_reload()
            
            # 获取主选择器
            primary_selector = self.safe_actions.css_manager.get_selector(
                element_key, self.region, "primary", self.category
            )
            
            if not primary_selector:
                logger.warning(f"⚠️ 找不到选择器配置: {element_key}")
                return None
            
            # 尝试获取元素文本
            element_timeout = self.config.navigation_timeouts.get("element_timeout", 5000)
            try:
                if primary_selector.startswith("//"):
                    element = self.page.wait_for_selector(f"xpath={primary_selector}", timeout=element_timeout)
                elif ":has-text(" in primary_selector:
                    element = self.page.locator(primary_selector)
                    element.wait_for(state="visible", timeout=element_timeout)
                else:
                    element = self.page.wait_for_selector(primary_selector, timeout=element_timeout)
                
                if element:
                    text = element.inner_text()
                    logger.debug(f"✅ 获取到按钮文本: '{text}'")
                    return text
                    
            except Exception as e:
                logger.debug(f"选择器获取文本失败: {e}")
            
            logger.warning(f"⚠️ 无法获取按钮文本: {element_key}")
            
            # 如果允许用户输入，尝试让用户输入新的选择器
            if allow_user_input:
                logger.info(f"🔄 尝试让用户输入新的CSS选择器来获取按钮文本")
                return self._get_button_text_with_user_input(element_key)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 获取按钮文本异常: {e}")
            
            # 如果允许用户输入，尝试让用户输入新的选择器
            if allow_user_input:
                logger.info(f"🔄 尝试让用户输入新的CSS选择器来获取按钮文本")
                return self._get_button_text_with_user_input(element_key)
            
            return None
    
    def _get_button_text_with_user_input(self, element_key: str) -> str:
        """
        通过用户输入CSS选择器来获取按钮文本
        
        Args:
            element_key: 元素键名
            
        Returns:
            str: 按钮的innerText值，如果获取失败返回None
        """
        try:
            # 复用现有的用户输入逻辑
            prompt = f"获取按钮文本 - {element_key}"
            new_selector = self.safe_actions._get_user_input(prompt, element_key, must_exist=False, region=self.region)
            
            if new_selector == "SKIP":
                logger.info("用户选择跳过获取按钮文本")
                return None
            
            if not new_selector or new_selector == "SKIP":
                return None
            
            # 使用用户输入的选择器尝试获取文本
            logger.info(f"🔄 使用用户输入的选择器尝试获取按钮文本: {new_selector}")
            
            element_timeout = self.config.navigation_timeouts.get("element_timeout", 5000)
            try:
                # 判断选择器类型并获取元素
                if new_selector.startswith("//"):
                    element = self.page.wait_for_selector(f"xpath={new_selector}", timeout=element_timeout)
                elif ":has-text(" in new_selector:
                    element = self.page.locator(new_selector)
                    element.wait_for(state="visible", timeout=element_timeout)
                else:
                    element = self.page.wait_for_selector(new_selector, timeout=element_timeout)
                
                if element:
                    text = element.inner_text()
                    logger.info(f"✅ 使用用户选择器成功获取按钮文本: '{text}'")
                    return text
                else:
                    logger.warning("⚠️ 用户选择器未找到元素")
                    return None
                    
            except Exception as e:
                logger.warning(f"⚠️ 用户选择器获取文本失败: {e}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 用户输入获取按钮文本异常: {e}")
            return None
        
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

        # 发布商品并检测dialog
        # self._publish_product_with_dialog_detection()
        # 判断dialog消失 - 使用role="dialog"元素消失作为判断条件
        try:
            # 等待dialog元素消失
            dialog_element = self.page.locator('[role="dialog"]')
            
            # 检查dialog是否存在
            if dialog_element.count() > 0:
                logger.info(f"{self.log_prefix}检测到dialog元素，等待其消失...")
                # 等待dialog消失
                dialog_timeout = self.config.navigation_timeouts.get("dialog_timeout", 30000)
                dialog_element.wait_for(state="hidden", timeout=dialog_timeout)
                logger.info(f"{self.log_prefix}Dialog已消失，操作完成，继续执行后续流程")
            else:
                logger.info(f"{self.log_prefix}未检测到dialog元素，可能已经消失，继续执行后续流程")
                
        except Exception as e:
            logger.warning(f"{self.log_prefix}等待dialog消失时发生异常: {e}")
            # 即使出现异常，也继续执行，因为dialog可能已经消失
            logger.info(f"{self.log_prefix}继续执行后续流程")
            
            
        # 等待页面加载结束（从配置读取超时时间）
        network_idle_timeout = self.config.navigation_timeouts.get("network_idle_timeout", 5000)
        try:
            self.page.wait_for_load_state("networkidle", timeout=network_idle_timeout)
            logger.info(f"{self.log_prefix}✅ 页面网络活动已结束")
        except Exception as e:
            logger.warning(f"{self.log_prefix}⚠️ 等待页面网络活动结束超时: {e}")
            # 即使超时也继续执行，因为dialog已经消失，操作基本完成
            logger.info(f"{self.log_prefix}✅ 继续执行后续流程")
    
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
            meetup_enabled = (self.page.locator("text=添加地點").is_visible() or 
                            self.page.locator("text=Add location").is_visible())
            
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

    def _openmeetup(self, enriched_info=None):
        """开启面交"""
        logger.info(f"{self.log_prefix}开始检查面交状态")
        
        try:
            # 检测面交状态文字（支持中英文）
            meetup_enabled = (self.page.locator("text=添加地點").is_visible() or 
                             self.page.locator("text=Add location").is_visible())
            
            if not meetup_enabled:
                logger.info(f"{self.log_prefix}检测到面交未开启，准备开启")
                self.safe_actions.safe_click_with_config(
                    "popups_and_settings.meetup_toggle", self.region, must_exist=True,
                    operation="开启面交"
                )
                if enriched_info and hasattr(enriched_info, 'meetup_location'):
                    self.safe_actions.safe_input_with_config(
                        "popups_and_settings.meetup_input", enriched_info.meetup_location, self.region, must_exist=True,
                        operation="输入面交地点"
                    )
                else:
                    logger.warning(f"{self.log_prefix}未提供面交地点信息，跳过输入操作")

                self.safe_actions.safe_click_with_config(
                    "popups_and_settings.meetup_option", self.region, must_exist=True,
                    operation="选择面交地点"
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
            # 检测送货状态文字（支持中英文）
            delivery_enabled = (self.page.locator("text=仲有冇額外郵寄資料同埋更多選擇").is_visible() or 
                               self.page.locator("text=Carousell Official Delivery").is_visible())
            
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
            # 检测收款保障状态文字（支持中英文）
            buyer_protection_enabled = (self.page.locator("text=所有透過「平台收款功能」成功交易的訂單將豁免所有費用").is_visible() or 
                                       self.page.locator("text=We're waiving the platform fee for a limited time！").is_visible())
            
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
        timeout = self.config.navigation_timeouts.get("homepage_timeout", 120000)
        smart_goto(self.page, domain, wait_until="domcontentloaded", timeout=timeout)
        logger.info("🌐 已打开主页")
        
    def _navigate_to_manage_page(self):
        """导航到管理页面"""
        domain = self._get_domain_by_region()
        timeout = self.config.navigation_timeouts.get("manage_page_timeout", 30000)
        smart_goto(self.page, f"{domain}/manage-listings/", wait_until="domcontentloaded", timeout=timeout)
        logger.info("🌐 已打开目标页面")
    
    def _navigate_to_upload_page(self):
        """导航到上传图片页面"""
        domain = self._get_domain_by_region()
        timeout = self.config.navigation_timeouts.get("upload_page_timeout", 30000)
        smart_goto(self.page, f"{domain}/sell?source=nav_bar", wait_until="domcontentloaded", timeout=timeout)
        logger.info("🌐 已打开目标页面")
        
    # ========= 公共方法：上传流程 =========
    def _start_upload_flow(self, folder_path: str):
        """开始上传流程"""

        # 获取按钮文本并保存到self中，支持默认值
        self.sell_button_text = self._get_button_text("basic_elements.sell_button")
        if not self.sell_button_text:
            # 根据地区设置默认按钮文本
            self.sell_button_text = "賣嘢" if self.region == "HK" else "Sell"
            logger.warning(f"⚠️ 未能获取到Sell按钮文本，使用默认值: '{self.sell_button_text}'")
        else:
            logger.info(f"✅ 已获取Sell按钮文本: '{self.sell_button_text}'")

    
        self._navigate_to_upload_page()

        # 等待页面加载（从配置读取超时时间，默认10秒）
        page_load_timeout = self.config.navigation_timeouts.get("page_load_timeout", 10000)
        try:
            logger.info(f"{self.log_prefix}等待页面加载完成（最多{page_load_timeout/1000:.0f}秒）...")
            self.page.wait_for_load_state("domcontentloaded", timeout=page_load_timeout)
            logger.info(f"{self.log_prefix}页面加载完成")
        except Exception as e:
            logger.warning(f"{self.log_prefix}页面加载等待超时，继续执行: {e}")
        
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
            # 连续点击两次关闭按钮（某些环境下需要连续点击才能关闭）
            for click_num in range(2):
                self.safe_actions.safe_click_with_config(
                    "basic_elements.new_account_popup_close", self.region, must_exist=False,
                    operation=f"关闭新账号弹窗（第{click_num + 1}次点击）"
                )
                # 两次点击之间稍作等待
                if click_num == 0:
                    self.page.wait_for_timeout(1000)  # 等待1秒
        
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
        根据按钮文本或地域获取服务类目搜索关键词
        
        Returns:
            str: 搜索关键词
        """
        # 优先根据按钮文本判断语言
        if self.sell_button_text == "賣嘢":
            keyword = "其他"
        elif self.sell_button_text == "Sell":
            keyword = "others"
        else:
            # 备用方案：根据地区判断
            keyword = "其他" if self.region == "HK" else "others"
        
        logger.info(f"使用服务搜索关键词: '{keyword}' (按钮文本: '{self.sell_button_text}', 地区: {self.region})")
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
                "sneakers_specific.condition_selector", self.region, must_exist=True,
                operation="点击新旧程度选择"
            )
      
        # 输入产品价格
        self.safe_actions.safe_input_with_config(
            "product_info.price_input", enriched_info.price, self.region, must_exist=True,
            operation="输入产品价格"
        )
        
        # 输入产品描述
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
            "basic_elements.location_selector", self.region, must_exist=True,
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
    
    def _publish_product_with_dialog_detection(self):
        """发布商品并检测dialog，支持重试机制"""
        max_retries = 3
        
        for attempt in range(max_retries):
            logger.info(f"{self.log_prefix}🔄 第 {attempt + 1}/{max_retries} 次尝试发布商品")
            
            try:
                # 发布商品
                self._publish_product()
                                
                # 检测dialog是否存在
                dialog_element = self.page.locator('[role="dialog"]')
                dialog_count = dialog_element.count()
                
                if dialog_count > 0:
                    logger.info(f"{self.log_prefix}✅ 检测到dialog元素，等待其消失...")
                    # 等待dialog消失
                    dialog_timeout = self.config.navigation_timeouts.get("dialog_timeout", 30000)
                    dialog_element.wait_for(state="hidden", timeout=dialog_timeout)
                    logger.info(f"{self.log_prefix}✅ Dialog已消失，操作完成，继续执行后续流程")
                    return True
                else:
                    logger.warning(f"{self.log_prefix}⚠️ 第 {attempt + 1} 次尝试未检测到dialog元素")
                    
                if attempt < max_retries - 1:
                    logger.info(f"{self.log_prefix}🔄 准备重试发布商品...")
                    # 继续循环，下次会再次执行 _publish_product()
                else:
                    # 最后一次重试失败
                    error_msg = f"经过 {max_retries} 次重试后仍未检测到dialog元素，发布可能失败"
                    if self.browser_id and self.sku:
                        error_msg = f"BrowserID: {self.browser_id}, SKU: {self.sku}, {error_msg}"
                    logger.error(error_msg)
                    raise CriticalOperationFailed(error_msg)
                        
            except Exception as e:
                logger.warning(f"{self.log_prefix}⚠️ 第 {attempt + 1} 次尝试发布商品时发生异常: {e}")
                
                if attempt < max_retries - 1:
                    logger.info(f"{self.log_prefix}🔄 准备重试发布商品...")
                    # 继续循环，下次会再次执行 _publish_product()
                else:
                    # 最后一次重试失败
                    error_msg = f"经过 {max_retries} 次重试后发布商品失败: {e}"
                    if self.browser_id and self.sku:
                        error_msg = f"BrowserID: {self.browser_id}, SKU: {self.sku}, {error_msg}"
                    logger.error(error_msg)
                    raise CriticalOperationFailed(error_msg)
        
        # 如果所有重试都失败，抛出异常（这行代码不应该被执行到，因为成功时会return True）
        error_msg = f"经过 {max_retries} 次重试后发布商品失败"
        if self.browser_id and self.sku:
            error_msg = f"BrowserID: {self.browser_id}, SKU: {self.sku}, {error_msg}"
        raise CriticalOperationFailed(error_msg)
        
    # ========= 公共方法：编辑模式 =========
    def _enter_edit_mode(self):
        """进入编辑模式"""

        # 点击成功跳服务的产品
        self.safe_actions.safe_click_with_config(
            "editing.inactive_image", self.region, must_exist=True,
            operation="点击成功跳服务的产品"
        )

        self.page.wait_for_timeout(2000)
        
        # 编辑
        self.safe_actions.safe_click_with_config(
            "editing.edit_button", self.region, must_exist=True,
            operation="点击编辑按钮"
        )
        
    def _wait_for_page_load_and_enter_edit(self):
        """
        等待当前页面加载结束，然后直接进入编辑模式
        优化：不重新导航，直接等待页面稳定后点击编辑按钮
        """
        logger.info(f"{self.log_prefix}⏳ 等待页面加载并进入编辑模式")
        
        try:
            # 等待页面稳定
            self._wait_for_page_stability()
            
            # 进入编辑模式
            self._enter_edit_mode_directly()
            
            logger.info(f"{self.log_prefix}✅ 页面加载并进入编辑模式完成")
            
        except Exception as e:
            logger.error(f"{self.log_prefix}❌ 进入编辑模式失败")
            raise RuntimeError(f"进入编辑模式失败")

    def _enter_edit_mode_directly(self):
        """直接进入编辑模式"""
        logger.info(f"{self.log_prefix}🚀 直接进入编辑模式")
        self._enter_edit_mode()

    def _wait_for_page_stability(self, timeout: int = 10000):
        """
        等待页面稳定 - 简化版本
        
        Args:
            timeout: 超时时间（毫秒）
        """
        logger.info(f"{self.log_prefix}⏳ 等待页面稳定...")
        
        try:
            # 只等待DOM内容加载完成，这是最重要的
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
            logger.info(f"{self.log_prefix}✅ 页面已稳定")
            
        except Exception as e:
            logger.warning(f"{self.log_prefix}⚠️ 页面稳定等待超时: {e}")
            # 即使超时也继续执行，但记录警告
            self.page.wait_for_timeout(500)  # 至少等待0.5秒

    def _click_inactive_product(self):
        """点击未激活的商品"""
        logger.info(f"{self.log_prefix}🎯 点击未激活的商品")
        self.safe_actions.safe_click_with_config(
            "editing.inactive_image", self.region, must_exist=True,
            operation="点击成功跳服务的产品"
        )
        self.page.wait_for_timeout(2000)

    def _click_activate_button(self):
        """点击激活按钮并等待激活完成"""
        logger.info(f"{self.log_prefix}🚀 点击激活按钮")
        
        # 获取按钮选择器
        button_selector = self.safe_actions.get_selector("editing.activate_button", self.region)
        
        # 点击前先获取按钮的初始文字
        try:
            element = self.page.query_selector(button_selector)
            if element:
                initial_text = element.text_content().strip()
                logger.info(f"{self.log_prefix}📝 按钮初始文字: '{initial_text}'")
            else:
                initial_text = None
                logger.warning(f"{self.log_prefix}⚠️ 无法获取按钮初始文字")
        except Exception as e:
            initial_text = None
            logger.warning(f"{self.log_prefix}⚠️ 获取按钮初始文字失败: {e}")
        
        # 点击激活按钮
        self.safe_actions.safe_click_with_config(
            "editing.activate_button", self.region, must_exist=True,
            operation="点击激活商品"
        )
        
        # 立即等待激活完成（按钮文字变化）
        logger.info(f"{self.log_prefix}⏳ 等待激活完成...")
        activation_timeout = self.config.navigation_timeouts.get("activation_timeout", 15000)
        self._wait_for_activation_complete(button_selector, initial_text, timeout=activation_timeout)
        logger.info(f"{self.log_prefix}✅ 商品激活完成")

    def _activate_product(self):
        """激活商品 - 主流程"""
        logger.info(f"{self.log_prefix}开始激活商品流程")
        
        try:
            # 等待页面稳定
            self._wait_for_page_stability()
            
            # 点击未激活的商品
            # self._click_inactive_product()
            
            # 点击激活按钮（已包含等待激活完成逻辑）
            self._click_activate_button()
            
            logger.info(f"{self.log_prefix}✅ 激活商品流程完成")
            
        except Exception as e:
            logger.error(f"{self.log_prefix}❌ 激活商品失败: {e}")
            raise RuntimeError(f"激活商品失败: {e}")     
        
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
    
    def _wait_for_activation_complete(self, selector: str = "button[innerText='Mark as active']", initial_text: str = None, timeout: int = 60000):
        """
        等待激活完成，通过监控按钮文字变化
        
        Args:
            selector: 按钮CSS选择器，默认查找 "Mark as active" 按钮
            initial_text: 按钮初始文字，如果提供则等待文字从初始文字改变
            timeout: 超时时间（毫秒），默认60秒
        """
        logger.info(f"{self.log_prefix}等待激活完成: {selector}, 初始文字: {initial_text}, 超时时间: {timeout}ms")
        
        start_time = time.time()
        last_text = ""
        
        while (time.time() - start_time) * 1000 < timeout:
            try:
                # 检查按钮是否存在
                element = self.page.query_selector(selector)
                if not element:
                    logger.info(f"{self.log_prefix}激活按钮已消失，激活可能完成")
                    return True
                
                # 获取当前按钮文字
                current_text = element.text_content().strip() if element else ""
                
                # 如果文字发生变化，记录日志
                if current_text != last_text:
                    logger.info(f"{self.log_prefix}按钮文字变化: '{last_text}' -> '{current_text}'")
                    last_text = current_text
                
                # 如果提供了初始文字，检查是否已从初始文字改变
                if initial_text and current_text != initial_text:
                    logger.info(f"{self.log_prefix}激活完成，按钮文字已从初始文字改变: '{initial_text}' -> '{current_text}'")
                    return True
                
                # 如果没有提供初始文字，使用默认逻辑（按钮文字不再是 "Mark as active"）
                if not initial_text and current_text and current_text != "Mark as active":
                    logger.info(f"{self.log_prefix}激活完成，按钮文字变为: '{current_text}'")
                    return True
                
                # 检查是否按钮变为不可用状态（表示激活完成）
                if element.is_disabled():
                    logger.info(f"{self.log_prefix}按钮变为禁用状态，激活完成")
                    return True
                
                # 等待一段时间后再次检查
                self.page.wait_for_timeout(1000)
                
            except Exception as e:
                logger.warning(f"{self.log_prefix}检查激活状态时出错: {e}")
                self.page.wait_for_timeout(1000)
        
        # 超时处理
        try:
            element = self.page.query_selector(selector)
            if element:
                current_text = element.text_content().strip() if element else ""
                error_msg = f"等待激活完成超时: {selector}, 当前文字: '{current_text}', 超时时间: {timeout}ms"
            else:
                error_msg = f"等待激活完成超时: {selector}, 按钮已消失, 超时时间: {timeout}ms"
        except Exception as e:
            error_msg = f"等待激活完成超时: {selector}, 超时时间: {timeout}ms, 错误: {e}"
        
        if self.browser_id and self.sku:
            error_msg = f"BrowserID: {self.browser_id}, SKU: {self.sku}, {error_msg}"
        
        logger.error(error_msg)
        raise CriticalOperationFailed(error_msg)
    
    def _wait_for_button_text_change(self, selector: str, initial_text: str = None, expected_texts: list = None, timeout: int = 60000):
        """
        等待按钮文字变化
        
        Args:
            selector: 按钮CSS选择器
            initial_text: 初始文字，如果提供则等待文字从初始文字改变
            expected_texts: 期望的文字列表，如果提供则等待文字变为期望文字之一
            timeout: 超时时间（毫秒），默认60秒
        """
        logger.info(f"{self.log_prefix}等待按钮文字变化: {selector}, 初始文字: {initial_text}, 期望文字: {expected_texts}, 超时时间: {timeout}ms")
        
        start_time = time.time()
        last_text = ""
        
        while (time.time() - start_time) * 1000 < timeout:
            try:
                # 检查按钮是否存在
                element = self.page.query_selector(selector)
                if not element:
                    logger.info(f"{self.log_prefix}按钮已消失: {selector}")
                    return True
                
                # 获取当前按钮文字
                current_text = element.text_content().strip() if element else ""
                
                # 如果文字发生变化，记录日志
                if current_text != last_text:
                    logger.info(f"{self.log_prefix}按钮文字变化: '{last_text}' -> '{current_text}'")
                    last_text = current_text
                
                # 如果提供了初始文字，检查是否已从初始文字改变
                if initial_text and current_text != initial_text:
                    logger.info(f"{self.log_prefix}按钮文字已从初始文字改变: '{initial_text}' -> '{current_text}'")
                    return True
                
                # 如果提供了期望文字，检查是否达到期望文字
                if expected_texts and current_text in expected_texts:
                    logger.info(f"{self.log_prefix}按钮文字已达到期望文字: '{current_text}'")
                    return True
                
                # 等待一段时间后再次检查
                self.page.wait_for_timeout(1000)
                
            except Exception as e:
                logger.warning(f"{self.log_prefix}检查按钮文字变化时出错: {e}")
                self.page.wait_for_timeout(1000)
        
        # 超时处理
        try:
            element = self.page.query_selector(selector)
            if element:
                current_text = element.text_content().strip() if element else ""
                error_msg = f"等待按钮文字变化超时: {selector}, 当前文字: '{current_text}', 初始文字: {initial_text}, 期望文字: {expected_texts}, 超时时间: {timeout}ms"
            else:
                error_msg = f"等待按钮文字变化超时: {selector}, 按钮已消失, 超时时间: {timeout}ms"
        except Exception as e:
            error_msg = f"等待按钮文字变化超时: {selector}, 超时时间: {timeout}ms, 错误: {e}"
        
        if self.browser_id and self.sku:
            error_msg = f"BrowserID: {self.browser_id}, SKU: {self.sku}, {error_msg}"
        
        logger.error(error_msg)
        raise CriticalOperationFailed(error_msg)
    
    def _wait_for_element_visible(self, selector: str, timeout: int = 30000):
        """
        等待元素可见
        
        Args:
            selector: CSS选择器
            timeout: 超时时间（毫秒），默认30秒
        """
        logger.info(f"{self.log_prefix}等待元素可见: {selector}, 超时时间: {timeout}ms")
        
        try:
            # 等待元素可见
            self.page.wait_for_selector(selector, state="visible", timeout=timeout)
            logger.info(f"{self.log_prefix}元素已可见: {selector}")
            return True
        except Exception as e:
            error_msg = f"等待元素可见超时: {selector}, 超时时间: {timeout}ms"
            if self.browser_id and self.sku:
                error_msg = f"BrowserID: {self.browser_id}, SKU: {self.sku}, {error_msg}"
            error_msg += f", 失败原因: {e}"
            logger.error(error_msg)
            raise CriticalOperationFailed(error_msg)
    
    def _wait_for_element_clickable(self, selector: str, timeout: int = 30000):
        """
        等待元素可点击
        
        Args:
            selector: CSS选择器
            timeout: 超时时间（毫秒），默认30秒
        """
        logger.info(f"{self.log_prefix}等待元素可点击: {selector}, 超时时间: {timeout}ms")
        
        try:
            # 等待元素可见且可点击
            self.page.wait_for_selector(selector, state="visible", timeout=timeout)
            
            # 额外检查元素是否可点击
            self.page.wait_for_function(
                """
                el => {
                    const rect = el.getBoundingClientRect();
                    const style = window.getComputedStyle(el);
                    return rect.width > 0 && rect.height > 0 && 
                           style.visibility !== 'hidden' && 
                           style.display !== 'none' &&
                           !el.disabled;
                }
                """,
                arg=self.page.locator(selector),
                timeout=timeout
            )
            
            logger.info(f"{self.log_prefix}元素已可点击: {selector}")
            return True
        except Exception as e:
            error_msg = f"等待元素可点击超时: {selector}, 超时时间: {timeout}ms"
            if self.browser_id and self.sku:
                error_msg = f"BrowserID: {self.browser_id}, SKU: {self.sku}, {error_msg}"
            error_msg += f", 失败原因: {e}"
            logger.error(error_msg)
            raise CriticalOperationFailed(error_msg)
    
    def _wait_for_text_content(self, selector: str, expected_text: str, timeout: int = 30000):
        """
        等待元素包含指定文本
        
        Args:
            selector: CSS选择器
            expected_text: 期望的文本内容
            timeout: 超时时间（毫秒），默认30秒
        """
        logger.info(f"{self.log_prefix}等待文本内容: {selector} -> '{expected_text}', 超时时间: {timeout}ms")
        
        try:
            # 等待元素包含指定文本
            self.page.wait_for_function(
                f"""
                el => {{
                    const text = el.textContent || el.innerText || '';
                    return text.includes('{expected_text}');
                }}
                """,
                arg=self.page.locator(selector),
                timeout=timeout
            )
            
            logger.info(f"{self.log_prefix}文本内容已匹配: {selector} -> '{expected_text}'")
            return True
        except Exception as e:
            error_msg = f"等待文本内容超时: {selector} -> '{expected_text}', 超时时间: {timeout}ms"
            if self.browser_id and self.sku:
                error_msg = f"BrowserID: {self.browser_id}, SKU: {self.sku}, {error_msg}"
            error_msg += f", 失败原因: {e}"
            logger.error(error_msg)
            raise CriticalOperationFailed(error_msg)
    
    def _wait_for_url_change(self, current_url: str, timeout: int = 30000):
        """
        等待URL变化
        
        Args:
            current_url: 当前URL
            timeout: 超时时间（毫秒），默认30秒
        """
        logger.info(f"{self.log_prefix}等待URL变化: {current_url}, 超时时间: {timeout}ms")
        
        try:
            # 等待URL变化
            self.page.wait_for_function(
                f"""
                () => {{
                    return window.location.href !== '{current_url}';
                }}
                """,
                timeout=timeout
            )
            
            new_url = self.page.url
            logger.info(f"{self.log_prefix}URL已变化: {current_url} -> {new_url}")
            return new_url
        except Exception as e:
            error_msg = f"等待URL变化超时: {current_url}, 超时时间: {timeout}ms"
            if self.browser_id and self.sku:
                error_msg = f"BrowserID: {self.browser_id}, SKU: {self.sku}, {error_msg}"
            error_msg += f", 失败原因: {e}"
            logger.error(error_msg)
            raise CriticalOperationFailed(error_msg)
