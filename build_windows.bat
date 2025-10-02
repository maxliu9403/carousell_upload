@echo off
chcp 65001 >nul
echo ========================================
echo Carousell Uploader - Windows 快速构建
echo ========================================

echo.
echo 📁 检查构建工具...
if not exist "build\build.py" (
    echo ❌ 构建工具不存在，请检查项目结构
    pause
    exit /b 1
)

echo.
echo 🚀 开始构建...
python build\build.py %*

if errorlevel 1 (
    echo ❌ 构建失败
    pause
    exit /b 1
)

echo.
echo ✅ 构建完成！
echo 📁 可执行文件位置: dist\CarousellUploader.exe
echo.
pause