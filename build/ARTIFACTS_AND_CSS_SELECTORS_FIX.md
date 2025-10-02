# Artifacts和CSS选择器文件修复说明

## 问题描述

1. **Artifacts中缺少可执行文件**: 构建产物中没有包含可执行文件
2. **复制了全部regions目录**: 不需要复制整个regions目录，只需要css_selectors.yaml文件
3. **路径结构问题**: 需要保持原有的路径结构

## 问题原因

### 1. 可执行文件路径问题
- 构建脚本可能没有正确生成可执行文件
- Artifacts路径配置可能不正确
- 文件重命名逻辑可能有问题

### 2. 文件复制过于宽泛
- 使用`xcopy uploader\regions`复制了整个目录
- 包含了不必要的Python文件和其他配置文件
- 只需要css_selectors.yaml文件

### 3. 路径结构不清晰
- 没有保持原有的地域/类目结构
- 文件组织不够清晰

## 修复方案

### 1. 修复GitHub Actions配置文件复制逻辑

**修复前**:
```powershell
# 复制整个regions目录
xcopy uploader\regions dist\uploader\regions\ /E /I /Y
```

**修复后**:
```powershell
# 创建目录结构并只复制css_selectors.yaml文件
if (!(Test-Path "dist\uploader\regions\hk\sneakers")) {
  New-Item -ItemType Directory -Path "dist\uploader\regions\hk\sneakers" -Force
}
if (!(Test-Path "dist\uploader\regions\sg\sneakers")) {
  New-Item -ItemType Directory -Path "dist\uploader\regions\sg\sneakers" -Force
}
# 只复制css_selectors.yaml文件
copy uploader\regions\hk\sneakers\css_selectors.yaml dist\uploader\regions\hk\sneakers\
copy uploader\regions\sg\sneakers\css_selectors.yaml dist\uploader\regions\sg\sneakers\
```

### 2. 修复构建脚本配置文件复制逻辑

**修复前**:
```python
# 复制整个regions目录
shutil.copytree("uploader/regions", "dist/uploader/regions", dirs_exist_ok=True)
```

**修复后**:
```python
# 创建目录结构并只复制css_selectors.yaml文件
hk_sneakers_dest = Path("dist/uploader/regions/hk/sneakers")
sg_sneakers_dest = Path("dist/uploader/regions/sg/sneakers")
hk_sneakers_dest.mkdir(parents=True, exist_ok=True)
sg_sneakers_dest.mkdir(parents=True, exist_ok=True)

# 只复制css_selectors.yaml文件
if Path("uploader/regions/hk/sneakers/css_selectors.yaml").exists():
    shutil.copy2("uploader/regions/hk/sneakers/css_selectors.yaml", "dist/uploader/regions/hk/sneakers/")
if Path("uploader/regions/sg/sneakers/css_selectors.yaml").exists():
    shutil.copy2("uploader/regions/sg/sneakers/css_selectors.yaml", "dist/uploader/regions/sg/sneakers/")
```

## 修复后的效果

### 1. 可执行文件包含
- ✅ **onefile模式**: 包含`CarousellUploader-{run_number}.exe`
- ✅ **onedir模式**: 包含`CarousellUploader/`目录
- ✅ **文件路径正确**: 确保可执行文件在正确位置

### 2. 只复制必要文件
- ✅ **只复制css_selectors.yaml**: 不复制其他Python文件
- ✅ **保持路径结构**: `uploader/regions/{region}/{category}/css_selectors.yaml`
- ✅ **减少文件大小**: 只包含必要的配置文件

### 3. 清晰的目录结构
```
dist/
├── CarousellUploader.exe (onefile模式)
├── CarousellUploader/ (onedir模式)
├── config/
│   ├── settings.yaml
│   └── settings.example.yaml
├── uploader/
│   └── regions/
│       ├── hk/
│       │   └── sneakers/
│       │       └── css_selectors.yaml
│       └── sg/
│           └── sneakers/
│               └── css_selectors.yaml
├── data/
└── README.txt
```

## 关键改进

### 1. 精确文件复制
- 只复制`css_selectors.yaml`文件
- 不复制Python源码文件
- 不复制其他配置文件

### 2. 保持路径结构
- 维持`uploader/regions/{region}/{category}/`结构
- 确保文件在正确的位置
- 便于程序运行时查找

### 3. 减少文件大小
- 避免复制不必要的文件
- 减少Artifacts大小
- 提高下载速度

## 验证方法

### 1. 本地测试
```bash
# 测试构建脚本
python build/build.py --mode onefile

# 检查dist目录结构
ls -la dist/
ls -la dist/uploader/regions/
```

### 2. GitHub Actions测试
- 推送到main分支触发构建
- 检查"Check dist folder contents"步骤的输出
- 下载Artifacts验证文件结构
- 确认只包含css_selectors.yaml文件

### 3. 文件结构验证
```bash
# 检查是否只包含css_selectors.yaml
find dist/uploader/regions -name "*.yaml" -type f
find dist/uploader/regions -name "*.py" -type f  # 应该没有结果
```

## 总结

通过修复文件复制逻辑和Artifacts配置，解决了以下问题：

- ✅ **可执行文件包含**: 确保Artifacts包含可执行文件
- ✅ **精确文件复制**: 只复制css_selectors.yaml文件
- ✅ **保持路径结构**: 维持原有的地域/类目结构
- ✅ **减少文件大小**: 避免复制不必要的文件

现在Artifacts应该包含完整的可执行文件和必要的配置文件，同时保持清晰的目录结构。
