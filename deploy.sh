#!/bin/bash
# Carousell Uploader 统一部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# 显示帮助信息
show_help() {
    print_header "🚀 Carousell Uploader 统一部署脚本"
    echo ""
    echo "使用方法:"
    echo "  ./deploy.sh [选项]"
    echo ""
    echo "选项:"
    echo "  --mode=MODE     指定部署模式"
    echo "  --help          显示此帮助信息"
    echo ""
    echo "部署模式:"
    echo "  local           本地开发部署 (默认)"
    echo "  system          系统级生产部署"
    echo "  docker          Docker容器部署"
    echo "  auto            自动检测最佳方式"
    echo ""
    echo "示例:"
    echo "  ./deploy.sh                    # 本地开发部署"
    echo "  ./deploy.sh --mode=system      # 系统级部署"
    echo "  ./deploy.sh --mode=docker       # Docker部署"
    echo "  ./deploy.sh --mode=auto         # 自动检测"
    echo ""
}

# 检查脚本依赖
check_script_dependencies() {
    print_info "检查脚本依赖..."
    
    # 检查必要的脚本文件
    if [ ! -f "scripts/quick-deploy.sh" ]; then
        print_error "未找到 scripts/quick-deploy.sh"
        exit 1
    fi
    
    if [ ! -f "scripts/docker-deploy.sh" ]; then
        print_error "未找到 scripts/docker-deploy.sh"
        exit 1
    fi
    
    if [ ! -f "install.sh" ]; then
        print_error "未找到 install.sh"
        exit 1
    fi
    
    print_success "脚本依赖检查通过"
}

# 自动检测最佳部署方式
auto_detect_mode() {
    print_info "自动检测最佳部署方式..."
    
    # 检查是否为root用户
    if [ "$EUID" -eq 0 ]; then
        print_info "检测到root权限，推荐系统级部署"
        echo "system"
        return
    fi
    
    # 检查Docker是否可用
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        print_info "检测到Docker环境，推荐容器化部署"
        echo "docker"
        return
    fi
    
    # 检查Python环境
    if command -v python3 &> /dev/null; then
        print_info "检测到Python环境，使用本地部署"
        echo "local"
        return
    fi
    
    print_warning "无法自动检测，使用默认本地部署"
    echo "local"
}

# 执行本地部署
deploy_local() {
    print_header "🚀 执行本地开发部署..."
    
    if [ ! -f "scripts/quick-deploy.sh" ]; then
        print_error "未找到快速部署脚本"
        exit 1
    fi
    
    chmod +x scripts/quick-deploy.sh
    ./scripts/quick-deploy.sh
}

# 执行系统级部署
deploy_system() {
    print_header "🚀 执行系统级生产部署..."
    
    if [ ! -f "install.sh" ]; then
        print_error "未找到系统安装脚本"
        exit 1
    fi
    
    chmod +x install.sh
    ./install.sh
}

# 执行Docker部署
deploy_docker() {
    print_header "🚀 执行Docker容器部署..."
    
    if [ ! -f "scripts/docker-deploy.sh" ]; then
        print_error "未找到Docker部署脚本"
        exit 1
    fi
    
    chmod +x scripts/docker-deploy.sh
    ./scripts/docker-deploy.sh
}

# 验证部署结果
verify_deployment() {
    print_info "验证部署结果..."
    
    # 检查Python环境
    if command -v python3 &> /dev/null; then
        print_success "Python环境正常"
    else
        print_warning "Python环境检查失败"
    fi
    
    # 检查虚拟环境
    if [ -d "venv" ]; then
        print_success "虚拟环境已创建"
    else
        print_warning "虚拟环境未找到"
    fi
    
    # 检查依赖文件
    if [ -f "requirements.txt" ]; then
        print_success "依赖文件存在"
    else
        print_warning "依赖文件未找到"
    fi
    
    # 检查配置文件
    if [ -f "config/settings.yaml" ]; then
        print_success "配置文件已创建"
    else
        print_warning "配置文件未找到，请手动创建"
    fi
}

# 显示部署后信息
show_post_deployment_info() {
    print_header "🎉 部署完成！"
    echo ""
    print_info "下一步操作:"
    echo "1. 编辑配置文件: nano config/settings.yaml"
    echo "2. 运行程序: python -m cli.main"
    echo "3. 查看日志: tail -f logs/carousell_uploader.log"
    echo ""
    print_info "更多信息:"
    echo "- 项目文档: README.md"
    echo "- 快速部署: QUICK_DEPLOYMENT.md"
    echo "- 详细部署: DEPLOYMENT_GUIDE.md"
    echo ""
}

# 主函数
main() {
    # 解析命令行参数
    MODE="auto"
    HELP=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --mode=*)
                MODE="${1#*=}"
                shift
                ;;
            --mode)
                MODE="$2"
                shift 2
                ;;
            --help|-h)
                HELP=true
                shift
                ;;
            *)
                print_error "未知参数: $1"
                echo "使用 --help 查看帮助信息"
                exit 1
                ;;
        esac
    done
    
    # 显示帮助信息
    if [ "$HELP" = true ]; then
        show_help
        exit 0
    fi
    
    # 检查脚本依赖
    check_script_dependencies
    
    # 自动检测模式
    if [ "$MODE" = "auto" ]; then
        MODE=$(auto_detect_mode)
        print_info "自动检测到部署模式: $MODE"
    fi
    
    # 根据模式执行部署
    case $MODE in
        "local")
            deploy_local
            ;;
        "system")
            deploy_system
            ;;
        "docker")
            deploy_docker
            ;;
        *)
            print_error "未知部署模式: $MODE"
            echo "支持的模式: local, system, docker, auto"
            exit 1
            ;;
    esac
    
    # 验证部署结果
    verify_deployment
    
    # 显示部署后信息
    show_post_deployment_info
}

# 运行主函数
main "$@"
