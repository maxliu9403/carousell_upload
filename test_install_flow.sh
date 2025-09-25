#!/bin/bash
# 测试install.sh的执行流程

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

# 模拟create_project_dir函数
test_create_project_dir() {
    print_info "🧪 测试create_project_dir函数..."
    
    # 使用当前目录作为项目目录
    PROJECT_DIR="$(pwd)"
    print_info "项目目录: $PROJECT_DIR"
    
    # 检查当前目录是否包含项目文件
    if [ ! -f "requirements.txt" ] && [ ! -f "README.md" ]; then
        print_warning "当前目录不包含项目文件"
        print_info "正在自动下载项目文件..."
        print_info "会调用update_project_code函数"
    else
        print_success "检测到项目文件，正在更新到最新版本..."
        print_info "会调用update_project_code函数"
        
        # 模拟update_project_code调用
        test_update_project_code
    fi
}

# 模拟update_project_code函数
test_update_project_code() {
    print_info "🔄 更新项目代码到最新版本..."
    
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
    
    print_info "如果Git失败，会继续使用curl下载..."
    return 1
}

# 主函数
main() {
    print_info "🚀 开始测试install.sh执行流程"
    
    print_info "📋 当前目录文件:"
    ls -la | head -10
    
    print_info "📋 检查项目文件:"
    if [ -f "requirements.txt" ]; then
        print_success "✅ 找到requirements.txt"
    else
        print_warning "⚠️ 未找到requirements.txt"
    fi
    
    if [ -f "README.md" ]; then
        print_success "✅ 找到README.md"
    else
        print_warning "⚠️ 未找到README.md"
    fi
    
    if [ -d ".git" ]; then
        print_success "✅ 找到.git目录"
    else
        print_warning "⚠️ 未找到.git目录"
    fi
    
    echo ""
    test_create_project_dir
    
    print_success "🎉 测试完成"
}

# 运行主函数
main "$@"
