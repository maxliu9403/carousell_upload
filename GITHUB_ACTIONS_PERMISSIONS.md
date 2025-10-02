# GitHub Actions 权限配置说明

## 🚨 403错误解决方案

如果GitHub Actions在创建Release时遇到403错误，需要配置以下权限：

### 1. 仓库设置

1. 进入仓库的 **Settings** 页面
2. 找到 **Actions** → **General**
3. 在 **Workflow permissions** 部分：
   - 选择 **Read and write permissions**
   - 勾选 **Allow GitHub Actions to create and approve pull requests**

### 2. 权限配置

```yaml
# 在 .github/workflows/build-windows.yml 中添加权限
permissions:
  contents: write
  pull-requests: write
```

### 3. 完整的权限配置

在workflow文件顶部添加：

```yaml
name: Build Windows Executable

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  workflow_dispatch:
    inputs:
      build_mode:
        description: 'Build mode'
        required: true
        default: 'onefile'
        type: choice
        options:
        - onefile
        - onedir

permissions:
  contents: write
  pull-requests: write

jobs:
  build-windows:
    runs-on: windows-latest
    # ... 其他配置
```

### 4. 检查步骤

如果仍然遇到403错误，请检查：

1. **仓库是否为私有仓库**
   - 私有仓库需要特殊权限配置
   - 确保GitHub Actions有足够权限

2. **GITHUB_TOKEN权限**
   - 默认的`GITHUB_TOKEN`可能权限不足
   - 可以创建Personal Access Token (PAT)

3. **分支保护规则**
   - 检查是否有分支保护规则阻止创建Release
   - 确保main/master分支允许Actions写入

### 5. 替代方案

如果权限问题无法解决，可以：

1. **禁用自动Release创建**
   ```yaml
   # 注释掉Create release步骤
   # - name: Create release
   ```

2. **手动创建Release**
   - 在GitHub仓库页面手动创建Release
   - 上传构建产物

3. **使用Artifacts**
   - 构建产物会保存在Actions的Artifacts中
   - 可以手动下载使用

## 🔧 修复后的配置

修复后的workflow会：

1. ✅ 分别处理onefile和onedir构建
2. ✅ 检查构建产物是否存在
3. ✅ 使用不同的tag名称避免冲突
4. ✅ 提供详细的错误信息

## 📋 权限检查清单

- [ ] 仓库设置中启用"Read and write permissions"
- [ ] 勾选"Allow GitHub Actions to create and approve pull requests"
- [ ] 在workflow中添加`permissions`配置
- [ ] 检查分支保护规则
- [ ] 确认仓库不是私有仓库（或已配置特殊权限）

## 🚀 测试步骤

1. 推送代码到main分支
2. 检查Actions运行日志
3. 查看是否成功创建Release
4. 验证构建产物是否正确上传
