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

# 检查并获取有效的GitHub Token
check_and_get_github_token() {
    print_info "🔑 强制检查GitHub Token配置..."
    
    local github_token=""
    local token_file="$HOME/.github_token"
    
    # 检查本地Token文件是否存在
    if [ -f "$token_file" ]; then
        print_info "发现本地Token文件: $token_file"
        print_info "文件权限: $(ls -la "$token_file" 2>/dev/null || echo "无法获取权限信息")"
        
        # Windows兼容的Token读取，处理编码问题
        if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
            # Windows环境下的特殊处理 - 强制使用UTF-8编码
            github_token=$(cat "$token_file" 2>/dev/null | iconv -f UTF-8 -t UTF-8 2>/dev/null | tr -d '\n\r\0' | sed 's/[[:space:]]*$//' | sed 's/^[[:space:]]*//')
        else
            # 标准处理
            github_token=$(cat "$token_file" 2>/dev/null | tr -d '\n\r' | sed 's/[[:space:]]*$//')
        fi
        
        if [ -n "$github_token" ]; then
            # 清理Token，移除可能的BOM和特殊字符
            github_token=$(echo "$github_token" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | tr -d '\0')
            
            print_info "从文件读取GitHub Token (长度: ${#github_token})"
            print_info "Token前缀: ${github_token:0:10}..."
            
            # 验证Token格式
            if [[ ! "$github_token" =~ ^ghp_[A-Za-z0-9]{36}$ ]]; then
                print_warning "Token格式不正确，可能是编码问题"
                print_info "实际Token: $github_token"
                print_info "Token长度: ${#github_token}"
                print_info "Token十六进制: $(echo "$github_token" | hexdump -C | head -2)"
                print_info "需要重新输入Token"
                github_token=""
            fi
            
            # 强制验证Token是否有效
            print_info "开始验证Token有效性..."
            if validate_github_token "$github_token"; then
                print_success "✅ GitHub Token验证成功"
                echo "$github_token"
                return 0
            else
                print_error "❌ GitHub Token验证失败"
                print_info "需要重新配置Token"
                # 不要继续，直接退出让用户重新配置
                return 1
            fi
        else
            print_error "❌ Token文件为空或无法读取"
        fi
    else
        print_error "❌ 未找到本地Token文件: $token_file"
    fi
    
    # 提示用户输入新的Token
    print_info "🔑 请输入您的GitHub Token"
    print_info "获取Token步骤:"
    print_info "  1. 访问: https://github.com/settings/tokens"
    print_info "  2. 点击 'Generate new token (classic)'"
    print_info "  3. 选择 'public_repo' 权限"
    print_info "  4. 复制生成的Token"
    echo ""
    
    while true; do
        read -p "请输入GitHub Token: " github_token
        
        if [ -z "$github_token" ]; then
            print_error "Token不能为空，请重新输入"
            continue
        fi
        
        # 验证Token格式
        if [[ ! "$github_token" =~ ^ghp_[A-Za-z0-9]{36}$ ]]; then
            print_warning "Token格式可能不正确，标准格式: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            read -p "是否继续使用此Token? (y/n): " confirm
            if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
                continue
            fi
        fi
        
        # 验证Token有效性
        if validate_github_token "$github_token"; then
            print_success "✅ GitHub Token验证成功"
            
            # 保存Token到文件
            echo "$github_token" > "$token_file"
            chmod 600 "$token_file"
            print_success "Token已保存到: $token_file"
            
            echo "$github_token"
            return 0
        else
            print_error "❌ Token验证失败，请检查Token是否正确"
            read -p "是否重新输入Token? (y/n): " retry
            if [[ ! "$retry" =~ ^[Yy]$ ]]; then
                print_error "安装终止：需要有效的GitHub Token"
                exit 1
            fi
        fi
    done
}

# 验证GitHub Token有效性
validate_github_token() {
    local token="$1"
    
    if [ -z "$token" ]; then
        print_error "Token为空，无法验证"
        return 1
    fi
    
    print_info "🔍 开始验证GitHub Token有效性..."
    print_info "API端点: https://api.github.com/rate_limit"
    print_info "请求头: Authorization: token ${token:0:10}..."
    
    # 使用Token测试API访问 - 处理字符编码问题
    # Windows环境下的特殊处理
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        # 确保Token是纯ASCII
        local clean_token=$(echo "$token" | tr -d '\0' | sed 's/[^A-Za-z0-9_]//g')
        if [[ "$clean_token" =~ ^ghp_[A-Za-z0-9]{36}$ ]]; then
            local response=$(curl -s -H "Authorization: token $clean_token" -H "Accept: application/json" https://api.github.com/rate_limit 2>/dev/null)
        else
            print_error "Token清理后格式仍然不正确: $clean_token"
            return 1
        fi
    else
        local response=$(curl -s -H "Authorization: token $token" -H "Accept: application/json" https://api.github.com/rate_limit 2>/dev/null)
    fi
    local curl_exit_code=$?
    
    print_info "Curl退出码: $curl_exit_code"
    
    if [ $curl_exit_code -ne 0 ]; then
        print_error "❌ 网络请求失败，退出码: $curl_exit_code"
        return 1
    fi
    
    print_info "API响应长度: ${#response}"
    print_info "API响应内容: $response"
    
    # 检查响应是否为HTML（表示错误页面）
    if echo "$response" | grep -q '<html>'; then
        print_error "❌ API返回HTML错误页面，可能是网络或代理问题"
        print_info "响应内容: $response"
        return 1
    fi
    
    # 检查是否为有效的JSON响应
    if ! echo "$response" | grep -q '"limit"'; then
        print_error "❌ API响应格式异常，不是有效的JSON"
        print_info "响应内容: $response"
        return 1
    fi
    
    if echo "$response" | grep -q '"limit": 5000'; then
        print_success "✅ Token验证成功 - 认证用户权限 (5000次/小时)"
        return 0
    elif echo "$response" | grep -q '"message": "Bad credentials"'; then
        print_error "❌ Token无效或已过期"
        return 1
    elif echo "$response" | grep -q '"limit": 60'; then
        print_error "❌ Token可能无效，返回匿名用户权限 (60次/小时)"
        return 1
    else
        print_error "❌ 无法验证Token，网络或API错误"
        print_info "响应内容: $response"
        return 1
    fi
}

# 获取项目文件列表（仅使用Token方式）
get_project_files() {
    print_info "🔍 获取项目文件列表..."
    
    # 获取有效的GitHub Token
    local github_token
    if ! github_token=$(check_and_get_github_token); then
        print_error "❌ 无法获取有效的GitHub Token"
        exit 1
    fi
    
    print_info "获取到的Token长度: ${#github_token}"
    print_info "获取到的Token前缀: ${github_token:0:10}..."
    
    if [ -z "$github_token" ]; then
        print_error "❌ 无法获取有效的GitHub Token"
        exit 1
    fi
    
    # 从GitHub API获取文件列表
    local api_url="https://api.github.com/repos/maxliu9403/carousell_upload/contents"
    
    # Windows兼容的临时文件路径
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        local temp_file="/tmp/project_files.json"
    else
        # Windows Git Bash 或其他环境
        local temp_file="${TEMP:-/tmp}/project_files.json"
    fi
    
    print_info "使用GitHub Token获取文件列表..."
    print_info "Token前缀: ${github_token:0:10}..."
    print_info "API URL: $api_url"
    
    # 测试GitHub API连接
    print_info "测试GitHub API连接..."
    print_info "使用Token: ${github_token:0:10}..."
    print_info "测试URL: https://api.github.com/rate_limit"
    
    # Windows环境下的Token清理
    local clean_token="$github_token"
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        clean_token=$(echo "$github_token" | tr -d '\0' | sed 's/[^A-Za-z0-9_]//g')
        print_info "清理后的Token: ${clean_token:0:10}..."
    fi
    
    local test_response=$(curl -s -H "Authorization: token $clean_token" -H "Accept: application/json" https://api.github.com/rate_limit 2>/dev/null)
    local test_exit_code=$?
    
    print_info "测试请求退出码: $test_exit_code"
    print_info "测试响应长度: ${#test_response}"
    
    if [ $test_exit_code -ne 0 ]; then
        print_error "❌ 测试请求失败，退出码: $test_exit_code"
        return 1
    fi
    
    if echo "$test_response" | grep -q '"limit": 5000'; then
        print_success "✅ GitHub API连接正常"
    else
        print_warning "⚠️ GitHub API连接可能有问题"
        print_info "测试响应: $test_response"
        
        # 检查是否是HTML错误页面
        if echo "$test_response" | grep -q '<html>'; then
            print_error "❌ 收到HTML错误页面，可能是网络或代理问题"
        fi
    fi
    
    print_info "开始获取项目文件列表..."
    print_info "目标URL: $api_url"
    print_info "输出文件: $temp_file"
    
    local curl_exit_code=0
    # 使用清理后的Token进行主请求
    local main_token="$github_token"
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        main_token=$(echo "$github_token" | tr -d '\0' | sed 's/[^A-Za-z0-9_]//g')
        print_info "主请求使用清理后的Token: ${main_token:0:10}..."
    fi
    
    if curl -fsSL -H "Authorization: token $main_token" -H "Accept: application/json" -o "$temp_file" "$api_url" 2>/dev/null; then
        curl_exit_code=0
    else
        curl_exit_code=$?
    fi
    
    print_info "Curl退出码: $curl_exit_code"
    
    if [ $curl_exit_code -eq 0 ] && [ -f "$temp_file" ]; then
        print_info "GitHub API响应已保存到: $temp_file"
        # Windows兼容的文件大小检查
        if command -v wc >/dev/null 2>&1; then
            print_info "响应文件大小: $(wc -c < "$temp_file" 2>/dev/null || echo "0") 字节"
        else
            # Windows下使用PowerShell或Python检查文件大小
            local file_size=$(python -c "import os; print(os.path.getsize('$temp_file') if os.path.exists('$temp_file') else 0)" 2>/dev/null || echo "0")
            print_info "响应文件大小: $file_size 字节"
        fi
        
        # 使用Python解析GitHub API响应，获取文件哈希和修改时间
        # Windows兼容的Python命令
        local python_cmd="python3"
        if ! command -v python3 >/dev/null 2>&1; then
            if command -v python >/dev/null 2>&1; then
                python_cmd="python"
            else
                print_error "❌ 未找到Python命令"
                exit 1
            fi
        fi
        
        GITHUB_TOKEN="$github_token" $python_cmd -c "
import json
import sys
import subprocess
import hashlib
import os
from datetime import datetime

def get_files_from_api(data, prefix='', github_token=''):
    files = []
    for item in data:
        if item['type'] == 'file':
            # 包含文件哈希和修改时间信息
            file_info = {
                'path': prefix + item['name'],
                'sha': item.get('sha', ''),
                'size': item.get('size', 0),
                'download_url': item.get('download_url', ''),
                'last_modified': item.get('last_modified', '')
            }
            files.append(file_info)
        elif item['type'] == 'dir' and item['name'] not in ['.git', '__pycache__', '.venv', 'node_modules', 'logs', 'temp']:
            # 递归获取子目录文件
            try:
                auth_header = f'Authorization: token {github_token}'
                result = subprocess.run(['curl', '-fsSL', '-H', auth_header, item['url']], 
                                      capture_output=True, text=True, timeout=10, shell=False)
                if result.returncode == 0:
                    subdata = json.loads(result.stdout)
                    files.extend(get_files_from_api(subdata, prefix + item['name'] + '/', github_token))
                else:
                    print(f'Warning: Failed to fetch directory {item[\"name\"]}: {result.stderr}', file=sys.stderr)
            except Exception as e:
                print(f'Warning: Error processing directory {item[\"name\"]}: {e}', file=sys.stderr)
    return files

try:
    with open('$temp_file', 'r') as f:
        data = json.load(f)
    
    print(f'Processing {len(data)} root items...')
    github_token = os.environ.get('GITHUB_TOKEN', '')
    print(f'Using GitHub token: {github_token[:10]}...')
    files = get_files_from_api(data, '', github_token)
    print(f'Found {len(files)} files total')
    
    # 输出文件信息到临时文件 - Windows兼容
    import tempfile
    temp_dir = tempfile.gettempdir()
    with open(f'{temp_dir}/project_files_info.json', 'w') as f:
        json.dump(files, f, indent=2)
    
    # 输出文件路径列表
    for file_info in sorted(files, key=lambda x: x['path']):
        print(file_info['path'])
        
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    print(f'Temp file content preview:', file=sys.stderr)
    try:
        with open('$temp_file', 'r') as f:
            content = f.read()
            print(f'File size: {len(content)}', file=sys.stderr)
            print(f'First 200 chars: {content[:200]}', file=sys.stderr)
    except:
        print('Could not read temp file', file=sys.stderr)
    sys.exit(1)
" > "$temp_dir/project_files_list.txt" 2>/dev/null
        
        if [ -s "$temp_dir/project_files_list.txt" ]; then
            print_success "✅ 成功获取项目文件列表"
            if command -v wc >/dev/null 2>&1; then
                print_info "文件列表行数: $(wc -l < "$temp_dir/project_files_list.txt" 2>/dev/null || echo "0")"
            else
                print_info "文件列表已生成: $temp_dir/project_files_list.txt"
            fi
            return 0
        else
            print_error "❌ 文件列表为空"
            print_info "检查临时文件:"
            print_info "  - $temp_dir/project_files.json: $(ls -la "$temp_dir/project_files.json" 2>/dev/null || echo "不存在")"
            print_info "  - $temp_dir/project_files_list.txt: $(ls -la "$temp_dir/project_files_list.txt" 2>/dev/null || echo "不存在")"
            if [ -f "$temp_dir/project_files.json" ]; then
                print_info "API响应内容预览:"
                head -5 "$temp_dir/project_files.json" 2>/dev/null || echo "无法读取文件"
            fi
        fi
    else
        print_error "❌ GitHub API请求失败"
        print_info "Curl退出码: $curl_exit_code"
        print_info "检查网络连接和Token权限"
        print_info "API URL: $api_url"
        print_info "Token前缀: ${github_token:0:10}..."
        
        # 检查输出文件内容
        if [ -f "$temp_file" ]; then
            print_info "输出文件内容预览:"
            head -5 "$temp_file" 2>/dev/null || echo "无法读取文件"
        else
            print_info "输出文件不存在: $temp_file"
        fi
        
        # 尝试不带重定向的请求来获取详细错误信息
        print_info "尝试获取详细错误信息..."
        curl -v -H "Authorization: token $github_token" "$api_url" 2>&1 | head -20
    fi
    
    # API获取失败
    print_error "❌ 无法从GitHub API获取文件列表"
    print_error "请检查网络连接和Token权限"
    exit 1
}


# 更新项目代码到最新版本
update_project_code() {
    print_info "🔄 更新项目代码到最新版本..."
    
    # 直接执行更新，不检查版本
    print_info "开始更新项目代码..."
    
    # 检查是否已存在项目目录
    if [ -d ".git" ]; then
        print_info "检测到Git仓库，尝试拉取最新代码..."
        print_info "当前Git状态:"
        git status --porcelain
        print_info "尝试拉取最新代码..."
        if git pull origin main; then
            print_success "✅ 代码更新成功"
            return 0
        else
            print_warning "⚠️ Git拉取失败，尝试重新下载..."
            print_info "Git错误信息:"
            git pull origin main 2>&1 || true
        fi
    else
        print_info "未检测到Git仓库，使用curl下载..."
    fi
    
    # 如果Git更新失败或不存在，使用curl下载最新文件
    print_info "📥 下载最新项目文件..."
    
    # 检查curl是否可用
    if ! command -v curl &> /dev/null; then
        print_error "curl不可用，无法下载项目文件"
        return 1
    fi
    
    # 获取项目文件并更新
    if get_project_files; then
        print_info "📋 使用GitHub API获取文件列表..."
        update_with_dynamic_list
    else
        print_error "❌ 无法获取项目文件"
        exit 1
    fi
}

# 使用动态文件列表更新（智能增量更新）
update_with_dynamic_list() {
    print_info "🔄 执行智能增量更新..."
    
    # 检查是否有文件信息 - Windows兼容
    local temp_dir="/tmp"
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        temp_dir="/tmp"
    else
        temp_dir="${TEMP:-/tmp}"
    fi
    
    if [ ! -f "$temp_dir/project_files_info.json" ]; then
        print_error "文件信息不可用，回退到静态更新"
        update_with_static_list
        return $?
    fi
    
    # 使用Python进行智能增量更新 - Windows兼容
    local python_cmd="python3"
    if ! command -v python3 >/dev/null 2>&1; then
        if command -v python >/dev/null 2>&1; then
            python_cmd="python"
        else
            print_error "❌ 未找到Python命令"
            return 1
        fi
    fi
    
    $python_cmd -c "
import json
import os
import hashlib
import subprocess
import sys
from pathlib import Path

def calculate_file_hash(filepath):
    \"\"\"计算文件SHA256哈希\"\"\"
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except:
        return None

def download_file(url, filepath):
    \"\"\"下载文件\"\"\"
    try:
        result = subprocess.run(['curl', '-fsSL', url], 
                              capture_output=True, timeout=30)
        if result.returncode == 0:
            # 确保目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'wb') as f:
                f.write(result.stdout)
            return True
        return False
    except:
        return False

def main():
    # 读取远程文件信息 - Windows兼容
    import tempfile
    temp_dir = tempfile.gettempdir()
    with open(f'{temp_dir}/project_files_info.json', 'r') as f:
        remote_files = json.load(f)
    
    # 统计信息
    stats = {
        'new_files': 0,
        'updated_files': 0,
        'unchanged_files': 0,
        'deleted_files': 0,
        'failed_downloads': 0
    }
    
    # 获取本地文件列表
    local_files = set()
    for root, dirs, files in os.walk('.'):
        for file in files:
            if not any(skip in root for skip in ['.git', '__pycache__', '.venv', 'node_modules', 'logs', 'temp']):
                rel_path = os.path.relpath(os.path.join(root, file), '.')
                local_files.add(rel_path)
    
    # 处理远程文件
    for file_info in remote_files:
        filepath = file_info['path']
        remote_sha = file_info.get('sha', '')
        download_url = file_info.get('download_url', '')
        
        if not download_url:
            continue
        
        # 直接覆盖更新所有文件，包括install.sh
        print(f'🔄 准备更新文件: {filepath}')
        
        # 强制覆盖更新所有文件
        print(f'📥 强制下载并覆盖: {filepath}')
        if download_file(download_url, filepath):
            if os.path.exists(filepath):
                stats['updated_files'] += 1
                print(f'✅ 覆盖更新: {filepath}')
            else:
                stats['new_files'] += 1
                print(f'✅ 新增文件: {filepath}')
        else:
            stats['failed_downloads'] += 1
            print(f'❌ 下载失败: {filepath}')
    
    # 检查需要删除的文件
    remote_file_paths = {f['path'] for f in remote_files}
    for local_file in local_files:
        if local_file not in remote_file_paths:
            # 检查是否是项目文件（排除用户数据）
            if not any(skip in local_file for skip in ['logs/', 'temp/', 'screenshots/', 'data/', 'venv/']):
                try:
                    os.remove(local_file)
                    stats['deleted_files'] += 1
                    print(f'🗑️  删除: {local_file}')
                except:
                    print(f'⚠️  无法删除: {local_file}')
    
    # 输出统计信息
    print(f'\\n📊 强制覆盖更新统计:')
    print(f'  ✅ 新增文件: {stats[\"new_files\"]}')
    print(f'  🔄 覆盖更新: {stats[\"updated_files\"]}')
    print(f'  🗑️  删除文件: {stats[\"deleted_files\"]}')
    print(f'  ❌ 下载失败: {stats[\"failed_downloads\"]}')
    print(f'  📝 总计处理: {stats[\"new_files\"] + stats[\"updated_files\"]} 个文件')
    
    return 0 if stats['failed_downloads'] == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
"
    
    local update_result=$?
    
    # 设置执行权限
    print_info "🔧 设置执行权限..."
    chmod +x deploy.sh 2>/dev/null || true
    chmod +x scripts/docker-deploy.sh 2>/dev/null || true
    chmod +x scripts/quick-deploy.sh 2>/dev/null || true
    
    # 清理临时文件 - Windows兼容
    local temp_dir="/tmp"
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        temp_dir="/tmp"
    else
        temp_dir="${TEMP:-/tmp}"
    fi
    
    rm -f "$temp_dir/project_files.json" "$temp_dir/project_files_list.txt" "$temp_dir/project_files_info.json"
    
    if [ $update_result -eq 0 ]; then
        print_success "✅ 智能增量更新完成"
        return 0
    else
        print_warning "⚠️ 部分文件更新失败，但继续安装"
        return 0
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
        print_info "当前目录不包含项目文件，开始下载..."
        
        # 使用GitHub API下载项目文件
        if ! update_project_code; then
            print_error "❌ 无法下载项目文件"
            print_error "请检查网络连接和GitHub Token权限"
            exit 1
        fi
    else
        print_success "检测到项目文件，正在更新到最新版本..."
        # 更新现有项目到最新版本
        if ! update_project_code; then
            print_warning "⚠️ 代码更新失败，使用现有文件继续安装"
        else
            print_success "✅ 项目代码更新成功"
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

# 显示GitHub Token配置指南
show_github_token_guide() {
    print_info "🔑 GitHub Token 配置说明"
    echo ""
    print_info "本安装脚本使用GitHub Token进行文件下载和更新:"
    echo ""
    print_info "Token已保存到: ~/.github_token"
    print_info "下次运行安装脚本时会自动使用此Token"
    echo ""
    print_info "获取新Token步骤:"
    print_info "  1. 访问: https://github.com/settings/tokens"
    print_info "  2. 点击 'Generate new token (classic)'"
    print_info "  3. 选择 'public_repo' 权限"
    print_info "  4. 复制生成的Token"
    echo ""
    print_info "Token优势:"
    print_info "  - 每小时5000次API请求 (vs 60次匿名)"
    print_info "  - 智能增量更新，只下载有变化的文件"
    print_info "  - 更稳定的文件更新体验"
    echo ""
}

# 显示使用说明
show_usage() {
    print_success "🎉 安装完成！"
    echo ""
    print_info "📁 项目目录: $PROJECT_DIR"
    print_info "🐍 虚拟环境: $PROJECT_DIR/venv"
    echo ""
    
    # 显示GitHub Token配置指南
    show_github_token_guide
    
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
