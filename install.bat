@echo off
REM =============================================================================
REM Carousell Uploader - Windows 批处理安装脚本
REM =============================================================================
REM 支持系统: Windows 10/11
REM 版本: 2.0.0
REM 作者: Carousell Uploader Team
REM =============================================================================

setlocal enabledelayedexpansion

REM 设置错误处理
set "ErrorActionPreference=Stop"

REM =============================================================================
REM 全局配置
REM =============================================================================
set "ScriptVersion=2.0.0"
set "ProjectName=Carousell Uploader"
set "RepoUrl=https://github.com/maxliu9403/carousell_upload"
set "PythonMinVersion=3.8"

REM =============================================================================
REM 工具函数
REM =============================================================================

:WriteHeader
echo ╔══════════════════════════════════════════════════════════════╗
echo ║ 🚀 %ProjectName% 一键安装脚本 v%ScriptVersion% ║
echo ║ 支持系统: Windows 10/11 ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
goto :eof

:WriteInfo
echo ℹ️  %~1
goto :eof

:WriteSuccess
echo ✅ %~1
goto :eof

:WriteWarning
echo ⚠️  %~1
goto :eof

:WriteError
echo ❌ %~1
goto :eof

:WriteStep
echo 🔧 %~1
goto :eof

:WriteProgress
echo ⏳ %~1
goto :eof

REM 检查命令是否存在
:TestCommand
set "Command=%~1"
where "%Command%" >nul 2>&1
if %errorlevel% equ 0 (
    exit /b 0
) else (
    exit /b 1
)
goto :eof

REM 获取系统信息
:GetSystemInfo
call :WriteStep "检测系统环境..."

for /f "tokens=2 delims==" %%i in ('wmic os get caption /value ^| find "="') do set "OSName=%%i"
for /f "tokens=2 delims==" %%i in ('wmic os get version /value ^| find "="') do set "OSVersion=%%i"

call :WriteSuccess "检测到Windows系统"
call :WriteInfo "操作系统: %OSName%"
call :WriteInfo "版本: %OSVersion%"

REM 检测架构
set "Arch=%PROCESSOR_ARCHITECTURE%"
call :WriteInfo "系统架构: %Arch%"
goto :eof

REM 检查网络连接
:TestNetworkConnection
call :WriteStep "检查网络连接..."

set "TestUrls=https://pypi.org https://github.com https://raw.githubusercontent.com"

for %%u in (%TestUrls%) do (
    curl -fsSL --connect-timeout 10 "%%u" >nul 2>&1
    if !errorlevel! equ 0 (
        call :WriteSuccess "网络连接正常: %%u"
        goto :eof
    )
)

call :WriteError "网络连接失败，请检查网络设置"
call :WriteInfo "请确保可以访问以下网站:"
for %%u in (%TestUrls%) do (
    call :WriteInfo "  - %%u"
)
exit /b 1

REM 检查并安装系统依赖
:InstallSystemDependencies
call :WriteStep "检查系统依赖..."

REM 检查Python
call :TestCommand "python"
if %errorlevel% neq 0 (
    call :TestCommand "python3"
    if %errorlevel% neq 0 (
        call :WriteError "未找到Python，请先安装Python 3.8+"
        call :WriteInfo "安装指南:"
        call :WriteInfo "  1. 访问 https://python.org"
        call :WriteInfo "  2. 下载Python 3.8+"
        call :WriteInfo "  3. 安装时勾选 'Add Python to PATH'"
        call :WriteInfo "  4. 避免使用Microsoft Store版本"
        call :WriteInfo "  5. 重启命令提示符后重新运行此脚本"
        exit /b 1
    )
)

REM 检查Git
call :TestCommand "git"
if %errorlevel% neq 0 (
    call :WriteWarning "未找到Git，建议安装Git for Windows"
    call :WriteInfo "下载地址: https://git-scm.com/download/win"
    call :WriteInfo "安装后重启命令提示符"
)

REM 检查curl
call :TestCommand "curl"
if %errorlevel% neq 0 (
    call :WriteWarning "未找到curl，将使用PowerShell的Invoke-WebRequest"
)

call :WriteSuccess "系统依赖检查完成"
goto :eof

REM 检测Python环境
:GetPythonEnvironment
call :WriteStep "检测Python环境..."

set "PythonCommands=python python3 py"
set "FoundPython="

for %%c in (%PythonCommands%) do (
    call :TestCommand "%%c"
    if !errorlevel! equ 0 (
        REM 检查版本
        for /f "tokens=2" %%v in ('%%c --version 2^>^&1') do set "Version=%%v"
        
        REM 检查是否指向Microsoft Store
        echo !Version! | findstr /i "Microsoft Store" >nul
        if !errorlevel! equ 0 (
            call :WriteWarning "跳过Microsoft Store Python: %%c"
            continue
        )
        
        REM 检查版本是否符合要求
        %%c -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
        if !errorlevel! equ 0 (
            set "FoundPython=%%c"
            call :WriteSuccess "找到Python: %%c (版本: !Version!)"
            goto :found
        ) else (
            call :WriteWarning "Python版本过低: %%c (!Version!)"
        )
    )
)

:found
if "%FoundPython%"=="" (
    call :WriteError "未找到合适的Python安装 (需要>=3.8)"
    call :WriteInfo "安装指南:"
    call :WriteInfo "  1. 访问 https://python.org"
    call :WriteInfo "  2. 下载Python 3.8+"
    call :WriteInfo "  3. 安装时勾选 'Add Python to PATH'"
    call :WriteInfo "  4. 重启命令提示符后重新运行此脚本"
    exit /b 1
)

REM 检测pip
%FoundPython% -m pip --version >nul 2>&1
if !errorlevel! equ 0 (
    set "PythonCmd=%FoundPython%"
    set "PipCmd=%FoundPython% -m pip"
    call :WriteSuccess "pip可用: %PipCmd%"
) else (
    call :WriteError "pip不可用，请重新安装Python"
    exit /b 1
)
goto :eof

REM 创建项目目录
:SetupProjectDirectory
call :WriteStep "设置项目目录..."

set "ProjectDir=%CD%"
call :WriteInfo "项目目录: %ProjectDir%"

REM 检查是否已有项目文件
if exist "requirements.txt" (
    call :WriteSuccess "检测到项目文件，使用当前目录"
    goto :eof
)
if exist "pyproject.toml" (
    call :WriteSuccess "检测到项目文件，使用当前目录"
    goto :eof
)

call :WriteInfo "当前目录不包含项目文件，将下载项目代码"
call :DownloadProjectCode
goto :eof

REM 下载项目代码
:DownloadProjectCode
call :WriteStep "下载项目代码..."

REM 检查Git
call :TestCommand "git"
if %errorlevel% equ 0 (
    call :WriteInfo "使用Git克隆项目..."
    git clone "%RepoUrl%.git" temp_project
    if !errorlevel! equ 0 (
        REM 移动文件到当前目录
        xcopy /E /I /Y "temp_project\*" "."
        xcopy /E /I /Y /H "temp_project\.*" "." 2>nul
        rmdir /S /Q "temp_project"
        call :WriteSuccess "项目代码下载完成"
        goto :eof
    )
)

call :WriteWarning "Git克隆失败，尝试其他方式"
call :DownloadWithPowerShell
goto :eof

REM 使用PowerShell下载项目代码
:DownloadWithPowerShell
call :WriteInfo "使用PowerShell下载项目代码..."

REM 创建临时目录
mkdir "temp_project" 2>nul
cd "temp_project"

REM 下载主要文件
set "files=requirements.txt pyproject.toml setup.py README.md cli\main.py core\config.py core\logger.py core\models.py"

for %%f in (%files%) do (
    set "url=%RepoUrl%/raw/main/%%f"
    set "dir=%%f"
    
    REM 创建目录
    for %%d in ("!dir!") do (
        if not "%%~dpd"=="." (
            mkdir "%%~dpd" 2>nul
        )
    )
    
    REM 下载文件
    powershell -Command "Invoke-WebRequest -Uri '!url!' -OutFile '%%f' -UseBasicParsing" 2>nul
    if !errorlevel! equ 0 (
        call :WriteInfo "下载: %%f"
    ) else (
        call :WriteWarning "下载失败: %%f"
    )
)

REM 移动文件到上级目录
xcopy /E /I /Y "*" ".."
xcopy /E /I /Y /H ".*" ".." 2>nul
cd ".."
rmdir /S /Q "temp_project"

call :WriteSuccess "项目代码下载完成"
goto :eof

REM 创建虚拟环境
:NewVirtualEnvironment
call :WriteStep "创建Python虚拟环境..."

REM 检查是否已存在虚拟环境
if exist "venv" (
    call :WriteWarning "虚拟环境已存在，将重新创建"
    rmdir /S /Q "venv"
)

call :WriteInfo "创建虚拟环境..."
%PythonCmd% -m venv venv
if !errorlevel! equ 0 (
    call :WriteSuccess "虚拟环境创建成功"
) else (
    call :WriteError "虚拟环境创建失败"
    call :WriteInfo "故障排除:"
    call :WriteInfo "  1. 检查Python版本: %PythonCmd% --version"
    call :WriteInfo "  2. 检查磁盘空间"
    call :WriteInfo "  3. 检查权限"
    exit /b 1
)

REM 验证虚拟环境
if exist "venv\Scripts\activate" (
    call :WriteSuccess "虚拟环境验证通过"
) else (
    call :WriteError "虚拟环境创建失败 - 激活脚本不存在"
    exit /b 1
)
goto :eof

REM 激活虚拟环境
:EnableVirtualEnvironment
call :WriteStep "激活虚拟环境..."

if exist "venv\Scripts\activate" (
    call "venv\Scripts\activate"
    call :WriteSuccess "虚拟环境已激活 (Windows)"
) else (
    call :WriteError "虚拟环境激活失败"
    exit /b 1
)

REM 验证激活
if "%VIRTUAL_ENV%"=="%ProjectDir%\venv" (
    call :WriteSuccess "虚拟环境激活成功: %VIRTUAL_ENV%"
) else (
    call :WriteError "虚拟环境激活失败"
    exit /b 1
)
goto :eof

REM 安装Python依赖
:InstallPythonDependencies
call :WriteStep "安装Python依赖..."

REM 升级pip
call :WriteInfo "升级pip..."
%PipCmd% install --upgrade pip

REM 安装基础包
call :WriteInfo "安装基础包..."
%PipCmd% install wheel setuptools

REM 安装项目依赖
if exist "requirements.txt" (
    call :WriteInfo "安装项目依赖..."
    %PipCmd% install -r requirements.txt
    call :WriteSuccess "项目依赖安装完成"
) else (
    call :WriteError "未找到requirements.txt文件"
    exit /b 1
)

REM 安装Playwright浏览器
call :WriteInfo "安装Playwright浏览器..."
python -m playwright install chromium
call :WriteSuccess "Playwright浏览器安装完成"

REM 验证安装
call :WriteInfo "验证Python包安装..."
python -c "import sys; import playwright; import requests; import yaml; import pandas; import openpyxl; import pyautogui; import pyperclip; print('✅ 所有依赖包验证通过')"
if !errorlevel! neq 0 (
    call :WriteError "依赖包验证失败"
    exit /b 1
)

call :WriteSuccess "Python环境配置完成"
goto :eof

REM 创建配置文件
:NewConfiguration
call :WriteStep "创建配置文件..."

REM 创建必要目录
set "directories=logs data screenshots temp config"
for %%d in (%directories%) do (
    if not exist "%%d" (
        mkdir "%%d" 2>nul
    )
)

REM 创建配置文件
if not exist "config\settings.yaml" (
    if exist "config\settings.example.yaml" (
        copy "config\settings.example.yaml" "config\settings.yaml" >nul
        call :WriteSuccess "配置文件创建完成: config\settings.yaml"
    ) else (
        REM 创建基本配置文件
        (
            echo # Carousell Uploader 配置文件
            echo # 请根据您的需求修改以下配置
            echo.
            echo # 浏览器设置
            echo browser:
            echo   headless: false
            echo   timeout: 30
            echo   retry_count: 3
            echo.
            echo # 日志设置
            echo logging:
            echo   level: INFO
            echo   file: logs/carousell.log
            echo.
            echo # 上传设置
            echo upload:
            echo   delay_between_actions: 2
            echo   max_retries: 3
            echo   screenshot_on_error: true
        ) > "config\settings.yaml"
        call :WriteSuccess "基本配置文件创建完成: config\settings.yaml"
    )
) else (
    call :WriteWarning "配置文件已存在: config\settings.yaml"
)
goto :eof

REM 创建启动脚本
:NewStartupScripts
call :WriteStep "创建启动脚本..."

REM 创建激活脚本
(
    echo @echo off
    echo REM Carousell Uploader 虚拟环境激活脚本
    echo.
    echo set "ProjectDir=%%~dp0"
    echo set "VenvDir=%%ProjectDir%%venv"
    echo.
    echo echo 🚀 激活 Carousell Uploader 虚拟环境...
    echo.
    echo if exist "%%VenvDir%%\Scripts\activate" ^(
    echo     call "%%VenvDir%%\Scripts\activate"
    echo     echo ✅ 虚拟环境已激活 ^(Windows^)
    echo ^) else ^(
    echo     echo ❌ 虚拟环境未找到: %%VenvDir%%
    echo     echo 请先运行安装脚本: .\install.bat
    echo     exit /b 1
    echo ^)
    echo.
    echo echo 📁 项目目录: %%ProjectDir%%
    echo echo 🐍 Python路径: %%VIRTUAL_ENV%%\Scripts\python.exe
    echo echo.
    echo echo 💡 使用说明:
    echo echo   - 运行程序: python -m cli.main
    echo echo   - 退出环境: deactivate
    echo echo   - 查看帮助: python -m cli.main --help
) > "activate_env.bat"

call :WriteSuccess "激活脚本创建完成: activate_env.bat"

REM 创建快速启动脚本
(
    echo @echo off
    echo REM Carousell Uploader 快速启动脚本
    echo.
    echo set "ProjectDir=%%~dp0"
    echo set "VenvDir=%%ProjectDir%%venv"
    echo.
    echo REM 激活虚拟环境
    echo if exist "%%VenvDir%%\Scripts\activate" ^(
    echo     call "%%VenvDir%%\Scripts\activate"
    echo ^) else ^(
    echo     echo ❌ 虚拟环境未找到，请先运行安装脚本
    echo     exit /b 1
    echo ^)
    echo.
    echo echo 🚀 启动 Carousell Uploader...
    echo python -m cli.main %%*
) > "run.bat"

call :WriteSuccess "启动脚本创建完成: run.bat"
goto :eof

REM 测试安装
:TestInstallation
call :WriteStep "测试安装..."

python -c "import sys; print('Python版本:', sys.version); print('Python路径:', sys.executable); import playwright; print('✅ Playwright导入成功'); import requests; print('✅ Requests导入成功'); import yaml; print('✅ PyYAML导入成功'); import pandas; print('✅ Pandas导入成功'); print('✅ 所有测试通过')"
if !errorlevel! neq 0 (
    call :WriteError "安装测试失败"
    exit /b 1
)

call :WriteSuccess "安装测试通过"
goto :eof

REM 显示使用说明
:ShowUsage
echo.
call :WriteSuccess "🎉 安装完成！"
echo.
call :WriteInfo "📁 项目目录: %ProjectDir%"
call :WriteInfo "🐍 虚拟环境: %ProjectDir%\venv"
call :WriteInfo "⚙️  配置文件: %ProjectDir%\config\settings.yaml"
echo.
call :WriteInfo "🚀 快速使用:"
echo.
echo 1. 激活虚拟环境:
echo    cd %ProjectDir%
echo    .\activate_env.bat
echo.
echo 2. 或直接运行:
echo    cd %ProjectDir%
echo    .\run.bat
echo.
echo 3. 配置设置:
echo    notepad %ProjectDir%\config\settings.yaml
echo.
call :WriteInfo "📚 更多信息:"
echo - 项目文档: README.md
echo - 配置说明: config\settings.example.yaml
echo - 问题反馈: %RepoUrl%/issues
echo.
call :WriteSuccess "安装完成！开始使用 Carousell Uploader 吧！"
goto :eof

REM 主函数
:Main
call :WriteHeader

REM 环境检查
call :GetSystemInfo
call :TestNetworkConnection
call :InstallSystemDependencies
call :GetPythonEnvironment

REM 项目设置
call :SetupProjectDirectory
call :NewVirtualEnvironment
call :EnableVirtualEnvironment
call :InstallPythonDependencies

REM 配置完成
call :NewConfiguration
call :NewStartupScripts
call :TestInstallation

REM 显示使用说明
call :ShowUsage
goto :eof

REM 运行主函数
call :Main

