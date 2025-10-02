#!/usr/bin/env python3
"""
Carousell Uploader - 快速构建脚本
这是一个便捷的构建入口，实际构建逻辑在 build/ 文件夹中
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """主函数 - 调用build文件夹中的构建脚本"""
    print("🚀 Carousell Uploader - 快速构建")
    print("=" * 50)
    
    # 检查build文件夹是否存在
    build_dir = Path("build")
    if not build_dir.exists():
        print("❌ build文件夹不存在，请检查项目结构")
        return False
    
    # 检查构建脚本是否存在
    build_script = build_dir / "build.py"
    if not build_script.exists():
        print("❌ 构建脚本不存在，请检查build文件夹")
        return False
    
    # 构建命令
    cmd = [sys.executable, str(build_script)] + sys.argv[1:]
    
    print(f"🔧 执行构建命令: {' '.join(cmd)}")
    print("=" * 50)
    
    try:
        # 执行构建脚本
        result = subprocess.run(cmd, check=True)
        print("\n✅ 构建完成！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 构建失败: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⚠️ 构建被用户中断")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)