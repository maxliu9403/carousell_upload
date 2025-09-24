@echo off
setlocal enabledelayedexpansion

REM Carousell Uploader Windows 安装脚本
REM 支持在空目录下自动下载项目文件

echo.
echo ========================================
echo   Carousell Uploader Windows 安装
echo ========================================
echo.

REM 设置颜色
color 0A

REM 检查当前目录是否包含项目文件
if exist "requirements.txt" if exist "README.md" (
    echo ✅ 检测到项目文件，开始安装...
    goto :start_install
)

echo ⚠️  当前目录不包含项目文件
echo 📥 正在自动下载项目文件...
echo.

REM 检查git是否可用
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo 🔄 使用git克隆项目...
    git clone https://github.com/maxliu9403/carousell_upload.git temp_project
    if %errorlevel% equ 0 (
        echo ✅ git克隆成功
        xcopy /E /Y temp_project\* .
        rmdir /S /Q temp_project
        echo ✅ 项目文件下载完成
        goto :start_install
    ) else (
        echo ❌ git克隆失败，尝试其他方式...
        goto :download_with_curl
    )
) else (
    echo ⚠️  git不可用，尝试其他方式...
    goto :download_with_curl
)

:download_with_curl
echo 🔄 使用curl下载项目文件...

REM 检查curl是否可用
curl --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ curl不可用，无法下载项目文件
    echo 📋 请手动克隆项目: git clone https://github.com/maxliu9403/carousell_upload.git
    pause
    exit /b 1
)

REM 创建目录结构
mkdir config 2>nul
mkdir uploader 2>nul
mkdir browser 2>nul
mkdir cli 2>nul
mkdir scripts 2>nul

echo 📥 下载核心文件...
curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/requirements.txt -o requirements.txt
curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/README.md -o README.md
curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/setup.py -o setup.py
curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/pyproject.toml -o pyproject.toml

echo 📥 下载配置文件...
curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/config/settings.yaml -o config\settings.yaml

echo 📥 下载Python文件...
curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/cli/main.py -o cli\main.py
curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/cli/cli.py -o cli\cli.py

echo 📥 下载启动脚本...
curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/scripts/windows-simple-install.bat -o windows-simple-install.bat

echo ✅ 项目文件下载完成

:start_install
echo.
echo 🚀 开始安装Carousell Uploader...
echo.

REM 检查Python
echo 🔍 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Python
    echo 📋 请先安装Python 3.8+
    echo 📋 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

python --version
echo ✅ Python环境正常

REM 检查pip
echo 🔍 检查pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到pip
    echo 📋 请先安装pip
    pause
    exit /b 1
)

echo ✅ pip环境正常

REM 创建虚拟环境
echo 🔄 创建Python虚拟环境...
python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ 虚拟环境创建失败
    pause
    exit /b 1
)

echo ✅ 虚拟环境创建成功

REM 激活虚拟环境
echo 🔄 激活虚拟环境...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ 虚拟环境激活失败
    pause
    exit /b 1
)

echo ✅ 虚拟环境激活成功

REM 升级pip
echo 🔄 升级pip...
python -m pip install --upgrade pip

REM 安装依赖
echo 🔄 安装项目依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo ✅ 依赖安装成功

REM 安装playwright
echo 🔄 安装playwright浏览器...
python -m playwright install chromium
if %errorlevel% neq 0 (
    echo ⚠️  playwright浏览器安装失败，但可以继续
)

REM 创建必要目录
echo 🔄 创建必要目录...
mkdir logs 2>nul
mkdir data 2>nul
mkdir screenshots 2>nul
mkdir temp 2>nul

echo ✅ 目录创建完成

REM 创建启动脚本
echo 🔄 创建启动脚本...
echo @echo off > run.bat
echo echo 🚀 启动Carousell Uploader... >> run.bat
echo call venv\Scripts\activate.bat >> run.bat
echo python -m cli.main >> run.bat
echo pause >> run.bat

echo ✅ 启动脚本创建完成

REM 创建激活脚本
echo 🔄 创建激活脚本...
echo @echo off > activate.bat
echo echo 🔄 激活虚拟环境... >> activate.bat
echo call venv\Scripts\activate.bat >> activate.bat
echo echo ✅ 虚拟环境已激活 >> activate.bat
echo cmd /k >> activate.bat

echo ✅ 激活脚本创建完成

echo.
echo ========================================
echo   🎉 安装完成！
echo ========================================
echo.
echo 📁 项目目录: %CD%
echo 🐍 虚拟环境: %CD%\venv
echo.
echo 🚀 使用方法:
echo 1. 直接运行: run.bat
echo 2. 激活环境: activate.bat
echo 3. 手动运行: venv\Scripts\activate.bat ^&^& python -m cli.main
echo.
echo 📚 更多信息:
echo - 项目文档: README.md
echo - 配置说明: config\settings.yaml
echo - 问题反馈: https://github.com/maxliu9403/carousell_upload/issues
echo.
echo 按任意键退出...
pause >nul
