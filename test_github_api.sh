#!/bin/bash
# 测试GitHub API连接

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

# 检查Token文件
TOKEN_FILE="$HOME/.github_token"
if [ -f "$TOKEN_FILE" ]; then
    GITHUB_TOKEN=$(cat "$TOKEN_FILE" 2>/dev/null | tr -d '\n\r')
    print_info "发现Token文件: $TOKEN_FILE"
    print_info "Token长度: ${#GITHUB_TOKEN}"
    print_info "Token前缀: ${GITHUB_TOKEN:0:10}..."
else
    print_error "未找到Token文件: $TOKEN_FILE"
    exit 1
fi

# 测试API连接
print_info "测试GitHub API连接..."

# 测试rate_limit端点
print_info "1. 测试rate_limit端点..."
RATE_LIMIT_RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/rate_limit" 2>/dev/null)
RATE_LIMIT_EXIT_CODE=$?

print_info "Curl退出码: $RATE_LIMIT_EXIT_CODE"
print_info "响应长度: ${#RATE_LIMIT_RESPONSE}"
print_info "响应内容: $RATE_LIMIT_RESPONSE"

if [ $RATE_LIMIT_EXIT_CODE -eq 0 ]; then
    if echo "$RATE_LIMIT_RESPONSE" | grep -q '"limit": 5000'; then
        print_success "✅ rate_limit测试通过 - 认证用户权限"
    elif echo "$RATE_LIMIT_RESPONSE" | grep -q '"message": "Bad credentials"'; then
        print_error "❌ Token无效或已过期"
    else
        print_warning "⚠️ 未知响应格式"
    fi
else
    print_error "❌ 网络请求失败"
fi

# 测试contents端点
print_info "2. 测试contents端点..."
CONTENTS_URL="https://api.github.com/repos/maxliu9403/carousell_upload/contents"
CONTENTS_RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" "$CONTENTS_URL" 2>/dev/null)
CONTENTS_EXIT_CODE=$?

print_info "Curl退出码: $CONTENTS_EXIT_CODE"
print_info "响应长度: ${#CONTENTS_RESPONSE}"

if [ $CONTENTS_EXIT_CODE -eq 0 ]; then
    if echo "$CONTENTS_RESPONSE" | grep -q '"type": "file"'; then
        print_success "✅ contents端点测试通过"
        print_info "找到文件数量: $(echo "$CONTENTS_RESPONSE" | grep -c '"type": "file"' 2>/dev/null || echo "0")"
    elif echo "$CONTENTS_RESPONSE" | grep -q '"message": "Not Found"'; then
        print_error "❌ 仓库不存在或无权限访问"
    else
        print_warning "⚠️ 未知响应格式"
        print_info "响应内容预览:"
        echo "$CONTENTS_RESPONSE" | head -3
    fi
else
    print_error "❌ contents端点请求失败"
fi

# 测试特定文件
print_info "3. 测试特定文件访问..."
FILE_URL="https://api.github.com/repos/maxliu9403/carousell_upload/contents/README.md"
FILE_RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" "$FILE_URL" 2>/dev/null)
FILE_EXIT_CODE=$?

print_info "文件请求退出码: $FILE_EXIT_CODE"
if [ $FILE_EXIT_CODE -eq 0 ]; then
    if echo "$FILE_RESPONSE" | grep -q '"download_url"'; then
        print_success "✅ 文件访问测试通过"
    else
        print_warning "⚠️ 文件访问可能有问题"
    fi
else
    print_error "❌ 文件访问失败"
fi

print_info "测试完成"
