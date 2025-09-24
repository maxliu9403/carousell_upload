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
    
    # Windows系统特殊处理
    if [ "$OS" = "windows" ]; then
        print_info "检测到Windows系统，尝试多种Python路径..."
        
        # 尝试不同的Python命令
        PYTHON_CMD=""
        for cmd in python python3 py; do
            if command -v "$cmd" &> /dev/null; then
                # 检查是否指向Microsoft Store
                if "$cmd" --version 2>&1 | grep -q "Microsoft Store"; then
                    print_warning "检测到Microsoft Store Python，跳过: $cmd"
                    continue
                fi
                
                # 检查版本
                if "$cmd" -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
                    PYTHON_CMD="$cmd"
                    print_success "找到可用的Python: $cmd"
                    break
                fi
            fi
        done
        
        if [ -n "$PYTHON_CMD" ]; then
            PYTHON_VERSION=$("$PYTHON_CMD" --version 2>&1 | cut -d' ' -f2)
            print_success "使用Python: $PYTHON_CMD (版本: $PYTHON_VERSION)"
        else
            print_error "未找到合适的Python安装"
            print_info "Windows系统Python安装指南:"
            print_info "1. 从 https://python.org 下载Python 3.8+"
            print_info "2. 安装时勾选 'Add Python to PATH'"
            print_info "3. 或者使用 py launcher: py -3"
            print_info "4. 避免使用Microsoft Store版本"
            exit 1
        fi
    else
        # 非Windows系统
        if command -v python3 &> /dev/null; then
            PYTHON_CMD="python3"
            PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
            print_success "检测到Python版本: $PYTHON_VERSION"
        else
            print_error "未找到Python3，请先安装Python 3.8+"
            print_info "安装指南:"
            print_info "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
            print_info "  CentOS/RHEL: sudo yum install python3 python3-pip"
            print_info "  macOS: brew install python3"
            exit 1
        fi
    fi
    
    # 详细版本检查
    print_info "详细版本信息:"
    "$PYTHON_CMD" -c "
import sys
print(f'  Python版本: {sys.version}')
print(f'  主版本号: {sys.version_info.major}')
print(f'  次版本号: {sys.version_info.minor}')
print(f'  微版本号: {sys.version_info.micro}')
print(f'  版本元组: {sys.version_info[:3]}')
"
    
    # 检查版本是否>=3.8
    if "$PYTHON_CMD" -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
        print_success "Python版本符合要求 (>=3.8)"
        # 设置全局Python命令
        export PYTHON_CMD
    else
        print_error "Python版本不符合要求，需要>=3.8"
        print_info "当前版本: $PYTHON_VERSION"
        print_info "请升级Python版本到3.8或更高版本"
        exit 1
    fi
}

# 检查pip
check_pip() {
    print_info "检查pip..."
    
    if command -v pip3 &> /dev/null; then
        print_success "pip已安装"
    elif "$PYTHON_CMD" -m pip --version &> /dev/null; then
        print_success "pip已安装 (通过$PYTHON_CMD -m pip)"
    else
        print_error "未找到pip，请先安装pip"
        exit 1
    fi
}

# 创建项目目录
create_project_dir() {
    print_info "创建项目目录..."
    
    # 使用当前目录作为项目目录
    PROJECT_DIR="$(pwd)"
    
    print_info "项目目录: $PROJECT_DIR"
    
    # 检查当前目录是否为空或只包含项目文件
    if [ ! -f "requirements.txt" ] && [ ! -f "README.md" ]; then
        print_warning "当前目录不包含项目文件"
        print_info "请确保在项目根目录下运行安装脚本"
        print_info "或者先克隆项目: git clone https://github.com/maxliu9403/carousell_upload.git"
        read -p "是否继续? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "请先克隆项目到当前目录"
            exit 0
        fi
    fi
    
    print_success "使用当前目录作为项目目录: $PROJECT_DIR"
}

# 创建用户
create_user() {
    print_info "检查用户权限..."
    
    # 使用当前目录时，不需要创建系统用户
    print_info "使用当前目录部署，无需创建系统用户"
    print_success "将使用当前用户权限运行"
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

# 创建Python虚拟环境
create_virtual_env() {
    print_info "创建Python虚拟环境..."
    
    cd "$PROJECT_DIR"
    
    # 检查Python版本
    PYTHON_VERSION=$("$PYTHON_CMD" --version 2>&1 | cut -d' ' -f2)
    print_info "Python版本: $PYTHON_VERSION"
    
    # 检查版本是否>=3.8
    if "$PYTHON_CMD" -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_success "Python版本符合要求 (>=3.8)"
    else
        print_error "Python版本不符合要求，需要>=3.8"
        exit 1
    fi
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        print_info "创建虚拟环境..."
        "$PYTHON_CMD" -m venv venv
        print_success "虚拟环境创建完成: $PROJECT_DIR/venv"
    else
        print_warning "虚拟环境已存在: $PROJECT_DIR/venv"
    fi
    
    # 验证虚拟环境
    if [ -f "venv/bin/activate" ]; then
        print_success "虚拟环境验证通过"
    else
        print_error "虚拟环境创建失败"
        exit 1
    fi
}

# 安装Python依赖
install_python_deps() {
    print_info "安装Python依赖..."
    
    cd "$PROJECT_DIR"
    
    # 激活虚拟环境
    print_info "激活虚拟环境..."
    source venv/bin/activate
    
    # 验证虚拟环境激活
    if [ "$VIRTUAL_ENV" = "$PROJECT_DIR/venv" ]; then
        print_success "虚拟环境已激活: $VIRTUAL_ENV"
    else
        print_error "虚拟环境激活失败"
        exit 1
    fi
    
    # 升级pip
    print_info "升级pip..."
    pip install --upgrade pip
    
    # 安装wheel和setuptools
    print_info "安装基础包..."
    pip install wheel setuptools
    
    # 安装依赖
    if [ -f "requirements.txt" ]; then
        print_info "安装项目依赖..."
        pip install -r requirements.txt
        print_success "Python依赖安装完成"
    else
        print_error "未找到requirements.txt文件"
        exit 1
    fi
    
    # 安装开发依赖（可选）
    if [ -f "requirements-dev.txt" ]; then
        print_info "安装开发依赖..."
        pip install -r requirements-dev.txt
        print_success "开发依赖安装完成"
    else
        print_warning "未找到requirements-dev.txt文件，跳过开发依赖安装"
    fi
    
    # 安装Playwright浏览器
    print_info "安装Playwright浏览器..."
    playwright install chromium
    print_success "Playwright浏览器安装完成"
    
    # 验证安装
    print_info "验证Python包安装..."
    "$PYTHON_CMD" -c "
import sys
try:
    import playwright
    import requests
    import yaml
    import pandas
    print('✅ 核心依赖验证通过')
except ImportError as e:
    print(f'❌ 依赖验证失败: {e}')
    sys.exit(1)
"
    
    print_success "Python环境配置完成"
}

# 配置服务
configure_service() {
    print_info "配置运行环境..."
    
    # 使用当前目录时，不需要系统服务
    print_info "使用当前目录部署，跳过系统服务配置"
    print_success "将使用本地运行方式"
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
    
    # 使用当前目录时，不需要设置特殊权限
    print_success "目录创建完成"
}

# 测试安装
test_installation() {
    print_info "测试安装..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    # 测试Python导入
    "$PYTHON_CMD" -c "
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

# 创建虚拟环境管理脚本
create_venv_scripts() {
    print_info "创建虚拟环境管理脚本..."
    
    cd "$PROJECT_DIR"
    
    # 创建激活脚本
    cat > activate_env.sh << 'EOF'
#!/bin/bash
# Carousell Uploader 虚拟环境激活脚本

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

if [ -f "$VENV_DIR/bin/activate" ]; then
    echo "🚀 激活虚拟环境..."
    source "$VENV_DIR/bin/activate"
    echo "✅ 虚拟环境已激活: $VIRTUAL_ENV"
    echo "📁 项目目录: $PROJECT_DIR"
    echo ""
    echo "💡 使用说明:"
    echo "  - 运行程序: python -m cli.main"
    echo "  - 退出环境: deactivate"
    echo "  - 查看帮助: python -m cli.main --help"
else
    echo "❌ 虚拟环境未找到: $VENV_DIR"
    echo "请先运行安装脚本: sudo ./install.sh"
    exit 1
fi
EOF
    
    chmod +x activate_env.sh
    print_success "虚拟环境激活脚本创建完成: activate_env.sh"
    
    # 创建快速启动脚本
    cat > run.sh << 'EOF'
#!/bin/bash
# Carousell Uploader 快速启动脚本

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
    echo "🚀 启动 Carousell Uploader..."
    python -m cli.main "$@"
else
    echo "❌ 虚拟环境未找到，请先运行安装脚本"
    exit 1
fi
EOF
    
    chmod +x run.sh
    print_success "快速启动脚本创建完成: run.sh"
}

# 显示使用说明
show_usage() {
    print_success "🎉 安装完成！"
    echo ""
    print_info "📁 项目目录: $PROJECT_DIR"
    print_info "🐍 虚拟环境: $PROJECT_DIR/venv"
    echo ""
    print_info "🚀 快速使用:"
    echo "1. 激活虚拟环境: cd $PROJECT_DIR && source venv/bin/activate"
    echo "2. 或使用激活脚本: cd $PROJECT_DIR && ./activate_env.sh"
    echo "3. 或直接运行: cd $PROJECT_DIR && ./run.sh"
    echo ""
    print_info "⚙️ 配置设置:"
    echo "1. 编辑配置文件: nano $PROJECT_DIR/config/settings.yaml"
    echo "2. 设置API密钥和其他配置"
    echo ""
    print_info "🔧 运行方式:"
    echo "1. 直接运行: python -m cli.main"
    echo "2. 使用启动脚本: ./run.sh"
    echo "3. 激活环境后运行: source venv/bin/activate && python -m cli.main"
    echo ""
    print_info "📚 更多信息:"
    echo "- 项目文档: README.md"
    echo "- 配置说明: config/settings.example.yaml"
    echo "- 问题反馈: https://github.com/maxliu9403/carousell_upload/issues"
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
    create_virtual_env
    install_python_deps
    create_venv_scripts
    configure_service
    create_config
    create_directories
    test_installation
    show_usage
}

# 运行主函数
main "$@"
