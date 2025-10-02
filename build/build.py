#!/usr/bin/env python3
"""
Smart PyInstaller Build Script
Auto-detect project modules, generate PyInstaller config and build
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Set, Dict, Any


def load_config() -> Dict[str, Any]:
    """Load build configuration"""
    # Default configuration
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
    """Auto-discover project modules"""
    modules = set()
    project_root = Path(".")
    
    # Scan Python files
    for py_file in project_root.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        
        # Calculate module path
        rel_path = py_file.relative_to(project_root)
        parts = list(rel_path.parts[:-1])  # Remove filename
        
        if parts:
            module_name = ".".join(parts)
            modules.add(module_name)
    
    # Add top-level modules
    for item in project_root.iterdir():
        if item.is_dir() and (item / "__init__.py").exists():
            modules.add(item.name)
    
    return modules


def generate_spec_file(config: Dict[str, Any], build_mode: str = "onefile") -> str:
    """Generate PyInstaller spec file"""
    
    # Discover modules
    discovered_modules = discover_modules()
    important_modules = set(config.get('important_modules', []))
    exclude_modules = set(config.get('exclude_modules', []))
    
    # Merge modules
    all_modules = discovered_modules | important_modules
    all_modules = all_modules - exclude_modules
    
    # Data files
    data_files = config.get('data_files', [])
    existing_datas = []
    for data_file in data_files:
        src_path = Path(data_file['src'])
        if src_path.exists():
            existing_datas.append(f"('{data_file['src']}', '{data_file['dst']}')")
    
    # Build configuration
    build_config = config['build']
    entry_point = build_config['entry_point']
    output_name = build_config['output_name']
    
    # Generate spec content
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# Auto-generated PyInstaller config file

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
    """Build executable"""
    
    print("Analyzing project structure...")
    
    # Ensure running from project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"Working directory: {os.getcwd()}")
    
    # Load configuration
    config = load_config()
    print(f"Config file: build_config.yaml")
    
    # Generate spec file
    spec_content = generate_spec_file(config, build_mode)
    
    # Save spec file
    output_name = config['build']['output_name']
    spec_filename = f"{output_name}.spec"
    
    with open(spec_filename, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"Generated spec file: {spec_filename}")
    
    # Clean previous build
    if clean:
        for dir_name in ['build', 'dist', '__pycache__']:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)
                print(f"Cleaned: {dir_name}")
    
    # Execute build
    print(f"Building executable ({build_mode})...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller", 
            "--clean", spec_filename
        ], check=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        print("Build successful!")
        print(f"Output directory: dist/")
        
        # Show build results
        dist_path = Path("dist")
        if dist_path.exists():
            for item in dist_path.iterdir():
                if item.is_file():
                    size_mb = item.stat().st_size / (1024 * 1024)
                    print(f"File: {item.name} ({size_mb:.1f} MB)")
                elif item.is_dir():
                    print(f"Directory: {item.name}/")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart PyInstaller Build Tool")
    parser.add_argument("--mode", choices=["onefile", "onedir"], 
                       default="onefile", help="Build mode")
    parser.add_argument("--no-clean", action="store_true", 
                       help="Do not clean previous build")
    
    args = parser.parse_args()
    
    success = build_executable(
        build_mode=args.mode,
        clean=not args.no_clean
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
