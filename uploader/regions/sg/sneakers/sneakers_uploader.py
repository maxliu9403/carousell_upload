"""
新加坡运动鞋上传器 - 通过跳服务实现运动鞋上传
保持原有的点击操作顺序和CSS选择器不变
"""
from core.models import ProductInfo
from core.logger import logger
from uploader.base_uploader import BaseUploader

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
    
    def _edit_to_sneakers(self, enriched_info: ProductInfo):
        """
        编辑商品为运动鞋
        保持原有的点击操作顺序和CSS选择器不变
        """
        logger.info("开始编辑跳波鞋")
        
        # 进入管理页面
        self._navigate_to_manage_page()
        
        # 进入编辑模式
        self._enter_edit_mode()
        
        # 处理AI文案相关操作
        self._handle_ai_writing_operations()
        
        # 修改为运动鞋类目
        self._change_to_sneakers_category(enriched_info)
        
        # 填写运动鞋详细信息
        self._fill_sneakers_details(enriched_info)
        
        # 处理面交设置
        self._handle_meetup_settings(enriched_info)
    
    def _change_to_sneakers_category(self, enriched_info: ProductInfo):
        """修改为运动鞋类目"""
        # 修改产品类目
        self.safe_actions.safe_click_with_config(
            "sneakers_sg.category_selector", self.region, must_exist=True,
            operation="修改产品类目"
        )

        # 输入运动鞋搜索关键词
        search_keyword = self.safe_actions.css_manager.get_selector(
            "sneakers_sg.category_search_keyword", self.region, "primary"
        ) or "sneakers"
        
        self.safe_actions.safe_input_with_config(
            "sneakers_sg.category_search_input", search_keyword, self.region, must_exist=True,
            operation="输入运动鞋搜索关键词"
        )

        self.page.wait_for_timeout(2000)
        
        # 根据性别选择子类目
        if enriched_info.gender.lower() in ["male", "men", "mens"]:
            # 点击 男装波鞋
            self.safe_actions.safe_click_with_config(
                "sneakers_sg.men_sneakers_option", self.region, must_exist=True,
                operation="选择男装运动鞋"
            )
        else:
            # 点击女装波鞋
            self.safe_actions.safe_click_with_config(
                "sneakers_sg.women_sneakers_option", self.region, must_exist=True,
                operation="选择女装运动鞋"
            )
    
    def _fill_sneakers_details(self, enriched_info: ProductInfo):
        """
        填写运动鞋详细信息
        使用配置文件中的CSS选择器
        """
        # 点击 新旧
        self.safe_actions.safe_click_with_config(
            "sneakers_sg.condition_selector", self.region, must_exist=True,
            operation="点击新旧条件"
        )

        # 点击 品牌
        self.safe_actions.safe_click_with_config(
            "sneakers_sg.brand_selector", self.region, must_exist=True,
            operation="点击品牌选择"
        )

        # 点击搜索品牌
        brand_search_keyword = self.safe_actions.css_manager.get_selector(
            "sneakers_sg.brand_search_keyword", self.region, "primary"
        ) or "other"
        
        self.safe_actions.safe_input_with_config(
            "sneakers_sg.brand_search_input", brand_search_keyword, self.region, must_exist=True,
            operation="输入品牌搜索"
        )

        self.page.wait_for_timeout(2000)
        
        # 点击other品牌
        self.safe_actions.safe_click_with_config(
            "sneakers_sg.brand_option", self.region, must_exist=True,
            operation="点击Other品牌"
        )

        # 输入品牌
        self.safe_actions.safe_input_with_config(
            "sneakers_sg.brand_input", enriched_info.brand, self.region, must_exist=True,
            operation="输入品牌名称"
        )
        
        # 点击size
        self.safe_actions.safe_click_with_config(
            "sneakers_sg.size_selector", self.region, must_exist=True,
            operation="点击尺寸选择"
        )
      
        # 输入size
        self.safe_actions.safe_input_with_config(
            "sneakers_sg.size_search_input", str(enriched_info.size), self.region, must_exist=True,
            operation="输入尺寸搜索"
        )

        self.page.wait_for_timeout(2000)

        # 点击查找的size
        self.safe_actions.safe_click_with_config(
            "sneakers_sg.size_option", self.region, must_exist=True,
            operation="点击选择尺寸"
        )

        # 点击 多产品销售复选框
        self.safe_actions.safe_click_with_config(
            "sneakers_sg.multi_quantity_checkbox", self.region, must_exist=False,
            operation="点击多产品销售复选框"
        )
    
    
    def _handle_meetup_settings(self, enriched_info: ProductInfo):
        """处理面交设置"""
        # 检查是否存在已选好的面交地点
        meetup_input_selector = self.safe_actions.css_manager.get_selector(
            "sneakers_sg.meetup_input", self.region, "primary"
        ) or "input.D_tk"
        
        if not self.page.query_selector(meetup_input_selector):
            logger.info("页面中不存在已选好的面交地点，执行面交相关操作")
            
            # 开启面交
            self.safe_actions.safe_click_with_config(
                "sneakers_sg.meetup_toggle_sg", self.region, must_exist=True,
                operation="开启面交"
            )

            # 点击面交地点选择框
            self.safe_actions.safe_input_with_config(
                "sneakers_sg.meetup_input", enriched_info.meetup_location, self.region, must_exist=True,
                operation="输入面交地点"
            )
            
            self.page.wait_for_timeout(2000)
            
            # 选择面交地点
            self.safe_actions.safe_click_with_config(
                "sneakers_sg.meetup_option", self.region, must_exist=True,
                operation="选择面交地点"
            )
        else:
            logger.info("页面中存在已选好的面交地点，跳过面交相关操作")

    def _handle_other_settings(self):
        """处理其他设置 - 仅用于直上传方式"""
        # 条件判断：关闭送货
        delivery_check_selector = "button.D_ol"  # 检查是否已关闭送货
        if not self.page.query_selector(delivery_check_selector):
            logger.info("关闭送货")
            self.safe_actions.safe_click_with_config(
                "sneakers_sg.delivery_toggle_sg", self.region, must_exist=True,
                operation="关闭送货"
            )
        else:
            logger.info("跳过关闭送货操作")

        # 条件判断：关闭买家保障
        buyer_protection_check_selector = "span.D_aNX"  # 检查是否存在买家保障提示
        if self.page.query_selector(buyer_protection_check_selector):
            logger.info("关闭买家保障")
            self.safe_actions.safe_click_with_config(
                "sneakers_sg.platform_payment_close", self.region, must_exist=True,
                operation="关闭买家保障"
            )
            self.safe_actions.safe_click_with_config(
                "sneakers_sg.confirm_platform_payment", self.region, must_exist=True,
                operation="确认关闭买家保障"
            )
        else:
            logger.info("跳过关闭买家保障操作")