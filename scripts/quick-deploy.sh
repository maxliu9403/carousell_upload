#!/bin/bash
# Carousell Uploader 快速部署脚本

set -e

echo "🚀 Carousell Uploader 快速部署脚本"
echo "=================================="

# 检查Python版本
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        echo "✅ Python版本: $PYTHON_VERSION"
        
        # 检查版本是否>=3.8
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            echo "✅ Python版本符合要求 (>=3.8)"
        else
            echo "❌ Python版本不符合要求，需要>=3.8"
            exit 1
        fi
    else
        echo "❌ 未找到Python3，请先安装Python 3.8+"
        exit 1
    fi
}

# 创建虚拟环境
create_venv() {
    echo "📦 创建虚拟环境..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo "✅ 虚拟环境创建成功"
    else
        echo "⚠️  虚拟环境已存在"
    fi
}

# 激活虚拟环境
activate_venv() {
    echo "🔧 激活虚拟环境..."
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
}

# 安装依赖
install_deps() {
    echo "📦 安装Python依赖..."
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Python依赖安装完成"
    
    echo "🌐 安装Playwright浏览器..."
    playwright install chromium
    echo "✅ Playwright浏览器安装完成"
}

# 配置设置
setup_config() {
    echo "⚙️  配置设置..."
    if [ ! -f "config/settings.yaml" ]; then
        if [ -f "config/settings.example.yaml" ]; then
            cp config/settings.example.yaml config/settings.yaml
            echo "✅ 配置文件已创建: config/settings.yaml"
            echo "⚠️  请编辑 config/settings.yaml 文件配置您的设置"
        else
            echo "❌ 未找到配置文件模板"
            exit 1
        fi
    else
        echo "⚠️  配置文件已存在: config/settings.yaml"
    fi
}

# 创建必要目录
create_dirs() {
    echo "📁 创建必要目录..."
    mkdir -p logs
    mkdir -p data
    mkdir -p screenshots
    echo "✅ 目录创建完成"
}

# 测试安装
test_installation() {
    echo "🧪 测试安装..."
    python3 -c "
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
    echo "✅ 安装测试通过"
}

# 显示使用说明
show_usage() {
    echo ""
    echo "🎉 部署完成！"
    echo "============="
    echo ""
    echo "📋 使用说明:"
    echo "1. 激活虚拟环境: source venv/bin/activate"
    echo "2. 编辑配置: vim config/settings.yaml"
    echo "3. 运行程序: python -m cli.main"
    echo ""
    echo "📚 更多信息请查看 README.md"
    echo ""
}

# 主函数
main() {
    check_python
    create_venv
    activate_venv
    install_deps
    setup_config
    create_dirs
    test_installation
    show_usage
}

# 运行主函数
main "$@"
