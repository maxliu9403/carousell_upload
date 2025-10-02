#!/usr/bin/env python3
"""
GitHub Actions 诊断脚本
检查GitHub Actions配置是否正确
"""

import os
import sys
import subprocess
from pathlib import Path

def check_git_repo():
    """检查是否在Git仓库中"""
    print("🔍 检查Git仓库...")
    
    if not Path(".git").exists():
        print("❌ 当前目录不是Git仓库")
        print("💡 解决方案: git init")
        return False
    
    try:
        result = subprocess.run(["git", "status"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git仓库正常")
            return True
        else:
            print(f"❌ Git仓库异常: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Git未安装")
        return False

def check_github_remote():
    """检查GitHub远程仓库"""
    print("🔍 检查GitHub远程仓库...")
    
    try:
        result = subprocess.run(["git", "remote", "-v"], capture_output=True, text=True)
        if result.returncode == 0:
            if "github.com" in result.stdout:
                print("✅ GitHub远程仓库已配置")
                return True
            else:
                print("❌ 未配置GitHub远程仓库")
                print("💡 解决方案: git remote add origin https://github.com/username/repo.git")
                return False
        else:
            print(f"❌ 无法获取远程仓库信息: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Git未安装")
        return False

def check_workflow_files():
    """检查工作流文件"""
    print("🔍 检查工作流文件...")
    
    workflow_dir = Path(".github/workflows")
    if not workflow_dir.exists():
        print("❌ .github/workflows目录不存在")
        return False
    
    workflow_files = list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml"))
    if not workflow_files:
        print("❌ 没有找到工作流文件")
        return False
    
    print(f"✅ 找到 {len(workflow_files)} 个工作流文件:")
    for file in workflow_files:
        print(f"  - {file.name}")
    
    return True

def check_workflow_syntax():
    """检查工作流语法"""
    print("🔍 检查工作流语法...")
    
    workflow_dir = Path(".github/workflows")
    for workflow_file in workflow_dir.glob("*.yml"):
        print(f"检查 {workflow_file.name}...")
        
        # 简单的YAML语法检查
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查基本语法
            if "name:" in content and "on:" in content and "jobs:" in content:
                print(f"✅ {workflow_file.name} 语法正确")
            else:
                print(f"❌ {workflow_file.name} 语法错误")
                return False
        except Exception as e:
            print(f"❌ {workflow_file.name} 读取失败: {e}")
            return False
    
    return True

def check_required_files():
    """检查必需文件"""
    print("🔍 检查必需文件...")
    
    required_files = [
        "cli/main.py",
        "requirements.txt",
        "config/settings.yaml"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ 缺少必需文件:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    print("✅ 所有必需文件都存在")
    return True

def check_branch():
    """检查当前分支"""
    print("🔍 检查当前分支...")
    
    try:
        result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
        if result.returncode == 0:
            current_branch = result.stdout.strip()
            print(f"✅ 当前分支: {current_branch}")
            
            # 检查是否是main或master分支
            if current_branch in ["main", "master"]:
                print("✅ 分支名称正确")
                return True
            else:
                print("⚠️ 分支名称不是main或master")
                print("💡 工作流只在main/master分支触发")
                return False
        else:
            print(f"❌ 无法获取当前分支: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Git未安装")
        return False

def show_troubleshooting():
    """显示故障排除建议"""
    print("\n🔧 故障排除建议:")
    print("=" * 50)
    
    print("\n1. 检查GitHub仓库设置")
    print("   - 确保仓库是公开的或你有推送权限")
    print("   - 检查Actions是否已启用")
    print("   - 访问: https://github.com/username/repo/settings/actions")
    
    print("\n2. 检查工作流文件")
    print("   - 确保文件在 .github/workflows/ 目录中")
    print("   - 确保文件扩展名是 .yml 或 .yaml")
    print("   - 确保YAML语法正确")
    
    print("\n3. 检查触发条件")
    print("   - push: 推送到main/master分支")
    print("   - pull_request: 创建PR到main/master分支")
    print("   - workflow_dispatch: 手动触发")
    
    print("\n4. 检查分支名称")
    print("   - 确保当前分支是main或master")
    print("   - 或者修改工作流文件中的分支名称")
    
    print("\n5. 手动触发工作流")
    print("   - 访问GitHub仓库的Actions页面")
    print("   - 点击对应的工作流")
    print("   - 点击'Run workflow'按钮")
    
    print("\n6. 查看工作流日志")
    print("   - 在Actions页面点击失败的运行")
    print("   - 查看详细的错误信息")
    print("   - 根据错误信息进行修复")

def main():
    """主函数"""
    print("🔍 GitHub Actions 诊断工具")
    print("=" * 50)
    
    checks = [
        ("Git仓库", check_git_repo),
        ("GitHub远程仓库", check_github_remote),
        ("工作流文件", check_workflow_files),
        ("工作流语法", check_workflow_syntax),
        ("必需文件", check_required_files),
        ("当前分支", check_branch),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 检查 {name}...")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ 检查失败: {e}")
            results.append((name, False))
    
    # 总结结果
    print("\n" + "=" * 50)
    print("📊 检查结果:")
    
    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有检查都通过！GitHub Actions应该能正常工作")
        print("\n💡 下一步:")
        print("1. 提交代码: git add . && git commit -m 'Add GitHub Actions'")
        print("2. 推送到GitHub: git push origin main")
        print("3. 查看Actions页面: https://github.com/username/repo/actions")
    else:
        print("\n⚠️ 发现问题，请根据上述检查结果进行修复")
        show_troubleshooting()

if __name__ == "__main__":
    main()
