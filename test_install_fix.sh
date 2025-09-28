#!/bin/bash
# 测试install.sh修复

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

# 测试Token读取和验证
test_token_validation() {
    print_info "测试Token验证功能..."
    
    # 模拟check_and_get_github_token函数
    local github_token=""
    local token_file="$HOME/.github_token"
    
    if [ -f "$token_file" ]; then
        github_token=$(cat "$token_file" 2>/dev/null | tr -d '\n\r')
        
        if [ -n "$github_token" ]; then
            print_info "Token长度: ${#github_token}"
            print_info "Token前缀: ${github_token:0:10}..."
            
            # 测试API调用
            local response=$(curl -s -H "Authorization: token $github_token" "https://api.github.com/rate_limit" 2>/dev/null)
            local curl_exit_code=$?
            
            if [ $curl_exit_code -eq 0 ] && echo "$response" | grep -q '"limit": 5000'; then
                print_success "✅ Token验证成功"
                return 0
            else
                print_error "❌ Token验证失败"
                return 1
            fi
        else
            print_error "❌ Token文件为空"
            return 1
        fi
    else
        print_error "❌ Token文件不存在"
        return 1
    fi
}

# 测试文件获取
test_file_fetch() {
    print_info "测试文件获取功能..."
    
    local github_token=$(cat "$HOME/.github_token" 2>/dev/null | tr -d '\n\r')
    local api_url="https://api.github.com/repos/maxliu9403/carousell_upload/contents"
    local temp_file="/tmp/test_project_files.json"
    
    print_info "使用Token: ${github_token:0:10}..."
    print_info "API URL: $api_url"
    
    if curl -fsSL -H "Authorization: token $github_token" "$api_url" -o "$temp_file" 2>/dev/null; then
        print_info "API响应已保存到: $temp_file"
        print_info "响应文件大小: $(wc -c < "$temp_file" 2>/dev/null || echo "0") 字节"
        
        # 检查响应内容
        if [ -s "$temp_file" ]; then
            print_info "响应内容预览:"
            head -3 "$temp_file"
            
            # 检查是否包含文件信息
            if grep -q '"type": "file"' "$temp_file"; then
                local file_count=$(grep -c '"type": "file"' "$temp_file" 2>/dev/null || echo "0")
                print_success "✅ 成功获取 $file_count 个文件"
                return 0
            else
                print_error "❌ 响应中未找到文件信息"
                return 1
            fi
        else
            print_error "❌ 响应文件为空"
            return 1
        fi
    else
        print_error "❌ API请求失败"
        return 1
    fi
}

# 主测试
main() {
    print_info "开始测试install.sh修复..."
    
    # 测试Token验证
    if test_token_validation; then
        print_success "✅ Token验证测试通过"
    else
        print_error "❌ Token验证测试失败"
        exit 1
    fi
    
    # 测试文件获取
    if test_file_fetch; then
        print_success "✅ 文件获取测试通过"
    else
        print_error "❌ 文件获取测试失败"
        exit 1
    fi
    
    # 清理测试文件
    rm -f /tmp/test_project_files.json
    
    print_success "🎉 所有测试通过，修复成功！"
}

main "$@"
