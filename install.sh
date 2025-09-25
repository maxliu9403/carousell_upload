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

# 下载文件函数（带错误处理）
download_file() {
    local url="$1"
    local output="$2"
    local retries=3
    local count=0
    
    while [ $count -lt $retries ]; do
        if curl -fsSL "$url" -o "$output" 2>/dev/null; then
            return 0
        else
            count=$((count + 1))
            if [ $count -lt $retries ]; then
                print_warning "下载失败，重试中... ($count/$retries)"
                sleep 2
            fi
        fi
    done
    
    print_error "下载失败: $url"
    return 1
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

# 下载项目文件
# 获取项目文件列表（动态适配）
get_project_files() {
    print_info "🔍 获取项目文件列表..."
    
    # 尝试从GitHub API获取文件列表
    local api_url="https://api.github.com/repos/maxliu9403/carousell_upload/contents"
    local temp_file="/tmp/project_files.json"
    
    if curl -fsSL "$api_url" -o "$temp_file" 2>/dev/null; then
        # 使用Python解析GitHub API响应
        python3 -c "
import json
import sys
import subprocess

def get_files_from_api(data, prefix=''):
    files = []
    for item in data:
        if item['type'] == 'file':
            files.append(prefix + item['name'])
        elif item['type'] == 'dir' and item['name'] not in ['.git', '__pycache__', '.venv']:
            # 递归获取子目录文件
            try:
                result = subprocess.run(['curl', '-fsSL', item['url']], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    subdata = json.loads(result.stdout)
                    files.extend(get_files_from_api(subdata, prefix + item['name'] + '/'))
            except:
                pass
    return files

try:
    with open('$temp_file', 'r') as f:
        data = json.load(f)
    
    files = get_files_from_api(data)
    for file in sorted(files):
        print(file)
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
" > /tmp/project_files_list.txt 2>/dev/null
        
        if [ -s /tmp/project_files_list.txt ]; then
            print_success "✅ 成功获取项目文件列表"
            return 0
        fi
    fi
    
    # 如果API失败，使用预定义的文件列表作为备用
    print_warning "⚠️ API获取失败，使用预定义文件列表"
    return 1
}

# 更新项目代码到最新版本
update_project_code() {
    print_info "🔄 更新项目代码到最新版本..."
    
    # 检查是否已存在项目目录
    if [ -d ".git" ]; then
        print_info "检测到Git仓库，尝试拉取最新代码..."
        if git pull origin main; then
            print_success "✅ 代码更新成功"
            return 0
        else
            print_warning "⚠️ Git拉取失败，尝试重新下载..."
        fi
    fi
    
    # 如果Git更新失败或不存在，使用curl下载最新文件
    print_info "📥 下载最新项目文件..."
    
    # 检查curl是否可用
    if ! command -v curl &> /dev/null; then
        print_error "curl不可用，无法下载项目文件"
        return 1
    fi
    
    # 尝试获取动态文件列表
    if get_project_files; then
        print_info "📋 使用动态文件列表..."
        update_with_dynamic_list
    else
        print_info "📋 使用预定义文件列表..."
        update_with_static_list
    fi
}

# 使用动态文件列表更新
update_with_dynamic_list() {
    # 创建必要的目录结构
    print_info "📁 创建目录结构..."
    while IFS= read -r file; do
        if [[ "$file" == *"/"* ]]; then
            dir=$(dirname "$file")
            mkdir -p "$dir"
        fi
    done < /tmp/project_files_list.txt
    
    # 下载所有文件
    print_info "📥 下载项目文件..."
    local success_count=0
    local total_count=0
    
    while IFS= read -r file; do
        total_count=$((total_count + 1))
        print_info "下载: $file"
        
        if download_file "https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/$file" "$file"; then
            success_count=$((success_count + 1))
        else
            print_warning "跳过: $file"
        fi
    done < /tmp/project_files_list.txt
    
    # 设置执行权限
    print_info "🔧 设置执行权限..."
    chmod +x deploy.sh 2>/dev/null || true
    chmod +x scripts/docker-deploy.sh 2>/dev/null || true
    chmod +x scripts/quick-deploy.sh 2>/dev/null || true
    
    # 清理临时文件
    rm -f /tmp/project_files.json /tmp/project_files_list.txt
    
    print_success "✅ 项目代码更新完成 ($success_count/$total_count 文件)"
    return 0
}

# 使用预定义文件列表更新
update_with_static_list() {
    # 创建必要的目录结构
    mkdir -p config uploader browser cli scripts core data uploader/regions/hk/sneakers uploader/regions/hk/bags uploader/regions/hk/clothes uploader/regions/sg/sneakers uploader/regions/sg/bags uploader/regions/sg/clothes uploader/regions/my/sneakers uploader/regions/my/bags uploader/regions/my/clothes
    
    # 下载根目录文件
    print_info "📄 下载根目录文件..."
    download_file "https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/__init__.py" "__init__.py"
    download_file "https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/requirements.txt" "requirements.txt"
    download_file "https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/README.md" "README.md"
    download_file "https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/setup.py" "setup.py"
    download_file "https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/pyproject.toml" "pyproject.toml"
    download_file "https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/.gitignore" ".gitignore"
    download_file "https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/create_example_excel.py" "create_example_excel.py"
    download_file "https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/deploy.sh" "deploy.sh"
    chmod +x deploy.sh
    
    # 下载核心配置文件
    print_info "📋 下载配置文件..."
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/config/settings.yaml -o config/settings.yaml
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/config/settings.example.yaml -o config/settings.example.yaml
    
    # 下载核心Python模块
    print_info "🐍 下载核心Python模块..."
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/core/__init__.py -o core/__init__.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/core/config.py -o core/config.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/core/logger.py -o core/logger.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/core/models.py -o core/models.py
    
    # 下载浏览器模块
    print_info "🌐 下载浏览器模块..."
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/browser/__init__.py -o browser/__init__.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/browser/browser.py -o browser/browser.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/browser/browser_interface.py -o browser/browser_interface.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/browser/browser_factory.py -o browser/browser_factory.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/browser/browser_selector.py -o browser/browser_selector.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/browser/actions.py -o browser/actions.py
    
    # 下载上传器模块
    print_info "📤 下载上传器模块..."
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/__init__.py -o uploader/__init__.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/base_uploader.py -o uploader/base_uploader.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/carousell_uploader_new.py -o uploader/carousell_uploader_new.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/multi_account_uploader.py -o uploader/multi_account_uploader.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/uploader_factory.py -o uploader/uploader_factory.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/utils.py -o uploader/utils.py
    
    # 下载地域上传器 - 完整支持所有地域和类目
    print_info "🌍 下载地域上传器..."
    # 地域模块初始化文件
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/regions/__init__.py -o uploader/regions/__init__.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/regions/hk/__init__.py -o uploader/regions/hk/__init__.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/regions/sg/__init__.py -o uploader/regions/sg/__init__.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/regions/my/__init__.py -o uploader/regions/my/__init__.py
    
    # HK地域上传器
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/regions/hk/sneakers/__init__.py -o uploader/regions/hk/sneakers/__init__.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/regions/hk/sneakers/sneakers_uploader.py -o uploader/regions/hk/sneakers/sneakers_uploader.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/regions/hk/bags/__init__.py -o uploader/regions/hk/bags/__init__.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/regions/hk/bags/bags_uploader.py -o uploader/regions/hk/bags/bags_uploader.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/regions/hk/clothes/__init__.py -o uploader/regions/hk/clothes/__init__.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/regions/hk/clothes/clothes_uploader.py -o uploader/regions/hk/clothes/clothes_uploader.py
    
    # SG地域上传器
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/regions/sg/sneakers/__init__.py -o uploader/regions/sg/sneakers/__init__.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/regions/sg/sneakers/sneakers_uploader.py -o uploader/regions/sg/sneakers/sneakers_uploader.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/regions/sg/bags/__init__.py -o uploader/regions/sg/bags/__init__.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/regions/sg/bags/bags_uploader.py -o uploader/regions/sg/bags/bags_uploader.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/regions/sg/clothes/__init__.py -o uploader/regions/sg/clothes/__init__.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/regions/sg/clothes/clothes_uploader.py -o uploader/regions/sg/clothes/clothes_uploader.py
    
    # MY地域上传器
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/regions/my/sneakers/__init__.py -o uploader/regions/my/sneakers/__init__.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/regions/my/sneakers/sneakers_uploader.py -o uploader/regions/my/sneakers/sneakers_uploader.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/regions/my/bags/__init__.py -o uploader/regions/my/bags/__init__.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/regions/my/bags/bags_uploader.py -o uploader/regions/my/bags/bags_uploader.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/regions/my/clothes/__init__.py -o uploader/regions/my/clothes/__init__.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/uploader/regions/my/clothes/clothes_uploader.py -o uploader/regions/my/clothes/clothes_uploader.py
    
    # 下载CLI模块
    print_info "💻 下载CLI模块..."
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/cli/__init__.py -o cli/__init__.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/cli/main.py -o cli/main.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/cli/cli.py -o cli/cli.py
    
    # 下载数据模块
    print_info "📊 下载数据模块..."
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/data/__init__.py -o data/__init__.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/data/excel_parser.py -o data/excel_parser.py
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/data/record_manager.py -o data/record_manager.py
    
    # 下载脚本文件
    print_info "🚀 下载脚本文件..."
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/scripts/docker-deploy.sh -o scripts/docker-deploy.sh
    curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/scripts/quick-deploy.sh -o scripts/quick-deploy.sh
    chmod +x scripts/docker-deploy.sh scripts/quick-deploy.sh
    
    print_success "✅ 项目代码更新完成"
    return 0
}

download_project_files() {
    print_info "尝试下载项目文件..."
    
    # 检查curl是否可用
    if command -v curl &> /dev/null; then
        print_info "使用curl下载项目文件..."
        
        # 调用完整的update_project_code函数
        update_project_code
        
        print_success "项目文件下载完成"
        return 0
    else
        print_error "curl不可用，无法下载项目文件"
        print_info "请手动克隆项目: git clone https://github.com/maxliu9403/carousell_upload.git"
        return 1
    fi
}

# 创建项目目录
create_project_dir() {
    print_info "创建项目目录..."
    
    # 使用当前目录作为项目目录
    PROJECT_DIR="$(pwd)"
    
    print_info "项目目录: $PROJECT_DIR"
    
    # 检查当前目录是否包含项目文件
    if [ ! -f "requirements.txt" ] && [ ! -f "README.md" ]; then
        print_warning "当前目录不包含项目文件"
        print_info "正在自动下载项目文件..."
        
        # 使用新的更新函数
        if ! update_project_code; then
            print_error "无法下载项目文件"
            print_info "请手动克隆项目: git clone https://github.com/maxliu9403/carousell_upload.git"
            exit 1
        fi
    else
        print_success "检测到项目文件，正在更新到最新版本..."
        # 即使存在项目文件，也尝试更新到最新版本
        if ! update_project_code; then
            print_warning "代码更新失败，使用现有文件继续安装"
        fi
    fi
    
    print_success "使用当前目录作为项目目录: $PROJECT_DIR"
}

# 安装系统依赖
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
        
        # 详细日志：显示创建过程
        print_info "执行命令: $PYTHON_CMD -m venv venv"
        
        # 捕获详细输出
        VENV_OUTPUT=$("$PYTHON_CMD" -m venv venv 2>&1)
        VENV_EXIT_CODE=$?
        
        if [ $VENV_EXIT_CODE -eq 0 ]; then
            print_success "虚拟环境创建完成: $PROJECT_DIR/venv"
        else
            print_error "虚拟环境创建失败 (退出码: $VENV_EXIT_CODE)"
            print_error "错误输出: $VENV_OUTPUT"
            
            # 提供详细的故障排除信息
            print_info "故障排除建议:"
            print_info "1. 检查Python版本: $PYTHON_CMD --version"
            print_info "2. 检查Python模块: $PYTHON_CMD -m venv --help"
            print_info "3. 检查磁盘空间: df -h ."
            print_info "4. 检查权限: ls -la ."
            print_info "5. 尝试手动创建: $PYTHON_CMD -m venv test_venv"
            
            # 检查常见问题
            if echo "$VENV_OUTPUT" | grep -q "No module named venv"; then
                print_error "Python venv模块不可用"
                print_info "解决方案:"
                print_info "  Ubuntu/Debian: sudo apt install python3-venv"
                print_info "  CentOS/RHEL: sudo yum install python3-venv"
                print_info "  macOS: brew install python3"
            elif echo "$VENV_OUTPUT" | grep -q "Permission denied"; then
                print_error "权限不足"
                print_info "解决方案: 检查当前目录权限或使用sudo"
            elif echo "$VENV_OUTPUT" | grep -q "No space left"; then
                print_error "磁盘空间不足"
                print_info "解决方案: 清理磁盘空间或更换目录"
            fi
            
            exit 1
        fi
    else
        print_warning "虚拟环境已存在: $PROJECT_DIR/venv"
    fi
    
    # 验证虚拟环境
    print_info "检查虚拟环境激活脚本..."
    print_info "检查 venv/bin/activate: $([ -f "venv/bin/activate" ] && echo "存在" || echo "不存在")"
    print_info "检查 venv/Scripts/activate: $([ -f "venv/Scripts/activate" ] && echo "存在" || echo "不存在")"
    
    if [ -f "venv/bin/activate" ] || [ -f "venv/Scripts/activate" ]; then
        print_success "虚拟环境验证通过"
    else
        print_error "虚拟环境创建失败 - 激活脚本不存在"
        print_info "检查虚拟环境结构:"
        ls -la venv/ 2>/dev/null || print_info "venv目录不存在"
        
        # 检查不同操作系统的激活脚本位置
        if [ -d "venv/bin" ]; then
            print_info "Linux/macOS结构: venv/bin/"
            ls -la venv/bin/ 2>/dev/null || print_info "venv/bin目录不存在"
        elif [ -d "venv/Scripts" ]; then
            print_info "Windows结构: venv/Scripts/"
            ls -la venv/Scripts/ 2>/dev/null || print_info "venv/Scripts目录不存在"
        else
            print_info "未找到标准的虚拟环境结构"
        fi
        exit 1
    fi
}

# 安装Python依赖
install_python_deps() {
    print_info "安装Python依赖..."
    
    cd "$PROJECT_DIR"
    
    # 激活虚拟环境
    print_info "激活虚拟环境..."
    
    # 根据操作系统选择激活脚本
    if [ -f "venv/bin/activate" ]; then
        # Linux/macOS
        source venv/bin/activate
        print_info "使用Linux/macOS激活脚本: venv/bin/activate"
    elif [ -f "venv/Scripts/activate" ]; then
        # Windows
        source venv/Scripts/activate
        print_info "使用Windows激活脚本: venv/Scripts/activate"
    else
        print_error "未找到虚拟环境激活脚本"
        print_info "检查激活脚本位置:"
        ls -la venv/bin/activate 2>/dev/null || print_info "venv/bin/activate不存在"
        ls -la venv/Scripts/activate 2>/dev/null || print_info "venv/Scripts/activate不存在"
        exit 1
    fi
    
    # 验证虚拟环境激活
    if [ "$VIRTUAL_ENV" = "$PROJECT_DIR/venv" ]; then
        print_success "虚拟环境已激活: $VIRTUAL_ENV"
    else
        print_error "虚拟环境激活失败"
        print_info "当前VIRTUAL_ENV: $VIRTUAL_ENV"
        print_info "期望VIRTUAL_ENV: $PROJECT_DIR/venv"
        print_info "请检查虚拟环境是否正确创建"
        exit 1
    fi
    
    # 验证Python路径
    print_info "验证Python路径..."
    PYTHON_PATH=$(which python)
    print_info "当前Python路径: $PYTHON_PATH"
    
    if [[ "$PYTHON_PATH" == *"$PROJECT_DIR/venv"* ]]; then
        print_success "Python路径正确，使用虚拟环境中的Python"
    else
        print_warning "Python路径可能不正确，但继续执行"
        print_info "期望路径包含: $PROJECT_DIR/venv"
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
    python -m playwright install chromium
    print_success "Playwright浏览器安装完成"
    
    # 验证安装
    print_info "验证Python包安装..."
    python -c "
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

# 配置运行环境
configure_service() {
    print_info "配置运行环境..."
    print_success "使用本地运行方式"
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
    
    # 根据操作系统选择激活脚本
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    else
        print_error "未找到虚拟环境激活脚本"
        exit 1
    fi
    
    # 测试Python导入
    python -c "
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

# 根据操作系统选择激活脚本
if [ -f "$VENV_DIR/bin/activate" ]; then
    echo "🚀 激活虚拟环境 (Linux/macOS)..."
    source "$VENV_DIR/bin/activate"
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
    echo "🚀 激活虚拟环境 (Windows)..."
    source "$VENV_DIR/Scripts/activate"
else
    echo "❌ 虚拟环境未找到: $VENV_DIR"
    echo "请先运行安装脚本: ./install.sh"
    exit 1
fi

echo "✅ 虚拟环境已激活: $VIRTUAL_ENV"
echo "📁 项目目录: $PROJECT_DIR"
echo ""
echo "💡 使用说明:"
echo "  - 运行程序: python -m cli.main"
echo "  - 退出环境: deactivate"
echo "  - 查看帮助: python -m cli.main --help"
EOF
    
    chmod +x activate_env.sh
    print_success "虚拟环境激活脚本创建完成: activate_env.sh"
    
    # 创建快速启动脚本
    cat > run.sh << 'EOF'
#!/bin/bash
# Carousell Uploader 快速启动脚本

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

# 根据操作系统选择激活脚本
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
    echo "🚀 启动 Carousell Uploader (Linux/macOS)..."
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
    source "$VENV_DIR/Scripts/activate"
    echo "🚀 启动 Carousell Uploader (Windows)..."
else
    echo "❌ 虚拟环境未找到，请先运行安装脚本"
    exit 1
fi

python -m cli.main "$@"
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
    
    # 根据操作系统显示正确的激活路径
    if [ -f "$PROJECT_DIR/venv/Scripts/activate" ]; then
        # Windows系统
        echo "1. 激活虚拟环境: cd $PROJECT_DIR && venv\\Scripts\\activate"
        echo "2. 或使用激活脚本: cd $PROJECT_DIR && ./activate_env.sh"
        echo "3. 或直接运行: cd $PROJECT_DIR && ./run.sh"
        echo ""
        print_info "⚙️ 配置设置:"
        echo "1. 编辑配置文件: notepad $PROJECT_DIR\\config\\settings.yaml"
        echo "2. 设置API密钥和其他配置"
        echo ""
        print_info "🔧 运行方式:"
        echo "1. 直接运行: python -m cli.main"
        echo "2. 使用启动脚本: ./run.sh"
        echo "3. 激活环境后运行: venv\\Scripts\\activate && python -m cli.main"
    else
        # Linux/macOS系统
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
    fi
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
    
    # 环境检查阶段
    print_info "🔍 环境检查阶段"
    check_system
    check_python
    check_pip
    
    # 项目设置阶段
    print_info "📁 项目设置阶段"
    create_project_dir
    install_dependencies
    
    # Python环境阶段
    print_info "🐍 Python环境阶段"
    create_virtual_env
    install_python_deps
    
    # 配置完成阶段
    print_info "⚙️ 配置完成阶段"
    create_venv_scripts
    configure_service
    create_config
    create_directories
    test_installation
    
    # 完成安装
    show_usage
}

# 运行主函数
main "$@"
