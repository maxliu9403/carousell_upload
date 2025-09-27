"""
增强的安全操作函数 - 支持配置文件管理和用户交互式更新
"""

import time
from typing import Optional, Tuple, List
from playwright.sync_api import Page
from browser.actions import click_with_wait, input_with_wait, human_delay, DEFAULT_TIMEOUT
from core.logger import logger
from .css_selector_manager import get_css_manager, CSSSelectorManager


class CriticalOperationFailed(Exception):
    """关键操作失败异常，需要立即停止当前流程"""
    pass


class EnhancedSafeActions:
    """增强的安全操作类 - 支持配置文件和用户交互"""
    
    def __init__(self, page: Page, browser_id: str = None, sku: str = None):
        """
        初始化增强安全操作
        
        Args:
            page: Playwright页面对象
            browser_id: 浏览器ID
            sku: 商品SKU
        """
        self.page = page
        self.browser_id = browser_id
        self.sku = sku
        self.css_manager = get_css_manager()
        self.log_prefix = f"BrowserID: {browser_id}, SKU: {sku}, " if browser_id and sku else ""
    
    def _smart_click(self, selector: str, must_exist: bool = True, timeout: int = None) -> bool:
        """
        智能点击方法，支持CSS、XPath和Playwright Locator
        """
        if timeout is None:
            timeout = DEFAULT_TIMEOUT
        
        try:
            # 判断选择器类型
            if selector.startswith("//"):
                # XPath选择器
                element = self.page.wait_for_selector(f"xpath={selector}", timeout=timeout)
            elif selector.startswith("text="):
                # Playwright Locator
                element = self.page.get_by_text(selector.replace("text=", "")).first
                element.wait_for(state="visible", timeout=timeout)
            elif ":has-text(" in selector:
                # Playwright has-text选择器
                element = self.page.locator(selector)
                element.wait_for(state="visible", timeout=timeout)
            else:
                # 普通CSS选择器
                element = self.page.wait_for_selector(selector, timeout=timeout)
            
            if element:
                element.scroll_into_view_if_needed()
                human_delay(0.5, 1.0)
                element.click()
                return True
            else:
                if must_exist:
                    raise RuntimeError(f"元素未找到: {selector}")
                return False
                
        except Exception as e:
            if must_exist:
                raise RuntimeError(f"点击失败: {selector}, 错误: {e}")
            return False
    
    def _smart_input(self, selector: str, text: str, must_exist: bool = True, timeout: int = None) -> bool:
        """
        智能输入方法，支持CSS、XPath和Playwright Locator
        """
        if timeout is None:
            timeout = DEFAULT_TIMEOUT
        
        try:
            # 判断选择器类型
            if selector.startswith("//"):
                # XPath选择器
                element = self.page.wait_for_selector(f"xpath={selector}", timeout=timeout)
            elif selector.startswith("text="):
                # Playwright Locator - 文本选择器通常用于点击，这里需要找到对应的输入框
                # 这里可能需要更复杂的逻辑来找到对应的输入框
                element = self.page.wait_for_selector("textarea, input[type='text']", timeout=timeout)
            elif ":has-text(" in selector:
                # Playwright has-text选择器
                element = self.page.locator(selector)
                element.wait_for(state="visible", timeout=timeout)
            else:
                # 普通CSS选择器
                element = self.page.wait_for_selector(selector, timeout=timeout)
            
            if element:
                element.scroll_into_view_if_needed()
                human_delay(0.5, 1.0)
                element.fill(text)
                return True
            else:
                if must_exist:
                    raise RuntimeError(f"元素未找到: {selector}")
                return False
                
        except Exception as e:
            if must_exist:
                raise RuntimeError(f"输入失败: {selector}, 错误: {e}")
            return False
    
    def _get_user_input(self, prompt: str, element_key: str, must_exist: bool = True) -> str:
        """
        获取用户输入的新CSS选择器
        
        Args:
            prompt: 提示信息
            element_key: 元素键名
            
        Returns:
            str: 用户输入的选择器
        """
        print(f"\n{'='*80}")
        print(f"🔧 CSS选择器更新请求")
        print(f"{'='*80}")
        print(f"📍 当前操作: {prompt}")
        print(f"🎯 元素键名: {element_key}")
        print(f"📋 元素描述: {self.css_manager.get_element_description(element_key)}")
        print(f"🌐 当前页面: {self.page.url}")
        print(f"📝 请使用浏览器开发者工具捕获新的CSS选择器")
        print(f"💡 提示: 右键元素 -> 检查 -> 复制选择器")
        print(f"{'='*80}")
        
        while True:
            try:
                if not must_exist:
                    print(f"⚠️ 这是非必要操作，如果当前页面没有此元素，可以选择跳过")
                    new_selector = input(f"请输入新的CSS选择器 (输入'q'退出程序, 输入'skip'跳过此操作): ").strip()
                else:
                    new_selector = input(f"请输入新的CSS选择器 (输入'q'退出程序): ").strip()
                
                if new_selector.lower() == 'q':
                    logger.info("用户选择退出程序")
                    raise KeyboardInterrupt("用户主动退出程序")
                
                if new_selector.lower() == 'skip' and not must_exist:
                    logger.info(f"用户选择跳过非必要操作: {element_key}")
                    return "SKIP"
                
                if not new_selector:
                    print("❌ 选择器不能为空，请重新输入")
                    continue
                
                # 验证选择器格式
                if not self.css_manager.validate_selector(new_selector):
                    print("⚠️ 选择器格式可能不正确，是否继续? (y/n): ", end="")
                    confirm = input().strip().lower()
                    if confirm != 'y':
                        continue
                
                print(f"✅ 已接收新选择器: {new_selector}")
                return new_selector
                
            except KeyboardInterrupt:
                logger.info("用户中断操作")
                raise
            except Exception as e:
                print(f"❌ 输入错误: {e}")
                continue
    
    def _update_selector_and_retry(self, element_key: str, operation_type: str, 
                                  operation_func, must_exist: bool = True, *args, **kwargs) -> bool:
        """
        更新选择器并重试操作
        
        Args:
            element_key: 元素键名
            operation_type: 操作类型 (click, input)
            operation_func: 操作函数
            *args, **kwargs: 操作函数参数
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 获取用户输入的新选择器
            prompt = f"{operation_type.upper()}操作失败，需要更新CSS选择器"
            new_selector = self._get_user_input(prompt, element_key, must_exist)
            
            # 如果用户选择跳过操作
            if new_selector == "SKIP":
                logger.info(f"✅ 用户跳过非必要操作: {element_key}")
                return True  # 返回True表示操作"成功"（被跳过）
            
            # 更新配置文件
            success = self.css_manager.update_selector(
                element_key, "primary", new_selector
            )
            
            if not success:
                logger.error(f"❌ 更新CSS选择器配置失败: {element_key}")
                return False
            
            logger.info(f"✅ CSS选择器已更新: {element_key} -> {new_selector}")
            
            # 使用新选择器重试操作
            logger.info(f"🔄 使用新选择器重试操作: {element_key}")
            
            # 等待页面稳定
            human_delay(1, 2)
            
            # 执行操作
            if operation_type == "click":
                result = self._smart_click(new_selector, True, DEFAULT_TIMEOUT)
            elif operation_type == "input":
                result = self._smart_input(new_selector, args[0], True, DEFAULT_TIMEOUT)
            else:
                logger.error(f"❌ 不支持的操作类型: {operation_type}")
                return False
            
            if result:
                logger.info(f"✅ 使用新选择器操作成功: {element_key}")
                return True
            else:
                logger.error(f"❌ 使用新选择器操作仍然失败: {element_key}")
                return False
                
        except KeyboardInterrupt:
            logger.info("用户中断操作")
            raise
        except Exception as e:
            logger.error(f"❌ 更新选择器并重试失败: {element_key}, 错误: {e}")
            return False
    
    def safe_click_with_config(self, element_key: str, region: str = None, 
                              must_exist: bool = True, timeout: int = None,
                              operation: str = "点击操作", max_retries: int = 1) -> bool:
        """
        基于配置文件的安全点击操作
        
        Args:
            element_key: 元素键名
            region: 地域代码
            must_exist: 是否必须存在
            timeout: 超时时间
            operation: 操作描述
            max_retries: 最大重试次数
            
        Returns:
            bool: 操作是否成功
        """
        # 设置默认超时时间
        if timeout is None:
            timeout = DEFAULT_TIMEOUT
        
        # 检查并重新加载配置
        self.css_manager.check_and_reload()
        
        # 获取选择器
        primary_selector, fallback_selector = self.css_manager.get_selector_with_fallback(
            element_key, region
        )
        
        if not primary_selector:
            logger.error(f"❌ 找不到CSS选择器配置: {element_key}")
            if must_exist:
                raise CriticalOperationFailed(f"找不到CSS选择器配置: {element_key}")
            return False
        
        element_description = self.css_manager.get_element_description(element_key)
        full_operation = f"{operation}: {element_description}"
        
        # 尝试主选择器
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(f"{self.log_prefix}第{attempt + 1}次尝试{full_operation}")
                    human_delay(1, 2)
                else:
                    logger.info(f"{self.log_prefix}正在{full_operation}: {primary_selector}")
                
                result = self._smart_click(primary_selector, must_exist, timeout)
                if result:
                    logger.info(f"{self.log_prefix}{full_operation}成功")
                    return True
                else:
                    logger.warning(f"{self.log_prefix}主选择器失败: {primary_selector}")
                    
                    # 尝试备用选择器
                    if fallback_selector and fallback_selector != primary_selector:
                        logger.info(f"{self.log_prefix}尝试备用选择器: {fallback_selector}")
                        result = self._smart_click(fallback_selector, must_exist, timeout)
                        if result:
                            logger.info(f"{self.log_prefix}{full_operation}成功 (备用选择器)")
                            return True
                        else:
                            logger.warning(f"{self.log_prefix}备用选择器也失败: {fallback_selector}")
                    
                    # 如果重试次数达到上限，请求用户输入新选择器
                    if attempt >= max_retries:
                        logger.error(f"{self.log_prefix}所有选择器都失败，请求用户更新")
                        return self._update_selector_and_retry(
                            element_key, "click", click_with_wait, 
                            must_exist, self.page, primary_selector, must_exist, timeout
                        )
                        
            except Exception as e:
                logger.warning(f"{self.log_prefix}第{attempt + 1}次尝试异常: {e}")
                
                if attempt >= max_retries:
                    logger.error(f"{self.log_prefix}操作失败，请求用户更新选择器")
                    return self._update_selector_and_retry(
                        element_key, "click", click_with_wait,
                        must_exist, self.page, primary_selector, must_exist, timeout
                    )
        
        return False
    
    def safe_input_with_config(self, element_key: str, text: str, region: str = None,
                              must_exist: bool = True, timeout: int = None,
                              operation: str = "输入操作", max_retries: int = 1) -> bool:
        """
        基于配置文件的安全输入操作
        
        Args:
            element_key: 元素键名
            text: 要输入的文本
            region: 地域代码
            must_exist: 是否必须存在
            timeout: 超时时间
            operation: 操作描述
            max_retries: 最大重试次数
            
        Returns:
            bool: 操作是否成功
        """
        # 设置默认超时时间
        if timeout is None:
            timeout = DEFAULT_TIMEOUT
        
        # 检查并重新加载配置
        self.css_manager.check_and_reload()
        
        # 获取选择器
        primary_selector, fallback_selector = self.css_manager.get_selector_with_fallback(
            element_key, region
        )
        
        if not primary_selector:
            logger.error(f"❌ 找不到CSS选择器配置: {element_key}")
            if must_exist:
                raise CriticalOperationFailed(f"找不到CSS选择器配置: {element_key}")
            return False
        
        element_description = self.css_manager.get_element_description(element_key)
        full_operation = f"{operation}: {element_description}"
        
        # 尝试主选择器
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(f"{self.log_prefix}第{attempt + 1}次尝试{full_operation}, 输入内容: '{text}'")
                    human_delay(1, 2)
                else:
                    logger.info(f"{self.log_prefix}正在{full_operation}: {primary_selector}, 输入内容: '{text}'")
                
                result = self._smart_input(primary_selector, text, must_exist, timeout)
                if result:
                    logger.info(f"{self.log_prefix}{full_operation}成功")
                    return True
                else:
                    logger.warning(f"{self.log_prefix}主选择器失败: {primary_selector}")
                    
                    # 尝试备用选择器
                    if fallback_selector and fallback_selector != primary_selector:
                        logger.info(f"{self.log_prefix}尝试备用选择器: {fallback_selector}")
                        result = self._smart_input(fallback_selector, text, must_exist, timeout)
                        if result:
                            logger.info(f"{self.log_prefix}{full_operation}成功 (备用选择器)")
                            return True
                        else:
                            logger.warning(f"{self.log_prefix}备用选择器也失败: {fallback_selector}")
                    
                    # 如果重试次数达到上限，请求用户输入新选择器
                    if attempt >= max_retries:
                        logger.error(f"{self.log_prefix}所有选择器都失败，请求用户更新")
                        return self._update_selector_and_retry(
                            element_key, "input", input_with_wait,
                            must_exist, self.page, primary_selector, text, must_exist, timeout
                        )
                        
            except Exception as e:
                logger.warning(f"{self.log_prefix}第{attempt + 1}次尝试异常: {e}")
                
                if attempt >= max_retries:
                    logger.error(f"{self.log_prefix}操作失败，请求用户更新选择器")
                    return self._update_selector_and_retry(
                        element_key, "input", input_with_wait,
                        must_exist, self.page, primary_selector, text, must_exist, timeout
                    )
        
        return False
    
    def safe_click_with_fallback_config(self, element_key: str, region: str = None,
                                       must_exist: bool = True, timeout: int = None,
                                       operation: str = "点击操作", max_retries: int = 1) -> bool:
        """
        基于配置文件的安全点击操作（带回退）
        
        Args:
            element_key: 元素键名
            region: 地域代码
            must_exist: 是否必须存在
            timeout: 超时时间
            operation: 操作描述
            max_retries: 最大重试次数
            
        Returns:
            bool: 操作是否成功
        """
        return self.safe_click_with_config(
            element_key, region, must_exist, timeout, operation, max_retries
        )
    
    def safe_input_with_fallback_config(self, element_key: str, text: str, region: str = None,
                                       must_exist: bool = True, timeout: int = None,
                                       operation: str = "输入操作", max_retries: int = 1) -> bool:
        """
        基于配置文件的安全输入操作（带回退）
        
        Args:
            element_key: 元素键名
            text: 要输入的文本
            region: 地域代码
            must_exist: 是否必须存在
            timeout: 超时时间
            operation: 操作描述
            max_retries: 最大重试次数
            
        Returns:
            bool: 操作是否成功
        """
        return self.safe_input_with_config(
            element_key, text, region, must_exist, timeout, operation, max_retries
        )


# 便捷函数
def create_enhanced_safe_actions(page: Page, browser_id: str = None, sku: str = None) -> EnhancedSafeActions:
    """创建增强安全操作实例"""
    return EnhancedSafeActions(page, browser_id, sku)
