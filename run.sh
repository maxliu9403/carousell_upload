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
