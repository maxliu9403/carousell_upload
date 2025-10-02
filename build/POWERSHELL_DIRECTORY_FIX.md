# PowerShell目录创建错误修复

## 问题描述

GitHub Actions中的PowerShell脚本出现以下错误：

```
New-Item: D:\a\_temp\56cd7cca-7f17-47d0-b95f-70893dd3a61d.ps1:4
Line |
   4 |  mkdir dist\config
     |  ~~~~~~~~~~~~~~~~~
     | An item with the specified name D:\a\carousell_upload\carousell_upload\dist\config already exists.
Error: Process completed with exit code 1.
```

## 问题原因

PowerShell脚本试图创建已经存在的目录，导致错误：
- `mkdir dist\config` - 目录已存在
- `mkdir dist\uploader\regions` - 目录已存在

这是因为构建脚本已经创建了这些目录，但GitHub Actions工作流又试图重新创建它们。

## 修复方案

### 修复前
```powershell
# 创建 dist/config
mkdir dist\config
copy config\settings.yaml dist\config\
copy config\settings.example.yaml dist\config\
# 创建 dist/uploader/regions
mkdir dist\uploader\regions
xcopy uploader\regions dist\uploader\regions\ /E /I /Y
```

### 修复后
```powershell
# 创建 dist/config (如果不存在)
if (!(Test-Path "dist\config")) {
  New-Item -ItemType Directory -Path "dist\config" -Force
}
copy config\settings.yaml dist\config\
copy config\settings.example.yaml dist\config\
# 创建 dist/uploader/regions (如果不存在)
if (!(Test-Path "dist\uploader\regions")) {
  New-Item -ItemType Directory -Path "dist\uploader\regions" -Force
}
xcopy uploader\regions dist\uploader\regions\ /E /I /Y
```

## 修复说明

### 1. 使用条件检查
- `Test-Path "dist\config"` - 检查目录是否存在
- `Test-Path "dist\uploader\regions"` - 检查目录是否存在

### 2. 使用New-Item命令
- `New-Item -ItemType Directory` - 创建目录
- `-Force` 参数 - 如果目录已存在，不会报错

### 3. 避免重复创建
- 只有在目录不存在时才创建
- 如果目录已存在，跳过创建步骤

## 修复后的效果

### 1. 不再出现目录已存在错误
- ✅ 检查目录是否存在
- ✅ 只在需要时创建目录
- ✅ 避免重复创建

### 2. 保持功能完整
- ✅ 配置文件复制正常
- ✅ 地域文件夹复制正常
- ✅ 目录结构显示正常

### 3. 兼容性更好
- ✅ 支持目录已存在的情况
- ✅ 支持目录不存在的情况
- ✅ 支持多次运行

## 验证方法

### 1. 本地测试
```powershell
# 测试目录创建逻辑
if (!(Test-Path "test\config")) {
  New-Item -ItemType Directory -Path "test\config" -Force
}
```

### 2. GitHub Actions测试
- 推送到main分支触发构建
- 检查构建日志确认没有目录创建错误
- 验证配置文件复制成功

## 总结

通过添加条件检查和使用`New-Item`命令，解决了PowerShell目录创建错误：

- ✅ **避免重复创建**: 检查目录是否存在
- ✅ **使用正确命令**: 使用`New-Item`而不是`mkdir`
- ✅ **添加错误处理**: 使用`-Force`参数
- ✅ **保持功能完整**: 配置文件复制正常

现在GitHub Actions应该可以正常运行，不会再出现目录已存在的错误。
