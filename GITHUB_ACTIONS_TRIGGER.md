# GitHub Actions 触发条件说明

## 🎯 当前配置

GitHub Actions现在只在以下情况下触发：

### 1. 自动触发条件
- ✅ **推送到main分支**: 当代码合并到main分支时自动触发
- ✅ **手动触发**: 通过GitHub Actions页面手动运行

### 2. 不会触发的情况
- ❌ **推送到其他分支**: 如feature分支、develop分支等
- ❌ **Pull Request**: 创建或更新PR时不会触发
- ❌ **推送到master分支**: 只监听main分支

## 🔧 配置详情

```yaml
on:
  push:
    branches: [ main ]  # 只监听main分支
  workflow_dispatch:   # 允许手动触发
    inputs:
      build_mode:
        description: 'Build mode'
        required: true
        default: 'onefile'
        type: choice
        options:
        - onefile
        - onedir
```

## 🚀 工作流程

### 自动构建流程
1. 开发者推送代码到feature分支
2. 创建Pull Request
3. 代码审查通过后合并到main分支
4. **GitHub Actions自动触发** 🎉
5. 构建Windows可执行文件
6. 创建GitHub Release
7. 上传构建产物

### 手动构建流程
1. 进入GitHub仓库的Actions页面
2. 选择"Build Windows Executable"工作流
3. 点击"Run workflow"
4. 选择构建模式（onefile或onedir）
5. 点击"Run workflow"开始构建

## 📋 触发条件总结

| 事件 | 分支 | 是否触发 | 说明 |
|------|------|----------|------|
| push | main | ✅ | 自动触发构建和Release |
| push | feature/* | ❌ | 不会触发 |
| push | develop | ❌ | 不会触发 |
| push | master | ❌ | 不会触发 |
| pull_request | main | ❌ | 不会触发 |
| workflow_dispatch | 任意 | ✅ | 手动触发 |

## 🎯 优势

1. **节省资源**: 避免不必要的构建
2. **稳定发布**: 只在正式合并后构建
3. **清晰流程**: 明确的触发条件
4. **手动控制**: 支持手动触发进行测试

## 🔄 如果需要修改触发条件

### 添加其他分支触发
```yaml
on:
  push:
    branches: [ main, develop ]  # 添加develop分支
```

### 添加Pull Request触发
```yaml
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]  # PR合并到main时触发
```

### 添加定时触发
```yaml
on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # 每天凌晨2点触发
```

## 📝 注意事项

1. **分支名称**: 确保使用`main`而不是`master`
2. **权限配置**: 需要配置正确的权限才能创建Release
3. **构建产物**: 只有成功构建后才会创建Release
4. **手动触发**: 可以通过Actions页面手动触发进行测试
