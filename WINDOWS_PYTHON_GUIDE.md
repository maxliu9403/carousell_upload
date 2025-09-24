# 🪟 Windows系统Python安装指南

## 🎯 问题说明

Windows系统上经常遇到"Python was not found but can be installed from the Microsoft Store"的错误，这是因为：

1. **Microsoft Store优先级** - Windows 10/11默认优先使用Microsoft Store的Python
2. **PATH环境变量** - 官网下载的Python可能没有正确添加到PATH
3. **Python Launcher** - Windows的py launcher可能指向错误的Python版本

## 🔧 解决方案

### 方案一：从官网下载安装 (推荐)

#### 1. 下载Python
- 访问 https://python.org/downloads/
- 下载Python 3.8+版本
- 选择"Windows installer (64-bit)"

#### 2. 安装Python
- 运行下载的安装程序
- **重要**: 勾选 "Add Python to PATH"
- 选择 "Install Now" 或 "Customize installation"
- 如果选择自定义，确保勾选 "pip" 和 "Add Python to environment variables"

#### 3. 验证安装
```cmd
# 打开命令提示符或PowerShell
python --version
python -m pip --version
```

### 方案二：使用Python Launcher

#### 1. 检查py launcher
```cmd
py --version
py -3 --version
py -3.8 --version
```

#### 2. 使用py launcher
```cmd
# 使用Python 3
py -3 -m pip install package_name

# 使用特定版本
py -3.8 -m pip install package_name
```

### 方案三：手动配置PATH

#### 1. 找到Python安装路径
通常位于：
- `C:\Users\用户名\AppData\Local\Programs\Python\Python3x\`
- `C:\Program Files\Python3x\`

#### 2. 添加到PATH
1. 右键"此电脑" → "属性"
2. 点击"高级系统设置"
3. 点击"环境变量"
4. 在"系统变量"中找到"Path"
5. 点击"编辑" → "新建"
6. 添加Python路径和Scripts路径：
   - `C:\Users\用户名\AppData\Local\Programs\Python\Python3x\`
   - `C:\Users\用户名\AppData\Local\Programs\Python\Python3x\Scripts\`

## 🚫 避免的问题

### 1. 不要使用Microsoft Store版本
- Microsoft Store的Python可能有权限限制
- 某些包可能无法正常安装
- 虚拟环境可能有问题

### 2. 检查多个Python版本
```cmd
# 检查所有Python版本
where python
where python3
where py

# 检查版本
python --version
python3 --version
py --version
```

### 3. 清理PATH中的重复项
- 删除PATH中的重复Python路径
- 确保只有一个Python版本在PATH中
- 避免Microsoft Store的Python路径

## 🔍 故障排除

### 问题1：仍然提示Microsoft Store
```cmd
# 解决方案：使用完整路径
C:\Users\用户名\AppData\Local\Programs\Python\Python3x\python.exe --version
```

### 问题2：pip不可用
```cmd
# 解决方案：使用python -m pip
python -m pip --version
python -m pip install package_name
```

### 问题3：虚拟环境问题
```cmd
# 解决方案：使用完整路径创建虚拟环境
python -m venv venv
# 或
py -3 -m venv venv
```

## ✅ 验证安装

### 1. 基本验证
```cmd
python --version
python -m pip --version
python -c "import sys; print(sys.version)"
```

### 2. 功能验证
```cmd
# 创建虚拟环境
python -m venv test_env
test_env\Scripts\activate
python -m pip install requests
python -c "import requests; print('OK')"
deactivate
rmdir /s test_env
```

### 3. 路径验证
```cmd
# 检查Python路径
where python
python -c "import sys; print(sys.executable)"
```

## 🎯 最佳实践

### 1. 使用虚拟环境
```cmd
# 创建项目虚拟环境
python -m venv project_env
project_env\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 退出虚拟环境
deactivate
```

### 2. 使用requirements.txt
```cmd
# 生成依赖文件
pip freeze > requirements.txt

# 安装依赖
pip install -r requirements.txt
```

### 3. 使用py launcher
```cmd
# 推荐使用py launcher
py -3 -m venv venv
py -3 -m pip install package_name
```

## 📚 相关资源

- [Python官方文档](https://docs.python.org/3/)
- [Python Windows安装指南](https://docs.python.org/3/using/windows.html)
- [pip用户指南](https://pip.pypa.io/en/stable/user_guide/)
- [虚拟环境指南](https://docs.python.org/3/tutorial/venv.html)

---

**💡 提示**: 如果仍然遇到问题，建议完全卸载所有Python版本，然后重新从官网下载安装，确保勾选"Add Python to PATH"选项。
