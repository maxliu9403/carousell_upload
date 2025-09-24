# Carousell Uploader Windows PowerShell 安装脚本
# 支持在空目录下自动下载项目文件

param(
    [switch]$Force = $false
)

# 设置控制台编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 颜色函数
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    } else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Success { Write-ColorOutput Green "✅ $args" }
function Write-Info { Write-ColorOutput Blue "ℹ️  $args" }
function Write-Warning { Write-ColorOutput Yellow "⚠️  $args" }
function Write-Error { Write-ColorOutput Red "❌ $args" }
function Write-Header { Write-ColorOutput Magenta "🚀 $args" }

Write-Header "Carousell Uploader Windows 安装"
Write-Info ""

# 检查当前目录是否包含项目文件
if ((Test-Path "requirements.txt") -and (Test-Path "README.md")) {
    Write-Success "检测到项目文件，开始安装..."
} else {
    Write-Warning "当前目录不包含项目文件"
    Write-Info "正在自动下载项目文件..."
    Write-Info ""
    
    # 检查git是否可用
    if (Get-Command git -ErrorAction SilentlyContinue) {
        Write-Info "使用git克隆项目..."
        try {
            git clone https://github.com/maxliu9403/carousell_upload.git temp_project
            if ($LASTEXITCODE -eq 0) {
                Write-Success "git克隆成功"
                Copy-Item -Path "temp_project\*" -Destination "." -Recurse -Force
                Copy-Item -Path "temp_project\.*" -Destination "." -Recurse -Force -ErrorAction SilentlyContinue
                Remove-Item -Path "temp_project" -Recurse -Force
                Write-Success "项目文件下载完成"
            } else {
                Write-Error "git克隆失败，尝试其他方式..."
                Download-ProjectFiles
            }
        } catch {
            Write-Error "git克隆失败，尝试其他方式..."
            Download-ProjectFiles
        }
    } else {
        Write-Warning "git不可用，尝试其他方式..."
        Download-ProjectFiles
    }
}

# 下载项目文件函数
function Download-ProjectFiles {
    Write-Info "使用curl下载项目文件..."
    
    # 检查curl是否可用
    if (Get-Command curl -ErrorAction SilentlyContinue) {
        Write-Info "创建目录结构..."
        New-Item -ItemType Directory -Path "config", "uploader", "browser", "cli", "scripts" -Force | Out-Null
        
        Write-Info "下载核心文件..."
        try {
            Invoke-WebRequest -Uri "https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/requirements.txt" -OutFile "requirements.txt"
            Invoke-WebRequest -Uri "https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/README.md" -OutFile "README.md"
            Invoke-WebRequest -Uri "https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/setup.py" -OutFile "setup.py"
            Invoke-WebRequest -Uri "https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/pyproject.toml" -OutFile "pyproject.toml"
            
            Write-Info "下载配置文件..."
            Invoke-WebRequest -Uri "https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/config/settings.yaml" -OutFile "config\settings.yaml"
            
            Write-Info "下载Python文件..."
            Invoke-WebRequest -Uri "https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/cli/main.py" -OutFile "cli\main.py"
            Invoke-WebRequest -Uri "https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/cli/cli.py" -OutFile "cli\cli.py"
            
            Write-Success "项目文件下载完成"
        } catch {
            Write-Error "下载失败: $($_.Exception.Message)"
            Write-Info "请手动克隆项目: git clone https://github.com/maxliu9403/carousell_upload.git"
            exit 1
        }
    } else {
        Write-Error "curl不可用，无法下载项目文件"
        Write-Info "请手动克隆项目: git clone https://github.com/maxliu9403/carousell_upload.git"
        exit 1
    }
}

Write-Info ""
Write-Header "开始安装Carousell Uploader"
Write-Info ""

# 检查Python
Write-Info "检查Python环境..."
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Python环境正常: $pythonVersion"
    } else {
        Write-Error "未找到Python"
        Write-Info "请先安装Python 3.8+"
        Write-Info "下载地址: https://www.python.org/downloads/"
        exit 1
    }
} catch {
    Write-Error "未找到Python"
    Write-Info "请先安装Python 3.8+"
    Write-Info "下载地址: https://www.python.org/downloads/"
    exit 1
}

# 检查pip
Write-Info "检查pip..."
try {
    $pipVersion = pip --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "pip环境正常"
    } else {
        Write-Error "未找到pip"
        Write-Info "请先安装pip"
        exit 1
    }
} catch {
    Write-Error "未找到pip"
    Write-Info "请先安装pip"
    exit 1
}

# 创建虚拟环境
Write-Info "创建Python虚拟环境..."
try {
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Success "虚拟环境创建成功"
    } else {
        Write-Error "虚拟环境创建失败"
        exit 1
    }
} catch {
    Write-Error "虚拟环境创建失败"
    exit 1
}

# 激活虚拟环境
Write-Info "激活虚拟环境..."
try {
    & "venv\Scripts\Activate.ps1"
    if ($LASTEXITCODE -eq 0) {
        Write-Success "虚拟环境激活成功"
    } else {
        Write-Error "虚拟环境激活失败"
        exit 1
    }
} catch {
    Write-Error "虚拟环境激活失败"
    exit 1
}

# 升级pip
Write-Info "升级pip..."
python -m pip install --upgrade pip

# 安装依赖
Write-Info "安装项目依赖..."
try {
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Success "依赖安装成功"
    } else {
        Write-Error "依赖安装失败"
        exit 1
    }
} catch {
    Write-Error "依赖安装失败"
    exit 1
}

# 安装playwright
Write-Info "安装playwright浏览器..."
try {
    python -m playwright install chromium
    if ($LASTEXITCODE -eq 0) {
        Write-Success "playwright浏览器安装成功"
    } else {
        Write-Warning "playwright浏览器安装失败，但可以继续"
    }
} catch {
    Write-Warning "playwright浏览器安装失败，但可以继续"
}

# 创建必要目录
Write-Info "创建必要目录..."
New-Item -ItemType Directory -Path "logs", "data", "screenshots", "temp" -Force | Out-Null
Write-Success "目录创建完成"

# 创建启动脚本
Write-Info "创建启动脚本..."
$runScript = @"
@echo off
echo 🚀 启动Carousell Uploader...
call venv\Scripts\activate.bat
python -m cli.main
pause
"@
$runScript | Out-File -FilePath "run.bat" -Encoding UTF8
Write-Success "启动脚本创建完成"

# 创建激活脚本
Write-Info "创建激活脚本..."
$activateScript = @"
@echo off
echo 🔄 激活虚拟环境...
call venv\Scripts\activate.bat
echo ✅ 虚拟环境已激活
cmd /k
"@
$activateScript | Out-File -FilePath "activate.bat" -Encoding UTF8
Write-Success "激活脚本创建完成"

Write-Info ""
Write-Header "🎉 安装完成！"
Write-Info ""
Write-Info "📁 项目目录: $(Get-Location)"
Write-Info "🐍 虚拟环境: $(Get-Location)\venv"
Write-Info ""
Write-Info "🚀 使用方法:"
Write-Info "1. 直接运行: .\run.bat"
Write-Info "2. 激活环境: .\activate.bat"
Write-Info "3. 手动运行: venv\Scripts\activate.bat && python -m cli.main"
Write-Info ""
Write-Info "📚 更多信息:"
Write-Info "- 项目文档: README.md"
Write-Info "- 配置说明: config\settings.yaml"
Write-Info "- 问题反馈: https://github.com/maxliu9403/carousell_upload/issues"
Write-Info ""
Write-Info "按任意键退出..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
