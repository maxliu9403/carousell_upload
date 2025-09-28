"""
AI文案按钮模板创建工具
用于创建和管理图片匹配模板
"""

import os
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from uploader.image_clicker import ImageClicker
from playwright.sync_api import sync_playwright


def create_ai_writing_templates():
    """创建AI文案相关的图片模板"""
    print("🎨 开始创建AI文案按钮模板")
    print("=" * 60)
    
    # 启动浏览器
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 非无头模式，方便截图
        page = browser.new_page()
        
        try:
            # 导航到Carousell页面
            print("🌐 正在导航到Carousell页面...")
            page.goto("https://www.carousell.com.hk/sell", wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            
            # 创建图片点击器
            image_clicker = ImageClicker(page)
            
            print("\n📝 模板创建指南:")
            print("1. 在浏览器中找到'改為手動填寫'或'取消AI编写'按钮")
            print("2. 右键点击按钮，选择'检查元素'")
            print("3. 在开发者工具中，右键点击按钮元素")
            print("4. 选择'Capture node screenshot'或'截图节点'")
            print("5. 保存截图到 templates/ai_writing/ 目录")
            print("\n推荐的文件名:")
            print("- manual_writing_button_hk.png (HK地域手动填写按钮)")
            print("- manual_writing_button_sg.png (SG地域手动填写按钮)")
            print("- ai_writing_cancel.png (取消AI编写按钮)")
            print("- manual_writing_text.png (手动填写文本)")
            
            # 检查是否已有模板
            templates_dir = Path("templates/ai_writing")
            if templates_dir.exists():
                existing_templates = list(templates_dir.glob("*.png"))
                if existing_templates:
                    print(f"\n✅ 发现现有模板: {len(existing_templates)} 个")
                    for template in existing_templates:
                        size = template.stat().st_size
                        print(f"   📄 {template.name} ({size} bytes)")
                    
                    # 测试现有模板
                    print("\n🧪 测试现有模板...")
                    test_result = image_clicker.click_ai_writing_button("all")
                    if test_result:
                        print("✅ 模板测试成功!")
                    else:
                        print("⚠️ 模板测试失败，可能需要更新模板")
                    
                    return True
            
            print("\n⚠️ 未发现现有模板")
            print("请按照上述指南手动创建模板")
            
            # 等待用户操作
            input("\n按回车键继续...")
            
        except Exception as e:
            print(f"❌ 创建模板失败: {e}")
            return False
        finally:
            browser.close()
    
    return True


def capture_template_interactive():
    """交互式截图模板"""
    print("📸 交互式模板截图工具")
    print("=" * 60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # 导航到页面
            print("🌐 正在导航到Carousell页面...")
            page.goto("https://www.carousell.com.hk/sell", wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            
            # 创建图片点击器
            image_clicker = ImageClicker(page)
            
            print("\n📝 截图指南:")
            print("1. 找到页面上的'改為手動填寫'或'取消AI编写'按钮")
            print("2. 输入按钮的坐标信息")
            print("3. 按回车键截图")
            print("4. 输入 'q' 退出")
            print("\n💡 提示: 截图会自动保存到 templates/ai_writing/ 目录")
            
            while True:
                print("\n请输入按钮坐标信息:")
                print("格式: x,y,width,height")
                print("例如: 100,200,150,40")
                print("输入 'q' 退出")
                
                user_input = input("坐标: ").strip()
                
                if user_input.lower() == 'q':
                    print("👋 退出截图工具")
                    break
                
                try:
                    x, y, w, h = map(int, user_input.split(','))
                    
                    template_name = f"ai_writing_template_{int(time.time())}"
                    if image_clicker.create_template_from_screenshot(template_name, x, y, w, h):
                        print(f"✅ 模板已创建: {template_name}")
                        
                        # 测试新创建的模板
                        print("🧪 测试新模板...")
                        if image_clicker.click_ai_writing_button("all"):
                            print("✅ 模板测试成功!")
                        else:
                            print("⚠️ 模板测试失败")
                    else:
                        print("❌ 模板创建失败")
                        
                except ValueError:
                    print("❌ 坐标格式错误，请使用格式: x,y,width,height")
                except Exception as e:
                    print(f"❌ 截图失败: {e}")
            
        except Exception as e:
            print(f"❌ 截图工具失败: {e}")
            return False
        finally:
            browser.close()
    
    return True


def list_existing_templates():
    """列出现有模板"""
    print("📋 现有AI文案模板列表")
    print("=" * 60)
    
    templates_dir = Path("templates/ai_writing")
    if not templates_dir.exists():
        print("❌ 模板目录不存在")
        return False
    
    templates = list(templates_dir.glob("*.png"))
    if not templates:
        print("⚠️ 没有找到模板文件")
        return False
    
    print(f"✅ 找到 {len(templates)} 个模板:")
    for i, template in enumerate(templates, 1):
        size = template.stat().st_size
        print(f"   {i}. {template.name} ({size} bytes)")
    
    return True


def test_template_matching():
    """测试模板匹配"""
    print("🧪 测试模板匹配功能")
    print("=" * 60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # 导航到页面
            print("🌐 正在导航到Carousell页面...")
            page.goto("https://www.carousell.com.hk/sell", wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            
            # 创建图片点击器
            image_clicker = ImageClicker(page)
            
            # 测试模板匹配
            print("🔍 开始测试模板匹配...")
            result = image_clicker.click_ai_writing_button("all")
            
            if result:
                print("✅ 模板匹配成功!")
            else:
                print("❌ 模板匹配失败")
            
            return result
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False
        finally:
            browser.close()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI文案按钮模板管理工具")
    parser.add_argument("--capture", action="store_true", help="交互式截图模板")
    parser.add_argument("--list", action="store_true", help="列出现有模板")
    parser.add_argument("--test", action="store_true", help="测试模板匹配")
    
    args = parser.parse_args()
    
    if args.capture:
        capture_template_interactive()
    elif args.list:
        list_existing_templates()
    elif args.test:
        test_template_matching()
    else:
        create_ai_writing_templates()


if __name__ == "__main__":
    main()
