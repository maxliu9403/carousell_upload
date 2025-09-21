from typing import Optional
from playwright.sync_api import Page  # pyright: ignore[reportMissingImports]
from .models import ProductInfo, UploadConfig
from .actions import (
    click_with_wait, 
    upload_folder_with_keyboard, 
    human_delay, 
    input_with_wait, 
    scroll_page
)
from .logger import logger
from .utils import enrich_product_info

class CarousellUploader:
    """Carousell 上传器主类"""
    
    def __init__(self, page: Page, config: UploadConfig):
        self.page = page
        self.config = config
        
    def upload_product(self, product_info: ProductInfo, folder_path: str = None) -> bool:
        """
        完整的商品上传和管理流程 - 严格按照原始源代码逻辑实现
        包含：上传商品 + 管理商品列表的完整流程
        """
        try:
            logger.info(f"开始执行完整流程: {product_info.title}")
            
            # 丰富商品信息（添加随机生成的 description、size、meetup_location）
            enriched_info = enrich_product_info(product_info, self.config)
            
            # ========= 第一部分：上传商品 =========
            self.page.goto("https://www.carousell.sg/")
            logger.info("🌐 已打开目标页面")

            # 第一次点击
            click_with_wait(self.page, ".D_AT > div", must_exist=True)

            # 第二次点击 - 弹出文件窗口
            click_with_wait(self.page, "div.D_JM", must_exist=True)
            logger.info("✅ 第二次点击完成，等待文件选择窗口...")
            human_delay(1.5, 2.5)

            # 上传文件夹
            if folder_path:
                upload_folder_with_keyboard(folder_path, set(self.config.image_extensions))
            else:
                raise ValueError("folder_path参数不能为空")

            # 第三次点击（可选）
            click_with_wait(self.page, ".D_ayX > .D_oI > .D_oU", must_exist=False)

            # 忽略AI
            click_with_wait(self.page, ".D_o_ use", must_exist=False)

            # 点击产品类目选择
            click_with_wait(self.page, "div.D_aES", must_exist=True)

            # 输入其他服务
            input_with_wait(self.page, "input.D_Kf", "others", must_exist=True)

            # 异常处理
            click_with_wait(self.page, ".D_oK > .D_oU", must_exist=False)

            # 选择服务
            click_with_wait(self.page, ".D_aEZ:nth-child(2) > .D_aFi", must_exist=True)

            # 输入产品标题
            input_with_wait(self.page, "input#title", enriched_info.title, must_exist=True)

            # 输入产品价格
            input_with_wait(self.page, "input#price", enriched_info.price, must_exist=True)

            # 输入产品描述
            input_with_wait(self.page, "textarea.D_uI", enriched_info.description, must_exist=True)

            # 新加坡 - 点击 选择 Location
            click_with_wait(self.page, "input.D_tA", must_exist=False)

            # 新加坡 - 选择 All of Singapore
            click_with_wait(self.page, ".D_bLC:nth-child(2) > .D_lO", must_exist=False)

            # 新加坡 - 点击上传
            click_with_wait(self.page, ".D_wO > .D_oU", must_exist=False)

            self.page.wait_for_timeout(5000)

            # ========= 第二部分：管理商品列表 =========
            logger.info("开始管理商品列表")
            
            # 进入管理页面
            self.page.goto("https://www.carousell.sg/manage-listings/")
            logger.info("🌐 已打开目标页面")

            # 点击 未活跃
            click_with_wait(self.page, "button.D_buS:nth-child(2)", must_exist=True)

            # 点击 未活跃第一个元素
            click_with_wait(self.page, "tr:nth-child(1) .D_bwo", must_exist=True)

            # 点击编辑
            click_with_wait(self.page, ".D_bpA:nth-child(1) > .D_lO", must_exist=True)

            # 点击 波鞋
            click_with_wait(self.page, "p.D_mk:nth-child(1)", must_exist=True)
            # 新加坡 输入其他服务
            input_with_wait(self.page, "input.D_Kf", "sneakers", must_exist=True)
            # 通过判断选择时男装还是女装，需要传入参数
            # 点击 男装波鞋
            click_with_wait(self.page, ".D_aEZ:nth-child(2) > .D_aFi > .D_lO", must_exist=True)

            # 点击女装波鞋
            # click_with_wait(self.page, ".D_aEZ:nth-child(3) > .D_aFi > .D_lO", must_exist=True)

            # 点击 新旧
            click_with_wait(self.page, ".D_ahq:nth-child(2) .D_op:nth-child(1) > .D_lO", must_exist=True)

            # 点击 品牌
            click_with_wait(self.page, "#FieldSetField-Container-field_brand_enum .D_sx", must_exist=True)

            # 点击搜索品牌
            input_with_wait(self.page, ".D_vs .D_Kf", "other", must_exist=True)

            # 点击other
            click_with_wait(self.page, ".D_abY > .D_acf > .D_lO", must_exist=True)

            # 输入品牌
            input_with_wait(self.page, "input#brand", enriched_info.brand, must_exist=True)
            
            # 点击szie
            click_with_wait(self.page, "#FieldSetField-Container-field_size .D_sx", must_exist=True)

            # 输入size
            input_with_wait(self.page, ".D_vs .D_Kf", enriched_info.size, must_exist=True)

            # 点击查找的size
            click_with_wait(self.page, ".D_abT:nth-child(1) .D_abY > .D_acf > .D_lO", must_exist=True)

            # 点击 多产品销售复选框
            click_with_wait(self.page, "#FieldSetField-Container-field_multi_quantities .D_a_N", must_exist=False)

            # 开启面交
            click_with_wait(self.page, ".D_pO > .D_lO", must_exist=True)

            # 点击面交地点选择框
            input_with_wait(self.page, "input.D_tA", enriched_info.meetup_location, must_exist=True)
            
            # 选择面交地点
            click_with_wait(self.page, "div.D_cCl:nth-child(2)", must_exist=True)

            # 点击发布
            click_with_wait(self.page, ".D_wa > .D_oU", must_exist=True)

            # 进入新页面
            self.page.goto("https://www.carousell.sg/manage-listings/")
            logger.info("🌐 已打开目标页面")

            # 点击 未活跃
            click_with_wait(self.page, "button.D_buS:nth-child(2)", must_exist=True)

            # 点击 激活
            click_with_wait(self.page, "tr:nth-child(1) .D_bw_ .D_lO", must_exist=True)

            # 点击确认激活
            click_with_wait(self.page, "button.D_na", must_exist=True)

            logger.info("完整流程执行成功")
            return True
            
        except Exception as e:
            logger.error(f"完整流程执行失败: {product_info.title}, 错误: {e}")
            return False

