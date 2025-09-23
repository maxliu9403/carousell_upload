"""
Carousell上传器主类 - 使用工厂模式创建地域和类目特定的上传器
保持原有的接口不变，内部使用模块化的上传器
"""
from playwright.sync_api import Page  # pyright: ignore[reportMissingImports]
from core.models import ProductInfo, UploadConfig
from core.logger import logger
from .uploader_factory import UploaderFactory
from .base_uploader import BaseUploader

class CarousellUploader:
    """
    Carousell 上传器主类 - 使用工厂模式
    保持原有的接口不变，内部使用模块化的上传器
    """
    
    def __init__(self, page: Page, config: UploadConfig, region: str = "SG", browser_id: str = None, sku: str = None):
        """
        初始化上传器
        
        Args:
            page: Playwright页面对象
            config: 上传配置
            region: 地域 (HK, SG, MY)
            browser_id: 浏览器ID
            sku: 商品SKU
        """
        self.page = page
        self.config = config
        self.region = region
        self.browser_id = browser_id
        self.sku = sku
        self._uploader = None
        
    def _get_uploader(self, category: str) -> BaseUploader:
        """
        获取对应的上传器实例
        
        Args:
            category: 商品类目
            
        Returns:
            BaseUploader: 对应的上传器实例
        """
        if self._uploader is None:
            try:
                self._uploader = UploaderFactory.create_uploader(
                    region=self.region,
                    category=category,
                    page=self.page,
                    config=self.config,
                    browser_id=self.browser_id,
                    sku=self.sku
                )
                logger.info(f"✅ 成功创建上传器: {self.region}-{category}")
            except Exception as e:
                logger.error(f"❌ 创建上传器失败: {self.region}-{category}, 错误: {e}")
                raise
        
        return self._uploader
        
    def upload_product(self, product_info: ProductInfo, folder_path: str = None, category: str = "sneakers") -> bool:
        """
        商品上传工厂函数 - 根据地域和类目选择不同的上传方法
        
        Args:
            product_info: 商品信息
            folder_path: 图片文件夹路径
            category: 商品类目 (sneakers, bags, clothes)
            
        Returns:
            bool: 上传是否成功
        """
        try:
            logger.info(f"开始上传商品: {self.region}-{category}")
            
            # 验证地域-类目组合
            if not UploaderFactory.validate_combination(self.region, category):
                logger.error(f"不支持的地域-类目组合: {self.region}-{category}")
                return False
            
            # 获取对应的上传器
            uploader = self._get_uploader(category)
            
            # 执行上传
            result = uploader.upload_product(product_info, folder_path, category)
            
            if result:
                logger.info(f"✅ 商品上传成功: {self.region}-{category}")
            else:
                logger.error(f"❌ 商品上传失败: {self.region}-{category}")
                
            return result
            
        except Exception as e:
            logger.error(f"❌ 商品上传异常: {self.region}-{category}, 错误: {e}")
            return False
    
    def get_supported_combinations(self) -> list:
        """
        获取支持的地域-类目组合
        
        Returns:
            list: 支持的地域-类目组合列表
        """
        return UploaderFactory.get_supported_combinations()
    
    def validate_combination(self, region: str, category: str) -> bool:
        """
        验证地域-类目组合是否支持
        
        Args:
            region: 地域
            category: 类目
            
        Returns:
            bool: 是否支持
        """
        return UploaderFactory.validate_combination(region, category)
