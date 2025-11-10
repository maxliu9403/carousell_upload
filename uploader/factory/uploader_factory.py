"""
上传器工厂类 - 根据地域和类目创建对应的上传器实例
"""
from typing import Type
from core.logger import logger

class UploaderFactory:
    """上传器工厂类"""
    
    @staticmethod
    def create_uploader(region: str, category: str, page, config, 
                       browser_id: str = None, sku: str = None):
        """
        根据地域和类目创建对应的上传器实例
        
        Args:
            region: 地域 (HK, SG, MY)
            category: 类目 (sneakers, bags, clothes)
            page: 页面对象
            config: 上传配置
            browser_id: 浏览器ID
            sku: 商品SKU
            
        Returns:
            对应的上传器实例
        """
        try:
            # 动态导入对应的上传器类
            module_name = f"uploader.regions.{region.lower()}.{category}.{category}_uploader"
            class_name = f"{region.upper()}{category.capitalize()}Uploader"
            
            logger.info(f"正在创建上传器: {region}-{category}")
            
            # 导入模块
            module = __import__(module_name, fromlist=[class_name])
            uploader_class = getattr(module, class_name)
            
            # 创建实例，传递 category 参数
            uploader = uploader_class(page, config, region, browser_id, sku, category)
            logger.info(f"✅ 成功创建上传器: {region}-{category}")
            
            return uploader
            
        except ImportError as e:
            logger.error(f"❌ 导入上传器失败: {region}-{category}, 错误: {e}")
            raise ValueError(f"不支持的地域-类目组合: {region}-{category}")
        except AttributeError as e:
            logger.error(f"❌ 找不到上传器类: {class_name}, 错误: {e}")
            raise ValueError(f"找不到对应的上传器类: {class_name}")
        except Exception as e:
            logger.error(f"❌ 创建上传器失败: {region}-{category}, 错误: {e}")
            raise
    
    @staticmethod
    def get_supported_combinations() -> list:
        """
        获取支持的地域-类目组合
        
        Returns:
            list: 支持的地域-类目组合列表
        """
        regions = ["HK", "SG", "MY"]
        categories = ["sneakers", "bags", "clothes"]
        
        combinations = []
        for region in regions:
            for category in categories:
                combinations.append(f"{region}-{category}")
        
        return combinations
    
    @staticmethod
    def validate_combination(region: str, category: str) -> bool:
        """
        验证地域-类目组合是否支持
        
        Args:
            region: 地域
            category: 类目
            
        Returns:
            bool: 是否支持
        """
        valid_regions = ["HK", "SG", "MY"]
        valid_categories = ["sneakers", "bags", "clothes"]
        
        return region.upper() in valid_regions and category.lower() in valid_categories
