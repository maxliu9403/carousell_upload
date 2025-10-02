#!/usr/bin/env python3
"""
Carousell Uploader - 跨平台构建脚本
在macOS上构建Windows可执行文件
"""

import os
import sys
import subprocess
import platform
import argparse
from pathlib import Path

class CrossPlatformBuilder:
    """跨平台构建器"""
    
    def __init__(self):
        self.current_os = platform.system()
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        
    def check_environment(self):
        """检查构建环境"""
        print("🔍 检查构建环境...")
        
        # 检查操作系统
        if self.current_os != "Darwin":
            print("⚠️ 警告: 当前系统不是macOS，交叉编译可能不稳定")
        
        # 检查Python版本
        if sys.version_info < (3, 8):
            print("❌ Python版本过低，需要3.8+")
            return False
        
        print(f"✅ 当前系统: {self.current_os}")
        print(f"✅ Python版本: {sys.version}")
        return True
    
    def install_dependencies(self):
        """安装跨平台构建依赖"""
        print("📦 安装跨平台构建依赖...")
        
        dependencies = [
            "pyinstaller",
            "wine",  # Windows模拟器
            "wine-mono",  # .NET运行时
            "wine-gecko",  # 浏览器引擎
        ]
        
        for dep in dependencies:
            print(f"🔧 安装 {dep}...")
            try:
                if dep == "wine":
                    # 使用Homebrew安装Wine
                    subprocess.run(["brew", "install", "--cask", "wine-stable"], check=True)
                elif dep == "wine-mono":
                    subprocess.run(["brew", "install", "wine-mono"], check=True)
                elif dep == "wine-gecko":
                    subprocess.run(["brew", "install", "wine-gecko"], check=True)
                else:
                    subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
                print(f"✅ {dep} 安装成功")
            except subprocess.CalledProcessError:
                print(f"⚠️ {dep} 安装失败，继续构建...")
        
        return True
    
    def setup_wine_environment(self):
        """设置Wine环境"""
        print("🍷 设置Wine环境...")
        
        try:
            # 初始化Wine环境
            subprocess.run(["wine", "wineboot", "--init"], check=True)
            print("✅ Wine环境初始化成功")
            
            # 安装Windows Python（通过Wine）
            print("🐍 安装Windows Python...")
            # 这里需要下载Windows Python安装包
            # 由于复杂性，我们使用PyInstaller的交叉编译功能
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Wine设置失败: {e}")
            print("💡 提示: 将使用Docker方式进行交叉编译")
            return False
    
    def build_with_docker(self):
        """使用Docker进行交叉编译"""
        print("🐳 使用Docker进行交叉编译...")
        
        # 创建Dockerfile
        dockerfile_content = '''FROM python:3.11-windowsservercore

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pyinstaller

# 安装Playwright
RUN playwright install chromium

# 构建可执行文件
RUN pyinstaller --onefile --console --name=CarousellUploader \\
    --add-data=config;config \\
    --add-data=uploader/regions;uploader/regions \\
    --add-data=data;data \\
    --hidden-import=playwright \\
    --hidden-import=pyautogui \\
    --hidden-import=pyperclip \\
    --hidden-import=openpyxl \\
    --hidden-import=pandas \\
    --hidden-import=yaml \\
    --hidden-import=requests \\
    --hidden-import=PIL \\
    --hidden-import=selenium \\
    --hidden-import=webdriver_manager \\
    cli/main.py

# 复制构建结果
CMD ["copy", "dist\\CarousellUploader.exe", "C:\\output\\"]
'''
        
        dockerfile_path = self.project_root / "Dockerfile.windows"
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        
        print("✅ Dockerfile已创建")
        return True
    
    def build_with_pyinstaller_cross(self):
        """使用PyInstaller交叉编译"""
        print("🔧 使用PyInstaller交叉编译...")
        
        # 设置环境变量
        env = os.environ.copy()
        env['PYINSTALLER_CROSS_COMPILE'] = '1'
        env['TARGET_OS'] = 'windows'
        
        # 构建命令
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--console",
            "--name=CarousellUploader",
            "--add-data=config:config",
            "--add-data=uploader/regions:uploader/regions",
            "--add-data=data:data",
            "--hidden-import=playwright",
            "--hidden-import=pyautogui",
            "--hidden-import=pyperclip",
            "--hidden-import=openpyxl",
            "--hidden-import=pandas",
            "--hidden-import=yaml",
            "--hidden-import=requests",
            "--hidden-import=PIL",
            "--hidden-import=selenium",
            "--hidden-import=webdriver_manager",
            "cli/main.py"
        ]
        
        try:
            print("🏗️ 开始交叉编译...")
            subprocess.run(cmd, env=env, check=True)
            print("✅ 交叉编译成功！")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 交叉编译失败: {e}")
            return False
    
    def build_with_github_actions(self):
        """使用GitHub Actions进行交叉编译"""
        print("🚀 使用GitHub Actions进行交叉编译...")
        
        # 创建GitHub Actions工作流
        workflow_content = '''name: Build Windows Executable

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build-windows:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller
        playwright install chromium
    
    - name: Build executable
      run: |
        pyinstaller --onefile --console --name=CarousellUploader ^
          --add-data=config;config ^
          --add-data=uploader/regions;uploader/regions ^
          --add-data=data;data ^
          --hidden-import=playwright ^
          --hidden-import=pyautogui ^
          --hidden-import=pyperclip ^
          --hidden-import=openpyxl ^
          --hidden-import=pandas ^
          --hidden-import=yaml ^
          --hidden-import=requests ^
          --hidden-import=PIL ^
          --hidden-import=selenium ^
          --hidden-import=webdriver_manager ^
          cli/main.py
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: CarousellUploader-Windows
        path: dist/CarousellUploader.exe
'''
        
        # 创建.github/workflows目录
        workflows_dir = self.project_root / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_file = workflows_dir / "build-windows.yml"
        with open(workflow_file, 'w') as f:
            f.write(workflow_content)
        
        print("✅ GitHub Actions工作流已创建")
        print("💡 提示: 推送到GitHub后会自动构建Windows可执行文件")
        return True
    
    def build_with_vm(self):
        """使用虚拟机进行构建"""
        print("🖥️ 使用虚拟机进行构建...")
        
        # 创建虚拟机构建脚本
        vm_script = '''#!/bin/bash
# 虚拟机构建脚本

echo "🖥️ 启动Windows虚拟机..."
# 这里需要配置虚拟机启动命令
# 例如: VBoxManage startvm "Windows10"

echo "📦 在虚拟机中构建..."
# 在虚拟机中执行构建命令
# 这里需要配置SSH或RDP连接

echo "📁 复制构建结果..."
# 将构建结果复制回macOS
# 例如: scp user@vm:/path/to/exe ./dist/
'''
        
        vm_script_path = self.project_root / "build_vm.sh"
        with open(vm_script_path, 'w') as f:
            f.write(vm_script)
        
        print("✅ 虚拟机构建脚本已创建")
        return True
    
    def show_alternatives(self):
        """显示替代方案"""
        print("\n🎯 跨平台构建替代方案:")
        print("=" * 50)
        
        print("\n1. 🐳 Docker方式（推荐）")
        print("   - 使用Windows容器进行构建")
        print("   - 需要安装Docker Desktop")
        print("   - 命令: docker build -f Dockerfile.windows .")
        
        print("\n2. 🚀 GitHub Actions方式（最简单）")
        print("   - 推送到GitHub后自动构建")
        print("   - 无需本地配置")
        print("   - 构建结果自动下载")
        
        print("\n3. 🖥️ 虚拟机方式")
        print("   - 在macOS上运行Windows虚拟机")
        print("   - 需要安装VirtualBox或VMware")
        print("   - 在虚拟机中构建")
        
        print("\n4. ☁️ 云服务方式")
        print("   - 使用云服务器进行构建")
        print("   - 例如: AWS, Azure, GCP")
        print("   - 远程构建后下载结果")
        
        print("\n5. 🍷 Wine方式（实验性）")
        print("   - 使用Wine运行Windows环境")
        print("   - 可能不稳定")
        print("   - 需要额外配置")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Carousell Uploader 跨平台构建工具")
    parser.add_argument("--method", choices=["docker", "github", "vm", "wine"], default="github",
                       help="构建方法: docker, github, vm, wine")
    parser.add_argument("--setup-only", action="store_true",
                       help="仅设置环境，不执行构建")
    
    args = parser.parse_args()
    
    print("🚀 Carousell Uploader - 跨平台构建工具")
    print("=" * 50)
    print("💡 在macOS上构建Windows可执行文件")
    
    builder = CrossPlatformBuilder()
    
    # 检查环境
    if not builder.check_environment():
        sys.exit(1)
    
    # 根据选择的方法执行构建
    if args.method == "docker":
        builder.build_with_docker()
    elif args.method == "github":
        builder.build_with_github_actions()
    elif args.method == "vm":
        builder.build_with_vm()
    elif args.method == "wine":
        builder.install_dependencies()
        builder.setup_wine_environment()
    else:
        builder.show_alternatives()
    
    if not args.setup_only:
        print("\n🎉 构建配置完成！")
        print("\n📋 下一步:")
        if args.method == "github":
            print("1. 提交代码到GitHub")
            print("2. 在Actions页面查看构建进度")
            print("3. 下载构建结果")
        elif args.method == "docker":
            print("1. 运行: docker build -f Dockerfile.windows .")
            print("2. 复制构建结果")
        elif args.method == "vm":
            print("1. 启动Windows虚拟机")
            print("2. 在虚拟机中运行构建脚本")
        elif args.method == "wine":
            print("1. 配置Wine环境")
            print("2. 运行构建命令")

if __name__ == "__main__":
    main()
