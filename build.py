#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carousell Uploader 构建脚本 - 使用 PyInstaller 打包项目
支持 regions 中各地域 CSS 配置文件的外部配置
"""

import os
import sys
import shutil
import platform
from pathlib import Path
from datetime import datetime


class CarousellBuilder:
    """Carousell Uploader 构建器"""
    
    def __init__(self):
        """初始化构建器"""
        self.project_root = Path(__file__).parent
        self.system = platform.system()
        self.separator = ";" if self.system == "Windows" else ":"
        self.build_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 构建配置
        self.app_name = "carousell_uploader"
        self.version = "1.0.0"
        self.entry_point = "cli/main.py"
        
        # 需要包含的数据目录和文件
        self.data_includes = [
            ("config", "config"),
            ("uploader/regions", "uploader/regions"),
            ("example_products.xlsx", "."),
        ]
        
        # 需要排除的模块（减小体积）
        self.excludes = [
            "tkinter",
            "unittest",
            "test",
            "setuptools",
            "pip",
            "wheel",
        ]
        
        # 隐藏导入（确保打包）
        self.hidden_imports = [
            "playwright",
            "yaml",
            "pandas",
            "openpyxl",
            "requests",
            "bs4",
            "lxml",
            # 项目模块
            "core",
            "core.config",
            "core.logger",
            "core.models",
            "browser",
            "browser.browser",
            "browser.actions",
            "browser.browser_factory",
            "browser.browser_interface",
            "browser.browser_selector",
            "data",
            "data.excel_parser",
            "data.record_manager",
            "uploader",
            "uploader.core",
            "uploader.core.base_uploader",
            "uploader.core.carousell_uploader",
            "uploader.actions",
            "uploader.actions.enhanced_safe_actions",
            "uploader.config",
            "uploader.config.enhanced_css_selector_manager",
            "uploader.config.regional_config_loader",
            "uploader.factory",
            "uploader.factory.uploader_factory",
            "uploader.multi",
            "uploader.multi.multi_account_uploader",
            "uploader.utils",
            "uploader.utils.utils",
            "uploader.regions",
            "uploader.regions.hk",
            "uploader.regions.sg",
            "cli",
            "cli.main",
            "cli.cli",
        ]
    
    def print_header(self, text):
        """打印标题"""
        print("\n" + "=" * 80)
        print(f"{'':^20}{text:^40}{'':^20}")
        print("=" * 80)
    
    def print_section(self, text):
        """打印章节"""
        print("\n" + "-" * 80)
        print(f"{'':^10}{text:^60}{'':^10}")
        print("-" * 80)
    
    def check_environment(self):
        """检查构建环境"""
        self.print_header("🔍 检查构建环境")
        
        # 检查 Python 版本
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        print(f"✅ Python 版本: {python_version}")
        
        if sys.version_info < (3, 8):
            print("❌ Python 版本过低，需要 3.8 或更高版本")
            sys.exit(1)
        
        # 检查操作系统
        print(f"✅ 操作系统: {self.system} ({platform.platform()})")
        
        # 检查项目依赖
        print("\n📦 检查项目依赖...")
        required_packages = {
            'PyYAML': 'yaml',
            'pandas': 'pandas',
            'openpyxl': 'openpyxl',
            'playwright': 'playwright',
            'requests': 'requests',
            'beautifulsoup4': 'bs4',
            'lxml': 'lxml',
        }
        
        missing_packages = []
        for package_name, import_name in required_packages.items():
            try:
                __import__(import_name)
                print(f"  ✅ {package_name}")
            except ImportError:
                print(f"  ❌ {package_name} (未安装)")
                missing_packages.append(package_name)
        
        if missing_packages:
            print(f"\n⚠️  缺少必要的依赖包: {', '.join(missing_packages)}")
            print("请先安装依赖:")
            print(f"  pip install {' '.join(missing_packages)}")
            print("或:")
            print("  pip install -r requirements.txt")
            sys.exit(1)
        
        # 检查 PyInstaller
        try:
            import PyInstaller
            print(f"✅ PyInstaller 版本: {PyInstaller.__version__}")
        except ImportError:
            print("⚠️  未安装 PyInstaller，正在安装...")
            os.system(f"{sys.executable} -m pip install pyinstaller")
            try:
                import PyInstaller
                print(f"✅ PyInstaller 安装完成: {PyInstaller.__version__}")
            except ImportError:
                print("❌ PyInstaller 安装失败")
                sys.exit(1)
        
        # 检查入口文件
        entry_file = self.project_root / self.entry_point
        if not entry_file.exists():
            print(f"❌ 找不到入口文件: {entry_file}")
            sys.exit(1)
        print(f"✅ 入口文件: {entry_file}")
        
        # 检查必要的数据文件
        missing_files = []
        for src, _ in self.data_includes:
            src_path = self.project_root / src
            if not src_path.exists():
                missing_files.append(src)
        
        if missing_files:
            print("⚠️  以下数据文件/目录不存在，将被跳过:")
            for f in missing_files:
                print(f"   - {f}")
        
        print("✅ 环境检查完成")
    
    def clean_build_artifacts(self):
        """清理构建产物"""
        self.print_section("🧹 清理旧的构建产物")
        
        artifacts = ['build', 'dist', '__pycache__', f'{self.app_name}.spec']
        for artifact in artifacts:
            artifact_path = self.project_root / artifact
            if artifact_path.exists():
                if artifact_path.is_dir():
                    shutil.rmtree(artifact_path)
                    print(f"🗑️  删除目录: {artifact}")
                else:
                    artifact_path.unlink()
                    print(f"🗑️  删除文件: {artifact}")
        
        print("✅ 清理完成")
    
    def build_pyinstaller_command(self):
        """构建 PyInstaller 命令"""
        self.print_section("🔨 构建打包命令")
        
        cmd = [
            "pyinstaller",
            "--onefile",  # 单文件模式
            "--name", self.app_name,
            "--clean",  # 清理临时文件
            "--noconfirm",  # 不询问确认
            "--paths", str(self.project_root),  # 添加项目根目录到搜索路径
        ]
        
        # 添加图标（如果存在）
        icon_path = self.project_root / "icon.ico"
        if icon_path.exists():
            cmd.extend(["--icon", str(icon_path)])
            print(f"✅ 添加图标: {icon_path}")
        
        # 添加数据文件
        for src, dst in self.data_includes:
            src_path = self.project_root / src
            if src_path.exists():
                # 使用正确的分隔符
                add_data = f"{src}{self.separator}{dst}"
                cmd.extend(["--add-data", add_data])
                print(f"✅ 添加数据: {src} -> {dst}")
            else:
                print(f"⚠️  跳过不存在的数据: {src}")
        
        # 添加隐藏导入
        for module in self.hidden_imports:
            cmd.extend(["--hidden-import", module])
        print(f"✅ 添加隐藏导入: {', '.join(self.hidden_imports)}")
        
        # 添加排除模块
        for module in self.excludes:
            cmd.extend(["--exclude-module", module])
        print(f"✅ 排除模块: {', '.join(self.excludes)}")
        
        # 添加入口文件
        cmd.append(str(self.project_root / self.entry_point))
        
        return cmd
    
    def run_build(self):
        """执行构建"""
        self.print_header("📦 开始构建可执行文件")
        
        cmd = self.build_pyinstaller_command()
        
        print(f"\n🔨 执行命令:")
        print(f"   {' '.join(cmd)}\n")
        
        # 执行打包
        result = os.system(' '.join(cmd))
        
        if result != 0:
            print("\n❌ 打包失败！")
            sys.exit(1)
        
        print("\n✅ 可执行文件构建成功！")
    
    def create_release_package(self):
        """创建发布包"""
        self.print_header("📂 创建发布包")
        
        # 创建发布目录
        release_name = f"carousell_uploader_{self.version}_{self.system.lower()}_{self.build_time}"
        release_dir = self.project_root / 'release' / release_name
        release_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 发布目录: {release_dir}")
        
        # 复制可执行文件
        exe_name = f"{self.app_name}.exe" if self.system == "Windows" else self.app_name
        exe_src = self.project_root / 'dist' / exe_name
        exe_dst = release_dir / exe_name
        
        if exe_src.exists():
            shutil.copy2(exe_src, exe_dst)
            # 在 Unix 系统上添加执行权限
            if self.system != "Windows":
                os.chmod(exe_dst, 0o755)
            print(f"✅ 可执行文件: {exe_dst.name}")
        else:
            print(f"❌ 找不到可执行文件: {exe_src}")
            sys.exit(1)
        
        # 复制配置目录
        config_src = self.project_root / 'config'
        config_dst = release_dir / 'config'
        
        if config_src.exists():
            if config_dst.exists():
                shutil.rmtree(config_dst)
            shutil.copytree(config_src, config_dst)
            print(f"✅ 配置目录: config/")
            
            # 删除实际的 settings.yaml，只保留示例文件
            settings_file = config_dst / 'settings.yaml'
            if settings_file.exists():
                settings_file.unlink()
                print(f"   ℹ️  已删除 settings.yaml（用户需自行配置）")
        
        # 复制 regions 配置目录（仅 YAML 文件）
        regions_src = self.project_root / 'uploader' / 'regions'
        regions_dst = release_dir / 'uploader' / 'regions'
        
        if regions_src.exists():
            if regions_dst.exists():
                shutil.rmtree(regions_dst)
            regions_dst.parent.mkdir(parents=True, exist_ok=True)
            
            # 只复制 yaml 文件，忽略 Python 文件和 __pycache__
            def ignore_non_yaml(dir, files):
                """忽略非 YAML 文件"""
                ignore_list = []
                for f in files:
                    # 忽略 Python 文件、__pycache__、__init__.py 等
                    if f.endswith('.py') or f == '__pycache__' or f.startswith('.'):
                        ignore_list.append(f)
                return ignore_list
            
            shutil.copytree(regions_src, regions_dst, ignore=ignore_non_yaml)
            print(f"✅ 地域配置: uploader/regions/ (仅 YAML 文件)")
            
            # 统计配置文件数量
            yaml_files = list(regions_dst.rglob("*.yaml"))
            print(f"   ℹ️  包含 {len(yaml_files)} 个 CSS 配置文件")
            
            # 显示复制的文件列表
            if yaml_files:
                print(f"   📝 配置文件列表:")
                for yaml_file in sorted(yaml_files):
                    rel_path = yaml_file.relative_to(regions_dst)
                    print(f"      - {rel_path}")
        
        # 复制示例 Excel 文件
        example_excel = self.project_root / 'example_products.xlsx'
        if example_excel.exists():
            shutil.copy2(example_excel, release_dir / 'example_products.xlsx')
            print(f"✅ 示例文件: example_products.xlsx")
        
        # 复制 README
        readme_src = self.project_root / 'README.md'
        if readme_src.exists():
            shutil.copy2(readme_src, release_dir / 'README.md')
            print(f"✅ 说明文档: README.md")
        
        # 复制 requirements
        req_src = self.project_root / 'requirements.txt'
        if req_src.exists():
            shutil.copy2(req_src, release_dir / 'requirements.txt')
            print(f"✅ 依赖列表: requirements.txt")
        
        # 创建使用说明
        self._create_usage_guide(release_dir, exe_name)
        
        # 创建快速启动脚本
        self._create_startup_scripts(release_dir, exe_name)
        
        return release_dir, exe_dst
    
    def _create_usage_guide(self, release_dir, exe_name):
        """创建使用说明"""
        usage_content = f"""Carousell Uploader 使用说明
{'=' * 80}

📦 发布版本信息
版本: {self.version}
系统: {self.system}
构建时间: {self.build_time}
Python: {sys.version}

📂 文件结构说明
├── {exe_name}                    # 主程序可执行文件
├── config/                       # 配置文件目录
│   ├── settings.example.yaml    # 配置文件示例（必读！）
│   └── settings.yaml            # 实际配置文件（需要创建）
├── uploader/regions/            # 地域配置目录（支持热更新）
│   ├── hk/sneakers/             # 香港运动鞋配置
│   │   └── css_selectors.yaml   # CSS 选择器配置
│   └── sg/sneakers/             # 新加坡运动鞋配置
│       └── css_selectors.yaml   # CSS 选择器配置
├── example_products.xlsx        # 商品模板示例
├── README.md                    # 项目说明文档
└── USAGE.txt                    # 本使用说明

🚀 快速开始

1️⃣ 配置文件设置
   复制 config/settings.example.yaml 为 config/settings.yaml
   根据您的环境修改以下配置：
   - browser: 指纹浏览器配置（BitBrowser/IxBrowser）
   - logging: 日志设置
   - meetup_locations: 各地域面交地点

2️⃣ 准备商品数据
   使用 example_products.xlsx 作为模板
   填写您的商品信息：
   - SKU: 商品编号
   - Title: 商品标题
   - Price: 价格
   - Images: 图片路径
   - 等等...

3️⃣ 运行程序
   Windows: 双击 {exe_name} 或在命令行运行
   Linux/Mac: 在终端运行 ./{exe_name}

4️⃣ 按提示操作
   - 选择指纹浏览器类型（BitBrowser/IxBrowser）
   - 输入 Excel 文件路径
   - 选择上传地域（HK/MY/SG）
   - 选择商品类目（sneakers/bags/clothes）
   - 等待自动上传完成

⚙️ 配置说明

🌐 浏览器配置 (config/settings.yaml)
browser:
  bitBrowser:
    api_port: 54345          # BitBrowser API 端口
    api_key: "your-api-key"  # API 密钥
  ixBrowser:
    api_port: 40000          # IxBrowser API 端口
    api_key: "your-api-key"  # API 密钥

📍 地域配置
- HK: 香港
- MY: 马来西亚  
- SG: 新加坡

🛍️ 商品类目
- sneakers: 运动鞋
- bags: 包包
- clothes: 服装

🔧 CSS 选择器配置（支持热更新）

CSS 配置文件位置：
- uploader/regions/{{region}}/{{category}}/css_selectors.yaml

配置示例：
```yaml
editing:
  activate_button:
    description: 激活按钮
    primary: innerText:has-text("Mark as active"), innerText:has-text("標記為有效")
    fallback: button.D_bra
```

支持特性：
✅ 多条件判断（逗号分隔，满足任一即可）
✅ CSS 选择器、XPath、文本选择器混合使用
✅ 主选择器 (primary) 和备用选择器 (fallback)
✅ 热更新（无需重启程序）
✅ 用户交互式更新（失败时提示用户更新选择器）

⚠️ 注意事项

1. 首次运行前必须配置 config/settings.yaml
2. 确保指纹浏览器已启动并正确配置
3. 确保网络连接正常
4. 建议先用少量数据测试
5. 检查日志文件排查问题（logs/carousell.log）
6. CSS 选择器配置可随时修改，程序会自动加载

📝 日志文件

日志位置: logs/carousell_YYYYMMDD.log
日志级别: INFO, WARNING, ERROR
建议定期检查日志排查问题

🆘 常见问题

Q: 程序启动失败？
A: 检查 Python 环境、依赖包是否安装完整

Q: 浏览器连接失败？
A: 检查浏览器是否启动、API 配置是否正确

Q: 上传失败？
A: 检查网络、账号状态、商品数据格式

Q: CSS 选择器失效？
A: 根据程序提示更新 uploader/regions/ 下的配置文件

💡 技巧提示

- 使用 Ctrl+C 可以安全中断程序
- 程序支持断点续传（基于 Excel 记录）
- 可同时运行多个实例（不同浏览器）
- 定期备份配置文件
- 使用浏览器开发者工具捕获新的 CSS 选择器

📞 获取帮助

- 项目文档: README.md
- 问题反馈: GitHub Issues
- 配置示例: settings.example.yaml

{'=' * 80}
祝您使用愉快，天天爆单！💰
{'=' * 80}
"""
        
        with open(release_dir / 'USAGE.txt', 'w', encoding='utf-8') as f:
            f.write(usage_content)
        print(f"✅ 使用说明: USAGE.txt")
    
    def _create_startup_scripts(self, release_dir, exe_name):
        """创建快速启动脚本"""
        if self.system == "Windows":
            # Windows 批处理脚本
            bat_content = f"""@echo off
chcp 65001 >nul
title Carousell Uploader
echo.
echo ========================================
echo    Carousell Uploader v{self.version}
echo ========================================
echo.
{exe_name}
echo.
echo 程序已退出
pause
"""
            bat_file = release_dir / 'run.bat'
            with open(bat_file, 'w', encoding='utf-8') as f:
                f.write(bat_content)
            print(f"✅ 启动脚本: run.bat")
        else:
            # Unix shell 脚本
            sh_content = f"""#!/bin/bash
echo ""
echo "========================================"
echo "   Carousell Uploader v{self.version}"
echo "========================================"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" && pwd )"
cd "$SCRIPT_DIR"

# 运行程序
./{exe_name}

echo ""
echo "程序已退出"
read -p "按 Enter 键继续..."
"""
            sh_file = release_dir / 'run.sh'
            with open(sh_file, 'w', encoding='utf-8') as f:
                f.write(sh_content)
            # 添加执行权限
            os.chmod(sh_file, 0o755)
            print(f"✅ 启动脚本: run.sh")
    
    def show_build_summary(self, release_dir, exe_file):
        """显示构建摘要"""
        self.print_header("🎉 构建完成")
        
        # 计算文件大小
        exe_size_mb = exe_file.stat().st_size / (1024 * 1024)
        
        # 统计发布包内容
        total_files = sum(1 for _ in release_dir.rglob('*') if _.is_file())
        total_dirs = sum(1 for _ in release_dir.rglob('*') if _.is_dir())
        
        print(f"""
📦 构建信息
   应用名称: {self.app_name}
   版本号: {self.version}
   构建时间: {self.build_time}
   操作系统: {self.system}

📁 发布包
   位置: {release_dir}
   文件数: {total_files}
   目录数: {total_dirs}

💾 可执行文件
   文件: {exe_file.name}
   大小: {exe_size_mb:.2f} MB
   位置: {exe_file}

✅ 包含内容
   ✓ 可执行文件
   ✓ 配置文件（config/）
   ✓ CSS 配置（uploader/regions/）
   ✓ 示例文件（example_products.xlsx）
   ✓ 说明文档（README.md, USAGE.txt）
   ✓ 启动脚本（run.bat/run.sh）

🚀 下一步操作
   1. 进入发布目录: cd {release_dir.name}
   2. 配置文件: 复制 config/settings.example.yaml 为 settings.yaml
   3. 运行程序: {'双击 run.bat' if self.system == 'Windows' else './run.sh'}
   
💡 提示
   - CSS 配置文件支持热更新，可随时修改
   - 配置文件修改后无需重新打包
   - 查看 USAGE.txt 获取详细使用说明
""")
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        self.print_section("🧹 清理临时文件")
        
        print("是否清理构建临时文件？")
        print("  - build/")
        print("  - dist/")
        print("  - *.spec")
        print("  - __pycache__/")
        
        try:
            choice = input("\n请选择 (y/n，默认 y): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            # 非交互式环境或用户中断，默认清理
            print("\n⚠️  非交互式环境，默认清理")
            choice = 'y'
        
        if choice in ('', 'y', 'yes'):
            temp_items = ['build', 'dist', f'{self.app_name}.spec']
            
            for item in temp_items:
                item_path = self.project_root / item
                if item_path.exists():
                    if item_path.is_dir():
                        shutil.rmtree(item_path)
                        print(f"🗑️  已删除: {item}/")
                    else:
                        item_path.unlink()
                        print(f"🗑️  已删除: {item}")
            
            # 清理 __pycache__
            for pycache in self.project_root.rglob('__pycache__'):
                if pycache.is_dir():
                    shutil.rmtree(pycache)
            print("🗑️  已删除: 所有 __pycache__/")
            
            print("✅ 临时文件清理完成")
        else:
            print("⏭️  跳过清理")
    
    def build(self):
        """执行完整的构建流程"""
        try:
            # 打印欢迎信息
            self.print_header("🚀 Carousell Uploader 构建工具")
            print(f"""
📦 项目: {self.app_name}
🔢 版本: {self.version}
🖥️  系统: {self.system}
📅 时间: {self.build_time}
""")
            
            # 1. 检查环境
            self.check_environment()
            
            # 2. 清理旧产物
            self.clean_build_artifacts()
            
            # 3. 执行构建
            self.run_build()
            
            # 4. 创建发布包
            release_dir, exe_file = self.create_release_package()
            
            # 5. 显示摘要
            self.show_build_summary(release_dir, exe_file)
            
            # 6. 清理临时文件
            self.cleanup_temp_files()
            
            # 完成
            self.print_header("✨ 构建流程全部完成")
            print("\n🎊 恭喜！您的应用已成功打包！")
            print(f"📂 发布包位置: {release_dir}\n")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  用户中断构建")
            sys.exit(1)
        except Exception as e:
            print(f"\n\n❌ 构建出错: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """主函数"""
    builder = CarousellBuilder()
    builder.build()


if __name__ == '__main__':
    main()

