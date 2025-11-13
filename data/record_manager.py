import json
import os
from pathlib import Path
from typing import Dict, List, Set, Any
from datetime import datetime, timedelta
from core.logger import logger

class SuccessRecordManager:
    """成功记录管理器"""
    
    def __init__(self, record_file: str = "success_records.json"):
        """
        初始化记录管理器
        
        Args:
            record_file: 记录文件路径
        """
        self.record_file = Path(record_file)
        self.records = self._load_records()
    
    def _load_records(self) -> Dict[str, Any]:
        """加载记录文件"""
        if not self.record_file.exists():
            return {
                "created_at": datetime.now().isoformat(),
                "records": {}
            }
        
        try:
            with open(self.record_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"成功加载记录文件: {self.record_file}")
                return data
        except Exception as e:
            logger.warning(f"加载记录文件失败: {e}，将创建新文件")
            return {
                "created_at": datetime.now().isoformat(),
                "records": {}
            }
    
    def _save_records(self):
        """保存记录文件"""
        try:
            self.records["updated_at"] = datetime.now().isoformat()
            with open(self.record_file, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
            logger.info(f"记录文件已保存: {self.record_file}")
        except Exception as e:
            logger.error(f"保存记录文件失败: {e}")
    
    def _get_record_key(self, excel_path: str, region: str, date: datetime = None) -> str:
        """生成记录的唯一键：文件路径_地域_日期"""
        # 使用指定日期或当前日期作为时间窗口
        if date is None:
            date = datetime.now()
        date_str = date.strftime("%Y-%m-%d")
        # 使用文件路径的标准化形式
        normalized_path = os.path.normpath(excel_path)
        return f"{normalized_path}_{region}_{date_str}"
    
    def _get_record_keys_in_days(self, excel_path: str, region: str, days: int = 2) -> List[str]:
        """
        获取过去N天的记录键列表
        
        Args:
            excel_path: Excel文件路径
            region: 地域（HK/MY/SG）
            days: 天数（默认2天）
            
        Returns:
            List[str]: 记录键列表，从今天到N天前
        """
        keys = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            key = self._get_record_key(excel_path, region, date)
            keys.append(key)
        return keys
    
    def get_successful_browser_ids(self, excel_path: str, region: str) -> Set[str]:
        """
        获取指定Excel文件和地域下已成功的BrowserID列表（检查过去2天）
        
        Args:
            excel_path: Excel文件路径
            region: 地域（HK/MY/SG）
            
        Returns:
            Set[str]: 已成功的BrowserID集合
        """
        # 获取过去2天的记录键
        record_keys = self._get_record_keys_in_days(excel_path, region, days=2)
        
        successful_browser_ids = set()
        # 遍历过去2天的记录
        for record_key in record_keys:
            record_data = self.records["records"].get(record_key, {})
            for browser_id, products in record_data.get("browser_records", {}).items():
                if products:  # 如果有商品记录，说明该BrowserID已成功
                    successful_browser_ids.add(browser_id)
        
        if successful_browser_ids:
            logger.info(f"找到已成功的BrowserID（过去2天）: {sorted(successful_browser_ids)}")
        else:
            logger.info("未找到已成功的BrowserID记录（过去2天）")
        
        return successful_browser_ids
    
    def get_successful_products(self, excel_path: str, region: str, browser_id: str) -> Set[str]:
        """
        获取指定BrowserID下已成功的商品SKU列表（检查过去2天）
        
        Args:
            excel_path: Excel文件路径
            region: 地域（HK/MY/SG）
            browser_id: 浏览器ID
            
        Returns:
            Set[str]: 已成功的商品SKU集合
        """
        # 获取过去2天的记录键
        record_keys = self._get_record_keys_in_days(excel_path, region, days=2)
        
        successful_skus = set()
        # 遍历过去2天的记录
        for record_key in record_keys:
            record_data = self.records["records"].get(record_key, {})
            browser_records = record_data.get("browser_records", {})
            skus = browser_records.get(browser_id, [])
            successful_skus.update(skus)
        
        if successful_skus:
            logger.info(f"BrowserID {browser_id} 已成功的商品SKU（过去2天）: {sorted(successful_skus)}")
        else:
            logger.info(f"BrowserID {browser_id} 无已成功的商品记录（过去2天）")
        
        return successful_skus
    
    def is_product_successful(self, excel_path: str, region: str, browser_id: str, sku: str) -> bool:
        """
        检查指定商品是否已成功上传（检查过去2天）
        
        Args:
            excel_path: Excel文件路径
            region: 地域（HK/MY/SG）
            browser_id: 浏览器ID
            sku: 商品SKU
            
        Returns:
            bool: 是否已成功
        """
        # 获取过去2天的记录键
        record_keys = self._get_record_keys_in_days(excel_path, region, days=2)
        
        # 遍历过去2天的记录
        for record_key in record_keys:
            record_data = self.records["records"].get(record_key, {})
            browser_records = record_data.get("browser_records", {})
            successful_skus = set(browser_records.get(browser_id, []))
            if sku in successful_skus:
                return True
        
        return False
    
    def record_success(self, excel_path: str, region: str, browser_id: str, sku: str):
        """
        记录成功执行的商品
        
        Args:
            excel_path: Excel文件路径
            region: 地域（HK/MY/SG）
            browser_id: 浏览器ID
            sku: 商品SKU
        """
        record_key = self._get_record_key(excel_path, region)
        
        # 确保记录结构存在
        if record_key not in self.records["records"]:
            self.records["records"][record_key] = {
                "excel_path": excel_path,
                "region": region,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "created_at": datetime.now().isoformat(),
                "browser_records": {}
            }
        
        # 确保BrowserID记录存在
        if browser_id not in self.records["records"][record_key]["browser_records"]:
            self.records["records"][record_key]["browser_records"][browser_id] = []
        
        # 添加SKU到成功记录
        if sku not in self.records["records"][record_key]["browser_records"][browser_id]:
            self.records["records"][record_key]["browser_records"][browser_id].append(sku)
            logger.info(f"记录成功: {region} - BrowserID {browser_id} - SKU {sku}")
        
        # 更新最后修改时间
        self.records["records"][record_key]["updated_at"] = datetime.now().isoformat()
        
        # 保存记录
        self._save_records()
    
    def record_browser_success(self, excel_path: str, region: str, browser_id: str, successful_skus: List[str]):
        """
        批量记录BrowserID的成功商品
        
        Args:
            excel_path: Excel文件路径
            region: 地域（HK/MY/SG）
            browser_id: 浏览器ID
            successful_skus: 成功的商品SKU列表
        """
        record_key = self._get_record_key(excel_path, region)
        
        # 确保记录结构存在
        if record_key not in self.records["records"]:
            self.records["records"][record_key] = {
                "excel_path": excel_path,
                "region": region,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "created_at": datetime.now().isoformat(),
                "browser_records": {}
            }
        
        # 记录成功的SKU
        self.records["records"][record_key]["browser_records"][browser_id] = successful_skus.copy()
        
        # 更新最后修改时间
        self.records["records"][record_key]["updated_at"] = datetime.now().isoformat()
        
        logger.info(f"批量记录成功: {region} - BrowserID {browser_id} - {len(successful_skus)} 个商品")
        
        # 保存记录
        self._save_records()
    
    def get_record_summary(self, excel_path: str, region: str) -> Dict[str, Any]:
        """
        获取记录摘要信息（汇总过去2天的数据）
        
        Args:
            excel_path: Excel文件路径
            region: 地域（HK/MY/SG）
            
        Returns:
            Dict[str, Any]: 记录摘要
        """
        # 获取过去2天的记录键
        record_keys = self._get_record_keys_in_days(excel_path, region, days=2)
        
        # 汇总所有浏览器和商品数据
        all_browser_details = {}
        dates_found = []
        earliest_created = None
        latest_updated = None
        
        for record_key in record_keys:
            record_data = self.records["records"].get(record_key, {})
            if not record_data:
                continue
                
            browser_records = record_data.get("browser_records", {})
            dates_found.append(record_data.get("date", ""))
            
            # 汇总浏览器记录
            for browser_id, skus in browser_records.items():
                if browser_id not in all_browser_details:
                    all_browser_details[browser_id] = set()
                all_browser_details[browser_id].update(skus)
            
            # 追踪最早创建时间和最新更新时间
            created_at = record_data.get("created_at", "")
            updated_at = record_data.get("updated_at", "")
            
            if created_at and (not earliest_created or created_at < earliest_created):
                earliest_created = created_at
            if updated_at and (not latest_updated or updated_at > latest_updated):
                latest_updated = updated_at
        
        # 计算汇总统计
        total_browsers = len(all_browser_details)
        total_products = sum(len(skus) for skus in all_browser_details.values())
        
        return {
            "excel_path": excel_path,
            "region": region,
            "dates": sorted(dates_found),  # 涉及的日期
            "days_checked": 2,  # 检查的天数
            "total_browsers": total_browsers,
            "total_products": total_products,
            "browser_details": {
                browser_id: len(skus) 
                for browser_id, skus in all_browser_details.items()
            },
            "created_at": earliest_created or "",
            "updated_at": latest_updated or ""
        }
    
    def clear_records(self, excel_path: str = None, region: str = None):
        """
        清除记录
        
        Args:
            excel_path: 指定Excel文件路径，为None时清除所有记录
            region: 指定地域，为None时清除该文件的所有地域记录
        """
        if excel_path is None:
            # 清除所有记录
            self.records["records"] = {}
            logger.info("已清除所有成功记录")
        elif region is None:
            # 清除指定Excel文件的所有记录
            normalized_path = os.path.normpath(excel_path)
            keys_to_remove = [
                key for key in self.records["records"].keys() 
                if key.startswith(normalized_path)
            ]
            for key in keys_to_remove:
                del self.records["records"][key]
            logger.info(f"已清除Excel文件 {excel_path} 的所有记录")
        else:
            # 清除指定Excel文件和地域的记录
            record_key = self._get_record_key(excel_path, region)
            if record_key in self.records["records"]:
                del self.records["records"][record_key]
                logger.info(f"已清除记录: {excel_path} - {region}")
        
        self._save_records()
