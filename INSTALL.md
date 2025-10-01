# Carousell Uploader 安装指南

## 🚀 一键安装

### 通用安装（推荐）

```bash
# 下载并运行通用安装脚本
curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/install | bash
```

### 分平台安装

#### Windows 系统

**方法1: PowerShell（推荐）**
```powershell
# 下载并运行PowerShell安装脚本
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/install.ps1" -OutFile "install.ps1"
.\install.ps1
```

**方法2: 批处理脚本**
```cmd
# 下载并运行批处理安装脚本
curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/install.bat -o install.bat
install.bat
```

**方法3: Git Bash**
```bash
# 在Git Bash中运行
curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/install.sh | bash
```

#### macOS 系统

```bash
# 下载并运行安装脚本
curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/install.sh | bash
```

#### Linux 系统

```bash
# 下载并运行安装脚本
curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/install.sh | bash
```

## 📋 系统要求

### 最低要求
- **Python**: 3.8 或更高版本
- **内存**: 2GB RAM
- **磁盘空间**: 1GB 可用空间
- **网络**: 稳定的互联网连接

### 推荐配置
- **Python**: 3.9 或更高版本
- **内存**: 4GB RAM 或更多
- **磁盘空间**: 2GB 可用空间
- **网络**: 高速互联网连接

## 🔧 依赖项

### 系统依赖

#### Windows
- Python 3.8+ (从 python.org 下载)
- Git for Windows (可选，用于代码更新)
- PowerShell 5.1+ 或 Windows PowerShell Core

#### macOS
- Python 3.8+ (通过 Homebrew 安装)
- Xcode Command Line Tools
- Homebrew (自动安装)

#### Linux
- Python 3.8+
- pip
- 构建工具 (gcc, make)
- 包管理器 (apt, yum, dnf, pacman, zypper)

### Python 依赖
- playwright>=1.40.0
- requests>=2.31.0
- PyYAML>=6.0.1
- pandas>=2.0.0
- openpyxl>=3.1.0
- pyautogui>=0.9.54
- pyperclip>=1.8.2

## 🛠️ 安装过程

### 1. 环境检查
- 检测操作系统类型和版本
- 检查网络连接
- 验证Python版本和pip

### 2. 系统依赖安装
- **Windows**: 检查Python和Git安装
- **macOS**: 安装Homebrew和Python
- **Linux**: 安装Python和构建工具

### 3. 项目设置
- 下载或更新项目代码
- 创建Python虚拟环境
- 激活虚拟环境

### 4. Python依赖安装
- 升级pip到最新版本
- 安装项目依赖包
- 安装Playwright浏览器

### 5. 配置完成
- 创建配置文件
- 创建启动脚本
- 验证安装

## 🚀 使用方法

### 激活虚拟环境

#### Windows
```cmd
# 使用批处理脚本
.\activate_env.bat

# 或手动激活
venv\Scripts\activate
```

#### macOS/Linux
```bash
# 使用激活脚本
source ./activate_env.sh

# 或手动激活
source venv/bin/activate
```

### 运行程序

#### 快速启动
```bash
# 使用启动脚本
./run.sh        # macOS/Linux
.\run.bat       # Windows
.\run.ps1       # Windows PowerShell
```

#### 手动运行
```bash
# 激活虚拟环境后运行
python -m cli.main
```

### 配置设置

编辑配置文件：
```bash
# Windows
notepad config\settings.yaml

# macOS/Linux
nano config/settings.yaml
```

## 🔧 故障排除

### 常见问题

#### 1. Python版本问题
**问题**: `Python版本不符合要求`
**解决方案**:
- Windows: 从 python.org 下载最新版本
- macOS: `brew install python3`
- Linux: 使用包管理器安装Python 3.8+

#### 2. 网络连接问题
**问题**: `网络连接失败`
**解决方案**:
- 检查网络连接
- 配置代理设置
- 使用VPN（如果在中国大陆）

#### 3. 权限问题
**问题**: `权限不足`
**解决方案**:
- Windows: 以管理员身份运行
- macOS/Linux: 使用sudo（如果需要）

#### 4. 虚拟环境问题
**问题**: `虚拟环境创建失败`
**解决方案**:
- 检查磁盘空间
- 检查Python安装
- 重新运行安装脚本

### 日志文件

安装过程中的日志保存在：
- **Windows**: `%TEMP%\carousell_install.log`
- **macOS/Linux**: `/tmp/carousell_install.log`

### 重新安装

如果需要重新安装：
```bash
# 删除虚拟环境
rm -rf venv

# 重新运行安装脚本
./install.sh
```

## 📚 更多信息

- **项目文档**: [README.md](README.md)
- **配置说明**: [config/settings.example.yaml](config/settings.example.yaml)
- **问题反馈**: [GitHub Issues](https://github.com/maxliu9403/carousell_upload/issues)
- **项目主页**: [GitHub Repository](https://github.com/maxliu9403/carousell_upload)

## 🤝 贡献

欢迎贡献代码和报告问题！

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持

如果您遇到问题，请：

1. 查看本文档的故障排除部分
2. 搜索 [GitHub Issues](https://github.com/maxliu9403/carousell_upload/issues)
3. 创建新的 Issue 描述您的问题

---

**注意**: 请确保在运行安装脚本前备份重要数据。

