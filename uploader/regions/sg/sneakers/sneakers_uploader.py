"""
新加坡运动鞋上传器 - 通过跳服务实现运动鞋上传
保持原有的点击操作顺序和CSS选择器不变
"""
from core.models import ProductInfo
from core.logger import logger
from uploader.core.base_uploader import BaseUploader

class SGSneakersUploader(BaseUploader):
    """新加坡运动鞋上传器"""
    
    def upload_product(self, product_info: ProductInfo, folder_path: str = None, category: str = "sneakers") -> bool:
        """
        新加坡运动鞋上传方法 - 通过跳服务实现
        
        Args:
            product_info: 商品信息
            folder_path: 图片文件夹路径
            category: 商品类目
            
        Returns:
            bool: 上传是否成功
        """
        try:
            logger.info("使用新加坡运动鞋跳服务上传方法")
            
            # 丰富商品信息
            enriched_info = self._enrich_product_info(product_info)
            
            # ========= 第一部分：上传服务商品 =========
            self._upload_sneaker_by_service(enriched_info, folder_path)
            
            # ========= 第二部分：激活商品 =========
            self._activate_product()
            
            return True
            
        except Exception as e:
            logger.error(f"新加坡运动鞋上传流程执行失败: {e}")
            return False
    
    def _upload_sneaker_by_service(self, enriched_info: ProductInfo, folder_path: str):
        """
        跳服务上传运动鞋商品
        保持原有的点击操作顺序和CSS选择器不变
        """
        # 第一步：上传服务商品
        self._upload_service_product(enriched_info, folder_path)
        
        # 第二步：编辑为运动鞋
        self._edit_to_sneakers(enriched_info)
        
        # 第三步：发布商品
        self._publish_product()

        # 等待页面加载结束
        try:
            self.page.wait_for_load_state("networkidle", timeout=30000)
            logger.info("✅ 页面网络活动已结束")
        except Exception as e:
            logger.warning(f"⚠️ 等待页面网络活动结束超时: {e}")
            # 即使超时也继续执行，因为发布操作已经完成
            logger.info("✅ 继续执行后续流程")
    
    def _edit_to_sneakers(self, enriched_info: ProductInfo):
        """
        编辑商品为运动鞋
        保持原有的点击操作顺序和CSS选择器不变
        """
        logger.info("开始编辑跳波鞋")
        
        # 等待当前页面加载结束，然后直接进入编辑模式
        self._wait_for_page_load_and_enter_edit()
        
        # 修改为运动鞋类目
        self._change_to_sneakers_category(enriched_info)
        
        # 填写运动鞋详细信息
        self._fill_sneakers_details(enriched_info)
        
        # 处理面交设置
        self._openmeetup(enriched_info)

        # 关闭平台收款
        self._close_buyer_protection()

        # 关闭送货
        self._close_delivery()

    def _change_to_sneakers_category(self, enriched_info: ProductInfo):
        """修改为运动鞋类目"""
        # 修改产品类目
        self.safe_actions.safe_click_with_config(
            "category_selection.service_category_selector", self.region, must_exist=True,
            operation="修改产品类目"
        )

        # 输入运动鞋搜索关键词
        search_keyword = self.safe_actions.css_manager.get_selector(
            "sneakers_specific.category_search_keyword", self.region, "primary"
        ) or "sneakers"
        
        self.safe_actions.safe_input_with_config(
            "sneakers_specific.category_search_input", search_keyword, self.region, must_exist=True,
            operation="输入运动鞋搜索关键词"
        )

        self.page.wait_for_timeout(2000)
        
        # 根据性别选择子类目
        if enriched_info.gender.lower() in ["male", "men", "mens"]:
            # 点击 男装波鞋
            self.safe_actions.safe_click_with_config(
                "sneakers_specific.men_sneakers_option", self.region, must_exist=True,
                operation="选择男装运动鞋"
            )
        else:
            # 点击女装波鞋
            self.safe_actions.safe_click_with_config(
                "sneakers_specific.women_sneakers_option", self.region, must_exist=True,
                operation="选择女装运动鞋"
            )
    
    def _fill_sneakers_details(self, enriched_info: ProductInfo):
        """
        填写运动鞋详细信息
        使用配置文件中的CSS选择器
        """
        # 点击 新旧
        self.safe_actions.safe_click_with_config(
            "sneakers_specific.condition_selector", self.region, must_exist=True,
            operation="点击新旧条件"
        )

        # 点击 品牌
        self.safe_actions.safe_click_with_config(
            "sneakers_specific.brand_selector", self.region, must_exist=True,
            operation="点击品牌选择"
        )

        # 点击搜索品牌
        brand_search_keyword = self.safe_actions.css_manager.get_selector(
            "sneakers_specific.brand_search_keyword", self.region, "primary"
        ) or "other"
        
        self.safe_actions.safe_input_with_config(
            "sneakers_specific.brand_search_input", brand_search_keyword, self.region, must_exist=True,
            operation="输入品牌搜索"
        )

        self.page.wait_for_timeout(2000)
        
        # 点击other品牌
        self.safe_actions.safe_click_with_config(
            "sneakers_specific.brand_option", self.region, must_exist=True,
            operation="点击Other品牌"
        )

        # 输入品牌
        self.safe_actions.safe_input_with_config(
            "sneakers_specific.brand_input", enriched_info.brand, self.region, must_exist=True,
            operation="输入品牌名称"
        )
        
        # 点击size
        self.safe_actions.safe_click_with_config(
            "sneakers_specific.size_selector", self.region, must_exist=True,
            operation="点击尺寸选择"
        )
      
        # 输入size
        self.safe_actions.safe_input_with_config(
            "sneakers_specific.size_search_input", str(enriched_info.size), self.region, must_exist=True,
            operation="输入尺寸搜索"
        )

        self.page.wait_for_timeout(2000)

        # 点击查找的size
        self.safe_actions.safe_click_with_config(
            "sneakers_specific.size_option", self.region, must_exist=True,
            operation="点击选择尺寸"
        )

        # 点击 多产品销售复选框
        # self.safe_actions.safe_click_with_config(
        #     "sneakers_specific.multi_quantity_checkbox", self.region, must_exist=False,
        #     operation="点击多产品销售复选框"
        # )
    
    


