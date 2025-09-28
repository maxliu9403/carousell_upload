"""
专门创建 ai_writing_cancel.png 模板的工具
基于现有的 ImageClicker 实现
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


def create_ai_cancel_template():
    """创建 ai_writing_cancel.png 模板"""
    print("🎯 创建 ai_writing_cancel.png 模板")
    print("=" * 60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # 导航到Carousell页面
            print("🌐 正在导航到Carousell页面...")
            page.goto("https://www.carousell.com.hk/sell", wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            
            # 创建图片点击器
            image_clicker = ImageClicker(page)
            
            print("\n📝 创建指南:")
            print("1. 在浏览器中找到'取消AI编写'或'取消'按钮")
            print("2. 右键点击按钮，选择'检查元素'")
            print("3. 在开发者工具中，右键点击按钮元素")
            print("4. 选择'Capture node screenshot'")
            print("5. 保存截图到 templates/ai_writing/ai_writing_cancel.png")
            
            print("\n或者使用交互式截图:")
            print("输入按钮的坐标信息 (x,y,width,height)")
            print("例如: 100,200,150,40")
            
            # 检查是否已有模板
            template_path = image_clicker.ai_templates_dir / "ai_writing_cancel.png"
            if template_path.exists():
                size = template_path.stat().st_size
                print(f"\n✅ 发现现有模板: {template_path.name} ({size} bytes)")
                
                # 测试现有模板
                print("\n🧪 测试现有模板...")
                result = test_template(image_clicker)
                if result:
                    print("✅ 模板测试成功!")
                else:
                    print("⚠️ 模板测试失败，建议重新创建")
            else:
                print("\n⚠️ 未发现现有模板")
                print("请按照指南创建模板")
            
            # 等待用户操作
            input("\n按回车键继续...")
            
        except Exception as e:
            print(f"❌ 创建模板失败: {e}")
            return False
        finally:
            browser.close()
    
    return True


def interactive_capture():
    """交互式截图 ai_writing_cancel.png"""
    print("📸 交互式截图 ai_writing_cancel.png")
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
            print("1. 找到页面上的'取消AI编写'或'取消'按钮")
            print("2. 输入按钮的坐标信息")
            print("3. 按回车键截图")
            print("4. 输入 'q' 退出")
            
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
                    
                    # 保存为 ai_writing_cancel.png
                    template_path = image_clicker.ai_templates_dir / "ai_writing_cancel.png"
                    
                    if image_clicker.save_template(str(template_path), (x, y, w, h), "AI编写取消按钮"):
                        print(f"✅ 模板已创建: {template_path}")
                        
                        # 测试新创建的模板
                        print("🧪 测试新模板...")
                        if test_template(image_clicker):
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


def test_template(image_clicker):
    """测试模板匹配"""
    try:
        template_path = image_clicker.ai_templates_dir / "ai_writing_cancel.png"
        if not template_path.exists():
            print("❌ 模板文件不存在")
            return False
        
        print("🔍 测试模板匹配...")
        thresholds = [0.8, 0.7, 0.6]
        
        for threshold in thresholds:
            print(f"   尝试阈值: {threshold}")
            match_result = image_clicker.find_image_on_page(str(template_path), threshold)
            if match_result:
                x, y, w, h = match_result
                print(f"   ✅ 找到匹配: ({x}, {y}, {w}, {h}) 置信度: {threshold}")
                return True
            else:
                print(f"   ❌ 未找到匹配 (阈值: {threshold})")
        
        print("❌ 所有阈值都未找到匹配")
        return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_click_functionality():
    """测试点击功能"""
    print("🖱️ 测试点击功能")
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
            
            # 测试点击功能
            print("🔍 测试点击功能...")
            template_path = image_clicker.ai_templates_dir / "ai_writing_cancel.png"
            
            if template_path.exists():
                print("✅ 模板文件存在，开始测试点击...")
                result = image_clicker.click_image(str(template_path), threshold=0.7)
                
                if result:
                    print("✅ 点击测试成功!")
                else:
                    print("❌ 点击测试失败")
                
                return result
            else:
                print("❌ 模板文件不存在")
                return False
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False
        finally:
            browser.close()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI编写取消按钮模板工具")
    parser.add_argument("--capture", action="store_true", help="交互式截图模板")
    parser.add_argument("--test", action="store_true", help="测试模板匹配")
    parser.add_argument("--click", action="store_true", help="测试点击功能")
    
    args = parser.parse_args()
    
    if args.capture:
        interactive_capture()
    elif args.test:
        # 测试现有模板
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            try:
                page.goto("https://www.carousell.com.hk/sell", wait_until="domcontentloaded")
                page.wait_for_timeout(3000)
                image_clicker = ImageClicker(page)
                test_template(image_clicker)
            finally:
                browser.close()
    elif args.click:
        test_click_functionality()
    else:
        create_ai_cancel_template()


if __name__ == "__main__":
    main()
