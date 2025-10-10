#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carousell Uploader 构建脚本 - 使用 PyInstaller 打包项目
支持 regions 中各地域 CSS 配置文件的外部配置
优化版：自动安装依赖、CI/CD 友好、日志统一化
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path
from datetime import datetime

class CarousellBuilder:
    """Carousell Uploader 构建器"""
    
    def __init__(self, keep_temp=False, onefile=True):
        """初始化构建器"""
        self.project_root = Path(__file__).parent.resolve()
        self.system = platform.system()
        self.separator = ";" if self.system == "Windows" else ":"
        self.build_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.app_name = "carousell_uploader"
        self.version = "1.0.0"
        self.entry_point = "cli/main.py"
        self.keep_temp = keep_temp
        self.onefile = onefile

        # 数据文件与目录
        self.data_includes = [
            ("config", "config"),
            ("uploader/regions", "uploader/regions"),
            ("example_products.xlsx", "."),
        ]

        # 排除模块
        self.excludes = ["tkinter","unittest","test","setuptools","pip","wheel"]

        # 隐藏导入
        self.hidden_imports = [
            # 第三方库
            "playwright","yaml","pandas","openpyxl","requests",
            "pyautogui","pyperclip",
            # pyautogui 的依赖
            "PIL","PIL._imaging","PIL.Image",
            "pymsgbox","pytweening","pyscreeze","mouseinfo",
            # 项目模块
            "core","core.config","core.logger","core.models",
            "browser","browser.browser","browser.actions","browser.browser_factory","browser.browser_interface","browser.browser_selector",
            "data","data.excel_parser","data.record_manager",
            "uploader","uploader.core","uploader.core.base_uploader","uploader.core.carousell_uploader",
            "uploader.actions","uploader.actions.enhanced_safe_actions",
            "uploader.config","uploader.config.enhanced_css_selector_manager","uploader.config.regional_config_loader",
            "uploader.factory","uploader.factory.uploader_factory",
            "uploader.multi","uploader.multi.multi_account_uploader",
            "uploader.utils","uploader.utils.utils",
            "uploader.regions","uploader.regions.hk","uploader.regions.sg",
            "cli","cli.main","cli.cli",
        ]

    # ---------------------- 日志 ----------------------
    def log(self, msg, level="INFO"):
        print(f"[{level}] {msg}")

    # ---------------------- 环境检查 ----------------------
    def check_environment(self):
        self.log("检查 Python 版本和依赖...")
        if sys.version_info < (3, 8):
            self.log("Python 版本过低，建议 >= 3.8", "WARN")
        # 检查依赖包
        required_packages = {
            'PyYAML': 'yaml',
            'pandas': 'pandas',
            'openpyxl': 'openpyxl',
            'playwright': 'playwright',
            'requests': 'requests',
            'pyautogui': 'pyautogui',
            'pyperclip': 'pyperclip',
            'Pillow': 'PIL',  # pyautogui 依赖
        }
        for pkg, mod in required_packages.items():
            try:
                __import__(mod)
                self.log(f"{pkg} 已安装")
            except ImportError:
                self.log(f"{pkg} 缺失，自动安装...", "WARN")
                subprocess.run([sys.executable, "-m", "pip", "install", pkg], check=True)

        # 检查 PyInstaller
        try:
            import PyInstaller
            self.log(f"PyInstaller 版本: {PyInstaller.__version__}")
        except ImportError:
            self.log("PyInstaller 未安装，正在安装...", "WARN")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            try:
                import PyInstaller
                self.log(f"PyInstaller 安装完成: {PyInstaller.__version__}")
            except ImportError:
                self.log("PyInstaller 安装失败", "ERROR")
                sys.exit(1)

        # 检查入口文件
        entry_file = self.project_root / self.entry_point
        if not entry_file.exists():
            self.log(f"入口文件不存在: {entry_file}", "ERROR")
            sys.exit(1)
        self.log(f"入口文件: {entry_file}")

        # 检查数据文件
        for src, _ in self.data_includes:
            src_path = self.project_root / src
            if not src_path.exists():
                self.log(f"数据文件/目录不存在，将跳过: {src}", "WARN")

    # ---------------------- 清理旧产物 ----------------------
    def clean_build_artifacts(self):
        if self.keep_temp:
            self.log("保留旧构建产物", "INFO")
            return
        artifacts = ['build','dist', f'{self.app_name}.spec']
        for artifact in artifacts:
            path = self.project_root / artifact
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
        for pyc in self.project_root.rglob("__pycache__"):
            if pyc.is_dir():
                shutil.rmtree(pyc)
        self.log("已清理旧构建产物", "INFO")

    # ---------------------- 构建 PyInstaller 命令 ----------------------
    def build_pyinstaller_command(self):
        cmd = ["pyinstaller","--noconfirm","--clean"]
        if self.onefile:
            cmd.append("--onefile")
        else:
            cmd.append("--onedir")
        cmd.extend(["--name", self.app_name])
        cmd.extend(["--paths", str(self.project_root)])
        # 收集子模块（确保所有依赖都被打包）
        cmd.extend(["--collect-all", "pyautogui"])
        cmd.extend(["--collect-all", "pyperclip"])
        cmd.extend(["--collect-all", "PIL"])

        # 添加数据文件
        for src, dst in self.data_includes:
            src_path = self.project_root / src
            if src_path.exists():
                cmd.extend(["--add-data", f"{src}{self.separator}{dst}"])

        # 添加隐藏导入
        for mod in self.hidden_imports:
            cmd.extend(["--hidden-import", mod])

        # 排除模块
        for mod in self.excludes:
            cmd.extend(["--exclude-module", mod])

        # 添加入口文件
        cmd.append(str(self.project_root / self.entry_point))
        return cmd

    # ---------------------- 执行构建 ----------------------
    def run_build(self):
        cmd = self.build_pyinstaller_command()
        self.log(f"执行打包命令: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            self.log("打包失败", "ERROR")
            sys.exit(1)

    # ---------------------- 创建发布包 ----------------------
    def create_release_package(self):
        release_dir = self.project_root / f"release/{self.app_name}_{self.version}_{self.system}_{self.build_time}"
        release_dir.mkdir(parents=True, exist_ok=True)
        exe_file = self.project_root / 'dist' / (f"{self.app_name}.exe" if self.system=="Windows" else self.app_name)

        if exe_file.exists():
            shutil.copy2(exe_file, release_dir)

        # 复制 config 文件夹
        config_src = self.project_root / 'config'
        config_dst = release_dir / 'config'
        if config_src.exists():
            shutil.copytree(config_src, config_dst)
            # 删除真实 settings.yaml
            settings_file = config_dst / 'settings.yaml'
            if settings_file.exists():
                settings_file.unlink()

        # 复制 regions YAML 文件
        regions_src = self.project_root / 'uploader' / 'regions'
        regions_dst = release_dir / 'uploader' / 'regions'
        if regions_src.exists():
            regions_dst.parent.mkdir(parents=True, exist_ok=True)
            def ignore_non_yaml(dir, files):
                return [f for f in files if f.endswith('.py') or f=='__pycache__' or f.startswith('.')]
            shutil.copytree(regions_src, regions_dst, ignore=ignore_non_yaml)

        # 复制示例 Excel
        example_excel = self.project_root / 'example_products.xlsx'
        if example_excel.exists():
            shutil.copy2(example_excel, release_dir / 'example_products.xlsx')

        # 复制 README
        readme_src = self.project_root / 'README.md'
        if readme_src.exists():
            shutil.copy2(readme_src, release_dir / 'README.md')

        # 复制 requirements
        req_src = self.project_root / 'requirements.txt'
        if req_src.exists():
            shutil.copy2(req_src, release_dir / 'requirements.txt')

        # 生成 USAGE.txt
        self._create_usage_guide(release_dir, exe_file.name)

        # 生成启动脚本
        self._create_startup_scripts(release_dir, exe_file.name)

        self.log(f"发布包创建成功: {release_dir}", "INFO")
        return release_dir, exe_file

    # ---------------------- 生成使用说明 ----------------------
    def _create_usage_guide(self, release_dir, exe_name):
        usage_content = f"""
Carousell Uploader 使用说明
版本: {self.version}  系统: {self.system}  构建时间: {self.build_time}

主要文件:
- {exe_name}           主程序可执行文件
- config/              配置目录
- uploader/regions/    CSS 选择器配置
- example_products.xlsx 示例 Excel
- README.md
- USAGE.txt
"""
        with open(release_dir / 'USAGE.txt', 'w', encoding='utf-8') as f:
            f.write(usage_content)

    # ---------------------- 生成启动脚本 ----------------------
    def _create_startup_scripts(self, release_dir, exe_name):
        if self.system == "Windows":
            bat_content = f"""@echo off
chcp 65001 >nul
title Carousell Uploader
echo.
{exe_name}
pause
"""
            bat_file = release_dir / 'run.bat'
            with open(bat_file, 'w', encoding='utf-8') as f:
                f.write(bat_content)
        else:
            sh_content = f"""#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" && pwd )"
cd "$SCRIPT_DIR"
./{exe_name}
read -p "按 Enter 键继续..."
"""
            sh_file = release_dir / 'run.sh'
            with open(sh_file, 'w', encoding='utf-8') as f:
                f.write(sh_content)
            os.chmod(sh_file, 0o755)

    # ---------------------- 构建流程 ----------------------
    def build(self):
        try:
            self.log("🚀 Carousell Uploader 构建开始")
            self.check_environment()
            self.clean_build_artifacts()
            self.run_build()
            release_dir, exe_file = self.create_release_package()
            self.log(f"🎉 构建完成: {exe_file} -> {release_dir}")
        except KeyboardInterrupt:
            self.log("用户中断构建", "WARN")
            sys.exit(1)
        except Exception as e:
            import traceback
            self.log(f"构建出错: {e}", "ERROR")
            traceback.print_exc()
            sys.exit(1)

# ---------------------- 主函数 ----------------------
def main():
    builder = CarousellBuilder()
    builder.build()

if __name__ == '__main__':
    main()
