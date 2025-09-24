# 🐍 install.sh 虚拟环境部署增强

## 🎯 增强目标

1. ✅ **完善Python虚拟环境部署** - 增强虚拟环境创建和管理功能
2. ✅ **添加虚拟环境验证** - 确保虚拟环境正确创建和激活
3. ✅ **创建管理脚本** - 提供便捷的虚拟环境管理工具
4. ✅ **优化用户体验** - 简化虚拟环境的使用流程

## 📋 增强内容

### 1. **虚拟环境创建增强** ✅

#### 新增功能
- **Python版本检查** - 确保Python版本>=3.8
- **虚拟环境验证** - 验证虚拟环境创建成功
- **详细日志输出** - 显示创建过程和结果

#### 代码实现
```bash
# 创建Python虚拟环境
create_virtual_env() {
    print_info "创建Python虚拟环境..."
    
    # 检查Python版本
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_info "Python版本: $PYTHON_VERSION"
    
    # 检查版本是否>=3.8
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_success "Python版本符合要求 (>=3.8)"
    else
        print_error "Python版本不符合要求，需要>=3.8"
        exit 1
    fi
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        print_info "创建虚拟环境..."
        python3 -m venv venv
        print_success "虚拟环境创建完成: $PROJECT_DIR/venv"
    else
        print_warning "虚拟环境已存在: $PROJECT_DIR/venv"
    fi
    
    # 验证虚拟环境
    if [ -f "venv/bin/activate" ]; then
        print_success "虚拟环境验证通过"
    else
        print_error "虚拟环境创建失败"
        exit 1
    fi
}
```

### 2. **Python依赖安装增强** ✅

#### 新增功能
- **虚拟环境激活验证** - 确保虚拟环境正确激活
- **基础包安装** - 安装wheel和setuptools
- **开发依赖支持** - 可选安装requirements-dev.txt
- **依赖验证** - 验证核心依赖安装成功

#### 代码实现
```bash
# 安装Python依赖
install_python_deps() {
    print_info "安装Python依赖..."
    
    # 激活虚拟环境
    print_info "激活虚拟环境..."
    source venv/bin/activate
    
    # 验证虚拟环境激活
    if [ "$VIRTUAL_ENV" = "$PROJECT_DIR/venv" ]; then
        print_success "虚拟环境已激活: $VIRTUAL_ENV"
    else
        print_error "虚拟环境激活失败"
        exit 1
    fi
    
    # 升级pip
    print_info "升级pip..."
    pip install --upgrade pip
    
    # 安装基础包
    print_info "安装基础包..."
    pip install wheel setuptools
    
    # 安装项目依赖
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
    
    # 验证安装
    print_info "验证Python包安装..."
    python3 -c "
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
```

### 3. **虚拟环境管理脚本** ✅

#### 创建激活脚本 (activate_env.sh)
```bash
#!/bin/bash
# Carousell Uploader 虚拟环境激活脚本

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

if [ -f "$VENV_DIR/bin/activate" ]; then
    echo "🚀 激活虚拟环境..."
    source "$VENV_DIR/bin/activate"
    echo "✅ 虚拟环境已激活: $VIRTUAL_ENV"
    echo "📁 项目目录: $PROJECT_DIR"
    echo ""
    echo "💡 使用说明:"
    echo "  - 运行程序: python -m cli.main"
    echo "  - 退出环境: deactivate"
    echo "  - 查看帮助: python -m cli.main --help"
else
    echo "❌ 虚拟环境未找到: $VENV_DIR"
    echo "请先运行安装脚本: sudo ./install.sh"
    exit 1
fi
```

#### 创建快速启动脚本 (run.sh)
```bash
#!/bin/bash
# Carousell Uploader 快速启动脚本

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
    echo "🚀 启动 Carousell Uploader..."
    python -m cli.main "$@"
else
    echo "❌ 虚拟环境未找到，请先运行安装脚本"
    exit 1
fi
```

### 4. **使用说明优化** ✅

#### 增强的使用说明
```bash
# 显示使用说明
show_usage() {
    print_success "🎉 安装完成！"
    echo ""
    print_info "📁 项目目录: $PROJECT_DIR"
    print_info "🐍 虚拟环境: $PROJECT_DIR/venv"
    echo ""
    print_info "🚀 快速使用:"
    echo "1. 激活虚拟环境: cd $PROJECT_DIR && source venv/bin/activate"
    echo "2. 或使用激活脚本: cd $PROJECT_DIR && ./activate_env.sh"
    echo "3. 或直接运行: cd $PROJECT_DIR && ./run.sh"
    echo ""
    print_info "⚙️ 配置设置:"
    echo "1. 编辑配置文件: nano $PROJECT_DIR/config/settings.yaml"
    echo "2. 设置API密钥和其他配置"
    echo ""
    print_info "🔧 系统服务 (Linux):"
    echo "1. 启动服务: sudo systemctl start carousell-uploader"
    echo "2. 查看状态: sudo systemctl status carousell-uploader"
    echo "3. 查看日志: sudo journalctl -u carousell-uploader -f"
    echo "4. 停止服务: sudo systemctl stop carousell-uploader"
    echo ""
    print_info "📚 更多信息:"
    echo "- 项目文档: README.md"
    echo "- 配置说明: config/settings.example.yaml"
    echo "- 问题反馈: https://github.com/maxliu9403/carousell_upload/issues"
}
```

## 🚀 使用方式

### 1. **安装后使用**
```bash
# 方式1: 手动激活虚拟环境
cd /opt/carousell_upload
source venv/bin/activate
python -m cli.main

# 方式2: 使用激活脚本
cd /opt/carousell_upload
./activate_env.sh
python -m cli.main

# 方式3: 直接运行
cd /opt/carousell_upload
./run.sh
```

### 2. **虚拟环境管理**
```bash
# 激活虚拟环境
source venv/bin/activate

# 查看已安装的包
pip list

# 安装新包
pip install package_name

# 退出虚拟环境
deactivate
```

### 3. **开发环境使用**
```bash
# 激活虚拟环境
source venv/bin/activate

# 运行测试
python -m pytest

# 代码格式化
black .

# 代码检查
flake8 .
```

## 📊 增强效果

### 1. **虚拟环境管理** ✅
- 自动创建和验证虚拟环境
- 提供便捷的激活脚本
- 支持开发和生产环境

### 2. **依赖管理** ✅
- 自动安装项目依赖
- 可选安装开发依赖
- 验证核心依赖安装

### 3. **用户体验** ✅
- 简化的使用流程
- 详细的使用说明
- 多种启动方式

### 4. **错误处理** ✅
- 完整的错误检查
- 详细的错误信息
- 优雅的失败处理

## 🎯 最终效果

**✅ install.sh脚本现在提供了完整的Python虚拟环境部署功能！**

- ✅ 虚拟环境创建和验证
- ✅ 依赖安装和验证
- ✅ 管理脚本创建
- ✅ 使用说明优化
- ✅ 错误处理完善
- ✅ 用户体验提升
