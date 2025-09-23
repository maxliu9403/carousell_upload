from typing import Optional
from playwright.sync_api import Page  # pyright: ignore[reportMissingImports]
from core.models import ProductInfo, UploadConfig
from browser.actions import (
    click_with_wait, 
    upload_folder_with_keyboard, 
    human_delay, 
    input_with_wait, 
    smart_goto
)
from core.logger import logger
from .utils import enrich_product_info

class CarousellUploader:
    """Carousell 上传器主类"""
    
    def __init__(self, page: Page, config: UploadConfig, region: str = "SG"):
        self.page = page
        self.config = config
        self.region = region
        
    def _get_domain_by_region(self) -> str:
        """根据地域获取对应的域名"""
        if self.region not in self.config.domains:
            logger.warning(f"未找到地域 {self.region} 的域名配置，使用默认地域 SG")
            self.region = "SG"
        
        domain = self.config.domains[self.region]
        logger.info(f"使用 {self.region} 地域域名: {domain}")
        return domain
        
    def upload_product(self, product_info: ProductInfo, folder_path: str = None, category: str = "sneakers") -> bool:
        """
        商品上传工厂函数 - 根据地域和类目选择不同的上传方法
        
        Args:
            product_info: 商品信息
            folder_path: 图片文件夹路径
            category: 商品类目 (sneakers, bags, clothes)
        """
        try:
            logger.info(f"开始执行完整流程: {product_info.title} (地域: {self.region}, 类目: {category})")
            
            # 验证类目是否支持
            if category not in self.config.categories:
                raise ValueError(f"不支持的类目: {category}，支持的类目: {list(self.config.categories.keys())}")
            
            # 丰富商品信息（添加随机生成的 description、size、meetup_location）
            enriched_info = enrich_product_info(product_info, self.config, self.region)
            
            # 根据类目选择上传方法
            upload_method = self._get_upload_method(category)
            return upload_method(enriched_info, folder_path)
            
        except Exception as e:
            logger.error(f"完整流程执行失败: {product_info.title}, 错误: {e}")
            return False
    
    def _get_upload_method(self, category: str):
        """根据类目获取对应的上传方法"""
        upload_methods = {
            "sneakers": self._upload_sneakers_by_service,
            # "bags": self._upload_bags,
            # "clothes": self._upload_clothes
        }
        
        if category not in upload_methods:
            raise ValueError(f"不支持的类目: {category}")
        
        return upload_methods[category]
    
    def _upload_sneakers_by_direct(self, enriched_info: ProductInfo, folder_path: str) -> bool:
        """运动鞋类目直上传方法"""
        try:
            logger.info("使用运动鞋类目上传方法")
            
            # ========= 第一部分：上传商品 =========
            self._upload_sneakers_by_direct(enriched_info, folder_path)
            
            # ========= 第二部分：发布商品 =========
            self._publish_product()

            logger.info("运动鞋上传流程执行成功")
            return True
            
        except Exception as e:
            logger.error(f"运动鞋上传流程执行失败: {e}")
            return False

    def _upload_sneakers_by_service(self, enriched_info: ProductInfo, folder_path: str) -> bool:
        """运动鞋跳服务上传方法"""
        try:
            logger.info("使用运动鞋类目上传方法")
            
            # ========= 第一部分：上传商品 =========
            self._upload_sneaker_by_service(enriched_info, folder_path)

            # ========= 第二部分：激活商品 =========
            self._activate_product()

            logger.info("运动鞋上传流程执行成功")
            return True
            
        except Exception as e:
            logger.error(f"运动鞋上传流程执行失败: {e}")
            return False
    
    def _upload_sneaker_by_service(self, enriched_info: ProductInfo, folder_path: str):
        """跳服务上传运动鞋商品"""
        # 第一步：上传服务商品
        self._upload_service_product(enriched_info, folder_path)
        
        # 第二步：编辑为运动鞋
        self._edit_to_sneakers(enriched_info)

        # 第三步：发布商品
        self._publish_product()

    def _upload_service_product(self, enriched_info: ProductInfo, folder_path: str):
        """上传服务商品，公共函数"""
        # 打开主页
        self._navigate_to_homepage()
        
        # 开始上传流程
        self._start_upload_flow(folder_path)
        
        # 选择服务类目
        self._select_service_category()
        
        # 填写基本信息
        self._fill_basic_info(enriched_info)
        
        # 选择地域相关设置
        self._select_location_by_region()
        
        # 发布商品
        self._publish_product()
        
        # 等待页面稳定
        self.page.wait_for_timeout(10000)

    def _edit_to_sneakers(self, enriched_info: ProductInfo):
        """编辑商品为运动鞋"""
        logger.info("开始编辑跳波鞋")
        
        # 进入管理页面
        self._navigate_to_manage_page()
        
        # 进入编辑模式
        self._enter_edit_mode()
        
        # 修改为运动鞋类目
        self._change_to_sneakers_category(enriched_info)
        
        # 填写运动鞋详细信息
        self._fill_sneakers_details(enriched_info)
        
        # 处理面交设置
        self._handle_meetup_settings(enriched_info)
        
        # 注意：跳服务方式不需要处理其他设置（关闭送货、买家保障等）

    def _navigate_to_homepage(self):
        """导航到主页"""
        domain = self._get_domain_by_region()
        smart_goto(self.page, f"{domain}/", wait_until="domcontentloaded", timeout=30000)
        logger.info("🌐 已打开目标页面")

    def _start_upload_flow(self, folder_path: str):
        """开始上传流程"""
        # 点击sell按钮
        click_with_wait(self.page, "a.D___", must_exist=True)

        # 点击上传图片
        click_with_wait(self.page, "div.D_JY", must_exist=True)
        logger.info("✅ 第二次点击完成，等待文件选择窗口...")
        human_delay(1.5, 2.5)

        # 上传文件夹
        if folder_path:
            upload_folder_with_keyboard(folder_path, set(self.config.image_extensions))
        else:
            raise ValueError("folder_path参数不能为空")

        # 新账号初次上品会出现（可选）
        click_with_wait(self.page, ".D_ayU > .D_oj > .D_ov", must_exist=False)

        # 忽略AI编写文案
        click_with_wait(self.page, ".D_oa use", must_exist=False)

    def _select_service_category(self):
        """选择服务类目"""
        # 选择类目
        click_with_wait(self.page, "div.D_aGp", must_exist=True)

        # 输入other，跳服务
        input_with_wait(self.page, "input.D_Kr", "others", must_exist=True)
        
        # 等待出现搜索结果
        self.page.wait_for_timeout(2000)
        # 点击服务
        self._safe_click_subcategory("div.D_aGw:nth-child(2)", "服務")

    def _fill_basic_info(self, enriched_info: ProductInfo):
        """填写基本信息"""
        # 输入产品标题
        input_with_wait(self.page, "input#title", enriched_info.title, must_exist=True)

        # 输入产品价格
        input_with_wait(self.page, "input#price", enriched_info.price, must_exist=True)

        # 输入产品描述
        input_with_wait(self.page, "textarea.D_tk", enriched_info.description, must_exist=True)

    def _navigate_to_manage_page(self):
        """导航到管理页面"""
        domain = self._get_domain_by_region()
        smart_goto(self.page, f"{domain}/manage-listings/", wait_until="domcontentloaded", timeout=30000)
        logger.info("🌐 已打开目标页面")

    def _enter_edit_mode(self):
        """进入编辑模式"""
        # 点击 未活跃
        click_with_wait(self.page, "button.D_buu:nth-child(2)", must_exist=True)

        # 点击 未活跃第一个元素
        click_with_wait(self.page, "div.D_bvN", must_exist=True) 

        # 编辑
        click_with_wait(self.page, ".D_bon:nth-child(1) > .D_lz", must_exist=True)

    def _change_to_sneakers_category(self, enriched_info: ProductInfo):
        """修改为运动鞋类目"""
        # 修改产品类目
        click_with_wait(self.page, "div.D_aGp", must_exist=True)

        # 输入运动鞋搜索关键词
        input_with_wait(self.page, ".D_aGu > .D_Kr", "sneakers", must_exist=True)

        # 根据性别选择子类目
        if enriched_info.gender.lower() in ["male", "men", "mens"]:
            # 点击 男装波鞋
            self._safe_click_subcategory(".D_aGw:nth-child(2) > .D_aGE", "男装波鞋")
        else:
            # 点击女装波鞋
            self._safe_click_subcategory(".D_aGw:nth-child(3) > .D_aGE", "女装波鞋")

    def _fill_sneakers_details(self, enriched_info: ProductInfo):
        """填写运动鞋详细信息"""
        # 点击 新旧
        click_with_wait(self.page, ".D_afX:nth-child(2) .D_pT:nth-child(1)", must_exist=True)

        # 点击 品牌
        click_with_wait(self.page, "#FieldSetField-Container-field_brand_enum .D_sp", must_exist=True)

        # 点击搜索品牌
        input_with_wait(self.page, ".D_vs .D_Kr", "other", must_exist=True)

        # 点击other品牌
        click_with_wait(self.page, "li.D_acO", must_exist=True)

        # 输入品牌
        input_with_wait(self.page, "input#brand", enriched_info.brand, must_exist=True)
        
        # 点击size
        click_with_wait(self.page, "#FieldSetField-Container-field_size .D_sp", must_exist=True)
      
        # 输入size
        input_with_wait(self.page, ".D_vs .D_Kr", str(enriched_info.size), must_exist=True)

        # 点击查找的size
        click_with_wait(self.page, ".D_acN:nth-child(1) .D_lz", must_exist=True)

        # 点击 多产品销售复选框
        click_with_wait(self.page, "#FieldSetField-Container-field_multi_quantities .D_axe", must_exist=False)

    def _handle_meetup_settings(self, enriched_info: ProductInfo):
        """处理面交设置"""
        # 检查是否存在 input.D_uN 选择器，如果不存在则执行面交相关操作
        if not self.page.query_selector("input.D_uN"):
            logger.info("页面中不存在已选好的面交地点，执行面交相关操作")
            
            # 开启面交
            click_with_wait(self.page, ".D_oz > .D_lz", must_exist=True)

            # 点击面交地点选择框
            input_with_wait(self.page, "input.D_uN", enriched_info.meetup_location, must_exist=True)
            
            # 选择面交地点
            click_with_wait(self.page, "div.D_cCv:nth-child(2)", must_exist=True)
        else:
            logger.info("页面中存在已选好的面交地点，跳过面交相关操作")

    def _handle_other_settings(self):
        """处理其他设置 - 仅用于直上传方式"""
        # 条件判断：关闭送货
        if not self.page.query_selector("button.D_ol"):
            logger.info("关闭送货")
            click_with_wait(self.page, "#FieldSetField-Container-field_delivery_v2 .D_oy", must_exist=True)
        else:
            logger.info("跳过关闭送货操作")

        # 条件判断：关闭买家保障
        if self.page.query_selector("span.D_aNX"):
            logger.info("关闭买家保障")
            click_with_wait(self.page, "#FieldSetField-Container-field_caroupay .D_oy", must_exist=True)
            click_with_wait(self.page, "button.D_Jp:nth-child(1)", must_exist=True)
        else:
            logger.info("跳过关闭买家保障操作")

    def _select_location_by_region(self):
        """根据地域选择Location"""
        # 新加坡 - 点击 选择 Location
        click_with_wait(self.page, "input.D_uN", must_exist=False)

        # 新加坡 - 选择 All of Singapore
        click_with_wait(self.page, "div.D_bKX:nth-child(2)", must_exist=False)

    def _upload_sneakers_by_direct(self, enriched_info: ProductInfo, folder_path: str):
        """直上传运动鞋"""
        # 打开主页
        self._navigate_to_homepage()
        
        # 开始上传流程
        self._start_upload_flow(folder_path)
        
        # 选择运动鞋类目
        self._select_sneakers_category_direct(enriched_info)
        
        # 填写基本信息
        self._fill_basic_info(enriched_info)
        
        # 填写运动鞋详细信息
        self._fill_sneakers_details_direct(enriched_info)
        
        # 处理面交设置
        self._handle_meetup_settings_direct(enriched_info)
        
        # 处理其他设置
        self._handle_other_settings()

    def _select_sneakers_category_direct(self, enriched_info: ProductInfo):
        """直接选择运动鞋类目"""
        # 选择类目
        click_with_wait(self.page, "div.D_aGp", must_exist=True)

        # 输入运动鞋搜索关键词
        input_with_wait(self.page, ".D_aGu > .D_Kr", "sneakers", must_exist=True)
        
        # 根据性别选择子类目
        if enriched_info.gender.lower() in ["male", "men", "mens"]:
            # 点击 男装波鞋
            self._safe_click_subcategory(".D_aGw:nth-child(2) > .D_aGE", "男装波鞋")
        else:
            # 点击女装波鞋
            self._safe_click_subcategory(".D_aGw:nth-child(3) > .D_aGE", "女装波鞋")

    def _fill_sneakers_details_direct(self, enriched_info: ProductInfo):
        """直接填写运动鞋详细信息"""
        # 点击 新旧
        click_with_wait(self.page, "#FieldSetField-Container-field_layered_condition .D_pT:nth-child(1)", must_exist=True)

        # 点击 品牌
        click_with_wait(self.page, "#FieldSetField-Container-field_brand_enum .D_sp", must_exist=True)

        # 点击搜索品牌
        input_with_wait(self.page, ".D_vs .D_Kr", "Other", must_exist=True)

        # 点击other
        click_with_wait(self.page, "li.D_acN", must_exist=True)

        # 输入品牌
        input_with_wait(self.page, "input#brand", enriched_info.brand, must_exist=True)

        # 点击size
        click_with_wait(self.page, "#FieldSetField-Container-field_size .D_sp", must_exist=True)

        # 输入size
        input_with_wait(self.page, ".D_vs .D_Kr", str(enriched_info.size), must_exist=True)

        # 点击查找的size
        click_with_wait(self.page, ".D_acN:nth-child(1) .D_lz", must_exist=True)

        # 输入产品描述
        input_with_wait(self.page, "textarea.D_tk", enriched_info.description, must_exist=True)

        # 输入产品价格
        input_with_wait(self.page, "input#price", enriched_info.price, must_exist=True)

    def _handle_meetup_settings_direct(self, enriched_info: ProductInfo):
        """直接处理面交设置"""
        # 检查是否存在 input.D_uN 选择器，如果不存在则执行面交相关操作
        if not self.page.query_selector("input.D_uN"):
            logger.info("页面中不存在已选好的面交地点，执行面交相关操作")
            
            # 开启面交
            click_with_wait(self.page, ".D_pO > .D_lO", must_exist=True)

            # 点击面交地点选择框
            input_with_wait(self.page, "input.D_tA", enriched_info.meetup_location, must_exist=True)
            
            # 选择面交地点
            click_with_wait(self.page, "div.D_cCl:nth-child(2)", must_exist=True)
        else:
            logger.info("页面中存在已选好的面交地点，跳过面交相关操作")

    def _safe_click_subcategory(self, selector: str, category_name: str):
        """安全点击子类目，处理DOM分离问题"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"尝试点击子类目: {category_name} (尝试 {attempt + 1}/{max_retries})")
                
                # 等待元素出现并稳定
                element = self.page.wait_for_selector(selector, timeout=5000)
                if not element:
                    logger.warning(f"子类目元素未找到: {selector}")
                    continue
                
                # 检查元素是否仍然连接到DOM
                if not element.is_visible():
                    logger.warning(f"子类目元素不可见: {selector}")
                    continue
                
                # 尝试点击
                element.click()
                human_delay(1.0, 2.0)
                logger.info(f"✅ 成功点击子类目: {category_name}")
                return True
                
            except Exception as e:
                logger.warning(f"点击子类目失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    # 等待页面稳定
                    human_delay(2.0, 3.0)
                    # 重新搜索关键词以刷新选项
                    try:
                        input_with_wait(self.page, "input.D_Kr", "sneakers", must_exist=True)
                        human_delay(1.0, 1.5)
                    except:
                        pass
                else:
                    logger.error(f"子类目点击最终失败: {category_name}")
                    raise

    def _publish_product(self):
        """第二部分：发布商品"""
        # 点击发布
        click_with_wait(self.page, "button.D_vx", must_exist=True)

    def _activate_product(self):
        """第五部分：激活商品"""
        domain = self._get_domain_by_region()
        smart_goto(self.page, f"{domain}/manage-listings/", wait_until="domcontentloaded", timeout=30000)
        logger.info("🌐 已打开目标页面")

        # 点击 未活跃
        click_with_wait(self.page, "button.D_buu:nth-child(2)", must_exist=True)

        # 点击 激活
        click_with_wait(self.page, "tr:nth-child(1) .D_bvZ .D_lz", must_exist=True)

        # 点击确认激活
        click_with_wait(self.page, "button.D_nb", must_exist=True)
