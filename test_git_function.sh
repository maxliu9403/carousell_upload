#!/bin/bash
# 测试Git功能

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

# 测试Git功能
test_git_function() {
    print_info "🧪 测试Git功能..."
    
    # 检查Git目录
    if [ -d ".git" ]; then
        print_success "✅ 检测到Git仓库"
        
        # 显示Git状态
        print_info "📊 Git状态:"
        git status --porcelain
        
        # 显示当前分支
        print_info "🌿 当前分支:"
        git branch --show-current
        
        # 显示远程仓库
        print_info "🔗 远程仓库:"
        git remote -v
        
        # 测试Git pull
        print_info "🔄 测试Git pull..."
        if git pull origin main; then
            print_success "✅ Git pull成功"
        else
            print_warning "⚠️ Git pull失败"
            print_info "Git错误信息:"
            git pull origin main 2>&1 || true
        fi
        
        # 显示最新提交
        print_info "📝 最新提交:"
        git log --oneline -1
        
    else
        print_warning "⚠️ 未检测到Git仓库"
    fi
}

# 测试update_project_code函数
test_update_function() {
    print_info "🧪 测试update_project_code函数..."
    
    # 模拟update_project_code函数的Git检查部分
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
}

# 主函数
main() {
    print_info "🚀 开始测试Git功能"
    
    test_git_function
    echo ""
    test_update_function
    
    print_success "🎉 测试完成"
}

# 运行主函数
main "$@"
