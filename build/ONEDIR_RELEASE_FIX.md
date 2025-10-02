# onedir模式发布错误修复

## 问题描述

GitHub Actions在创建onedir模式的发布时出现以下错误：

```
Error: Failed to upload release asset pkgIndex.tcl. received status code 422
Validation Failed
[{"resource":"ReleaseAsset","code":"already_exists","field":"name"}]
```

## 问题原因

### 1. 文件冲突
- onedir模式生成大量文件（exe、dll、pyd、tcl等）
- 某些系统文件（如`pkgIndex.tcl`）可能已经存在于之前的发布中
- GitHub不允许上传同名的文件

### 2. 文件数量过多
- onedir模式可能生成数百个文件
- 上传大量小文件效率低
- 容易产生文件名冲突

### 3. 系统文件问题
- PyInstaller生成的系统文件可能重复
- 某些文件在不同构建中可能相同
- 导致"already_exists"错误

## 修复方案

### 修复前
```yaml
- name: Create release (onedir)
  uses: softprops/action-gh-release@v1
  with:
    files: |
      dist/CarousellUploader/**
```

**问题**: 上传所有文件，容易产生冲突

### 修复后
```yaml
- name: Create zip package (onedir)
  shell: pwsh
  run: |
    Write-Host "Creating zip package for onedir mode..."
    $zip_name = "CarousellUploader-${{ github.run_number }}-onedir.zip"
    Compress-Archive -Path "dist\CarousellUploader\*" -DestinationPath "dist\$zip_name" -Force
    Write-Host "Created zip package: $zip_name"

- name: Create release (onedir)
  uses: softprops/action-gh-release@v1
  with:
    files: |
      dist/CarousellUploader-${{ github.run_number }}-onedir.zip
```

**优势**: 只上传一个zip文件，避免冲突

## 修复说明

### 1. 创建zip包
- 使用PowerShell的`Compress-Archive`命令
- 将整个onedir目录压缩为单个zip文件
- 文件名包含构建编号，确保唯一性

### 2. 上传zip文件
- 只上传一个zip文件，而不是数百个单独文件
- 避免文件名冲突
- 提高上传效率

### 3. 保持功能完整
- zip文件包含所有必要的文件
- 用户下载后解压即可使用
- 保持onedir模式的所有功能

## 修复后的效果

### 1. 避免文件冲突
- ✅ 只上传一个zip文件
- ✅ 文件名唯一（包含构建编号）
- ✅ 不再出现"already_exists"错误

### 2. 提高效率
- ✅ 上传速度更快
- ✅ 减少网络传输
- ✅ 简化发布管理

### 3. 用户体验更好
- ✅ 下载更方便（一个文件）
- ✅ 解压后直接使用
- ✅ 文件结构清晰

## 最终发布结构

### onefile模式
```
发布文件:
- CarousellUploader-{run_number}.exe
```

### onedir模式
```
发布文件:
- CarousellUploader-{run_number}-onedir.zip
  ├── CarousellUploader.exe
  ├── *.dll
  ├── *.pyd
  ├── config/
  ├── uploader/regions/
  └── data/
```

## 验证方法

### 1. 本地测试
```powershell
# 测试zip创建
Compress-Archive -Path "dist\CarousellUploader\*" -DestinationPath "test.zip" -Force
```

### 2. GitHub Actions测试
- 推送到main分支触发构建
- 选择onedir模式
- 检查发布是否成功创建
- 验证zip文件内容

## 总结

通过创建zip包的方式，解决了onedir模式发布时的文件冲突问题：

- ✅ **避免文件冲突**: 只上传一个zip文件
- ✅ **提高效率**: 减少文件数量
- ✅ **保持功能**: 用户下载后解压即可使用
- ✅ **简化管理**: 发布管理更简单

现在onedir模式应该可以正常发布，不会再出现422错误。
