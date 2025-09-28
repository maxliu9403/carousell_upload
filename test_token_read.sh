#!/bin/bash
# 测试Token读取

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 测试Token读取
test_token_read() {
    local github_token=""
    local token_file="$HOME/.github_token"
    
    print_info "测试Token读取..."
    print_info "Token文件: $token_file"
    
    # 检查文件是否存在
    if [ -f "$token_file" ]; then
        print_info "发现本地Token文件: $token_file"
        print_info "文件权限: $(ls -la "$token_file" 2>/dev/null || echo "无法获取权限信息")"
        
        # 读取Token
        github_token=$(cat "$token_file" 2>/dev/null | tr -d '\n\r')
        
        if [ -n "$github_token" ]; then
            print_info "从文件读取GitHub Token (长度: ${#github_token})"
            print_info "Token前缀: ${github_token:0:10}..."
            print_info "Token内容: $github_token"
            
            # 测试API调用
            print_info "测试API调用..."
            local response=$(curl -s -H "Authorization: token $github_token" "https://api.github.com/rate_limit" 2>/dev/null)
            local curl_exit_code=$?
            
            print_info "Curl退出码: $curl_exit_code"
            print_info "响应长度: ${#response}"
            
            if [ $curl_exit_code -eq 0 ]; then
                if echo "$response" | grep -q '"limit": 5000'; then
                    print_success "✅ Token有效，API调用成功"
                else
                    print_warning "⚠️ API响应异常"
                    print_info "响应内容: $response"
                fi
            else
                print_error "❌ API调用失败"
            fi
        else
            print_error "❌ Token文件为空或无法读取"
        fi
    else
        print_error "❌ 未找到本地Token文件: $token_file"
    fi
}

test_token_read
