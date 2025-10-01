# =============================================================================
# Carousell Uploader - Windows PowerShell 安装脚本
# =============================================================================
# 支持系统: Windows 10/11
# 版本: 2.0.0
# 作者: Carousell Uploader Team
# =============================================================================

# 设置错误处理
$ErrorActionPreference = "Stop"

# =============================================================================
# 全局配置
# =============================================================================
$ScriptVersion = "2.0.0"
$ProjectName = "Carousell Uploader"
$RepoUrl = "https://github.com/maxliu9403/carousell_upload"
$PythonMinVersion = "3.8"

# 颜色定义
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
    Magenta = "Magenta"
    Cyan = "Cyan"
    White = "White"
}

# =============================================================================
# 工具函数
# =============================================================================

function Write-Header {
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor White
    Write-Host "║ 🚀 $ProjectName 一键安装脚本 v$ScriptVersion ║" -ForegroundColor Cyan
    Write-Host "║ 支持系统: Windows 10/11 ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor White
    Write-Host ""
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Step {
    param([string]$Message)
    Write-Host "🔧 $Message" -ForegroundColor Magenta
}

function Write-Progress {
    param([string]$Message)
    Write-Host "⏳ $Message" -ForegroundColor Cyan
}

# 检查命令是否存在
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# 获取系统信息
function Get-SystemInfo {
    Write-Step "检测系统环境..."
    
    $OS = Get-WmiObject -Class Win32_OperatingSystem
    $OSName = $OS.Caption
    $OSVersion = $OS.Version
    
    Write-Success "检测到Windows系统"
    Write-Info "操作系统: $OSName"
    Write-Info "版本: $OSVersion"
    
    # 检测架构
    $Arch = $env:PROCESSOR_ARCHITECTURE
    Write-Info "系统架构: $Arch"
}

# 检查网络连接
function Test-NetworkConnection {
    Write-Step "检查网络连接..."
    
    $TestUrls = @(
        "https://pypi.org",
        "https://github.com",
        "https://raw.githubusercontent.com"
    )
    
    foreach ($url in $TestUrls) {
        try {
            $response = Invoke-WebRequest -Uri $url -TimeoutSec 10 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Success "网络连接正常: $url"
                return
            }
        }
        catch {
            continue
        }
    }
    
    Write-Error "网络连接失败，请检查网络设置"
    Write-Info "请确保可以访问以下网站:"
    foreach ($url in $TestUrls) {
        Write-Info "  - $url"
    }
    exit 1
}

# 检查并安装系统依赖
function Install-SystemDependencies {
    Write-Step "检查系统依赖..."
    
    # 检查Python
    if (-not (Test-Command "python") -and -not (Test-Command "python3")) {
        Write-Error "未找到Python，请先安装Python 3.8+"
        Write-Info "安装指南:"
        Write-Info "  1. 访问 https://python.org"
        Write-Info "  2. 下载Python 3.8+"
        Write-Info "  3. 安装时勾选 'Add Python to PATH'"
        Write-Info "  4. 避免使用Microsoft Store版本"
        Write-Info "  5. 重启PowerShell后重新运行此脚本"
        exit 1
    }
    
    # 检查Git
    if (-not (Test-Command "git")) {
        Write-Warning "未找到Git，建议安装Git for Windows"
        Write-Info "下载地址: https://git-scm.com/download/win"
        Write-Info "安装后重启PowerShell"
    }
    
    # 检查curl
    if (-not (Test-Command "curl")) {
        Write-Warning "未找到curl，将使用PowerShell的Invoke-WebRequest"
    }
    
    Write-Success "系统依赖检查完成"
}

# 检测Python环境
function Get-PythonEnvironment {
    Write-Step "检测Python环境..."
    
    $PythonCommands = @("python", "python3", "py")
    $FoundPython = $null
    
    foreach ($cmd in $PythonCommands) {
        if (Test-Command $cmd) {
            try {
                $version = & $cmd --version 2>&1
                
                # 检查是否指向Microsoft Store
                if ($version -match "Microsoft Store") {
                    Write-Warning "跳过Microsoft Store Python: $cmd"
                    continue
                }
                
                # 检查版本是否符合要求
                $pythonCode = @"
import sys
exit(0 if sys.version_info >= (3, 8) else 1)
"@
                
                try {
                    & $cmd -c $pythonCode
                    if ($LASTEXITCODE -eq 0) {
                        $FoundPython = $cmd
                        Write-Success "找到Python: $cmd (版本: $version)"
                        break
                    } else {
                        Write-Warning "Python版本过低: $cmd ($version)"
                    }
                }
                catch {
                    Write-Warning "Python版本检查失败: $cmd"
                }
            }
            catch {
                Write-Warning "Python命令执行失败: $cmd"
            }
        }
    }
    
    if (-not $FoundPython) {
        Write-Error "未找到合适的Python安装 (需要>=3.8)"
        Write-Info "安装指南:"
        Write-Info "  1. 访问 https://python.org"
        Write-Info "  2. 下载Python 3.8+"
        Write-Info "  3. 安装时勾选 'Add Python to PATH'"
        Write-Info "  4. 重启PowerShell后重新运行此脚本"
        exit 1
    }
    
    # 检测pip
    try {
        & $FoundPython -m pip --version | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $script:PythonCmd = $FoundPython
            $script:PipCmd = "$FoundPython -m pip"
            Write-Success "pip可用: $PipCmd"
        } else {
            Write-Error "pip不可用，请重新安装Python"
            exit 1
        }
    }
    catch {
        Write-Error "pip不可用，请重新安装Python"
        exit 1
    }
}

# 创建项目目录
function Setup-ProjectDirectory {
    Write-Step "设置项目目录..."
    
    $script:ProjectDir = Get-Location
    Write-Info "项目目录: $ProjectDir"
    
    # 检查是否已有项目文件
    if ((Test-Path "requirements.txt") -or (Test-Path "pyproject.toml")) {
        Write-Success "检测到项目文件，使用当前目录"
    } else {
        Write-Info "当前目录不包含项目文件，将下载项目代码"
        Download-ProjectCode
    }
}

# 下载项目代码
function Download-ProjectCode {
    Write-Step "下载项目代码..."
    
    # 检查Git
    if (Test-Command "git") {
        Write-Info "使用Git克隆项目..."
        try {
            git clone "$RepoUrl.git" temp_project
            if ($LASTEXITCODE -eq 0) {
                # 移动文件到当前目录
                Copy-Item -Path "temp_project\*" -Destination "." -Recurse -Force
                Copy-Item -Path "temp_project\.*" -Destination "." -Recurse -Force -ErrorAction SilentlyContinue
                Remove-Item -Path "temp_project" -Recurse -Force
                Write-Success "项目代码下载完成"
                return
            }
        }
        catch {
            Write-Warning "Git克隆失败，尝试其他方式"
        }
    }
    
    # 使用PowerShell下载
    Write-Info "使用PowerShell下载项目代码..."
    Download-WithPowerShell
}

# 使用PowerShell下载项目代码
function Download-WithPowerShell {
    Write-Info "使用PowerShell下载项目代码..."
    
    # 创建临时目录
    New-Item -ItemType Directory -Path "temp_project" -Force | Out-Null
    Set-Location "temp_project"
    
    # 下载主要文件
    $files = @(
        "requirements.txt",
        "pyproject.toml",
        "setup.py",
        "README.md",
        "cli/main.py",
        "core/config.py",
        "core/logger.py",
        "core/models.py"
    )
    
    foreach ($file in $files) {
        $url = "$RepoUrl/raw/main/$file"
        $dir = Split-Path $file -Parent
        
        if ($dir -ne ".") {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
        
        try {
            Invoke-WebRequest -Uri $url -OutFile $file -UseBasicParsing
            Write-Info "下载: $file"
        }
        catch {
            Write-Warning "下载失败: $file"
        }
    }
    
    # 移动文件到上级目录
    Copy-Item -Path "*" -Destination ".." -Recurse -Force
    Copy-Item -Path ".*" -Destination ".." -Recurse -Force -ErrorAction SilentlyContinue
    Set-Location ".."
    Remove-Item -Path "temp_project" -Recurse -Force
    
    Write-Success "项目代码下载完成"
}

# 创建虚拟环境
function New-VirtualEnvironment {
    Write-Step "创建Python虚拟环境..."
    
    # 检查是否已存在虚拟环境
    if (Test-Path "venv") {
        Write-Warning "虚拟环境已存在，将重新创建"
        Remove-Item -Path "venv" -Recurse -Force
    }
    
    Write-Info "创建虚拟环境..."
    try {
        & $PythonCmd -m venv venv
        if ($LASTEXITCODE -eq 0) {
            Write-Success "虚拟环境创建成功"
        } else {
            Write-Error "虚拟环境创建失败"
            Write-Info "故障排除:"
            Write-Info "  1. 检查Python版本: $PythonCmd --version"
            Write-Info "  2. 检查磁盘空间"
            Write-Info "  3. 检查权限"
            exit 1
        }
    }
    catch {
        Write-Error "虚拟环境创建失败: $_"
        exit 1
    }
    
    # 验证虚拟环境
    if ((Test-Path "venv\Scripts\activate") -or (Test-Path "venv\bin\activate")) {
        Write-Success "虚拟环境验证通过"
    } else {
        Write-Error "虚拟环境创建失败 - 激活脚本不存在"
        exit 1
    }
}

# 激活虚拟环境
function Enable-VirtualEnvironment {
    Write-Step "激活虚拟环境..."
    
    if (Test-Path "venv\Scripts\activate") {
        & "venv\Scripts\activate"
        Write-Success "虚拟环境已激活 (Windows)"
    } elseif (Test-Path "venv\bin\activate") {
        & "venv\bin\activate"
        Write-Success "虚拟环境已激活 (WSL)"
    } else {
        Write-Error "虚拟环境激活失败"
        exit 1
    }
    
    # 验证激活
    if ($env:VIRTUAL_ENV -eq "$ProjectDir\venv") {
        Write-Success "虚拟环境激活成功: $env:VIRTUAL_ENV"
    } else {
        Write-Error "虚拟环境激活失败"
        exit 1
    }
}

# 安装Python依赖
function Install-PythonDependencies {
    Write-Step "安装Python依赖..."
    
    # 升级pip
    Write-Info "升级pip..."
    & $PipCmd install --upgrade pip
    
    # 安装基础包
    Write-Info "安装基础包..."
    & $PipCmd install wheel setuptools
    
    # 安装项目依赖
    if (Test-Path "requirements.txt") {
        Write-Info "安装项目依赖..."
        & $PipCmd install -r requirements.txt
        Write-Success "项目依赖安装完成"
    } else {
        Write-Error "未找到requirements.txt文件"
        exit 1
    }
    
    # 安装Playwright浏览器
    Write-Info "安装Playwright浏览器..."
    & python -m playwright install chromium
    Write-Success "Playwright浏览器安装完成"
    
    # 验证安装
    Write-Info "验证Python包安装..."
    $pythonCode = @"
import sys
try:
    import playwright
    import requests
    import yaml
    import pandas
    import openpyxl
    import pyautogui
    import pyperclip
    print('✅ 所有依赖包验证通过')
except ImportError as e:
    print(f'❌ 依赖包验证失败: {e}')
    sys.exit(1)
"@
    
    & python -c $pythonCode
    if ($LASTEXITCODE -ne 0) {
        Write-Error "依赖包验证失败"
        exit 1
    }
    
    Write-Success "Python环境配置完成"
}

# 创建配置文件
function New-Configuration {
    Write-Step "创建配置文件..."
    
    # 创建必要目录
    $directories = @("logs", "data", "screenshots", "temp", "config")
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    # 创建配置文件
    if (-not (Test-Path "config\settings.yaml")) {
        if (Test-Path "config\settings.example.yaml") {
            Copy-Item "config\settings.example.yaml" "config\settings.yaml"
            Write-Success "配置文件创建完成: config\settings.yaml"
        } else {
            # 创建基本配置文件
            $configContent = @"
# Carousell Uploader 配置文件
# 请根据您的需求修改以下配置

# 浏览器设置
browser:
  headless: false
  timeout: 30
  retry_count: 3

# 日志设置
logging:
  level: INFO
  file: logs/carousell.log

# 上传设置
upload:
  delay_between_actions: 2
  max_retries: 3
  screenshot_on_error: true
"@
            $configContent | Out-File -FilePath "config\settings.yaml" -Encoding UTF8
            Write-Success "基本配置文件创建完成: config\settings.yaml"
        }
    } else {
        Write-Warning "配置文件已存在: config\settings.yaml"
    }
}

# 创建启动脚本
function New-StartupScripts {
    Write-Step "创建启动脚本..."
    
    # 创建激活脚本
    $activateScript = @"
# Carousell Uploader 虚拟环境激活脚本

`$ProjectDir = Split-Path -Parent `$MyInvocation.MyCommand.Path
`$VenvDir = "`$ProjectDir\venv"

Write-Host "🚀 激活 Carousell Uploader 虚拟环境..." -ForegroundColor Cyan

if (Test-Path "`$VenvDir\Scripts\activate") {
    & "`$VenvDir\Scripts\activate"
    Write-Host "✅ 虚拟环境已激活 (Windows)" -ForegroundColor Green
} elseif (Test-Path "`$VenvDir\bin\activate") {
    & "`$VenvDir\bin\activate"
    Write-Host "✅ 虚拟环境已激活 (WSL)" -ForegroundColor Green
} else {
    Write-Host "❌ 虚拟环境未找到: `$VenvDir" -ForegroundColor Red
    Write-Host "请先运行安装脚本: .\install.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "📁 项目目录: `$ProjectDir" -ForegroundColor Blue
Write-Host "🐍 Python路径: `$(Get-Command python).Source" -ForegroundColor Blue
Write-Host ""
Write-Host "💡 使用说明:" -ForegroundColor Cyan
Write-Host "  - 运行程序: python -m cli.main" -ForegroundColor White
Write-Host "  - 退出环境: deactivate" -ForegroundColor White
Write-Host "  - 查看帮助: python -m cli.main --help" -ForegroundColor White
"@
    
    $activateScript | Out-File -FilePath "activate_env.ps1" -Encoding UTF8
    Write-Success "激活脚本创建完成: activate_env.ps1"
    
    # 创建快速启动脚本
    $runScript = @"
# Carousell Uploader 快速启动脚本

`$ProjectDir = Split-Path -Parent `$MyInvocation.MyCommand.Path
`$VenvDir = "`$ProjectDir\venv"

# 激活虚拟环境
if (Test-Path "`$VenvDir\Scripts\activate") {
    & "`$VenvDir\Scripts\activate"
} elseif (Test-Path "`$VenvDir\bin\activate") {
    & "`$VenvDir\bin\activate"
} else {
    Write-Host "❌ 虚拟环境未找到，请先运行安装脚本" -ForegroundColor Red
    exit 1
}

Write-Host "🚀 启动 Carousell Uploader..." -ForegroundColor Cyan
& python -m cli.main @args
"@
    
    $runScript | Out-File -FilePath "run.ps1" -Encoding UTF8
    Write-Success "启动脚本创建完成: run.ps1"
}

# 测试安装
function Test-Installation {
    Write-Step "测试安装..."
    
    # 测试Python导入
    $pythonCode = @"
import sys
print('Python版本:', sys.version)
print('Python路径:', sys.executable)

try:
    import playwright
    print('✅ Playwright导入成功')
except ImportError as e:
    print(f'❌ Playwright导入失败: {e}')
    sys.exit(1)

try:
    import requests
    print('✅ Requests导入成功')
except ImportError as e:
    print(f'❌ Requests导入失败: {e}')
    sys.exit(1)

try:
    import yaml
    print('✅ PyYAML导入成功')
except ImportError as e:
    print(f'❌ PyYAML导入失败: {e}')
    sys.exit(1)

try:
    import pandas
    print('✅ Pandas导入成功')
except ImportError as e:
    print(f'❌ Pandas导入失败: {e}')
    sys.exit(1)

print('✅ 所有测试通过')
"@
    
    & python -c $pythonCode
    if ($LASTEXITCODE -ne 0) {
        Write-Error "安装测试失败"
        exit 1
    }
    
    Write-Success "安装测试通过"
}

# 显示使用说明
function Show-Usage {
    Write-Host ""
    Write-Success "🎉 安装完成！"
    Write-Host ""
    Write-Info "📁 项目目录: $ProjectDir"
    Write-Info "🐍 虚拟环境: $ProjectDir\venv"
    Write-Info "⚙️  配置文件: $ProjectDir\config\settings.yaml"
    Write-Host ""
    
    Write-Info "🚀 快速使用:"
    Write-Host ""
    Write-Host "1. 激活虚拟环境:"
    Write-Host "   cd $ProjectDir"
    Write-Host "   .\activate_env.ps1"
    Write-Host ""
    Write-Host "2. 或直接运行:"
    Write-Host "   cd $ProjectDir"
    Write-Host "   .\run.ps1"
    Write-Host ""
    Write-Host "3. 配置设置:"
    Write-Host "   notepad $ProjectDir\config\settings.yaml"
    Write-Host ""
    
    Write-Info "📚 更多信息:"
    Write-Host "- 项目文档: README.md"
    Write-Host "- 配置说明: config\settings.example.yaml"
    Write-Host "- 问题反馈: $RepoUrl/issues"
    Write-Host ""
    Write-Success "安装完成！开始使用 Carousell Uploader 吧！"
}

# 主函数
function Main {
    Write-Header
    
    # 环境检查
    Get-SystemInfo
    Test-NetworkConnection
    Install-SystemDependencies
    Get-PythonEnvironment
    
    # 项目设置
    Setup-ProjectDirectory
    New-VirtualEnvironment
    Enable-VirtualEnvironment
    Install-PythonDependencies
    
    # 配置完成
    New-Configuration
    New-StartupScripts
    Test-Installation
    
    # 显示使用说明
    Show-Usage
}

# 错误处理
trap {
    Write-Error "安装过程中发生错误，请检查上述输出信息"
    exit 1
}

# 运行主函数
Main

