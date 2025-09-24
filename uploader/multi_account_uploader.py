from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime
from playwright.sync_api import Page  # pyright: ignore[reportMissingImports]
from core.models import ProductInfo, UploadConfig
from .carousell_uploader_new import CarousellUploader
from .base_uploader import CriticalOperationFailed
from browser.browser import start_browser, get_profile_id_by_browser_id, fetch_all_browser_windows, close_browser_by_profile_id
from data.excel_parser import ExcelProductParser
from core.logger import logger
from data.record_manager import SuccessRecordManager

class MultiAccountUploader:
    """多账号串行上传器"""
    
    def __init__(self, config: UploadConfig, excel_path: str, region: str, category: str = "sneakers"):
        self.config = config
        self.excel_path = excel_path
        self.region = region
        self.category = category
        self.parser = ExcelProductParser(excel_path)
        self.record_manager = SuccessRecordManager()
    
    def run_upload_cycle(self) -> Dict[str, Any]:
        """
        执行完整的上传循环
        
        Returns:
            Dict[str, Any]: 上传结果统计
        """
        try:
            logger.info(f"开始执行多账号上传，地域: {self.region}")
            
            # 1. 解析 Excel 文件
            products_data = self.parser.parse_products(self.region)
            if not products_data:
                logger.warning("没有找到可上传的商品")
                return {
                    "success": False, 
                    "message": "没有找到可上传的商品",
                    "total_accounts": 0,
                    "total_products": 0,
                    "success_count": 0,
                    "failed_count": 0,
                    "success_rate": 0.0,
                    "account_details": []
                }
            
            # 2. 获取已成功的商品SKU，跳过已完成的商品
            successful_products = self._get_successful_products(products_data)
            logger.info(f"已成功的商品SKU: {sorted(successful_products)}")
            
            # 3. 过滤掉已成功的商品，只保留需要处理的商品
            filtered_products_data = self._filter_products_by_sku(products_data, successful_products)
            if not filtered_products_data:
                logger.info("所有商品都已成功上传，无需继续处理")
                # 返回完整的结果结构，避免KeyError
                return {
                    "success": True, 
                    "message": "所有商品都已成功上传",
                    "total_accounts": 0,
                    "total_products": len(products_data),
                    "success_count": len(products_data),
                    "failed_count": 0,
                    "success_rate": 100.0,
                    "account_details": []
                }
            
            # 4. 获取需要的BrowserID列表
            needed_browser_ids = set(product['browser_id'] for product in filtered_products_data)
            logger.info(f"需要处理的BrowserID: {sorted(needed_browser_ids)}")
            
            # 5. 只获取需要的浏览器窗口数据
            browser_windows = self._fetch_needed_browser_windows(needed_browser_ids)
            
            # 6. 严格按照Excel顺序执行商品上传
            results = self._upload_products_sequentially(filtered_products_data, browser_windows)
            
            # 7. 统计结果
            return self._generate_summary(results)
            
        except Exception as e:
            logger.error(f"多账号上传失败: {e}")
            return {
                "success": False, 
                "message": str(e),
                "total_accounts": 0,
                "total_products": 0,
                "success_count": 0,
                "failed_count": 0,
                "success_rate": 0.0,
                "account_details": []
            }
    
    def _get_successful_products(self, products_data: List[Dict[str, Any]]) -> set:
        """获取所有已成功的商品SKU"""
        successful_skus = set()
        
        for product in products_data:
            browser_id = product['browser_id']
            sku = product['sku']
            
            # 检查该商品是否已成功
            if self.record_manager.is_product_successful(self.excel_path, self.region, browser_id, sku):
                successful_skus.add(sku)
        
        return successful_skus
    
    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _filter_products_by_sku(self, products_data: List[Dict[str, Any]], successful_skus: set) -> List[Dict[str, Any]]:
        """过滤掉已成功的商品SKU，保持Excel顺序"""
        filtered_products = []
        skipped_count = 0
        
        for product in products_data:
            sku = product['sku']
            if sku in successful_skus:
                skipped_count += 1
                logger.info(f"跳过已成功的商品: {sku}")
                continue
            filtered_products.append(product)
        
        logger.info(f"商品过滤完成: 原始 {len(products_data)} 个，过滤后 {len(filtered_products)} 个，跳过 {skipped_count} 个")
        return filtered_products
    
    def _fetch_needed_browser_windows(self, needed_browser_ids: set) -> Dict[int, Dict[str, str]]:
        """只获取需要的浏览器窗口数据"""
        if not needed_browser_ids:
            return {}
        
        logger.info(f"正在获取 {len(needed_browser_ids)} 个BrowserID的窗口数据...")
        
        # 获取所有浏览器窗口
        all_browser_windows = fetch_all_browser_windows(self.config.api_port, self.config.api_key)
        
        # 只保留需要的BrowserID
        needed_browser_windows = {}
        for browser_id in needed_browser_ids:
            browser_id_int = int(browser_id)
            if browser_id_int in all_browser_windows:
                needed_browser_windows[browser_id_int] = all_browser_windows[browser_id_int]
            else:
                logger.warning(f"BrowserID {browser_id} 在浏览器窗口中未找到")
        
        logger.info(f"成功获取 {len(needed_browser_windows)} 个BrowserID的窗口数据")
        return needed_browser_windows
    
    def _upload_products_sequentially(self, products_data: List[Dict[str, Any]], browser_windows: Dict[int, Dict[str, str]]) -> List[Dict[str, Any]]:
        """严格按照Excel顺序执行商品上传"""
        results = []
        current_browser_id = None
        current_uploader = None
        current_browser = None
        current_playwright = None
        current_profile_id = None
        
        logger.info(f"开始按Excel顺序执行 {len(products_data)} 个商品的上传")
        
        for i, product_data in enumerate(products_data, 1):
            browser_id = product_data['browser_id']
            sku = product_data['sku']
            
            logger.info(f"[{i}/{len(products_data)}] 处理商品: {sku} (BrowserID: {browser_id})")
            
            # 启动浏览器（每个产品都需要启动新的浏览器）
            try:
                profile_id = get_profile_id_by_browser_id(
                    self.config.api_port, 
                    self.config.api_key, 
                    browser_id,
                    browser_windows
                )
                logger.info(f"启动浏览器 {browser_id} (profile_id: {profile_id})")
                
                current_playwright, current_browser, page = start_browser(
                    self.config.api_port,
                    self.config.api_key,
                    profile_id
                )
                
                current_uploader = CarousellUploader(page, self.config, self.region, browser_id, sku)
                current_browser_id = browser_id
                current_profile_id = profile_id
                
            except Exception as e:
                logger.error(f"启动浏览器 {browser_id} 失败: {e}")
                # 记录失败结果
                results.append({
                    'browser_id': browser_id,
                    'sku': sku,
                    'success': False,
                    'error': str(e)
                })
                continue
            
            # 执行商品上传
            try:
                logger.info(f"上传商品: {sku} - {product_data.get('product_name_cn', '')}")
                
                # 创建 ProductInfo 对象
                product_info = self.parser.create_product_info(product_data)
                
                # 执行上传
                folder_path = product_data['folder'] if product_data['folder'] else None
                success = current_uploader.upload_product(product_info, folder_path, self.category)
                
                if success:
                    logger.info(f"✅ 商品 {sku} 上传成功")
                    
                    # 立即记录成功
                    self.record_manager.record_success(
                        self.excel_path,
                        self.region,
                        browser_id,
                        sku
                    )
                    
                    # 输出美化的截断日志
                    logger.info("🎊" + "=" * 58 + "🎊")
                    logger.info("🎉 商品处理完成 - 详细信息 🎉")
                    logger.info("📍 所在地域: " + f"{self.region}")
                    logger.info("🌐 浏览器ID: " + f"{browser_id}")
                    logger.info("📦 商品SKU: " + f"{sku}")
                    logger.info("✅ 处理状态: 成功")
                    logger.info("⏰ 完成时间: " + f"{self._get_current_time()}")
                    logger.info("🎊" + "=" * 58 + "🎊")
                    
                    results.append({
                        'browser_id': browser_id,
                        'sku': sku,
                        'success': True,
                        'error': None
                    })
                else:

                    # 输出美化的截断日志（失败情况）
                    logger.error("💥" + "=" * 50 + "💥")
                    logger.error("❌ 商品处理失败 - 详细信息 ❌")
                    logger.error("📍 所在地域: " + f"{self.region}")
                    logger.error("🌐 浏览器ID: " + f"{browser_id}")
                    logger.error("📦 商品SKU: " + f"{sku}")
                    logger.error("❌ 处理状态: 失败")
                    logger.error("⏰ 失败时间: " + f"{self._get_current_time()}")
                    logger.error("💥" + "=" * 50 + "💥")
                    
                    results.append({
                        'browser_id': browser_id,
                        'sku': sku,
                        'success': False,
                        'error': '上传失败'
                    })
                
            except CriticalOperationFailed as e:
                logger.error(f"🚨 关键操作失败，立即停止当前商品流程: {sku} - {e}")
                
                # 输出美化的截断日志（关键操作失败）
                logger.error("🚨" + "=" * 50 + "🚨")
                logger.error("🚨 关键操作失败 - 详细信息 🚨")
                logger.error("📍 所在地域: " + f"{self.region}")
                logger.error("🌐 浏览器ID: " + f"{browser_id}")
                logger.error("📦 商品SKU: " + f"{sku}")
                logger.error("🚨 处理状态: 关键操作失败")
                logger.error("❌ 失败原因: " + f"{e}")
                logger.error("⏰ 失败时间: " + f"{self._get_current_time()}")
                logger.error("🚨" + "=" * 50 + "🚨")
                
                results.append({
                    'browser_id': browser_id,
                    'sku': sku,
                    'success': False,
                    'error': f"关键操作失败: {e}"
                })
                # 关键操作失败，需要立即关闭浏览器并继续下一个商品
                
            except Exception as e:
                logger.error(f"上传商品 {sku} 时出错: {e}")
                
                # 输出美化的截断日志（普通异常）
                logger.error("💥" + "=" * 50 + "💥")
                logger.error("💥 异常处理失败 - 详细信息 💥")
                logger.error("📍 所在地域: " + f"{self.region}")
                logger.error("🌐 浏览器ID: " + f"{browser_id}")
                logger.error("📦 商品SKU: " + f"{sku}")
                logger.error("💥 处理状态: 异常失败")
                logger.error("❌ 异常原因: " + f"{e}")
                logger.error("⏰ 失败时间: " + f"{self._get_current_time()}")
                logger.error("💥" + "=" * 50 + "💥")
                
                results.append({
                    'browser_id': browser_id,
                    'sku': sku,
                    'success': False,
                    'error': str(e)
                })
            
            # 每个产品上架后立即关闭浏览器窗口
            if current_browser and current_profile_id:
                try:
                    # 使用API接口关闭浏览器
                    close_success = close_browser_by_profile_id(
                        self.config.api_port,
                        self.config.api_key,
                        current_profile_id
                    )
                    
                    if close_success:
                        logger.info(f"✅ 商品 {sku} 处理完成，已通过API关闭浏览器 {browser_id} (profile_id: {current_profile_id})")
                    else:
                        logger.warning(f"⚠️ 商品 {sku} 处理完成，但API关闭浏览器失败 {browser_id} (profile_id: {current_profile_id})")
                    
                    # 尝试关闭Playwright连接
                    try:
                        current_playwright.stop()
                    except Exception as e:
                        logger.debug(f"关闭Playwright连接时出错: {e}")
                    
                    # 重置浏览器相关变量
                    current_browser = None
                    current_playwright = None
                    current_uploader = None
                    current_browser_id = None
                    current_profile_id = None
                    
                except Exception as e:
                    logger.error(f"关闭浏览器 {browser_id} 时出错: {e}")
                    # 即使关闭失败也要重置变量
                    current_browser = None
                    current_playwright = None
                    current_uploader = None
                    current_browser_id = None
                    current_profile_id = None
        
        # 注意：每个产品处理完后都已经关闭浏览器，无需额外关闭
        
        logger.info(f"顺序上传完成，共处理 {len(results)} 个商品")
        return results
    
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成上传结果统计"""
        total_products = len(results)
        total_success = sum(1 for r in results if r['success'])
        total_failed = sum(1 for r in results if not r['success'])
        success_rate = (total_success / total_products * 100) if total_products > 0 else 0
        
        # 按BrowserID分组统计
        account_stats = {}
        for result in results:
            browser_id = result['browser_id']
            if browser_id not in account_stats:
                account_stats[browser_id] = {
                    'browser_id': browser_id,
                    'total_products': 0,
                    'success_count': 0,
                    'failed_count': 0,
                    'failed_products': [],
                    'success': True
                }
            
            account_stats[browser_id]['total_products'] += 1
            if result['success']:
                account_stats[browser_id]['success_count'] += 1
            else:
                account_stats[browser_id]['failed_count'] += 1
                account_stats[browser_id]['failed_products'].append(result['sku'])
                account_stats[browser_id]['success'] = False
        
        account_details = list(account_stats.values())
        
        summary = {
            'success': total_failed == 0,
            'total_accounts': len(account_details),
            'total_products': total_products,
            'success_count': total_success,
            'failed_count': total_failed,
            'success_rate': success_rate,
            'account_details': account_details
        }
        
        return summary
