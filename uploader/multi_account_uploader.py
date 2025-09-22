from typing import List, Dict, Any
from pathlib import Path
from playwright.sync_api import Page
from .models import ProductInfo, UploadConfig
from .carousell_uploader import CarousellUploader
from .browser import start_browser, get_profile_id_by_browser_id, fetch_all_browser_windows
from .excel_parser import ExcelProductParser
from .logger import logger
from .record_manager import SuccessRecordManager

class MultiAccountUploader:
    """多账号串行上传器"""
    
    def __init__(self, config: UploadConfig, excel_path: str, region: str):
        self.config = config
        self.excel_path = excel_path
        self.region = region
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
            
            # 2. 获取已成功的BrowserID，跳过已完成的账号
            successful_browser_ids = self.record_manager.get_successful_browser_ids(self.excel_path, self.region)
            logger.info(f"已成功的BrowserID: {sorted(successful_browser_ids)}")
            
            # 3. 过滤掉已成功的BrowserID，只保留需要处理的商品
            filtered_products_data = self._filter_products_by_success(products_data, successful_browser_ids)
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
            
            # 6. 按浏览器ID分组商品
            products_by_browser = self._group_products_by_browser(filtered_products_data, browser_windows)
            
            # 4. 串行上传每个账号的商品
            results = self._upload_by_accounts(products_by_browser, browser_windows)
            
            # 5. 统计结果
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
    
    def _filter_products_by_success(self, products_data: List[Dict[str, Any]], successful_browser_ids: set) -> List[Dict[str, Any]]:
        """过滤掉已成功的BrowserID对应的商品"""
        filtered_products = []
        skipped_count = 0
        
        for product in products_data:
            browser_id = product['browser_id']
            if browser_id in successful_browser_ids:
                skipped_count += 1
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
    
    def _group_products_by_browser(self, products_data: List[Dict[str, Any]], browser_windows: Dict[int, Dict[str, str]]) -> Dict[str, List[Dict[str, Any]]]:
        """按浏览器ID分组商品"""
        products_by_browser = {}
        
        for product in products_data:
            browser_id = product['browser_id']
            if browser_id not in products_by_browser:
                products_by_browser[browser_id] = []
            products_by_browser[browser_id].append(product)
        
        logger.info(f"商品按浏览器分组完成，共 {len(products_by_browser)} 个账号")
        for browser_id, products in products_by_browser.items():
            logger.info(f"  浏览器 {browser_id}: {len(products)} 个商品")
        
        return products_by_browser
    
    def _upload_by_accounts(self, products_by_browser: Dict[str, List[Dict[str, Any]]], browser_windows: Dict[int, Dict[str, str]]) -> List[Dict[str, Any]]:
        """串行上传每个账号的商品"""
        results = []
        
        for browser_id, products in products_by_browser.items():
            logger.info(f"开始上传浏览器 {browser_id} 的商品，共 {len(products)} 个")
            
            account_result = {
                'browser_id': browser_id,
                'total_products': len(products),
                'success_count': 0,
                'failed_count': 0,
                'failed_products': [],
                'success': True
            }
            
            try:
                # 根据BrowserID获取对应的profile_id
                try:
                    profile_id = get_profile_id_by_browser_id(
                        self.config.api_port, 
                        self.config.api_key, 
                        browser_id,
                        browser_windows  # 传递已获取的browser_windows，避免重复调用
                    )
                    logger.info(f"成功获取BrowserID {browser_id} 对应的profile_id: {profile_id}")
                except Exception as e:
                    logger.error(f"获取BrowserID {browser_id} 对应的profile_id失败: {e}")
                    raise
                
                # 为每个账号创建新的浏览器实例，使用动态获取的profile_id
                playwright, browser, page = start_browser(
                    self.config.api_port,
                    self.config.api_key,
                    profile_id
                )
                
                uploader = CarousellUploader(page, self.config, self.region)
                
                # 上传该账号的所有商品
                for product_data in products:
                    try:
                        logger.info(f"上传商品: {product_data['sku']} - {product_data.get('product_name_cn', '')}")
                        
                        # 创建 ProductInfo 对象
                        product_info = self.parser.create_product_info(product_data)
                        
                        # 执行上传，传递文件夹路径
                        folder_path = product_data['folder'] if product_data['folder'] else None
                        success = uploader.upload_product(product_info, folder_path)
                        
                        if success:
                            account_result['success_count'] += 1
                            logger.info(f"商品 {product_data['sku']} 上传成功")
                            
                            # 记录成功
                            self.record_manager.record_success(
                                self.excel_path,
                                self.region,
                                browser_id,
                                product_data['sku']
                            )
                        else:
                            account_result['failed_count'] += 1
                            account_result['failed_products'].append(product_data['sku'])
                            logger.error(f"商品 {product_data['sku']} 上传失败")
                        
                    except Exception as e:
                        account_result['failed_count'] += 1
                        account_result['failed_products'].append(product_data['sku'])
                        logger.error(f"上传商品 {product_data['sku']} 时出错: {e}")
                
                # 关闭浏览器
                browser.close()
                playwright.stop()
                
                logger.info(f"浏览器 {browser_id} 上传完成: 成功 {account_result['success_count']}, 失败 {account_result['failed_count']}")
                
            except Exception as e:
                account_result['success'] = False
                account_result['failed_count'] = len(products)
                account_result['failed_products'] = [p['sku'] for p in products]
                logger.error(f"浏览器 {browser_id} 上传失败: {e}")
            
            results.append(account_result)
        
        return results
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成上传结果统计"""
        total_products = sum(r['total_products'] for r in results)
        total_success = sum(r['success_count'] for r in results)
        total_failed = sum(r['failed_count'] for r in results)
        
        summary = {
            'success': total_failed == 0,
            'total_accounts': len(results),
            'total_products': total_products,
            'success_count': total_success,
            'failed_count': total_failed,
            'success_rate': (total_success / total_products * 100) if total_products > 0 else 0,
            'account_details': results
        }
        
        logger.info("=" * 50)
        logger.info("上传结果统计:")
        logger.info(f"  总账号数: {summary['total_accounts']}")
        logger.info(f"  总商品数: {summary['total_products']}")
        logger.info(f"  成功数量: {summary['success_count']}")
        logger.info(f"  失败数量: {summary['failed_count']}")
        logger.info(f"  成功率: {summary['success_rate']:.2f}%")
        logger.info("=" * 50)
        
        return summary
