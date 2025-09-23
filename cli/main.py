from core.config import create_upload_config
from browser.browser import start_browser, check_browser_api_health
from uploader.carousell_uploader import CarousellUploader
from core.models import ProductInfo
from core.logger import logger
from uploader.multi_account_uploader import MultiAccountUploader
from data.excel_parser import ExcelProductParser

def run():
    """主运行函数"""
    try:
        # 加载配置
        config = create_upload_config()
        logger.info("开始执行 Carousell 多账号上传任务")
        
        # 输出配置信息到日志
        logger.info("=" * 50)
        logger.info("系统配置信息:")
        logger.info(f"  浏览器API地址: http://127.0.0.1:{config.api_port}")
        logger.info(f"  浏览器API_KEY: {config.api_key}")
        logger.info(f"  支持图片格式: {', '.join(config.image_extensions)}")
        logger.info(f"  商品描述数量: {len(config.descriptions)}")
        logger.info(f"  男性尺码: {', '.join(config.male_sizes)}")
        logger.info(f"  女性尺码: {', '.join(config.female_sizes)}")
        # 显示各地域面交地点数量
        for region, locations in config.meetup_locations.items():
            logger.info(f"  {region}地域面交地点数量: {len(locations)}")
        logger.info("=" * 50)
        
        # 检查浏览器API健康状态
        logger.info("🔍 正在检查浏览器API健康状态...")
        if not check_browser_api_health(config.api_port, config.api_key):
            logger.error("❌ 浏览器API健康检查失败，程序退出")
            logger.error("请检查以下项目:")
            logger.error("1. 浏览器服务是否已启动")
            logger.error("2. API端口是否正确")
            logger.error("3. API密钥是否正确")
            return
        
        logger.info("✅ 浏览器API健康检查通过，继续执行...")
        
        # 获取用户输入
        excel_path = input("请输入 Excel 文件路径: ").strip()
        if not excel_path:
            logger.error("Excel 文件路径不能为空")
            return
        
        # 地域选择
        print("\n请选择上传地域:")
        print("1. HK (香港)")
        print("2. MY (马来西亚)")
        print("3. SG (新加坡)")
        
        region_choice = input("请输入选择 (1/2/3): ").strip()
        region_mapping = {"1": "HK", "2": "MY", "3": "SG"}
        
        if region_choice not in region_mapping:
            logger.error("无效的地域选择")
            return
        
        region = region_mapping[region_choice]
        logger.info(f"选择的地域: {region}")
        
        # 选择商品类目
        print("\n请选择商品类目:")
        print("1. sneakers (运动鞋)")
        print("2. bags (包包)")
        print("3. clothes (服装)")
        
        category_choice = input("请输入选择 (1/2/3): ").strip()
        category_mapping = {"1": "sneakers", "2": "bags", "3": "clothes"}
        
        if category_choice not in category_mapping:
            logger.error("无效的类目选择")
            return
        
        category = category_mapping[category_choice]
        logger.info(f"选择的类目: {category}")
        
        # 创建多账号上传器
        multi_uploader = MultiAccountUploader(config, excel_path, region, category)
        
        # 显示历史记录摘要
        record_summary = multi_uploader.record_manager.get_record_summary(excel_path, region)
        if record_summary['total_products'] > 0:
            logger.info("📊 历史记录摘要:")
            logger.info(f"  已成功浏览器数量: {record_summary['total_browsers']}")
            logger.info(f"  已成功商品数量: {record_summary['total_products']}")
            logger.info(f"  浏览器详情: {record_summary['browser_details']}")
        else:
            logger.info("📊 无历史记录，将执行完整上传")
        
        # 执行上传循环
        result = multi_uploader.run_upload_cycle()
        
        if result['success']:
            logger.info("所有账号上传完成！")
        else:
            logger.error(f"上传过程中出现错误: {result.get('message', '未知错误')}")
        
        # 显示详细结果
        print("\n" + "=" * 60)
        print("上传结果详情:")
        print(f"总账号数: {result['total_accounts']}")
        print(f"总商品数: {result['total_products']}")
        print(f"成功数量: {result['success_count']}")
        print(f"失败数量: {result['failed_count']}")
        print(f"成功率: {result['success_rate']:.2f}%")
        
        if result['failed_count'] > 0:
            print("\n失败的商品:")
            for account in result['account_details']:
                if account['failed_products']:
                    print(f"  浏览器 {account['browser_id']}: {', '.join(account['failed_products'])}")
        
        print("=" * 60)
        
        input("🔵 按回车键结束程序...")
        
    except Exception as e:
        logger.error(f"程序执行出错: {e}")
        raise

if __name__ == "__main__":
    run()
