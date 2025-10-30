import signal
import sys
from core.config import create_upload_config
from browser.browser import start_browser, check_browser_api_health, initialize_browser_interface
from browser.browser_selector import select_browser_type, get_browser_display_name
from uploader.core.carousell_uploader import CarousellUploader
from core.models import ProductInfo
from core.logger import logger
from uploader.multi.multi_account_uploader import MultiAccountUploader
from uploader.actions.enhanced_safe_actions import set_unattended_mode
from data.excel_parser import ExcelProductParser

# 全局变量用于跟踪程序状态
program_running = True
current_uploader = None

def signal_handler(signum, frame):
    """信号处理函数，处理键盘中断"""
    global program_running, current_uploader
    
    logger.warning("\n" + "⚠️" + "=" * 50 + "⚠️")
    logger.warning(" " * 18 + "🛑 程序中断请求 🛑")
    logger.warning("⚠️" + "=" * 50 + "⚠️")
    logger.warning(" " * 15 + "检测到键盘中断信号 (Ctrl+C/Command+C)")
    logger.warning(" " * 15 + "正在安全退出程序...")
    
    # 记录中断日志
    logger.warning("用户请求中断程序 (KeyboardInterrupt)")
    
    # 如果有正在运行的上传器，尝试安全关闭
    if current_uploader:
        try:
            logger.info(" " * 15 + "🔄 正在关闭浏览器...")
            # 这里可以添加浏览器关闭逻辑
            logger.info("正在安全关闭浏览器...")
        except Exception as e:
            logger.warning(f"关闭浏览器时出错: {e}")
    
    program_running = False
    logger.info(" " * 15 + "✅ 程序已安全退出")
    logger.info(" " * 15 + "感谢使用 Carousell Uploader!")
    logger.warning("⚠️" + "=" * 50 + "⚠️")
    
    # 优雅退出
    sys.exit(0)

def setup_signal_handlers():
    """设置信号处理器"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # 终止信号
    
    # 在Windows上还需要处理其他信号
    if sys.platform == "win32":
        try:
            signal.signal(signal.SIGBREAK, signal_handler)  # Windows Ctrl+Break
        except AttributeError:
            pass

def run():
    """主运行函数"""
    # 设置信号处理器
    setup_signal_handlers()
    
    try:
        # 加载配置
        config = create_upload_config()
        logger.info("开始执行 Carousell 多账号上传任务")
        
        # 输出基础配置信息到日志 - 优化版本
        logger.info("🔧" + "=" * 48 + "🔧")
        logger.info(" " * 18 + "⚙️ 系统配置信息 ⚙️")
        logger.info("🔧" + "=" * 48 + "🔧")
        logger.info(f"🖼️ 支持图片格式: {', '.join(config.image_extensions)}")
        logger.info(f"📝 商品描述数量: {len(config.descriptions)}")
        logger.info(f"👨 男性尺码: {', '.join(config.male_sizes)}")
        logger.info(f"👩 女性尺码: {', '.join(config.female_sizes)}")
        # 显示各地域面交地点数量
        for region, locations in config.meetup_locations.items():
            logger.info(f"📍 {region}地域面交地点数量: {len(locations)}")
        logger.info("🔧" + "=" * 30 + "🔧")
        
        # 指纹浏览器选择 - 第一个用户输入参数
        logger.info("\n" + "🔧" + "=" * 30 + "🔧")
        logger.info(" " * 12 + "🌐 指纹浏览器选择 🌐")
        logger.info("🔧" + "=" * 30 + "🔧")
        logger.info(" " * 12 + "请选择您使用的指纹浏览器类型:")
        logger.info("")
        logger.info(" " * 8 + "1. 🔵 BitBrowser")
        logger.info(" " * 8 + "2. 🟢 IxBrowser")
        logger.info("")
        
        while True:
            try:
                choice = input(" " * 12 + "🎯 请输入选择 (1/2): ").strip()
                if choice == "1":
                    browser_type = "bitBrowser"
                    browser_name = "BitBrowser"
                    break
                elif choice == "2":
                    browser_type = "ixBrowser"
                    browser_name = "IxBrowser"
                    break
                else:
                    logger.warning(" " * 12 + "❌ 无效选择，请输入 1 或 2")
            except KeyboardInterrupt:
                logger.warning("\n❌ 用户取消选择")
                return
        
        logger.info(f"✅ 已选择指纹浏览器: {browser_name} ({browser_type})")
        
        # 获取选择的浏览器配置
        selected_browser_config = config.all_browser_configs[browser_type]
        
        # 初始化浏览器接口
        browser_config = {
            "type": browser_type,
            "api_port": selected_browser_config["api_port"],
            "api_key": selected_browser_config["api_key"]
        }
        
        # 初始化浏览器接口
        browser_interface = initialize_browser_interface(browser_config)
        logger.info(f"✅ 浏览器接口已初始化: {browser_name}")
        
        # 显示浏览器API配置信息
        logger.info("🌐 浏览器API配置 🌐")
        logger.info(f"🌐 浏览器类型: {browser_name} ({browser_type})")
        logger.info(f"🌐 浏览器API地址: http://127.0.0.1:{selected_browser_config['api_port']}")
        logger.info(f"🔑 浏览器API_KEY: {selected_browser_config['api_key']}")
        logger.info("🔧" + "=" * 30 + "🔧")
        
        # 检查浏览器API健康状态 - 立即检查
        logger.info("🔍 正在检查浏览器API健康状态...")
        if not check_browser_api_health(selected_browser_config["api_port"], selected_browser_config["api_key"]):
            logger.error("❌ 浏览器API健康检查失败，程序退出")
            logger.error("请检查以下项目:")
            logger.error("1. 浏览器服务是否已启动")
            logger.error("2. API端口是否正确")
            logger.error("3. API密钥是否正确")
            logger.error("4. 浏览器类型配置是否正确")
            logger.error("请修改配置文件后重新运行程序")
            return
        
        logger.info("✅ 浏览器API健康检查通过，继续执行...")
        
        # 获取用户输入
        excel_path = input("请输入 Excel 文件路径: ").strip()
        if not excel_path:
            logger.error("Excel 文件路径不能为空")
            return
        
        # 地域选择 - 优化版本
        logger.info("\n" + "🌍" + "=" * 30 + "🌍")
        logger.info(" " * 12 + "📍 请选择上传地域 📍")
        logger.info("🌍" + "=" * 30 + "🌍")
        logger.info(" " * 8 + "1. 🇭🇰 HK (香港)")
        logger.info(" " * 8 + "2. 🇲🇾 MY (马来西亚)")
        logger.info(" " * 8 + "3. 🇸🇬 SG (新加坡)")
        
        while True:
            try:
                region_choice = input("\n" + " " * 8 + "🎯 请输入选择 (1/2/3): ").strip()
                region_mapping = {"1": "HK", "2": "MY", "3": "SG"}
                
                if region_choice in region_mapping:
                    region = region_mapping[region_choice]
                    logger.info(f"✅ 选择的地域: {region}")
                    break
                else:
                    logger.warning(" " * 8 + "❌ 无效选择，请输入 1、2 或 3")
            except KeyboardInterrupt:
                logger.warning("\n❌ 用户取消选择")
                return
        
        # 选择商品类目 - 优化版本
        logger.info("\n" + "📦" + "=" * 30 + "📦")
        logger.info(" " * 12 + "🛍️ 请选择商品类目 🛍️")
        logger.info("📦" + "=" * 30 + "📦")
        logger.info(" " * 8 + "1. 👟 sneakers (运动鞋)")
        logger.info(" " * 8 + "2. 👜 bags (包包)")
        logger.info(" " * 8 + "3. 👕 clothes (服装)")
        
        while True:
            try:
                category_choice = input("\n" + " " * 8 + "🎯 请输入选择 (1/2/3): ").strip()
                category_mapping = {"1": "sneakers", "2": "bags", "3": "clothes"}
                
                if category_choice in category_mapping:
                    category = category_mapping[category_choice]
                    logger.info(f"✅ 选择的类目: {category}")
                    break
                else:
                    logger.warning(" " * 8 + "❌ 无效选择，请输入 1、2 或 3")
            except KeyboardInterrupt:
                logger.warning("\n❌ 用户取消选择")
                return
        
        # 运行模式选择（默认有人值守）
        logger.info("\n" + "🧭" + "=" * 30 + "🧭")
        logger.info(" " * 12 + "🔧 请选择运行模式 🔧")
        logger.info("🧭" + "=" * 30 + "🧭")
        logger.info(" " * 8 + "1. 👤 有人值守（默认）")
        logger.info(" " * 8 + "2. 🤖 无人值守（遇到选择器更新时自动使用当前主选择器）")

        unattended = False
        try:
            mode_choice = input("\n" + " " * 8 + "🎯 请输入选择 (1/2，默认1): ").strip()
            if mode_choice == "2":
                unattended = True
        except KeyboardInterrupt:
            logger.warning("\n❌ 用户取消选择，使用默认模式：有人值守")
            unattended = False

        set_unattended_mode(unattended)
        logger.info(f"✅ 已选择运行模式: {'无人值守' if unattended else '有人值守'}")

        # 创建多账号上传器
        multi_uploader = MultiAccountUploader(config, excel_path, region, category)
        
        # 显示历史记录摘要 - 优化版本
        record_summary = multi_uploader.record_manager.get_record_summary(excel_path, region)
        if record_summary['total_products'] > 0:
            logger.info("📊" + "=" * 50 + "📊")
            logger.info(" " * 18 + "📈 历史记录摘要 📈")
            logger.info("📊" + "=" * 50 + "📊")
            logger.info(f" " * 15 + "🌐 已成功浏览器数量: {record_summary['total_browsers']} 🏢")
            logger.info(f" " * 15 + "📦 已成功商品数量: {record_summary['total_products']} 🛍️")
            logger.info(f" " * 15 + "🔍 浏览器详情: {record_summary['browser_details']} 🌐")
            logger.info("📊" + "=" * 50 + "📊")
        else:
            logger.info("📊" + "=" * 50 + "📊")
            logger.info(" " * 18 + "🆕 无历史记录 🆕")
            logger.info(" " * 15 + "将执行完整上传 🚀")
            logger.info("📊" + "=" * 50 + "📊")
        
        # 设置当前上传器，用于中断处理
        global current_uploader
        current_uploader = multi_uploader
        
        # 执行上传循环
        result = multi_uploader.run_upload_cycle()
        
        if result['success']:
            logger.info("✅ 所有账号上传完成！ ✅")
            logger.info("🎯 任务执行成功 🎯")
        else:
            logger.error(f"❌ 上传过程中出现错误: {result.get('message', '未知错误')}")
            logger.error("⚠️ 请检查日志详情 ⚠️")
        
        # 显示详细结果
        logger.info("\n" + "🎊" + "=" * 60 + "🎊")
        logger.info(" " * 22 + "📊 上传结果详情 📊")
        logger.info("🎊" + "=" * 60 + "🎊")
        
        # 居中显示统计信息 
        logger.info(" " * 18 + f"🔢 总账号数: {result.get('total_accounts', 0)}")
        logger.info(" " * 18 + f"📦 总商品数: {result.get('total_products', 0)}")
        logger.info(" " * 18 + f"✅ 成功数量: {result.get('success_count', 0)}")
        logger.info(" " * 18 + f"❌ 失败数量: {result.get('failed_count', 0)}")
        logger.info(" " * 18 + f"📈 成功率: {result.get('success_rate', 0.0):.2f}%")
        
        if result.get('failed_count', 0) > 0:
            logger.warning("\n" + " " * 18 + "⚠️  失败的商品详情:")
            for account in result.get('account_details', []):
                # 安全地检查失败商品列表
                failed_products = account.get('failed_products', [])
                if failed_products:
                    logger.warning(" " * 22 + f"🌐 浏览器 {account.get('browser_id', 'Unknown')}: {', '.join(failed_products)}")
                else:
                    # 如果没有具体的失败商品列表，显示账号级别的失败信息
                    if account.get('failed_count', 0) > 0:
                        logger.warning(" " * 22 + f"🌐 浏览器 {account.get('browser_id', 'Unknown')}: {account.get('failed_count', 0)} 个商品失败")
        
        # 天天爆单
        logger.info("\n" + "🚀" + "=" * 60 + "🚀")
        logger.info(" " * 22 + "💰 天天爆单 💰")
        logger.info(" " * 18 + "❄️ 订单如雪花飘来 ❄️")
        logger.info(" " * 18 + "💎 财富如潮水涌来 💎")
        logger.info(" " * 18 + "🔥 生意红火到爆表 🔥")
        logger.info(" " * 18 + "⭐ 每天都是爆单日 ⭐")
        logger.info(" " * 18 + "💪 努力就有好收获 💪")
        logger.info(" " * 18 + "🎊 恭喜发财发大财 🎊")
        logger.info(" " * 18 + "🏆 业绩翻倍不是梦 🏆")
        logger.info(" " * 18 + "💸 钞票滚滚来不停 💸")
        logger.info(" " * 18 + "🎉 爆单爆单再爆单 🎉")
        logger.info("🚀" + "=" * 60 + "🚀")
        
        # 所有数据执行完成后，程序自动退出
        logger.info("\n" + " " * 22 + "🔵 所有任务完成，程序自动退出... 🔵")
        logger.info("所有任务完成，程序自动退出")
        
    except KeyboardInterrupt:
        # 处理键盘中断
        logger.warning("\n" + "⚠️" + "=" * 50 + "⚠️")
        logger.warning(" " * 18 + "🛑 程序中断请求 🛑")
        logger.warning("⚠️" + "=" * 50 + "⚠️")
        logger.warning(" " * 15 + "检测到键盘中断信号 (Ctrl+C/Command+C)")
        logger.warning(" " * 15 + "正在安全退出程序...")
        
        logger.warning("用户请求中断程序 (KeyboardInterrupt)")
        
        # 如果有正在运行的上传器，尝试安全关闭
        if current_uploader:
            try:
                logger.info(" " * 15 + "🔄 正在关闭浏览器...")
                logger.info("正在安全关闭浏览器...")
            except Exception as e:
                logger.warning(f"关闭浏览器时出错: {e}")
        
        logger.info(" " * 15 + "✅ 程序已安全退出")
        logger.info(" " * 15 + "感谢使用 Carousell Uploader!")
        logger.warning("⚠️" + "=" * 50 + "⚠️")
        
    except Exception as e:
        logger.error(f"程序执行出错: {e}")
        logger.error(f"\n❌ 程序执行出错: {e}")
        logger.error("请检查日志文件获取详细信息")
        raise

if __name__ == "__main__":
    run()
