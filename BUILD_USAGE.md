# build.py 使用说明

## 🚀 快速开始

### 基本用法

```bash
# 默认构建（单文件模式，自动清理）
python build.py

# 或在 Windows PowerShell
python build.py
```

### 高级用法

```bash
# 保留临时文件（用于调试）
python build.py --keep-temp

# 使用目录模式（启动更快）
python build.py --onedir

# 组合使用
python build.py --onedir --keep-temp

# 查看帮助
python build.py --help

# 查看版本
python build.py --version
```

## 📋 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--keep-temp` | 保留临时文件（build、dist、*.spec） | False（自动清理） |
| `--onedir` | 使用目录模式 | False（单文件模式） |
| `--help` | 显示帮助信息 | - |
| `--version` | 显示版本信息 | - |

## ✨ 特性说明

### 1. 自动清理（默认开启）

**清理内容：**
- `build/` - PyInstaller 构建缓存
- `dist/` - 临时输出目录
- `*.spec` - PyInstaller 配置文件
- `__pycache__/` - Python 缓存目录

**何时清理：**
- 构建开始前清理旧产物
- 构建完成后自动清理临时文件

**如何保留：**
```bash
python build.py --keep-temp
```

### 2. 自动安装依赖

构建脚本会自动检测并安装缺失的依赖：

```
[INFO] 检查 Python 版本和依赖...
[INFO] PyYAML 已安装
[INFO] pandas 已安装
[INFO] openpyxl 已安装
[WARN] pyautogui 缺失，自动安装...
[INFO] pyautogui 已安装
```

### 3. 只复制 YAML 配置

`uploader/regions/` 目录只复制 `.yaml` 文件：

**源目录：**
```
uploader/regions/
├── hk/sneakers/
│   ├── __init__.py
│   ├── sneakers_uploader.py
│   └── css_selectors.yaml
```

**发布包：**
```
uploader/regions/
└── hk/sneakers/
    └── css_selectors.yaml  ← 只有这个
```

### 4. 完整收集依赖

使用 `--collect-all` 确保以下库的完整打包：
- `pyautogui` - 包括所有子模块
- `pyperclip` - 剪贴板操作
- `PIL` (Pillow) - 图像处理

## 📊 构建输出示例

```
[INFO] 🚀 Carousell Uploader 构建开始
[INFO] 检查 Python 版本和依赖...
[INFO] PyYAML 已安装
[INFO] pandas 已安装
[INFO] openpyxl 已安装
[INFO] playwright 已安装
[INFO] requests 已安装
[INFO] pyautogui 已安装
[INFO] pyperclip 已安装
[INFO] Pillow 已安装
[INFO] PyInstaller 版本: 6.16.0
[INFO] 入口文件: /path/to/cli/main.py
[INFO] 已清理旧构建产物
[INFO] 执行打包命令: pyinstaller --noconfirm --clean --onefile...
[构建过程...]
[INFO] 发布包创建成功: /path/to/release/carousell_uploader_1.0.0_Windows_20251010_162030
[INFO] 🧹 自动清理构建临时文件...
[INFO] 删除目录: build
[INFO] 删除目录: dist
[INFO] 删除文件: carousell_uploader.spec
[INFO] 删除 5 个 __pycache__ 目录
[INFO] ✅ 临时文件清理完成
[INFO] 🎉 构建完成: carousell_uploader.exe -> carousell_uploader_1.0.0_Windows_20251010_162030
[INFO] 📂 发布包位置: /path/to/release/carousell_uploader_1.0.0_Windows_20251010_162030
```

## 🎯 使用场景

### 场景 1：正常发布

```bash
# 一键构建
python build.py

# 结果：
# - 生成可执行文件
# - 创建发布包
# - 自动清理临时文件
# - 项目目录干净整洁
```

### 场景 2：调试构建

```bash
# 保留临时文件以便调试
python build.py --keep-temp

# 结果：
# - 生成可执行文件
# - 创建发布包
# - 保留 build/、dist/、*.spec
# - 可以查看 .spec 文件或构建日志
```

### 场景 3：目录模式（启动更快）

```bash
# 使用目录模式
python build.py --onedir

# 结果：
# - 生成目录形式的可执行文件
# - 启动速度更快
# - 体积稍大
# - 自动清理临时文件
```

### 场景 4：调试目录模式

```bash
# 目录模式 + 保留临时文件
python build.py --onedir --keep-temp

# 结果：
# - 目录形式可执行文件
# - 保留所有临时文件
# - 便于调试和分析
```

## 📦 发布包结构

```
release/carousell_uploader_1.0.0_<系统>_<时间>/
├── carousell_uploader[.exe]      # 可执行文件
├── config/                        # 配置文件
│   └── settings.example.yaml
├── uploader/regions/             # CSS 配置（仅 YAML）
│   ├── hk/sneakers/css_selectors.yaml
│   └── sg/sneakers/css_selectors.yaml
├── example_products.xlsx         # 示例文件
├── README.md                     # 项目说明
├── requirements.txt              # 依赖列表
├── USAGE.txt                     # 使用说明
└── run.bat / run.sh              # 启动脚本
```

## 💡 常见问题

### Q: 为什么默认自动清理？

A: 
- 保持项目目录整洁
- 减少磁盘占用
- 避免旧文件干扰
- 发布包已包含所有需要的文件

### Q: 什么时候需要 --keep-temp？

A:
- 调试构建问题
- 查看 .spec 文件
- 分析依赖关系
- 手动修改 .spec 后重新构建

### Q: onefile 和 onedir 有什么区别？

A:

| 模式 | 优点 | 缺点 | 推荐场景 |
|------|------|------|----------|
| onefile | 单个文件，便于分发 | 启动慢，体积大 | 给用户分发 |
| onedir | 启动快，便于调试 | 多个文件 | 开发测试 |

### Q: 临时文件占用多少空间？

A: 通常 100-500 MB，取决于依赖数量。自动清理后只保留约 20-50 MB 的发布包。

## 🔍 文件说明

### 构建产生的文件

**临时文件（自动清理）：**
- `build/` - PyInstaller 构建缓存（~100-300 MB）
- `dist/` - 临时输出目录（~20-50 MB）
- `*.spec` - PyInstaller 配置文件（~5 KB）
- `__pycache__/` - Python 缓存（~1-10 MB）

**永久文件（保留）：**
- `release/` - 发布包目录（每次构建创建新子目录）

### 发布包内的文件

所有文件都是用户需要的：
- ✅ 可执行文件
- ✅ 配置文件（可修改）
- ✅ CSS 配置（可修改）
- ✅ 示例文件
- ✅ 文档和说明
- ✅ 启动脚本

## 📝 完整构建流程

```
1. 环境检查
   ├── Python 版本检查
   ├── 自动安装缺失依赖
   └── 验证入口文件

2. 清理旧产物
   ├── 删除 build/
   ├── 删除 dist/
   ├── 删除 *.spec
   └── 清理 __pycache__/

3. 执行构建
   ├── 生成 PyInstaller 命令
   ├── 添加数据文件
   ├── 添加隐藏导入
   ├── 收集完整依赖
   └── 执行打包

4. 创建发布包
   ├── 复制可执行文件
   ├── 复制配置文件
   ├── 复制 regions YAML
   ├── 复制示例文件
   ├── 生成 USAGE.txt
   └── 生成启动脚本

5. 自动清理（可选）
   ├── 删除 build/
   ├── 删除 dist/
   ├── 删除 *.spec
   └── 清理 __pycache__/

6. 完成
   └── 显示发布包位置
```

## 🎉 总结

现在的 `build.py` 是：
- ✅ **智能** - 自动安装依赖
- ✅ **简洁** - 自动清理临时文件
- ✅ **灵活** - 支持命令行参数
- ✅ **完整** - 收集所有必要依赖
- ✅ **优化** - 只打包 YAML 配置文件

一行命令，完成构建！🚀

```bash
python build.py
```

---

**最后更新：** 2025-10-10  
**版本：** v1.0.0  
**文件大小：** 约 350 行

