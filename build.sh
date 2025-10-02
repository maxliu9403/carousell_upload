#!/bin/bash
# 快速构建脚本 - 项目根目录入口

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查Python环境
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python未找到，请安装Python 3.8+"
        exit 1
    fi
    
    print_info "使用Python: $PYTHON_CMD"
}

# 检查构建目录
check_build_dir() {
    if [ ! -d "build" ]; then
        print_error "构建目录不存在: build/"
        exit 1
    fi
    
    if [ ! -f "build/build.py" ]; then
        print_error "构建脚本不存在: build/build.py"
        exit 1
    fi
}

# 显示帮助信息
show_help() {
    echo "🚀 Carousell Uploader 快速构建脚本"
    echo "=================================="
    echo ""
    echo "使用方法:"
    echo "  $0 [选项]"
    echo ""
    echo "选项:"
    echo "  onefile    构建单文件版本 (默认)"
    echo "  onedir     构建单目录版本"
    echo "  clean      清理构建文件"
    echo "  help       显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0              # 构建单文件版本"
    echo "  $0 onefile      # 构建单文件版本"
    echo "  $0 onedir       # 构建单目录版本"
    echo "  $0 clean        # 清理构建文件"
}

# 清理构建文件
clean_build() {
    print_info "正在清理构建文件..."
    
    if [ -d "build" ]; then
        cd build
        rm -rf build/ dist/ __pycache__/ *.spec
        print_success "构建文件已清理"
        cd ..
    fi
    
    if [ -d "dist" ]; then
        rm -rf dist/
        print_success "输出目录已清理"
    fi
}

# 执行构建
run_build() {
    local mode=$1
    
    print_info "开始构建 $mode 版本..."
    print_info "构建目录: build/"
    print_info "构建脚本: build/build.py"
    
    cd build
    $PYTHON_CMD build.py --mode $mode
    cd ..
    
    print_success "构建完成!"
    
    # 显示构建结果
    if [ -d "dist" ]; then
        print_info "构建结果:"
        ls -la dist/
    fi
}

# 主函数
main() {
    print_info "🚀 Carousell Uploader 快速构建脚本"
    print_info "=================================="
    
    # 检查环境
    check_python
    check_build_dir
    
    # 处理参数
    case "${1:-onefile}" in
        "onefile")
            run_build "onefile"
            ;;
        "onedir")
            run_build "onedir"
            ;;
        "clean")
            clean_build
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
