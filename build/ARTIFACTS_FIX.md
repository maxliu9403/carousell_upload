# GitHub Actions Artifacts 修复说明

## 问题描述

GitHub Actions工作流没有创建Artifacts，导致构建产物无法下载。

## 问题原因

### 1. 条件判断问题
- 原始条件: `${{ github.event.inputs.build_mode == 'onefile' }}`
- 问题: 当通过push触发时，`github.event.inputs.build_mode`为null
- 结果: 条件不匹配，Artifacts步骤不执行

### 2. 文件路径问题
- 可能某些文件不存在
- 路径配置不正确
- 缺少必要的文件

### 3. 默认行为问题
- push触发时没有默认的build_mode
- 需要为push触发设置默认值

## 修复方案

### 1. 修复条件判断

**修复前**:
```yaml
- name: Upload artifact (onefile)
  if: ${{ github.event.inputs.build_mode == 'onefile' }}
```

**修复后**:
```yaml
- name: Upload artifact (onefile)
  if: github.event.inputs.build_mode == 'onefile' || (github.event.inputs.build_mode == null && github.event_name == 'push')
```

**说明**:
- 支持手动触发时选择onefile模式
- 支持push触发时默认使用onefile模式

### 2. 添加调试步骤

```yaml
- name: Check dist folder contents
  shell: pwsh
  run: |
    Write-Host "Checking dist folder contents..."
    if (Test-Path "dist") {
      Get-ChildItem -Path "dist" -Recurse -Force | ForEach-Object {
        Write-Host "Found: $($_.FullName)"
      }
    } else {
      Write-Host "dist folder does not exist!"
    }
```

**作用**:
- 检查dist文件夹是否存在
- 列出所有文件，便于调试
- 帮助识别文件路径问题

### 3. 完善文件路径

**onefile模式**:
```yaml
path: |
  dist/CarousellUploader-${{ github.run_number }}.exe
  dist/config/**
  dist/uploader/regions/**
  dist/data/**
  dist/README.txt
```

**onedir模式**:
```yaml
path: |
  dist/CarousellUploader/**
  dist/config/**
  dist/uploader/regions/**
  dist/data/**
  dist/README.txt
```

**改进**:
- 添加了`dist/data/**`路径
- 添加了`dist/README.txt`文件
- 确保包含所有必要的文件

## 修复后的效果

### 1. 支持多种触发方式
- ✅ **手动触发**: 可以选择onefile或onedir模式
- ✅ **Push触发**: 默认使用onefile模式
- ✅ **条件匹配**: 确保Artifacts步骤执行

### 2. 包含完整文件
- ✅ **可执行文件**: exe文件
- ✅ **配置文件**: config目录
- ✅ **地域配置**: uploader/regions目录
- ✅ **数据模块**: data目录
- ✅ **说明文档**: README.txt

### 3. 调试支持
- ✅ **文件检查**: 列出所有生成的文件
- ✅ **路径验证**: 确认文件是否存在
- ✅ **错误诊断**: 便于排查问题

## 触发条件说明

### 1. onefile模式Artifacts
```yaml
if: github.event.inputs.build_mode == 'onefile' || (github.event.inputs.build_mode == null && github.event_name == 'push')
```

**触发条件**:
- 手动触发且选择onefile模式
- Push触发（默认onefile模式）

### 2. onedir模式Artifacts
```yaml
if: github.event.inputs.build_mode == 'onedir'
```

**触发条件**:
- 手动触发且选择onedir模式

## 验证方法

### 1. 本地测试
```bash
# 检查构建脚本是否生成正确文件
python build/build.py --mode onefile
ls -la dist/
```

### 2. GitHub Actions测试
- 推送到main分支触发构建
- 检查"Check dist folder contents"步骤的输出
- 验证Artifacts是否创建成功
- 下载Artifacts验证内容

### 3. 手动触发测试
- 在GitHub Actions页面手动触发
- 选择不同的build_mode
- 验证对应的Artifacts是否创建

## 总结

通过修复条件判断、添加调试步骤和完善文件路径，解决了Artifacts不创建的问题：

- ✅ **条件修复**: 支持push和手动触发
- ✅ **调试支持**: 添加文件检查步骤
- ✅ **路径完善**: 包含所有必要文件
- ✅ **默认行为**: push触发默认使用onefile模式

现在GitHub Actions应该可以正常创建Artifacts，用户可以从Actions页面下载构建产物。
