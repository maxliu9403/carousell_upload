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
