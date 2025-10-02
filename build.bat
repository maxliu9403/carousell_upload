@echo off
REM 快速构建脚本 - Windows版本

setlocal

echo 🚀 Carousell Uploader 快速构建脚本
echo ==================================

REM 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未找到，请安装Python 3.8+
    exit /b 1
)

REM 检查构建目录
if not exist "build" (
    echo ❌ 构建目录不存在: build/
    exit /b 1
)

if not exist "build\build.py" (
    echo ❌ 构建脚本不存在: build\build.py
    exit /b 1
)

REM 处理参数
set "mode=%~1"
if "%mode%"=="" set "mode=onefile"

if "%mode%"=="onefile" (
    echo ℹ️  开始构建单文件版本...
    cd build
    python build.py --mode onefile
    cd ..
    echo ✅ 构建完成!
) else if "%mode%"=="onedir" (
    echo ℹ️  开始构建单目录版本...
    cd build
    python build.py --mode onedir
    cd ..
    echo ✅ 构建完成!
) else if "%mode%"=="clean" (
    echo ℹ️  正在清理构建文件...
    if exist "build" (
        cd build
        rmdir /s /q build 2>nul
        rmdir /s /q dist 2>nul
        rmdir /s /q __pycache__ 2>nul
        del *.spec 2>nul
        cd ..
    )
    if exist "dist" (
        rmdir /s /q dist
    )
    echo ✅ 构建文件已清理
) else if "%mode%"=="help" (
    echo 使用方法:
    echo   %0 [选项]
    echo.
    echo 选项:
    echo   onefile    构建单文件版本 (默认)
    echo   onedir     构建单目录版本
    echo   clean      清理构建文件
    echo   help       显示此帮助信息
    echo.
    echo 示例:
    echo   %0              # 构建单文件版本
    echo   %0 onefile      # 构建单文件版本
    echo   %0 onedir       # 构建单目录版本
    echo   %0 clean        # 清理构建文件
) else (
    echo ❌ 未知选项: %mode%
    echo 使用 %0 help 查看帮助信息
    exit /b 1
)

REM 显示构建结果
if exist "dist" (
    echo.
    echo 📁 构建结果:
    dir dist
)

endlocal
