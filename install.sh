#!/bin/bash
# Carousell Uploader 一键安装脚本

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

# 检查系统
check_system() {
    print_info "检查系统环境..."
    
    # 检查操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_success "检测到Linux系统"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_success "检测到macOS系统"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        print_success "检测到Windows系统"
    else
        print_error "不支持的操作系统: $OSTYPE"
        exit 1
    fi
}

# 检查Python
check_python() {
    print_info "检查Python环境..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_success "Python版本: $PYTHON_VERSION"
        
        # 检查版本是否>=3.8
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
            print_success "Python版本符合要求 (>=3.8)"
        else
            print_error "Python版本不符合要求，需要>=3.8"
            exit 1
        fi
    else
        print_error "未找到Python3，请先安装Python 3.8+"
        print_info "安装指南:"
        print_info "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
        print_info "  CentOS/RHEL: sudo yum install python3 python3-pip"
        print_info "  macOS: brew install python3"
        print_info "  Windows: 从 https://python.org 下载安装"
        exit 1
    fi
}

# 检查pip
check_pip() {
    print_info "检查pip..."
    
    if command -v pip3 &> /dev/null; then
        print_success "pip已安装"
    elif python3 -m pip --version &> /dev/null; then
        print_success "pip已安装 (通过python3 -m pip)"
    else
        print_error "未找到pip，请先安装pip"
        exit 1
    fi
}

# 创建项目目录
create_project_dir() {
    print_info "创建项目目录..."
    
    PROJECT_DIR="/opt/carousell-uploader"
    
    if [ "$OS" = "windows" ]; then
        PROJECT_DIR="C:\\carousell-uploader"
    fi
    
    if [ ! -d "$PROJECT_DIR" ]; then
        sudo mkdir -p "$PROJECT_DIR"
        print_success "项目目录创建完成: $PROJECT_DIR"
    else
        print_warning "项目目录已存在: $PROJECT_DIR"
    fi
}

# 创建用户
create_user() {
    print_info "创建系统用户..."
    
    if [ "$OS" = "linux" ]; then
        if ! id "carousell" &>/dev/null; then
            sudo useradd -r -s /bin/false carousell
            print_success "用户创建完成: carousell"
        else
            print_warning "用户已存在: carousell"
        fi
    fi
}

# 安装依赖
install_dependencies() {
    print_info "安装系统依赖..."
    
    if [ "$OS" = "linux" ]; then
        # Ubuntu/Debian
        if command -v apt &> /dev/null; then
            sudo apt update
            sudo apt install -y python3-venv python3-dev build-essential wget gnupg
        # CentOS/RHEL
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3-devel gcc wget gnupg
        fi
    elif [ "$OS" = "macos" ]; then
        if command -v brew &> /dev/null; then
            brew install python3
        else
            print_warning "建议安装Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        fi
    fi
    
    print_success "系统依赖安装完成"
}

# 安装Python依赖
install_python_deps() {
    print_info "安装Python依赖..."
    
    cd "$PROJECT_DIR"
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "虚拟环境创建完成"
    else
        print_warning "虚拟环境已存在"
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装依赖
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Python依赖安装完成"
    else
        print_error "未找到requirements.txt文件"
        exit 1
    fi
    
    # 安装Playwright浏览器
    print_info "安装Playwright浏览器..."
    playwright install chromium
    print_success "Playwright浏览器安装完成"
}

# 配置服务
configure_service() {
    print_info "配置系统服务..."
    
    if [ "$OS" = "linux" ]; then
        # 复制服务文件
        sudo cp carousell-uploader.service /etc/systemd/system/
        
        # 设置权限
        sudo chown -R carousell:carousell "$PROJECT_DIR"
        sudo chmod +x "$PROJECT_DIR/scripts"/*.sh
        
        # 启用服务
        sudo systemctl daemon-reload
        sudo systemctl enable carousell-uploader
        
        print_success "系统服务配置完成"
    else
        print_warning "非Linux系统，跳过系统服务配置"
    fi
}

# 创建配置文件
create_config() {
    print_info "创建配置文件..."
    
    cd "$PROJECT_DIR"
    
    if [ ! -f "config/settings.yaml" ]; then
        if [ -f "config/settings.example.yaml" ]; then
            cp config/settings.example.yaml config/settings.yaml
            print_success "配置文件创建完成: config/settings.yaml"
            print_warning "请编辑配置文件设置您的API密钥"
        else
            print_error "未找到配置文件模板"
            exit 1
        fi
    else
        print_warning "配置文件已存在: config/settings.yaml"
    fi
}

# 创建必要目录
create_directories() {
    print_info "创建必要目录..."
    
    cd "$PROJECT_DIR"
    
    mkdir -p logs data screenshots temp
    
    if [ "$OS" = "linux" ]; then
        sudo chown -R carousell:carousell logs data screenshots temp
    fi
    
    print_success "目录创建完成"
}

# 测试安装
test_installation() {
    print_info "测试安装..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    # 测试Python导入
    python3 -c "
import sys
try:
    import playwright
    import requests
    import yaml
    import pandas
    import openpyxl
    print('✅ 所有依赖包导入成功')
except ImportError as e:
    print(f'❌ 依赖包导入失败: {e}')
    sys.exit(1)
"
    
    print_success "安装测试通过"
}

# 显示使用说明
show_usage() {
    print_success "安装完成！"
    echo ""
    print_info "使用说明:"
    echo "1. 编辑配置: sudo nano $PROJECT_DIR/config/settings.yaml"
    echo "2. 启动服务: sudo systemctl start carousell-uploader"
    echo "3. 查看状态: sudo systemctl status carousell-uploader"
    echo "4. 查看日志: sudo journalctl -u carousell-uploader -f"
    echo ""
    print_info "手动运行:"
    echo "cd $PROJECT_DIR"
    echo "source venv/bin/activate"
    echo "python -m cli.main"
    echo ""
    print_info "更多信息请查看 README.md 和 QUICK_DEPLOYMENT.md"
}

# 主函数
main() {
    echo "🚀 Carousell Uploader 一键安装脚本"
    echo "=================================="
    echo ""
    
    check_system
    check_python
    check_pip
    create_project_dir
    create_user
    install_dependencies
    install_python_deps
    configure_service
    create_config
    create_directories
    test_installation
    show_usage
}

# 运行主函数
main "$@"
