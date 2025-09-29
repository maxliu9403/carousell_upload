import argparse
import sys
from pathlib import Path
from core.config import create_upload_config
from browser.browser import start_browser, check_browser_api_health
from uploader.core.carousell_uploader import CarousellUploader
from core.models import ProductInfo
from core.logger import logger

def create_product_info_from_args(args) -> ProductInfo:
    """从命令行参数创建商品信息"""
    return ProductInfo(
        title=args.title,
        price=args.price,
        category=args.category,
        brand=args.brand or "",
        condition=args.condition,
        gender=args.gender,
        location=args.location,
        multi_quantity=args.multi_quantity
    )

def main():
    """命令行主函数"""
    parser = argparse.ArgumentParser(description="Carousell 自动上传工具")
    
    # 商品信息参数
    parser.add_argument("--title", required=True, help="商品标题")
    parser.add_argument("--price", required=True, help="商品价格")
    parser.add_argument("--category", default="others", help="商品类目")
    parser.add_argument("--brand", help="品牌")
    parser.add_argument("--condition", choices=["new", "used"], default="new", help="新旧程度")
    parser.add_argument("--gender", choices=["male", "female", "unisex"], default="unisex", help="性别")
    parser.add_argument("--location", default="All of Singapore", help="位置")
    parser.add_argument("--multi-quantity", action="store_true", help="是否多产品销售")
    
    # 其他选项
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    try:
        # 设置日志级别
        if args.verbose:
            logger.setLevel(logger.DEBUG)
        
        # 加载配置
        config = create_upload_config()
        logger.info("开始执行 Carousell 上传任务")
        
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
            sys.exit(1)
        
        logger.info("✅ 浏览器API健康检查通过，继续执行...")
        
        # 启动浏览器（使用默认profile_id，实际应用中应该通过BrowserID动态获取）
        # 注意：这里需要根据实际需求调整，可能需要从Excel或其他地方获取BrowserID
        playwright, browser, page = start_browser(
            config.api_port, 
            config.api_key, 
            "default_profile_id"  # 临时使用默认值，实际应该动态获取
        )
        
        # 创建上传器（CLI模式默认使用SG地域和sneakers类目）
        uploader = CarousellUploader(page, config, "SG")
        
        # 执行完整流程（上传商品 + 管理商品列表）
        product_info = create_product_info_from_args(args)
        # 注意：CLI模式下需要指定文件夹路径，这里使用默认路径
        default_folder = "/Users/liuxiang/Desktop/262/modified"  # 可以根据需要调整
        # CLI模式默认使用sneakers类目
        success = uploader.upload_product(product_info, default_folder, "sneakers")
        
        if not success:
            logger.error("完整流程执行失败")
            sys.exit(1)
        
        input("🔵 按回车键结束脚本并关闭浏览器...")
        
    except KeyboardInterrupt:
        logger.info("用户中断程序")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序执行出错: {e}")
        sys.exit(1)
    finally:
        try:
            browser.close()
            playwright.stop()
            logger.info("浏览器已关闭")
        except:
            pass

if __name__ == "__main__":
    main()

