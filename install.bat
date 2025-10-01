@echo off
REM =============================================================================
REM Carousell Uploader - Windows Batch Installation Script
REM =============================================================================
REM Supported Systems: Windows 10/11
REM Version: 2.0.0
REM Author: Carousell Uploader Team
REM =============================================================================

setlocal enabledelayedexpansion

REM Set error handling
set "ErrorActionPreference=Stop"

REM =============================================================================
REM Global Configuration
REM =============================================================================
set "ScriptVersion=2.0.0"
set "ProjectName=Carousell Uploader"
set "RepoUrl=https://github.com/maxliu9403/carousell_upload"
set "PythonMinVersion=3.8"

REM =============================================================================
REM Utility Functions
REM =============================================================================

:WriteHeader
echo ╔══════════════════════════════════════════════════════════════╗
echo ║ 🚀 %ProjectName% One-Click Installation Script v%ScriptVersion% ║
echo ║ Supported Systems: Windows 10/11 ║
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

REM Check if command exists
:TestCommand
set "Command=%~1"
where "%Command%" >nul 2>&1
if %errorlevel% equ 0 (
    exit /b 0
) else (
    exit /b 1
)
goto :eof

REM Get system information
:GetSystemInfo
call :WriteStep "Detecting system environment..."

for /f "tokens=2 delims==" %%i in ('wmic os get caption /value ^| find "="') do set "OSName=%%i"
for /f "tokens=2 delims==" %%i in ('wmic os get version /value ^| find "="') do set "OSVersion=%%i"

call :WriteSuccess "Detected Windows system"
call :WriteInfo "Operating System: %OSName%"
call :WriteInfo "Version: %OSVersion%"

REM Detect architecture
set "Arch=%PROCESSOR_ARCHITECTURE%"
call :WriteInfo "System Architecture: %Arch%"
goto :eof

REM Check network connection
:TestNetworkConnection
call :WriteStep "Checking network connection..."

set "TestUrls=https://pypi.org https://github.com https://raw.githubusercontent.com"

for %%u in (%TestUrls%) do (
    curl -fsSL --connect-timeout 10 "%%u" >nul 2>&1
    if !errorlevel! equ 0 (
        call :WriteSuccess "Network connection normal: %%u"
        goto :eof
    )
)

call :WriteError "Network connection failed, please check network settings"
call :WriteInfo "Please ensure you can access the following websites:"
for %%u in (%TestUrls%) do (
    call :WriteInfo "  - %%u"
)
exit /b 1

REM Check and install system dependencies
:InstallSystemDependencies
call :WriteStep "Checking system dependencies..."

REM Check Python
call :TestCommand "python"
if %errorlevel% neq 0 (
    call :TestCommand "python3"
    if %errorlevel% neq 0 (
        call :WriteError "Python not found, please install Python 3.8+ first"
        call :WriteInfo "Installation guide:"
        call :WriteInfo "  1. Visit https://python.org"
        call :WriteInfo "  2. Download Python 3.8+"
        call :WriteInfo "  3. Check 'Add Python to PATH' during installation"
        call :WriteInfo "  4. Avoid using Microsoft Store version"
        call :WriteInfo "  5. Restart command prompt and run this script again"
        exit /b 1
    )
)

REM Check Git
call :TestCommand "git"
if %errorlevel% neq 0 (
    call :WriteWarning "Git not found, recommend installing Git for Windows"
    call :WriteInfo "Download: https://git-scm.com/download/win"
    call :WriteInfo "Restart command prompt after installation"
)

REM Check curl
call :TestCommand "curl"
if %errorlevel% neq 0 (
    call :WriteWarning "curl not found, will use PowerShell's Invoke-WebRequest"
)

call :WriteSuccess "System dependencies check completed"
goto :eof

REM Detect Python environment
:GetPythonEnvironment
call :WriteStep "Detecting Python environment..."

set "PythonCommands=python python3 py"
set "FoundPython="

for %%c in (%PythonCommands%) do (
    call :TestCommand "%%c"
    if !errorlevel! equ 0 (
        REM Check version
        for /f "tokens=2" %%v in ('%%c --version 2^>^&1') do set "Version=%%v"
        
        REM Check if pointing to Microsoft Store
        echo !Version! | findstr /i "Microsoft Store" >nul
        if !errorlevel! equ 0 (
            call :WriteWarning "Skipping Microsoft Store Python: %%c"
            continue
        )
        
        REM Check if version meets requirements
        %%c -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
        if !errorlevel! equ 0 (
            set "FoundPython=%%c"
            call :WriteSuccess "Found Python: %%c (Version: !Version!)"
            goto :found
        ) else (
            call :WriteWarning "Python version too low: %%c (!Version!)"
        )
    )
)

:found
if "%FoundPython%"=="" (
    call :WriteError "No suitable Python installation found (requires >=3.8)"
    call :WriteInfo "Installation guide:"
    call :WriteInfo "  1. Visit https://python.org"
    call :WriteInfo "  2. Download Python 3.8+"
    call :WriteInfo "  3. Check 'Add Python to PATH' during installation"
    call :WriteInfo "  4. Restart command prompt and run this script again"
    exit /b 1
)

REM Detect pip
%FoundPython% -m pip --version >nul 2>&1
if !errorlevel! equ 0 (
    set "PythonCmd=%FoundPython%"
    set "PipCmd=%FoundPython% -m pip"
    call :WriteSuccess "pip available: %PipCmd%"
) else (
    call :WriteError "pip not available, please reinstall Python"
    exit /b 1
)
goto :eof

REM Create project directory
:SetupProjectDirectory
call :WriteStep "Setting up project directory..."

set "ProjectDir=%CD%"
call :WriteInfo "Project directory: %ProjectDir%"

REM Check if project files already exist
if exist "requirements.txt" (
    call :WriteSuccess "Project files detected, using current directory"
    goto :eof
)
if exist "pyproject.toml" (
    call :WriteSuccess "Project files detected, using current directory"
    goto :eof
)

call :WriteInfo "Current directory does not contain project files, will download project code"
call :DownloadProjectCode
goto :eof

REM Download project code
:DownloadProjectCode
call :WriteStep "Downloading project code..."

REM Check Git
call :TestCommand "git"
if %errorlevel% equ 0 (
    call :WriteInfo "Using Git to clone project..."
    git clone "%RepoUrl%.git" temp_project
    if !errorlevel! equ 0 (
        REM Move files to current directory
        xcopy /E /I /Y "temp_project\*" "."
        xcopy /E /I /Y /H "temp_project\.*" "." 2>nul
        rmdir /S /Q "temp_project"
        call :WriteSuccess "Project code download completed"
        goto :eof
    )
)

call :WriteWarning "Git clone failed, trying other methods"
call :DownloadWithPowerShell
goto :eof

REM Use PowerShell to download project code
:DownloadWithPowerShell
call :WriteInfo "Using PowerShell to download project code..."

REM Create temporary directory
mkdir "temp_project" 2>nul
cd "temp_project"

REM Download main files
set "files=requirements.txt pyproject.toml setup.py README.md cli\main.py core\config.py core\logger.py core\models.py"

for %%f in (%files%) do (
    set "url=%RepoUrl%/raw/main/%%f"
    set "dir=%%f"
    
    REM Create directory
    for %%d in ("!dir!") do (
        if not "%%~dpd"=="." (
            mkdir "%%~dpd" 2>nul
        )
    )
    
    REM Download file
    powershell -Command "Invoke-WebRequest -Uri '!url!' -OutFile '%%f' -UseBasicParsing" 2>nul
    if !errorlevel! equ 0 (
        call :WriteInfo "Downloaded: %%f"
    ) else (
        call :WriteWarning "Download failed: %%f"
    )
)

REM Move files to parent directory
xcopy /E /I /Y "*" ".."
xcopy /E /I /Y /H ".*" ".." 2>nul
cd ".."
rmdir /S /Q "temp_project"

call :WriteSuccess "Project code download completed"
goto :eof

REM Create virtual environment
:NewVirtualEnvironment
call :WriteStep "Creating Python virtual environment..."

REM Check if virtual environment already exists
if exist "venv" (
    call :WriteWarning "Virtual environment already exists, will recreate"
    rmdir /S /Q "venv"
)

call :WriteInfo "Creating virtual environment..."
%PythonCmd% -m venv venv
if !errorlevel! equ 0 (
    call :WriteSuccess "Virtual environment created successfully"
) else (
    call :WriteError "Virtual environment creation failed"
    call :WriteInfo "Troubleshooting:"
    call :WriteInfo "  1. Check Python version: %PythonCmd% --version"
    call :WriteInfo "  2. Check disk space"
    call :WriteInfo "  3. Check permissions"
    exit /b 1
)

REM Verify virtual environment
if exist "venv\Scripts\activate" (
    call :WriteSuccess "Virtual environment verification passed"
) else (
    call :WriteError "Virtual environment creation failed - activation script not found"
    exit /b 1
)
goto :eof

REM Activate virtual environment
:EnableVirtualEnvironment
call :WriteStep "Activating virtual environment..."

if exist "venv\Scripts\activate" (
    call "venv\Scripts\activate"
    call :WriteSuccess "Virtual environment activated (Windows)"
) else (
    call :WriteError "Virtual environment activation failed"
    exit /b 1
)

REM Verify activation
if "%VIRTUAL_ENV%"=="%ProjectDir%\venv" (
    call :WriteSuccess "Virtual environment activated successfully: %VIRTUAL_ENV%"
) else (
    call :WriteError "Virtual environment activation failed"
    exit /b 1
)
goto :eof

REM Install Python dependencies
:InstallPythonDependencies
call :WriteStep "Installing Python dependencies..."

REM Upgrade pip
call :WriteInfo "Upgrading pip..."
%PipCmd% install --upgrade pip --no-warn-script-location
if !errorlevel! neq 0 (
    call :WriteWarning "pip upgrade failed, continuing with installation..."
)

REM Install basic packages
call :WriteInfo "Installing basic packages..."
%PipCmd% install wheel setuptools --no-warn-script-location
if !errorlevel! neq 0 (
    call :WriteWarning "Basic packages installation failed, continuing..."
)

REM Install project dependencies
if exist "requirements.txt" (
    call :WriteInfo "Installing project dependencies..."
    %PipCmd% install -r requirements.txt --no-warn-script-location
    if !errorlevel! equ 0 (
        call :WriteSuccess "Project dependencies installation completed"
    ) else (
        call :WriteWarning "Some dependencies installation failed, continuing..."
    )
) else (
    call :WriteError "requirements.txt file not found"
    exit /b 1
)

REM Install Playwright browser
call :WriteInfo "Installing Playwright browser..."
python -m playwright install chromium
if !errorlevel! equ 0 (
    call :WriteSuccess "Playwright browser installation completed"
) else (
    call :WriteWarning "Playwright browser installation failed, continuing..."
)

REM Verify installation
call :WriteInfo "Verifying Python package installation..."
python -c "import sys; import playwright; import requests; import yaml; import pandas; import openpyxl; import pyautogui; import pyperclip; print('✅ All dependency packages verified successfully')"
if !errorlevel! neq 0 (
    call :WriteWarning "Some dependency packages verification failed, but continuing..."
)

call :WriteSuccess "Python environment configuration completed"
goto :eof

REM Create configuration
:NewConfiguration
call :WriteStep "Creating configuration..."

REM Create necessary directories
set "directories=logs data screenshots temp config"
for %%d in (%directories%) do (
    if not exist "%%d" (
        mkdir "%%d" 2>nul
    )
)

REM Create configuration file
if not exist "config\settings.yaml" (
    if exist "config\settings.example.yaml" (
        copy "config\settings.example.yaml" "config\settings.yaml" >nul
        call :WriteSuccess "Configuration file created: config\settings.yaml"
    ) else (
        REM Create basic configuration file
        (
            echo # Carousell Uploader Configuration File
            echo # Please modify the following configuration according to your needs
            echo.
            echo # Browser settings
            echo browser:
            echo   headless: false
            echo   timeout: 30
            echo   retry_count: 3
            echo.
            echo # Logging settings
            echo logging:
            echo   level: INFO
            echo   file: logs/carousell.log
            echo.
            echo # Upload settings
            echo upload:
            echo   delay_between_actions: 2
            echo   max_retries: 3
            echo   screenshot_on_error: true
        ) > "config\settings.yaml"
        call :WriteSuccess "Basic configuration file created: config\settings.yaml"
    )
) else (
    call :WriteWarning "Configuration file already exists: config\settings.yaml"
)
goto :eof

REM Create startup scripts
:NewStartupScripts
call :WriteStep "Creating startup scripts..."

REM Create activation script
(
    echo @echo off
    echo REM Carousell Uploader Virtual Environment Activation Script
    echo.
    echo set "ProjectDir=%%~dp0"
    echo set "VenvDir=%%ProjectDir%%venv"
    echo.
    echo echo 🚀 Activating Carousell Uploader virtual environment...
    echo.
    echo if exist "%%VenvDir%%\Scripts\activate" ^(
    echo     call "%%VenvDir%%\Scripts\activate"
    echo     echo ✅ Virtual environment activated ^(Windows^)
    echo ^) else ^(
    echo     echo ❌ Virtual environment not found: %%VenvDir%%
    echo     echo Please run the installation script first: .\install.bat
    echo     exit /b 1
    echo ^)
    echo.
    echo echo 📁 Project directory: %%ProjectDir%%
    echo echo 🐍 Python path: %%VIRTUAL_ENV%%\Scripts\python.exe
    echo echo.
    echo echo 💡 Usage instructions:
    echo echo   - Run program: python -m cli.main
    echo echo   - Exit environment: deactivate
    echo echo   - View help: python -m cli.main --help
) > "activate_env.bat"

call :WriteSuccess "Activation script created: activate_env.bat"

REM Create quick start script
(
    echo @echo off
    echo REM Carousell Uploader Quick Start Script
    echo.
    echo set "ProjectDir=%%~dp0"
    echo set "VenvDir=%%ProjectDir%%venv"
    echo.
    echo REM Activate virtual environment
    echo if exist "%%VenvDir%%\Scripts\activate" ^(
    echo     call "%%VenvDir%%\Scripts\activate"
    echo ^) else ^(
    echo     echo ❌ Virtual environment not found, please run installation script first
    echo     exit /b 1
    echo ^)
    echo.
    echo echo 🚀 Starting Carousell Uploader...
    echo python -m cli.main %%*
) > "run.bat"

call :WriteSuccess "Startup script created: run.bat"
goto :eof

REM Test installation
:TestInstallation
call :WriteStep "Testing installation..."

python -c "import sys; print('Python version:', sys.version); print('Python path:', sys.executable); import playwright; print('✅ Playwright import successful'); import requests; print('✅ Requests import successful'); import yaml; print('✅ PyYAML import successful'); import pandas; print('✅ Pandas import successful'); print('✅ All tests passed')"
if !errorlevel! neq 0 (
    call :WriteWarning "Some tests failed, but continuing..."
)

call :WriteSuccess "Installation test completed"
goto :eof

REM Show usage instructions
:ShowUsage
echo.
call :WriteSuccess "🎉 Installation completed!"
echo.
call :WriteInfo "📁 Project directory: %ProjectDir%"
call :WriteInfo "🐍 Virtual environment: %ProjectDir%\venv"
call :WriteInfo "⚙️  Configuration file: %ProjectDir%\config\settings.yaml"
echo.
call :WriteInfo "🚀 Quick usage:"
echo.
echo 1. Activate virtual environment:
echo    cd %ProjectDir%
echo    .\activate_env.bat
echo.
echo 2. Or run directly:
echo    cd %ProjectDir%
echo    .\run.bat
echo.
echo 3. Configuration settings:
echo    notepad %ProjectDir%\config\settings.yaml
echo.
call :WriteInfo "📚 More information:"
echo - Project documentation: README.md
echo - Configuration guide: config\settings.example.yaml
echo - Issue reporting: %RepoUrl%/issues
echo.
call :WriteSuccess "Installation completed! Start using Carousell Uploader now!"
goto :eof

REM Main function
:Main
call :WriteHeader

REM Environment check
call :GetSystemInfo
call :TestNetworkConnection
call :InstallSystemDependencies
call :GetPythonEnvironment

REM Project setup
call :SetupProjectDirectory
call :NewVirtualEnvironment
call :EnableVirtualEnvironment
call :InstallPythonDependencies

REM Configuration completion
call :NewConfiguration
call :NewStartupScripts
call :TestInstallation

REM Show usage instructions
call :ShowUsage
goto :eof

REM Run main function
call :Main