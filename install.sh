#!/bin/bash
# =============================================================================
# Carousell Uploader - 跨平台一键安装脚本
# =============================================================================
# 支持系统: Windows (Git Bash/WSL), macOS, Linux
# 版本: 2.0.0
# 作者: Carousell Uploader Team
# =============================================================================

set -e

# =============================================================================
# 全局配置
# =============================================================================
SCRIPT_VERSION="2.0.0"
PROJECT_NAME="Carousell Uploader"
REPO_URL="https://github.com/maxliu9403/carousell_upload"
PYTHON_MIN_VERSION="3.8"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# 操作系统检测
OS=""
ARCH=""
PYTHON_CMD=""
PIP_CMD=""

# =============================================================================
# 工具函数
# =============================================================================

# 打印函数
print_header() {
    echo -e "${WHITE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${WHITE}║${NC} ${CYAN}🚀 $PROJECT_NAME 一键安装脚本 v$SCRIPT_VERSION${NC} ${WHITE}║${NC}"
    echo -e "${WHITE}║${NC} ${CYAN}支持系统: Windows, macOS, Linux${NC} ${WHITE}║${NC}"
    echo -e "${WHITE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

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

print_step() {
    echo -e "${PURPLE}🔧 $1${NC}"
}

print_progress() {
    echo -e "${CYAN}⏳ $1${NC}"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 获取系统信息
get_system_info() {
    print_step "检测系统环境..."
    
    # 检测操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_success "检测到Linux系统"
        
        # 检测Linux发行版
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            print_info "发行版: $NAME $VERSION"
        fi
        
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_success "检测到macOS系统"
        
        # 检测macOS版本
        if command_exists sw_vers; then
            MACOS_VERSION=$(sw_vers -productVersion)
            print_info "macOS版本: $MACOS_VERSION"
        fi
        
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
        OS="windows"
        print_success "检测到Windows系统"
        
        # 检测Windows版本
        if command_exists systeminfo; then
            WINDOWS_VERSION=$(systeminfo | grep "OS Name" | head -1 | cut -d: -f2 | xargs)
            print_info "Windows版本: $WINDOWS_VERSION"
        fi
        
    else
        print_error "不支持的操作系统: $OSTYPE"
        print_info "支持的系统: Linux, macOS, Windows (Git Bash/WSL)"
        exit 1
    fi
    
    # 检测架构
    ARCH=$(uname -m)
    print_info "系统架构: $ARCH"
}

# 检查网络连接
check_network() {
    print_step "检查网络连接..."
    
    local test_urls=(
        "https://pypi.org"
        "https://github.com"
        "https://raw.githubusercontent.com"
    )
    
    for url in "${test_urls[@]}"; do
        if curl -fsSL --connect-timeout 10 "$url" >/dev/null 2>&1; then
            print_success "网络连接正常: $url"
            return 0
        fi
    done
    
    print_error "网络连接失败，请检查网络设置"
    print_info "请确保可以访问以下网站:"
    for url in "${test_urls[@]}"; do
        print_info "  - $url"
    done
    exit 1
}

# 检查并安装系统依赖
install_system_dependencies() {
    print_step "安装系统依赖..."
    
    case "$OS" in
        "linux")
            install_linux_dependencies
            ;;
        "macos")
            install_macos_dependencies
            ;;
        "windows")
            install_windows_dependencies
            ;;
    esac
}

# Linux系统依赖安装
install_linux_dependencies() {
    print_info "安装Linux系统依赖..."
    
    # 检测包管理器
    if command_exists apt; then
        print_info "使用apt包管理器 (Ubuntu/Debian)"
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential curl wget git
    elif command_exists yum; then
        print_info "使用yum包管理器 (CentOS/RHEL)"
        sudo yum install -y python3 python3-pip python3-venv python3-devel gcc curl wget git
    elif command_exists dnf; then
        print_info "使用dnf包管理器 (Fedora)"
        sudo dnf install -y python3 python3-pip python3-venv python3-devel gcc curl wget git
    elif command_exists pacman; then
        print_info "使用pacman包管理器 (Arch Linux)"
        sudo pacman -S --noconfirm python python-pip python-virtualenv base-devel curl wget git
    elif command_exists zypper; then
        print_info "使用zypper包管理器 (openSUSE)"
        sudo zypper install -y python3 python3-pip python3-venv python3-devel gcc curl wget git
    else
        print_warning "未检测到支持的包管理器，请手动安装Python 3.8+"
        print_info "安装指南:"
        print_info "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
        print_info "  CentOS/RHEL: sudo yum install python3 python3-pip"
        print_info "  Arch Linux: sudo pacman -S python python-pip"
    fi
}

# macOS系统依赖安装
install_macos_dependencies() {
    print_info "安装macOS系统依赖..."
    
    # 检查Homebrew
    if ! command_exists brew; then
        print_info "安装Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # 添加Homebrew到PATH
        if [[ -f "/opt/homebrew/bin/brew" ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
            eval "$(/opt/homebrew/bin/brew shellenv)"
        elif [[ -f "/usr/local/bin/brew" ]]; then
            echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zshrc
            eval "$(/usr/local/bin/brew shellenv)"
        fi
    else
        print_success "Homebrew已安装"
    fi
    
    # 安装Python
    if ! command_exists python3; then
        print_info "安装Python..."
        brew install python3
    else
        print_success "Python已安装"
    fi
}

# Windows系统依赖安装
install_windows_dependencies() {
    print_info "检查Windows系统依赖..."
    
    # 检查是否在WSL中
    if grep -q Microsoft /proc/version 2>/dev/null; then
        print_info "检测到WSL环境，使用Linux安装方式"
        install_linux_dependencies
        return
    fi
    
    # 检查Git Bash
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        print_info "检测到Git Bash环境"
        
        # 检查Python
        if ! command_exists python && ! command_exists python3; then
            print_error "未找到Python，请先安装Python 3.8+"
            print_info "安装指南:"
            print_info "  1. 访问 https://python.org"
            print_info "  2. 下载Python 3.8+"
            print_info "  3. 安装时勾选 'Add Python to PATH'"
            print_info "  4. 避免使用Microsoft Store版本"
            exit 1
        fi
    else
        print_warning "建议使用Git Bash或WSL运行此脚本"
        print_info "下载Git Bash: https://git-scm.com/download/win"
    fi
}

# 检测Python环境
detect_python() {
    print_step "检测Python环境..."
    
    local python_commands=("python3" "python" "py")
    local found_python=""
    
    for cmd in "${python_commands[@]}"; do
        if command_exists "$cmd"; then
            # 检查版本
            local version_output
            if version_output=$("$cmd" --version 2>&1); then
                # 检查是否指向Microsoft Store
                if echo "$version_output" | grep -q "Microsoft Store"; then
                    print_warning "跳过Microsoft Store Python: $cmd"
                    continue
                fi
                
                # 检查版本是否符合要求
                if "$cmd" -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
                    PYTHON_CMD="$cmd"
                    local version=$("$cmd" --version 2>&1 | cut -d' ' -f2)
                    print_success "找到Python: $cmd (版本: $version)"
                    break
                else
                    print_warning "Python版本过低: $cmd ($version_output)"
                fi
            fi
        fi
    done
    
    if [ -z "$PYTHON_CMD" ]; then
        print_error "未找到合适的Python安装 (需要>=3.8)"
        print_info "安装指南:"
        case "$OS" in
            "linux")
                print_info "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
                print_info "  CentOS/RHEL: sudo yum install python3 python3-pip"
                ;;
            "macos")
                print_info "  macOS: brew install python3"
                ;;
            "windows")
                print_info "  Windows: 从 https://python.org 下载安装"
                ;;
        esac
        exit 1
    fi
    
    # 检测pip
    if "$PYTHON_CMD" -m pip --version >/dev/null 2>&1; then
        PIP_CMD="$PYTHON_CMD -m pip"
        print_success "pip可用: $PIP_CMD"
    else
        print_error "pip不可用，请重新安装Python"
        exit 1
    fi
}

# 创建项目目录
setup_project_directory() {
    print_step "设置项目目录..."
    
    PROJECT_DIR="$(pwd)"
    print_info "项目目录: $PROJECT_DIR"
    
    # 检查是否已有项目文件
    if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
        print_success "检测到项目文件，检查是否需要更新"
        update_project_code
    else
        print_info "当前目录不包含项目文件，将下载项目代码"
        download_project_code
    fi
}

# 下载项目代码
download_project_code() {
    print_step "下载项目代码..."
    
    # 检查Git
    if command_exists git; then
        print_info "使用Git克隆项目..."
        if git clone "$REPO_URL.git" temp_project; then
            # 移动文件到当前目录
            cp -r temp_project/* .
            cp -r temp_project/.* . 2>/dev/null || true
            rm -rf temp_project
            print_success "项目代码下载完成"
        else
            print_warning "Git克隆失败，尝试其他方式"
            download_with_curl
        fi
    else
        print_warning "Git不可用，使用curl下载"
        download_with_curl
    fi
}

# 使用curl下载项目代码
download_with_curl() {
    print_info "使用curl下载项目代码..."
    
    # 创建临时目录
    mkdir -p temp_project
    cd temp_project
    
    # 下载主要文件
    local files=(
        "requirements.txt"
        "pyproject.toml"
        "setup.py"
        "README.md"
        "cli/main.py"
        "cli/__init__.py"
        "core/config.py"
        "core/logger.py"
        "core/models.py"
        "core/__init__.py"
        "browser/__init__.py"
        "browser/actions.py"
        "browser/browser.py"
        "browser/browser_interface.py"
        "browser/browser_factory.py"
        "browser/bit_browser_interface.py"
        "browser/ix_browser_interface.py"
        "browser/browser_selector.py"
        "uploader/__init__.py"
        "uploader/core/__init__.py"
        "uploader/core/base_uploader.py"
        "uploader/core/carousell_uploader.py"
        "uploader/multi/__init__.py"
        "uploader/multi/multi_account_uploader.py"
        "uploader/regions/__init__.py"
        "uploader/regions/hk/__init__.py"
        "uploader/regions/hk/sneakers/__init__.py"
        "uploader/regions/hk/sneakers/sneakers_uploader.py"
        "uploader/regions/hk/sneakers/css_selectors.yaml"
        "uploader/regions/sg/__init__.py"
        "uploader/regions/sg/sneakers/__init__.py"
        "uploader/regions/sg/sneakers/sneakers_uploader.py"
        "uploader/regions/sg/sneakers/css_selectors.yaml"
        "uploader/regions/my/__init__.py"
        "uploader/regions/my/sneakers/__init__.py"
        "uploader/regions/my/sneakers/sneakers_uploader.py"
        "uploader/regions/my/sneakers/css_selectors.yaml"
        "data/__init__.py"
        "data/excel_parser.py"
        "config/settings.example.yaml"
        "scripts/windows-install.bat"
        "scripts/windows-install.ps1"
        "scripts/windows-simple-install.bat"
        "scripts/windows-python-fix.sh"
        "scripts/quick-deploy.sh"
        "scripts/docker-deploy.sh"
        "deploy.sh"
        "run.sh"
        "activate_env.sh"
        ".gitignore"
    )
    
    local success_count=0
    local total_count=${#files[@]}
    
    for file in "${files[@]}"; do
        local url="$REPO_URL/raw/main/$file"
        local dir=$(dirname "$file")
        
        if [ "$dir" != "." ]; then
            mkdir -p "$dir"
        fi
        
        if curl -fsSL "$url" -o "$file" 2>/dev/null; then
            print_info "下载: $file"
            success_count=$((success_count + 1))
        else
            print_warning "下载失败: $file"
        fi
    done
    
    # 移动文件到上级目录
    cp -r * ../ 2>/dev/null || true
    cp -r .* ../ 2>/dev/null || true
    cd ..
    rm -rf temp_project
    
    print_success "项目代码下载完成 ($success_count/$total_count 文件)"
}

# 备份CSS选择器文件
backup_css_selectors() {
    local backup_dir="$1"
    print_info "备份CSS选择器文件..."
    
    # 定义地域和类目组合
    local regions=("hk" "sg" "my")
    local categories=("sneakers" "bags" "clothes")
    
    local backup_count=0
    
    # 遍历所有地域和类目组合
    for region in "${regions[@]}"; do
        for category in "${categories[@]}"; do
            local css_file="uploader/regions/$region/$category/css_selectors.yaml"
            
            # 检查文件是否存在
            if [ -f "$css_file" ]; then
                # 创建备份目录结构
                local backup_path="$backup_dir/uploader/regions/$region/$category"
                mkdir -p "$backup_path"
                
                # 备份文件
                if cp "$css_file" "$backup_path/css_selectors.yaml"; then
                    print_info "备份: $css_file"
                    backup_count=$((backup_count + 1))
                else
                    print_warning "备份失败: $css_file"
                fi
            fi
        done
    done
    
    # 创建备份说明文件
    cat > "$backup_dir/README.md" << EOF
# CSS选择器备份

## 备份信息
- 备份文件数量: $backup_count
- 备份目录: $backup_dir
- 注意: 此备份目录会在每次更新时被覆盖

## 文件结构
\`\`\`
$backup_dir/
├── uploader/
│   └── regions/
│       ├── hk/
│       │   ├── sneakers/
│       │   │   └── css_selectors.yaml
│       │   ├── bags/
│       │   │   └── css_selectors.yaml
│       │   └── clothes/
│       │       └── css_selectors.yaml
│       ├── sg/
│       │   ├── sneakers/
│       │   │   └── css_selectors.yaml
│       │   ├── bags/
│       │   │   └── css_selectors.yaml
│       │   └── clothes/
│       │       └── css_selectors.yaml
│       └── my/
│           ├── sneakers/
│           │   └── css_selectors.yaml
│           ├── bags/
│           │   └── css_selectors.yaml
│           └── clothes/
│               └── css_selectors.yaml
└── README.md
\`\`\`

## 恢复方法
如需恢复某个文件，请将对应的 \`css_selectors.yaml\` 文件复制回原位置。

例如恢复香港运动鞋的CSS选择器：
\`\`\`bash
cp $backup_dir/uploader/regions/hk/sneakers/css_selectors.yaml uploader/regions/hk/sneakers/css_selectors.yaml
\`\`\`

## 注意事项
- 此备份目录会在每次执行 \`./install.sh\` 时被覆盖
- 如需长期保存，请手动复制到其他位置
- 备份只包含CSS选择器文件，不包含其他项目文件
EOF
    
    print_success "CSS选择器备份完成 ($backup_count 个文件)"
}

# 更新项目代码
update_project_code() {
    print_step "更新项目代码..."
    
    # 检查是否在Git仓库中
    if [ -d ".git" ]; then
        print_info "检测到Git仓库，尝试拉取最新代码..."
        
        # 检查远程仓库
        if git remote get-url origin >/dev/null 2>&1; then
            print_info "当前远程仓库: $(git remote get-url origin)"
            
            # 检查是否有未提交的更改
            if ! git diff --quiet || ! git diff --cached --quiet; then
                print_warning "检测到未提交的更改，将备份CSS选择器文件"
                
                # 使用固定的备份目录名称
                local backup_dir="backup_css_selectors"
                
                # 如果备份目录已存在，先删除
                if [ -d "$backup_dir" ]; then
                    print_info "删除旧备份目录: $backup_dir"
                    rm -rf "$backup_dir"
                fi
                
                # 创建新的备份目录
                mkdir -p "$backup_dir"
                
                # 备份CSS选择器文件
                backup_css_selectors "$backup_dir"
                
                print_info "CSS选择器备份已创建: $backup_dir"
            fi
            
            # 拉取最新代码
            print_info "拉取最新代码..."
            if git pull origin main; then
                print_success "代码更新成功"
                
                # 检查是否有冲突
                if git status --porcelain | grep -q "^UU"; then
                    print_warning "检测到合并冲突，请手动解决"
                    print_info "冲突文件:"
                    git status --porcelain | grep "^UU" | cut -c4-
                fi
                
                return 0
            else
                print_warning "Git拉取失败，尝试重新下载"
                download_project_code
            fi
        else
            print_warning "未配置远程仓库，重新下载代码"
            download_project_code
        fi
    else
        print_info "未检测到Git仓库，重新下载代码"
        download_project_code
    fi
}

# 创建虚拟环境
create_virtual_environment() {
    print_step "创建Python虚拟环境..."
    
    # 检查是否已存在虚拟环境
    if [ -d "venv" ]; then
        print_info "虚拟环境已存在，检查是否可以复用..."
        
        # 检查虚拟环境是否有效
        if [ -f "venv/bin/activate" ] || [ -f "venv/Scripts/activate" ]; then
            print_success "虚拟环境有效，将复用现有环境"
            
            # 检查Python版本是否匹配
            if [ -f "venv/bin/python" ] || [ -f "venv/Scripts/python.exe" ]; then
                local venv_python=""
                if [ -f "venv/bin/python" ]; then
                    venv_python="venv/bin/python"
                elif [ -f "venv/Scripts/python.exe" ]; then
                    venv_python="venv/Scripts/python.exe"
                fi
                
                if [ -n "$venv_python" ]; then
                    local venv_version=$("$venv_python" --version 2>&1 | cut -d' ' -f2)
                    local current_version=$("$PYTHON_CMD" --version 2>&1 | cut -d' ' -f2)
                    
                    if [ "$venv_version" = "$current_version" ]; then
                        print_success "Python版本匹配，复用虚拟环境"
                        return 0
                    else
                        print_warning "Python版本不匹配 (虚拟环境: $venv_version, 当前: $current_version)"
                        print_info "将重新创建虚拟环境以确保兼容性"
                        rm -rf venv
                    fi
                else
                    print_warning "虚拟环境Python可执行文件不存在，将重新创建"
                    rm -rf venv
                fi
            else
                print_warning "虚拟环境Python可执行文件不存在，将重新创建"
                rm -rf venv
            fi
        else
            print_warning "虚拟环境无效，将重新创建"
            rm -rf venv
        fi
    fi
    
    print_info "创建虚拟环境..."
    if "$PYTHON_CMD" -m venv venv; then
        print_success "虚拟环境创建成功"
    else
        print_error "虚拟环境创建失败"
        print_info "故障排除:"
        print_info "  1. 检查Python版本: $PYTHON_CMD --version"
        print_info "  2. 检查磁盘空间: df -h ."
        print_info "  3. 检查权限: ls -la ."
        exit 1
    fi
    
    # 验证虚拟环境
    if [ -f "venv/bin/activate" ] || [ -f "venv/Scripts/activate" ]; then
        print_success "虚拟环境验证通过"
    else
        print_error "虚拟环境创建失败 - 激活脚本不存在"
        exit 1
    fi
}

# 激活虚拟环境
activate_virtual_environment() {
    print_step "激活虚拟环境..."
    
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_success "虚拟环境已激活 (Linux/macOS)"
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
        print_success "虚拟环境已激活 (Windows)"
    else
        print_error "虚拟环境激活失败"
        exit 1
    fi
    
    # 验证激活
    if [ "$VIRTUAL_ENV" = "$PROJECT_DIR/venv" ]; then
        print_success "虚拟环境激活成功: $VIRTUAL_ENV"
    else
        print_error "虚拟环境激活失败"
        exit 1
    fi
}

# 安装Python依赖
install_python_dependencies() {
    print_step "安装Python依赖..."
    
    # 升级pip
    print_info "升级pip..."
    pip install --upgrade pip
    
    # 安装基础包
    print_info "安装基础包..."
    pip install wheel setuptools
    
    # 安装项目依赖
    if [ -f "requirements.txt" ]; then
        print_info "安装项目依赖..."
        pip install -r requirements.txt
        print_success "项目依赖安装完成"
    else
        print_error "未找到requirements.txt文件"
        exit 1
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
    import openpyxl
    import pyautogui
    import pyperclip
    print('✅ 所有依赖包验证通过')
except ImportError as e:
    print(f'❌ 依赖包验证失败: {e}')
    sys.exit(1)
"
    
    print_success "Python环境配置完成"
}

# 创建配置文件
create_configuration() {
    print_step "创建配置文件..."
    
    # 创建必要目录
    mkdir -p logs data screenshots temp config
    
    # 创建配置文件
    if [ ! -f "config/settings.yaml" ]; then
        if [ -f "config/settings.example.yaml" ]; then
            cp config/settings.example.yaml config/settings.yaml
            print_success "配置文件创建完成: config/settings.yaml"
        else
            # 创建基本配置文件
            cat > config/settings.yaml << 'EOF'
# Carousell Uploader 配置文件
# 请根据您的需求修改以下配置

# 浏览器设置
browser:
  headless: false
  timeout: 30
  retry_count: 3

# 日志设置
logging:
  level: INFO
  file: logs/carousell.log

# 上传设置
upload:
  delay_between_actions: 2
  max_retries: 3
  screenshot_on_error: true
EOF
            print_success "基本配置文件创建完成: config/settings.yaml"
        fi
    else
        print_warning "配置文件已存在: config/settings.yaml"
    fi
}

# 创建启动脚本
create_startup_scripts() {
    print_step "创建启动脚本..."
    
    # 创建激活脚本
    cat > activate_env.sh << 'EOF'
#!/bin/bash
# Carousell Uploader 虚拟环境激活脚本

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

echo "🚀 激活 Carousell Uploader 虚拟环境..."

# 根据操作系统选择激活脚本
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
    echo "✅ 虚拟环境已激活 (Linux/macOS)"
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
    source "$VENV_DIR/Scripts/activate"
    echo "✅ 虚拟环境已激活 (Windows)"
else
    echo "❌ 虚拟环境未找到: $VENV_DIR"
    echo "请先运行安装脚本: ./install.sh"
    exit 1
fi

echo "📁 项目目录: $PROJECT_DIR"
echo "🐍 Python路径: $(which python)"
echo ""
echo "💡 使用说明:"
echo "  - 运行程序: python -m cli.main"
echo "  - 退出环境: deactivate"
echo "  - 查看帮助: python -m cli.main --help"
EOF
    
    chmod +x activate_env.sh
    print_success "激活脚本创建完成: activate_env.sh"
    
    # 创建快速启动脚本
    cat > run.sh << 'EOF'
#!/bin/bash
# Carousell Uploader 快速启动脚本

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

# 激活虚拟环境
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
    source "$VENV_DIR/Scripts/activate"
else
    echo "❌ 虚拟环境未找到，请先运行安装脚本"
    exit 1
fi

echo "🚀 启动 Carousell Uploader..."
python -m cli.main "$@"
EOF
    
    chmod +x run.sh
    print_success "启动脚本创建完成: run.sh"
}

# 测试安装
test_installation() {
    print_step "测试安装..."
    
    # 测试Python导入
    python -c "
import sys
print('Python版本:', sys.version)
print('Python路径:', sys.executable)

try:
    import playwright
    print('✅ Playwright导入成功')
except ImportError as e:
    print(f'❌ Playwright导入失败: {e}')
    sys.exit(1)

try:
    import requests
    print('✅ Requests导入成功')
except ImportError as e:
    print(f'❌ Requests导入失败: {e}')
    sys.exit(1)

try:
    import yaml
    print('✅ PyYAML导入成功')
except ImportError as e:
    print(f'❌ PyYAML导入失败: {e}')
    sys.exit(1)

try:
    import pandas
    print('✅ Pandas导入成功')
except ImportError as e:
    print(f'❌ Pandas导入失败: {e}')
    sys.exit(1)

print('✅ 所有测试通过')
"
    
    print_success "安装测试通过"
}

# 显示使用说明
show_usage() {
    echo ""
    print_success "🎉 安装完成！"
    echo ""
    print_info "📁 项目目录: $PROJECT_DIR"
    print_info "🐍 虚拟环境: $PROJECT_DIR/venv"
    print_info "⚙️  配置文件: $PROJECT_DIR/config/settings.yaml"
    echo ""
    
    print_info "🚀 快速使用:"
    echo ""
    
    case "$OS" in
        "windows")
            echo "1. 激活虚拟环境:"
            echo "   cd $PROJECT_DIR"
            echo "   ./activate_env.sh"
            echo ""
            echo "2. 或直接运行:"
            echo "   cd $PROJECT_DIR"
            echo "   ./run.sh"
            echo ""
            echo "3. 配置设置:"
            echo "   notepad $PROJECT_DIR\\config\\settings.yaml"
            ;;
        *)
            echo "1. 激活虚拟环境:"
            echo "   cd $PROJECT_DIR"
            echo "   source ./activate_env.sh"
            echo ""
            echo "2. 或直接运行:"
            echo "   cd $PROJECT_DIR"
            echo "   ./run.sh"
            echo ""
            echo "3. 配置设置:"
            echo "   nano $PROJECT_DIR/config/settings.yaml"
            ;;
    esac
    
    echo ""
    print_info "📁 CSS选择器备份功能:"
    echo "- 自动备份: 运行 ./install.sh 时自动检测并备份CSS选择器文件"
    echo "- 备份位置: backup_css_selectors/ 目录"
    echo "- 覆盖机制: 每次执行都会覆盖上次备份，节省磁盘空间"
    echo "- 恢复CSS选择器方法:"
    echo "  恢复单个文件"
    echo "  cp backup_css_selectors/uploader/regions/hk/sneakers/css_selectors.yaml \\"
    echo "      uploader/regions/hk/sneakers/css_selectors.yaml"
    echo ""
    echo "  恢复所有文件"
    echo "  cp -r backup_css_selectors/uploader/regions/* uploader/regions/"
    echo ""
    echo "  恢复特定地域"
    echo "  cp -r backup_css_selectors/uploader/regions/hk/* uploader/regions/hk/"
    echo ""
    echo "- 长期保存: 如需长期保存，请手动复制到其他位置"
    echo ""
    
    print_info "📚 更多信息:"
    echo "- 项目文档: README.md"
    echo "- 配置说明: config/settings.example.yaml"
    echo "- 问题反馈: $REPO_URL/issues"
    echo ""
    print_success "安装完成！开始使用 Carousell Uploader 吧！"
}

# 主函数
main() {
    print_header
    
    # 环境检查
    get_system_info
    check_network
    install_system_dependencies
    detect_python
    
    # 项目设置
    setup_project_directory
    create_virtual_environment
    activate_virtual_environment
    install_python_dependencies
    
    # 配置完成
    create_configuration
    create_startup_scripts
    test_installation
    
    # 显示使用说明
    show_usage
}

# 错误处理
trap 'print_error "安装过程中发生错误，请检查上述输出信息"; exit 1' ERR

# 运行主函数
main "$@"