#!/bin/bash
# 简化的API测试

TOKEN_FILE="$HOME/.github_token"
if [ -f "$TOKEN_FILE" ]; then
    TOKEN=$(cat "$TOKEN_FILE" 2>/dev/null | tr -d '\n\r')
    echo "Token: ${TOKEN:0:10}..."
    
    echo "测试rate_limit端点..."
    curl -s -H "Authorization: token $TOKEN" "https://api.github.com/rate_limit" | head -5
    
    echo -e "\n测试contents端点..."
    curl -s -H "Authorization: token $TOKEN" "https://api.github.com/repos/maxliu9403/carousell_upload/contents" | head -5
else
    echo "Token文件不存在"
fi
