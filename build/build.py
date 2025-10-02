#!/usr/bin/env python3
"""
简化的智能构建脚本
自动检测项目模块，生成PyInstaller配置并构建
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Set, Dict, Any


def load_config() -> Dict[str, Any]:
    """加载构建配置"""
    # 默认配置
    return {
        'build': {
            'entry_point': 'cli/main.py',
            'output_name': 'CarousellUploader',
            'default_mode': 'onefile'
        },
        'data_files': [
            {'src': 'config', 'dst': 'config'},
            {'src': 'uploader/regions', 'dst': 'uploader/regions'},
            {'src': 'data', 'dst': 'data'}
        ],
        'important_modules': [
            'core', 'uploader', 'browser', 'data', 'cli',
            'playwright', 'pyautogui', 'pyperclip', 'openpyxl',
            'pandas', 'yaml', 'requests', 'PIL', 'selenium', 'webdriver_manager'
        ],
        'exclude_modules': ['test', 'tests', 'pytest', 'unittest', 'doctest']
    }


def discover_modules() -> Set[str]:
    """自动发现项目模块"""
    modules = set()
    project_root = Path(".")
    
    # 扫描Python文件
    for py_file in project_root.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        
        # 计算模块路径
        rel_path = py_file.relative_to(project_root)
        parts = list(rel_path.parts[:-1])  # 去掉文件名
        
        if parts:
            module_name = ".".join(parts)
            modules.add(module_name)
    
    # 添加顶级模块
    for item in project_root.iterdir():
        if item.is_dir() and (item / "__init__.py").exists():
            modules.add(item.name)
    
    return modules


def generate_spec_file(config: Dict[str, Any], build_mode: str = "onefile") -> str:
    """生成PyInstaller spec文件"""
    
    # 发现模块
    discovered_modules = discover_modules()
    important_modules = set(config.get('important_modules', []))
    exclude_modules = set(config.get('exclude_modules', []))
    
    # 合并模块
    all_modules = discovered_modules | important_modules
    all_modules = all_modules - exclude_modules
    
    # 数据文件
    data_files = config.get('data_files', [])
    existing_datas = []
    for data_file in data_files:
        src_path = Path(data_file['src'])
        if src_path.exists():
            existing_datas.append(f"('{data_file['src']}', '{data_file['dst']}')")
    
    # 构建配置
    build_config = config['build']
    entry_point = build_config['entry_point']
    output_name = build_config['output_name']
    
    # 生成spec内容
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# 自动生成的PyInstaller配置文件

block_cipher = None

a = Analysis(
    ['{entry_point}'],
    pathex=[],
    binaries=[],
    datas=[{', '.join(existing_datas)}],
    hiddenimports={sorted(list(all_modules))},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes={sorted(list(exclude_modules))},
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{output_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)'''

    if build_mode == "onedir":
        spec_content += f'''

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{output_name}',
)'''
    
    return spec_content


def build_executable(build_mode: str = "onefile", clean: bool = True):
    """构建可执行文件"""
    
    print("🔍 正在分析项目结构...")
    
    # 加载配置
    config = load_config()
    print(f"📁 配置文件: build_config.yaml")
    
    # 生成spec文件
    spec_content = generate_spec_file(config, build_mode)
    
    # 保存spec文件
    output_name = config['build']['output_name']
    spec_filename = f"{output_name}.spec"
    
    with open(spec_filename, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"✅ 已生成spec文件: {spec_filename}")
    
    # 清理之前的构建
    if clean:
        for dir_name in ['build', 'dist', '__pycache__']:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)
                print(f"🧹 已清理: {dir_name}")
    
    # 执行构建
    print(f"🚀 开始构建可执行文件 ({build_mode})...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller", 
            "--clean", spec_filename
        ], check=True, capture_output=True, text=True)
        
        print("✅ 构建成功!")
        print(f"📁 输出目录: dist/")
        
        # 显示构建结果
        dist_path = Path("dist")
        if dist_path.exists():
            for item in dist_path.iterdir():
                if item.is_file():
                    size_mb = item.stat().st_size / (1024 * 1024)
                    print(f"📦 {item.name} ({size_mb:.1f} MB)")
                elif item.is_dir():
                    print(f"📁 {item.name}/")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="智能PyInstaller构建工具")
    parser.add_argument("--mode", choices=["onefile", "onedir"], 
                       default="onefile", help="构建模式")
    parser.add_argument("--no-clean", action="store_true", 
                       help="不清理之前的构建")
    
    args = parser.parse_args()
    
    success = build_executable(
        build_mode=args.mode,
        clean=not args.no_clean
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
