#!/usr/bin/env python3
"""
Carousell Uploader - macOS到Windows构建脚本
在macOS上构建Windows可执行文件
"""

import os
import sys
import subprocess
import platform
import argparse
from pathlib import Path

def check_environment():
    """检查构建环境"""
    print("🔍 检查构建环境...")
    
    # 检查操作系统
    if platform.system() != "Darwin":
        print("⚠️ 警告: 当前系统不是macOS")
        return False
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要3.8+")
        return False
    
    print(f"✅ 当前系统: {platform.system()}")
    print(f"✅ Python版本: {sys.version}")
    return True

def install_docker():
    """安装Docker"""
    print("🐳 检查Docker...")
    
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        print("✅ Docker已安装")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("📦 安装Docker...")
        try:
            subprocess.run(["brew", "install", "--cask", "docker"], check=True)
            print("✅ Docker安装成功")
            return True
        except subprocess.CalledProcessError:
            print("❌ Docker安装失败")
            print("💡 请手动安装Docker Desktop: https://www.docker.com/products/docker-desktop")
            return False

def build_with_docker():
    """使用Docker构建Windows可执行文件"""
    print("🐳 使用Docker构建Windows可执行文件...")
    
    # 检查Dockerfile是否存在
    dockerfile = Path("Dockerfile.windows")
    if not dockerfile.exists():
        print("❌ Dockerfile.windows不存在")
        return False
    
    try:
        # 构建Docker镜像
        print("🔧 构建Docker镜像...")
        subprocess.run([
            "docker", "build", 
            "-f", "Dockerfile.windows",
            "-t", "carousell-builder",
            "."
        ], check=True)
        
        # 运行容器并复制构建结果
        print("🚀 运行构建容器...")
        subprocess.run([
            "docker", "run", 
            "--name", "carousell-build",
            "carousell-builder"
        ], check=True)
        
        # 复制构建结果
        print("📁 复制构建结果...")
        subprocess.run([
            "docker", "cp", 
            "carousell-build:/app/dist/CarousellUploader.exe",
            "dist/"
        ], check=True)
        
        # 清理容器
        subprocess.run(["docker", "rm", "carousell-build"], check=True)
        
        print("✅ Docker构建成功！")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker构建失败: {e}")
        return False

def setup_github_actions():
    """设置GitHub Actions"""
    print("🚀 设置GitHub Actions...")
    
    # 检查是否在Git仓库中
    if not Path(".git").exists():
        print("❌ 当前目录不是Git仓库")
        print("💡 请先初始化Git仓库: git init")
        return False
    
    # 检查GitHub Actions工作流是否存在
    workflow_file = Path(".github/workflows/build-windows.yml")
    if not workflow_file.exists():
        print("❌ GitHub Actions工作流不存在")
        return False
    
    print("✅ GitHub Actions工作流已配置")
    print("\n📋 使用步骤:")
    print("1. 提交代码到GitHub:")
    print("   git add .")
    print("   git commit -m 'Add Windows build workflow'")
    print("   git push origin main")
    print("2. 在GitHub Actions页面查看构建进度")
    print("3. 下载构建结果")
    
    return True

def show_alternatives():
    """显示替代方案"""
    print("\n🎯 在macOS上构建Windows可执行文件的方案:")
    print("=" * 60)
    
    print("\n1. 🐳 Docker方式（推荐）")
    print("   ✅ 优点: 简单、可靠、跨平台")
    print("   ❌ 缺点: 需要安装Docker")
    print("   💡 命令: python3 build_macos_to_windows.py --method docker")
    
    print("\n2. 🚀 GitHub Actions方式（最简单）")
    print("   ✅ 优点: 无需本地配置、自动构建")
    print("   ❌ 缺点: 需要GitHub账号")
    print("   💡 命令: python3 build_macos_to_windows.py --method github")
    
    print("\n3. 🖥️ 虚拟机方式")
    print("   ✅ 优点: 完全原生Windows环境")
    print("   ❌ 缺点: 需要大量资源、配置复杂")
    print("   💡 需要: VirtualBox/VMware + Windows镜像")
    
    print("\n4. ☁️ 云服务方式")
    print("   ✅ 优点: 无需本地资源")
    print("   ❌ 缺点: 需要云服务账号")
    print("   💡 服务: AWS, Azure, GCP等")
    
    print("\n5. 🍷 Wine方式（实验性）")
    print("   ✅ 优点: 轻量级")
    print("   ❌ 缺点: 不稳定、兼容性问题")
    print("   💡 命令: brew install wine-stable")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Carousell Uploader macOS到Windows构建工具")
    parser.add_argument("--method", choices=["docker", "github", "alternatives"], default="alternatives",
                       help="构建方法: docker, github, alternatives")
    parser.add_argument("--setup-only", action="store_true",
                       help="仅设置环境，不执行构建")
    
    args = parser.parse_args()
    
    print("🚀 Carousell Uploader - macOS到Windows构建工具")
    print("=" * 60)
    print("💡 在macOS上构建Windows可执行文件")
    
    # 检查环境
    if not check_environment():
        sys.exit(1)
    
    # 根据选择的方法执行
    if args.method == "docker":
        if install_docker():
            if not args.setup_only:
                build_with_docker()
    elif args.method == "github":
        setup_github_actions()
    elif args.method == "alternatives":
        show_alternatives()
    
    print("\n🎉 构建配置完成！")
    print("\n📋 下一步:")
    if args.method == "docker":
        print("1. 运行: python3 build_macos_to_windows.py --method docker")
        print("2. 等待Docker构建完成")
        print("3. 在dist/目录找到CarousellUploader.exe")
    elif args.method == "github":
        print("1. 提交代码到GitHub")
        print("2. 在Actions页面查看构建进度")
        print("3. 下载构建结果")
    else:
        print("1. 选择适合的构建方法")
        print("2. 按照说明进行配置")
        print("3. 执行构建命令")

if __name__ == "__main__":
    main()
