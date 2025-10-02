# 构建相关文件

这个文件夹包含了所有与项目构建相关的文件和配置。

## 📁 文件说明

### 构建脚本
- **`build.py`** - 智能构建脚本
  - 自动检测项目模块和依赖
  - 动态生成PyInstaller配置
  - 支持onefile和onedir构建模式
  - 零维护成本

### Docker构建
- **`Dockerfile.windows`** - Windows Docker构建配置
  - 基于Windows Server Core
  - 包含Python环境和依赖
  - 支持PyInstaller构建

### 文档
- **`README.md`** - 本文件夹说明文档
- **`SMART_BUILD_SOLUTION.md`** - 智能构建解决方案详细说明

## 🚀 使用方法

### 本地构建
```bash
# 进入构建目录
cd build

# 单文件版本
python3 build.py --mode onefile

# 单目录版本
python3 build.py --mode onedir

# 不清理之前的构建
python3 build.py --mode onefile --no-clean
```

### Docker构建
```bash
# 构建Windows Docker镜像
docker build -f build/Dockerfile.windows -t carousell-uploader-windows .

# 运行容器
docker run -v $(pwd)/dist:/output carousell-uploader-windows
```

### GitHub Actions构建
GitHub Actions会自动使用这个文件夹中的构建脚本：
- 单文件构建：`python build/build.py --mode onefile`
- 单目录构建：`python build/build.py --mode onedir`

## 📋 构建模式

### onefile模式
- 生成单个可执行文件
- 文件较大但部署简单
- 适合单机使用

### onedir模式
- 生成包含所有文件的目录
- 文件较小但需要整个目录
- 适合批量部署

## 🔧 配置说明

构建脚本使用内置的默认配置，包括：

- **入口文件**: `cli/main.py`
- **输出名称**: `CarousellUploader`
- **数据文件**: `config/`, `uploader/regions/`, `data/`
- **重要模块**: 自动检测项目模块
- **排除模块**: 测试相关模块

## 📝 注意事项

1. **Python环境**: 确保Python 3.8+环境
2. **依赖安装**: 确保所有依赖已安装
3. **权限问题**: 确保有写入权限
4. **路径问题**: 在项目根目录运行构建脚本

## 🎯 优势

- ✅ **自动化**: 完全自动化的构建流程
- ✅ **智能化**: 自动检测项目变化
- ✅ **可维护**: 配置驱动的构建管理
- ✅ **可扩展**: 支持未来功能扩展
- ✅ **团队友好**: 统一的构建标准
