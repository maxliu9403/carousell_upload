import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path
from core.models import ProductInfo
from core.logger import logger

class ExcelProductParser:
    """Excel 商品信息解析器"""
    
    def __init__(self, excel_path: str):
        self.excel_path = Path(excel_path)
        if not self.excel_path.exists():
            raise FileNotFoundError(f"Excel 文件不存在: {excel_path}")
    
    def parse_products(self, region: str) -> List[Dict[str, Any]]:
        """
        解析 Excel 文件中的商品信息
        
        Args:
            region (str): 地域代码 (HK, MY, SG)
            
        Returns:
            List[Dict[str, Any]]: 解析后的商品信息列表
        """
        try:
            logger.info(f"开始解析 Excel 文件: {self.excel_path}")
            
            # 读取 Excel 文件
            df = pd.read_excel(self.excel_path)
            
            # 验证必要的列是否存在
            required_columns = [
                'URL', 'SKU', 'BrowserID', 'ProductNameCn', 'ProductNameEn',
                'GenderEn', 'HKPrice', 'SGPrice', 'MYPrice',
                'Brand', 'Folder'
            ]
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Excel 文件缺少必要的列: {missing_columns}")
            
            # 根据地域选择价格列
            price_column = self._get_price_column(region)
            if price_column not in df.columns:
                raise ValueError(f"地域 {region} 对应的价格列 {price_column} 不存在")
            
            products = []
            for index, row in df.iterrows():
                try:
                    # 跳过空行
                    if pd.isna(row['SKU']) or pd.isna(row['BrowserID']):
                        continue
                    
                    product_info = {
                        'url': str(row['URL']) if not pd.isna(row['URL']) else '',
                        'sku': str(row['SKU']),
                        'browser_id': str(row['BrowserID']),
                        'product_name_cn': str(row['ProductNameCn']) if not pd.isna(row['ProductNameCn']) else '',
                        'product_name_en': str(row['ProductNameEn']) if not pd.isna(row['ProductNameEn']) else '',
                        'gender_en': str(row['GenderEn']) if not pd.isna(row['GenderEn']) else '',
                        'price': str(row[price_column]) if not pd.isna(row[price_column]) else '0',
                        'brand': str(row['Brand']) if not pd.isna(row['Brand']) else '',
                        'folder': str(row['Folder']) if not pd.isna(row['Folder']) else '',
                        'region': region
                    }
                    
                    products.append(product_info)
                    logger.info(f"解析商品 {index + 1}: SKU={product_info['sku']}, 价格={product_info['price']}")
                    
                except Exception as e:
                    logger.error(f"解析第 {index + 1} 行数据失败: {e}")
                    continue
            
            logger.info(f"Excel 解析完成，共解析 {len(products)} 个商品")
            return products
            
        except Exception as e:
            logger.error(f"解析 Excel 文件失败: {e}")
            raise
    
    def _get_price_column(self, region: str) -> str:
        """根据地域获取对应的价格列名"""
        price_mapping = {
            'HK': 'HKPrice',
            'MY': 'MYPrice', 
            'SG': 'SGPrice'
        }
        
        if region not in price_mapping:
            raise ValueError(f"不支持的地域: {region}，支持的地域: {list(price_mapping.keys())}")
        
        return price_mapping[region]
    
    def _get_title_by_region(self, product_data: Dict[str, Any]) -> str:
        """根据地域获取对应的商品标题"""
        region = product_data['region']
        
        if region == 'HK':
            # HK地域使用中文标题
            title = product_data['product_name_cn'] or product_data['product_name_en']
        elif region == 'SG':
            # SG地域使用英文标题
            title = product_data['product_name_en'] or product_data['product_name_cn']
        elif region == 'MY':
            # MY地域使用英文标题
            title = product_data['product_name_en'] or product_data['product_name_cn']
        else:
            # 默认使用英文标题
            title = product_data['product_name_en'] or product_data['product_name_cn']
        
        return title
    
    def create_product_info(self, product_data: Dict[str, Any]) -> ProductInfo:
        """
        将解析的数据转换为 ProductInfo 对象
        
        Args:
            product_data (Dict[str, Any]): 解析的商品数据
            
        Returns:
            ProductInfo: 商品信息对象
        """
        # 根据地域选择商品名称
        title = self._get_title_by_region(product_data)
        
        # 使用英文性别字段
        gender = self._map_gender(product_data['gender_en'])
        
        return ProductInfo(
            title=title,
            price=product_data['price'],
            category="sneakers",  # 默认类目
            brand=product_data['brand'],
            condition="new",  # 默认新旧程度
            gender=gender,
            location="All of Singapore" if product_data['region'] == 'SG' else "All of Hong Kong" if product_data['region'] == 'HK' else "All of Malaysia",
            multi_quantity=False
        )
    
    def _map_gender(self, gender_str: str) -> str:
        """将性别字符串映射为标准格式"""
        if not gender_str:
            return "unisex"
        
        gender_str = gender_str.lower().strip()
        
        # 中文映射
        if gender_str in ['男', '男性', '男装', '男士', '男裝']:
            return "male"
        elif gender_str in ['女', '女性', '女装', '女士', '女裝']:
            return "female"
        
        # 英文映射
        if gender_str in ['male', 'men', 'mens']:
            return "male"
        elif gender_str in ['female', 'women', 'womens']:
            return "female"
        
        return "unisex"
