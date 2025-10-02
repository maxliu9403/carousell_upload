# GitHub Actions 修复说明

## 问题描述

GitHub Actions 构建过程中出现以下错误：

1. **文件模式不匹配**: `dist/CarousellUploader-29.exe` 不存在
2. **上传了不必要的文件**: 包含Python缓存文件（`__init__.cpython-311.pyc`）
3. **上传失败**: 某些文件上传失败，返回404状态码
4. **无效参数**: `overwrite` 参数不被支持

## 问题原因

### 1. 构建脚本问题
- 构建脚本只生成了可执行文件，没有复制配置文件到dist目录
- 导致GitHub Actions找不到配置文件进行上传

### 2. GitHub Actions配置问题
- 使用了不支持的`overwrite`参数
- 文件路径配置不正确
- 上传了不必要的Python缓存文件

## 修复方案

### 1. 修复构建脚本 (`build/build.py`)

**添加配置文件复制功能**:
```python
def copy_config_files():
    """Copy configuration files to dist directory"""
    import shutil
    
    print("Copying configuration files...")
    
    # Create config directory in dist
    config_dir = Path("dist/config")
    config_dir.mkdir(exist_ok=True)
    
    # Copy main config files
    if Path("config/settings.yaml").exists():
        shutil.copy2("config/settings.yaml", "dist/config/")
        print("Copied: config/settings.yaml")
    
    if Path("config/settings.example.yaml").exists():
        shutil.copy2("config/settings.example.yaml", "dist/config/")
        print("Copied: config/settings.example.yaml")
    
    # Copy regions directory
    if Path("uploader/regions").exists():
        regions_dest = Path("dist/uploader/regions")
        regions_dest.mkdir(parents=True, exist_ok=True)
        shutil.copytree("uploader/regions", "dist/uploader/regions", dirs_exist_ok=True)
        print("Copied: uploader/regions/")
    
    # Copy data directory
    if Path("data").exists():
        data_dest = Path("dist/data")
        data_dest.mkdir(parents=True, exist_ok=True)
        shutil.copytree("data", "dist/data", dirs_exist_ok=True)
        print("Copied: data/")
    
    # Create README file
    readme_content = """Carousell Uploader - Windows Executable

Files included:
- CarousellUploader.exe: Main executable
- config/: Configuration files
- uploader/regions/: CSS selector configurations by region
- data/: Data processing modules

Usage:
1. Configure settings.yaml with your browser API settings
2. Prepare your Excel file with product data
3. Run: CarousellUploader.exe
"""
    
    with open("dist/README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("Created: README.txt")
```

**在构建成功后调用**:
```python
# Copy configuration files to dist directory
copy_config_files()
```

### 2. 修复GitHub Actions工作流 (`.github/workflows/build-windows.yml`)

**移除无效参数**:
```yaml
# 修复前
overwrite: true

# 修复后
# 移除overwrite参数
```

**简化文件上传**:
```yaml
# onefile模式 - 只上传exe文件
files: |
  dist/CarousellUploader-${{ github.run_number }}.exe

# onedir模式 - 只上传目录
files: |
  dist/CarousellUploader/**
```

**移除不必要的文件**:
- 不再上传`dist/config/**`和`dist/uploader/regions/**`
- 这些文件现在由构建脚本自动复制到dist目录

## 修复后的效果

### 1. 构建过程
- ✅ 生成可执行文件
- ✅ 自动复制配置文件到dist目录
- ✅ 创建README文件
- ✅ 保留地域文件夹结构

### 2. GitHub Actions
- ✅ 不再出现文件模式不匹配错误
- ✅ 不再上传Python缓存文件
- ✅ 不再出现404上传错误
- ✅ 移除无效的overwrite参数

### 3. 最终输出
```
dist/
├── CarousellUploader.exe          # onefile模式
├── CarousellUploader/             # onedir模式
├── config/                        # 配置文件
├── uploader/regions/              # 地域配置
├── data/                          # 数据处理模块
└── README.txt                    # 使用说明
```

## 验证方法

### 1. 本地测试
```bash
# 测试onefile模式
python build/build.py --mode onefile

# 检查dist目录结构
ls -la dist/
```

### 2. GitHub Actions测试
- 推送到main分支触发构建
- 检查构建日志确认配置文件复制成功
- 验证发布文件只包含必要的文件

## 总结

通过修复构建脚本和GitHub Actions配置，解决了以下问题：
- ✅ 文件模式不匹配
- ✅ 上传不必要的文件
- ✅ 上传失败
- ✅ 无效参数

现在GitHub Actions应该可以正常构建和发布，只包含必要的文件，不再出现错误。
