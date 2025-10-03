#!/bin/bash

# Carousell Uploader 构建脚本
set -e  # 遇到错误时退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    echo "Carousell Uploader 构建脚本"
    echo ""
    echo "用法: $0 [选项] 或 $0 [简化参数]"
    echo ""
    echo "选项:"
    echo "  -m, --mode MODE     构建模式: onefile 或 onedir (默认: onedir)"
    echo "  -p, --python PATH   Python 路径 (默认: python3)"
    echo "  -c, --clean         构建前清理 dist 目录"
    echo "  -h, --help          显示此帮助信息"
    echo ""
    echo "简化用法:"
    echo "  $0 onefile          构建单文件版本"
    echo "  $0 onedir           构建单目录版本"
    echo "  $0 clean           清理构建文件"
    echo ""
    echo "示例:"
    echo "  $0 --mode onefile"
    echo "  $0 --mode onedir --clean"
    echo "  $0 onefile"
    echo "  $0 onedir"
}

# 默认参数
BUILD_MODE="onedir"
PYTHON_CMD="python3"
CLEAN_BUILD=false

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--mode)
            BUILD_MODE="$2"
            shift 2
            ;;
        -p|--python)
            PYTHON_CMD="$2"
            shift 2
            ;;
        -c|--clean)
            CLEAN_BUILD=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        # 简化用法支持
        onefile)
            BUILD_MODE="onefile"
            shift
            ;;
        onedir)
            BUILD_MODE="onedir"
            shift
            ;;
        clean)
            CLEAN_BUILD=true
            shift
            ;;
        *)
            log_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 验证构建模式
if [[ "$BUILD_MODE" != "onefile" && "$BUILD_MODE" != "onedir" ]]; then
    log_error "无效的构建模式: $BUILD_MODE"
    log_error "支持的模式: onefile, onedir"
    exit 1
fi

log_info "开始构建 Carousell Uploader..."
log_info "构建模式: $BUILD_MODE"
log_info "Python 命令: $PYTHON_CMD"

# 检查 Python 是否可用
if ! command -v "$PYTHON_CMD" &> /dev/null; then
    log_error "Python 命令 '$PYTHON_CMD' 不可用"
    exit 1
fi

# 检查 Python 版本
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
log_info "Python 版本: $PYTHON_VERSION"

# 清理构建目录
if [ "$CLEAN_BUILD" = true ]; then
    log_info "清理构建目录..."
    rm -rf dist/
    rm -rf build/
    rm -rf *.spec
    rm -rf venv/
    log_info "已清理所有构建文件和虚拟环境"
fi

# 创建必要的目录
log_info "创建构建目录..."
mkdir -p dist
mkdir -p build

# 检查并创建虚拟环境
if [ ! -d "venv" ]; then
    log_info "创建虚拟环境..."
    $PYTHON_CMD -m venv venv
fi

# 激活虚拟环境
log_info "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
log_info "安装依赖包..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
playwright install chromium

# 构建可执行文件
log_info "开始构建可执行文件 (模式: $BUILD_MODE)..."

if [ "$BUILD_MODE" = "onefile" ]; then
    log_info "构建单文件版本..."
    $PYTHON_CMD -m PyInstaller \
        --onefile \
        --console \
        --name=CarousellUploader \
        --add-data="config:config" \
        --add-data="uploader/regions:uploader/regions" \
        --add-data="browser:browser" \
        --add-data="data:data" \
        --paths=. \
        --hidden-import=playwright \
        --hidden-import=pyautogui \
        --hidden-import=pyperclip \
        --hidden-import=openpyxl \
        --hidden-import=pandas \
        --hidden-import=yaml \
        --hidden-import=requests \
        --hidden-import=PIL \
        --hidden-import=selenium \
        --hidden-import=webdriver_manager \
        --hidden-import=core \
        --hidden-import=core.config \
        --hidden-import=core.logger \
        --hidden-import=core.models \
        --hidden-import=uploader \
        --hidden-import=uploader.actions \
        --hidden-import=uploader.config \
        --hidden-import=uploader.core \
        --hidden-import=uploader.factory \
        --hidden-import=uploader.multi \
        --hidden-import=uploader.regions \
        --hidden-import=uploader.utils \
        --hidden-import=browser \
        --hidden-import=browser.browser \
        --hidden-import=browser.browser_factory \
        --hidden-import=browser.browser_interface \
        --hidden-import=browser.browser_selector \
        --hidden-import=data \
        --hidden-import=data.excel_parser \
        --hidden-import=data.record_manager \
        --hidden-import=cli \
        --hidden-import=cli.main \
        cli/main.py
else
    log_info "构建单目录版本..."
    $PYTHON_CMD -m PyInstaller \
        --onedir \
        --console \
        --name=CarousellUploader \
        --add-data="config:config" \
        --add-data="uploader/regions:uploader/regions" \
        --add-data="browser:browser" \
        --add-data="data:data" \
        --paths=. \
        --hidden-import=playwright \
        --hidden-import=pyautogui \
        --hidden-import=pyperclip \
        --hidden-import=openpyxl \
        --hidden-import=pandas \
        --hidden-import=yaml \
        --hidden-import=requests \
        --hidden-import=PIL \
        --hidden-import=selenium \
        --hidden-import=webdriver_manager \
        --hidden-import=core \
        --hidden-import=core.config \
        --hidden-import=core.logger \
        --hidden-import=core.models \
        --hidden-import=uploader \
        --hidden-import=uploader.actions \
        --hidden-import=uploader.config \
        --hidden-import=uploader.core \
        --hidden-import=uploader.factory \
        --hidden-import=uploader.multi \
        --hidden-import=uploader.regions \
        --hidden-import=uploader.utils \
        --hidden-import=browser \
        --hidden-import=browser.browser \
        --hidden-import=browser.browser_factory \
        --hidden-import=browser.browser_interface \
        --hidden-import=browser.browser_selector \
        --hidden-import=data \
        --hidden-import=data.excel_parser \
        --hidden-import=data.record_manager \
        --hidden-import=cli \
        --hidden-import=cli.main \
        cli/main.py
fi

# 检查构建结果
log_info "检查构建结果..."
if [ "$BUILD_MODE" = "onefile" ]; then
    if [ -f "dist/CarousellUploader" ]; then
        log_success "单文件可执行文件创建成功"
    else
        log_error "单文件可执行文件未找到"
        exit 1
    fi
else
    if [ -d "dist/CarousellUploader" ]; then
        log_success "单目录版本创建成功"
    else
        log_error "单目录版本未找到"
        exit 1
    fi
fi

# 复制配置文件和区域配置
log_info "复制配置文件和区域配置到 dist 目录..."

# 创建 config 目录
mkdir -p dist/config
cp config/settings.yaml dist/config/ 2>/dev/null || log_warning "settings.yaml 不存在，跳过复制"
cp config/settings.example.yaml dist/config/ 2>/dev/null || log_warning "settings.example.yaml 不存在，跳过复制"

# 创建 uploader/regions 目录结构
mkdir -p dist/uploader/regions/hk/sneakers
mkdir -p dist/uploader/regions/sg/sneakers

# 复制 CSS 选择器配置文件
cp uploader/regions/hk/sneakers/css_selectors.yaml dist/uploader/regions/hk/sneakers/ 2>/dev/null || log_warning "HK CSS 选择器文件不存在，跳过复制"
cp uploader/regions/sg/sneakers/css_selectors.yaml dist/uploader/regions/sg/sneakers/ 2>/dev/null || log_warning "SG CSS 选择器文件不存在，跳过复制"

# 创建 logs 目录
mkdir -p dist/logs

# 创建 README.txt
log_info "创建 README.txt..."
cat > dist/README.txt << 'EOF'
Carousell Uploader Linux/macOS 可执行文件

使用方法:
1. 确保系统已安装必要的依赖库
2. 直接运行 CarousellUploader (单文件版本) 或 CarousellUploader/CarousellUploader (单目录版本)
3. 配置文件位于 config/ 目录
4. CSS选择器配置位于 uploader/regions/ 目录

配置说明:
- 程序会优先使用外部配置文件
- 如果外部配置文件不存在，会使用内置配置
- 修改 config/settings.yaml 来调整主配置
- 修改 uploader/regions/*/css_selectors.yaml 来调整CSS选择器

CSS选择器配置:
- HK: uploader/regions/hk/sneakers/css_selectors.yaml
- SG: uploader/regions/sg/sneakers/css_selectors.yaml
- 支持热更新，修改后程序会自动重新加载

日志文件:
- 日志文件保存在 logs/ 目录
- 按日期自动分割: carousell_YYYYMMDD.log
- 支持外部查看和管理日志文件
- 自动清理: 只保留最近5天的日志文件
- 时间轮转: 每天午夜自动创建新的日志文件

系统要求:
- Linux: 需要安装必要的系统库
- macOS: 需要安装 Xcode Command Line Tools
- 确保有足够的磁盘空间和内存
EOF

# 清理构建过程中的临时文件
log_info "清理构建临时文件..."
rm -rf build/
rm -rf *.spec
log_info "已清理 build/ 目录和 .spec 文件"

# 显示目录结构
log_info "Dist 目录结构:"
find dist -type f -o -type d | sort

# 显示构建统计信息
log_info "构建统计信息:"
if [ "$BUILD_MODE" = "onefile" ]; then
    if [ -f "dist/CarousellUploader" ]; then
        FILE_SIZE=$(du -h dist/CarousellUploader | cut -f1)
        log_info "可执行文件大小: $FILE_SIZE"
    fi
else
    if [ -d "dist/CarousellUploader" ]; then
        DIR_SIZE=$(du -sh dist/CarousellUploader | cut -f1)
        log_info "目录大小: $DIR_SIZE"
    fi
fi

log_success "构建完成！"
log_info "输出目录: dist/"
if [ "$BUILD_MODE" = "onefile" ]; then
    log_info "可执行文件: dist/CarousellUploader"
else
    log_info "可执行文件: dist/CarousellUploader/CarousellUploader"
fi
