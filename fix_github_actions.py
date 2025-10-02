#!/usr/bin/env python3
"""
GitHub Actions 快速修复脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def init_git_repo():
    """初始化Git仓库"""
    print("🔧 初始化Git仓库...")
    
    if not Path(".git").exists():
        try:
            subprocess.run(["git", "init"], check=True)
            print("✅ Git仓库初始化成功")
        except subprocess.CalledProcessError:
            print("❌ Git仓库初始化失败")
            return False
    else:
        print("✅ Git仓库已存在")
    
    return True

def create_gitignore():
    """创建.gitignore文件"""
    print("🔧 创建.gitignore文件...")
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Temporary files
*.tmp
*.temp
"""
    
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        print("✅ .gitignore文件已创建")
    else:
        print("✅ .gitignore文件已存在")
    
    return True

def create_simple_workflow():
    """创建简化的工作流"""
    print("🔧 创建简化的工作流...")
    
    # 确保目录存在
    workflow_dir = Path(".github/workflows")
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建简化的工作流
    simple_workflow = """name: Build Windows Executable

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v4
    
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
      uses: actions/upload-artifact@v4
      with:
        name: CarousellUploader-Windows
        path: dist/CarousellUploader.exe
        retention-days: 30
"""
    
    workflow_file = workflow_dir / "build-windows.yml"
    with open(workflow_file, 'w', encoding='utf-8') as f:
        f.write(simple_workflow)
    
    print("✅ 简化工作流已创建")
    return True

def commit_and_push():
    """提交并推送代码"""
    print("🔧 提交并推送代码...")
    
    try:
        # 添加所有文件
        subprocess.run(["git", "add", "."], check=True)
        print("✅ 文件已添加到暂存区")
        
        # 提交
        subprocess.run(["git", "commit", "-m", "Add GitHub Actions workflow"], check=True)
        print("✅ 代码已提交")
        
        # 检查远程仓库
        result = subprocess.run(["git", "remote", "-v"], capture_output=True, text=True)
        if result.returncode == 0 and "github.com" in result.stdout:
            # 推送
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("✅ 代码已推送到GitHub")
        else:
            print("⚠️ 未配置GitHub远程仓库")
            print("💡 请手动配置: git remote add origin https://github.com/username/repo.git")
            return False
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 操作失败: {e}")
        return False

def show_next_steps():
    """显示下一步操作"""
    print("\n🎯 下一步操作:")
    print("=" * 50)
    
    print("\n1. 检查GitHub仓库")
    print("   - 访问你的GitHub仓库")
    print("   - 点击 'Actions' 标签")
    print("   - 查看 'Build Windows Executable' 工作流")
    
    print("\n2. 手动触发工作流")
    print("   - 在Actions页面点击工作流")
    print("   - 点击 'Run workflow' 按钮")
    print("   - 选择分支并点击 'Run workflow'")
    
    print("\n3. 查看构建结果")
    print("   - 等待构建完成（约5-10分钟）")
    print("   - 点击构建任务查看日志")
    print("   - 在 'Artifacts' 部分下载可执行文件")
    
    print("\n4. 如果构建失败")
    print("   - 查看构建日志中的错误信息")
    print("   - 根据错误信息修复问题")
    print("   - 重新提交代码触发构建")

def main():
    """主函数"""
    print("🔧 GitHub Actions 快速修复工具")
    print("=" * 50)
    
    steps = [
        ("初始化Git仓库", init_git_repo),
        ("创建.gitignore文件", create_gitignore),
        ("创建简化工作流", create_simple_workflow),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        try:
            if step_func():
                print(f"✅ {step_name}成功")
            else:
                print(f"❌ {step_name}失败")
                return False
        except Exception as e:
            print(f"❌ {step_name}异常: {e}")
            return False
    
    # 询问是否提交代码
    print("\n" + "=" * 50)
    try:
        choice = input("是否现在提交并推送代码到GitHub? (y/n): ").strip().lower()
        if choice in ['y', 'yes', '是']:
            if commit_and_push():
                print("✅ 代码已推送到GitHub")
                show_next_steps()
            else:
                print("❌ 推送失败，请手动操作")
        else:
            print("💡 请手动执行以下命令:")
            print("   git add .")
            print("   git commit -m 'Add GitHub Actions workflow'")
            print("   git push origin main")
    except KeyboardInterrupt:
        print("\n⚠️ 操作被用户中断")
    
    return True

if __name__ == "__main__":
    main()
