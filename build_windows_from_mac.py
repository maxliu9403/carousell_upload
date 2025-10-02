#!/usr/bin/env python3
"""
Carousell Uploader - macOS快速构建Windows可执行文件
"""

import sys
import subprocess
from pathlib import Path

def main():
    """主函数 - 快速构建Windows可执行文件"""
    print("🚀 Carousell Uploader - macOS快速构建Windows可执行文件")
    print("=" * 60)
    
    # 检查构建脚本是否存在
    build_script = Path("build_macos_to_windows.py")
    if not build_script.exists():
        print("❌ 构建脚本不存在")
        return False
    
    # 显示选项
    print("\n🎯 选择构建方式:")
    print("1. GitHub Actions（推荐，最简单）")
    print("2. Docker方式（本地构建）")
    print("3. 查看所有方案")
    
    try:
        choice = input("\n请输入选择 (1-3): ").strip()
        
        if choice == "1":
            print("\n🚀 使用GitHub Actions构建...")
            subprocess.run([sys.executable, "build_macos_to_windows.py", "--method", "github"])
        elif choice == "2":
            print("\n🐳 使用Docker构建...")
            subprocess.run([sys.executable, "build_macos_to_windows.py", "--method", "docker"])
        elif choice == "3":
            print("\n📋 查看所有方案...")
            subprocess.run([sys.executable, "build_macos_to_windows.py", "--method", "alternatives"])
        else:
            print("❌ 无效选择")
            return False
        
        print("\n✅ 构建配置完成！")
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️ 构建被用户中断")
        return False
    except Exception as e:
        print(f"\n❌ 构建失败: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
