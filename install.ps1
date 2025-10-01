# =============================================================================
# Carousell Uploader - Windows PowerShell Installation Script
# =============================================================================
# Supported Systems: Windows 10/11
# Version: 2.0.0
# Author: Carousell Uploader Team
# =============================================================================

# Set error handling
$ErrorActionPreference = "Stop"

# =============================================================================
# Global Configuration
# =============================================================================
$ScriptVersion = "2.0.0"
$ProjectName = "Carousell Uploader"
$RepoUrl = "https://github.com/maxliu9403/carousell_upload"
$PythonMinVersion = "3.8"

# Color definitions
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
# Utility Functions
# =============================================================================

function Write-Header {
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor White
    Write-Host "║ 🚀 $ProjectName One-Click Installation Script v$ScriptVersion ║" -ForegroundColor Cyan
    Write-Host "║ Supported Systems: Windows 10/11 ║" -ForegroundColor Cyan
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

# Check if command exists
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

# Get system information
function Get-SystemInfo {
    Write-Step "Detecting system environment..."
    
    $OS = Get-WmiObject -Class Win32_OperatingSystem
    $OSName = $OS.Caption
    $OSVersion = $OS.Version
    
    Write-Success "Detected Windows system"
    Write-Info "Operating System: $OSName"
    Write-Info "Version: $OSVersion"
    
    # Detect architecture
    $Arch = $env:PROCESSOR_ARCHITECTURE
    Write-Info "System Architecture: $Arch"
}

# Check network connection
function Test-NetworkConnection {
    Write-Step "Checking network connection..."
    
    $TestUrls = @(
        "https://pypi.org",
        "https://github.com",
        "https://raw.githubusercontent.com"
    )
    
    foreach ($url in $TestUrls) {
        try {
            $response = Invoke-WebRequest -Uri $url -TimeoutSec 10 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Success "Network connection normal: $url"
                return
            }
        }
        catch {
            continue
        }
    }
    
    Write-Error "Network connection failed, please check network settings"
    Write-Info "Please ensure you can access the following websites:"
    foreach ($url in $TestUrls) {
        Write-Info "  - $url"
    }
    exit 1
}

# Check and install system dependencies
function Install-SystemDependencies {
    Write-Step "Checking system dependencies..."
    
    # Check Python
    if (-not (Test-Command "python") -and -not (Test-Command "python3")) {
        Write-Error "Python not found, please install Python 3.8+ first"
        Write-Info "Installation guide:"
        Write-Info "  1. Visit https://python.org"
        Write-Info "  2. Download Python 3.8+"
        Write-Info "  3. Check 'Add Python to PATH' during installation"
        Write-Info "  4. Avoid using Microsoft Store version"
        Write-Info "  5. Restart PowerShell and run this script again"
        exit 1
    }
    
    # Check Git
    if (-not (Test-Command "git")) {
        Write-Warning "Git not found, recommend installing Git for Windows"
        Write-Info "Download: https://git-scm.com/download/win"
        Write-Info "Restart PowerShell after installation"
    }
    
    # Check curl
    if (-not (Test-Command "curl")) {
        Write-Warning "curl not found, will use PowerShell's Invoke-WebRequest"
    }
    
    Write-Success "System dependencies check completed"
}

# Detect Python environment
function Get-PythonEnvironment {
    Write-Step "Detecting Python environment..."
    
    $PythonCommands = @("python", "python3", "py")
    $FoundPython = $null
    
    foreach ($cmd in $PythonCommands) {
        if (Test-Command $cmd) {
            try {
                $version = & $cmd --version 2>&1
                
                # Check if pointing to Microsoft Store
                if ($version -match "Microsoft Store") {
                    Write-Warning "Skipping Microsoft Store Python: $cmd"
                    continue
                }
                
                # Check if version meets requirements
                $pythonCode = @"
import sys
exit(0 if sys.version_info >= (3, 8) else 1)
"@
                
                try {
                    & $cmd -c $pythonCode
                    if ($LASTEXITCODE -eq 0) {
                        $FoundPython = $cmd
                        Write-Success "Found Python: $cmd (Version: $version)"
                        break
                    } else {
                        Write-Warning "Python version too low: $cmd ($version)"
                    }
                }
                catch {
                    Write-Warning "Python version check failed: $cmd"
                }
            }
            catch {
                Write-Warning "Python command execution failed: $cmd"
            }
        }
    }
    
    if (-not $FoundPython) {
        Write-Error "No suitable Python installation found (requires >=3.8)"
        Write-Info "Installation guide:"
        Write-Info "  1. Visit https://python.org"
        Write-Info "  2. Download Python 3.8+"
        Write-Info "  3. Check 'Add Python to PATH' during installation"
        Write-Info "  4. Restart PowerShell and run this script again"
        exit 1
    }
    
    # Detect pip
    try {
        & $FoundPython -m pip --version | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $script:PythonCmd = $FoundPython
            $script:PipCmd = "$FoundPython -m pip"
            Write-Success "pip available: $PipCmd"
        } else {
            Write-Error "pip not available, please reinstall Python"
            exit 1
        }
    }
    catch {
        Write-Error "pip not available, please reinstall Python"
        exit 1
    }
}

# Create project directory
function Setup-ProjectDirectory {
    Write-Step "Setting up project directory..."
    
    $script:ProjectDir = Get-Location
    Write-Info "Project directory: $ProjectDir"
    
    # Check if project files already exist
    if ((Test-Path "requirements.txt") -or (Test-Path "pyproject.toml")) {
        Write-Success "Project files detected, using current directory"
    } else {
        Write-Info "Current directory does not contain project files, will download project code"
        Download-ProjectCode
    }
}

# Download project code
function Download-ProjectCode {
    Write-Step "Downloading project code..."
    
    # Check Git
    if (Test-Command "git") {
        Write-Info "Using Git to clone project..."
        try {
            git clone "$RepoUrl.git" temp_project
            if ($LASTEXITCODE -eq 0) {
                # Move files to current directory
                Copy-Item -Path "temp_project\*" -Destination "." -Recurse -Force
                Copy-Item -Path "temp_project\.*" -Destination "." -Recurse -Force -ErrorAction SilentlyContinue
                Remove-Item -Path "temp_project" -Recurse -Force
                Write-Success "Project code download completed"
                return
            }
        }
        catch {
            Write-Warning "Git clone failed, trying other methods"
        }
    }
    
    # Use PowerShell download
    Write-Info "Using PowerShell to download project code..."
    Download-WithPowerShell
}

# Use PowerShell to download project code
function Download-WithPowerShell {
    Write-Info "Using PowerShell to download project code..."
    
    # Create temporary directory
    New-Item -ItemType Directory -Path "temp_project" -Force | Out-Null
    Set-Location "temp_project"
    
    # Download main files
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
            Write-Info "Downloaded: $file"
        }
        catch {
            Write-Warning "Download failed: $file"
        }
    }
    
    # Move files to parent directory
    Copy-Item -Path "*" -Destination ".." -Recurse -Force
    Copy-Item -Path ".*" -Destination ".." -Recurse -Force -ErrorAction SilentlyContinue
    Set-Location ".."
    Remove-Item -Path "temp_project" -Recurse -Force
    
    Write-Success "Project code download completed"
}

# Create virtual environment
function New-VirtualEnvironment {
    Write-Step "Creating Python virtual environment..."
    
    # Check if virtual environment already exists
    if (Test-Path "venv") {
        Write-Warning "Virtual environment already exists, will recreate"
        Remove-Item -Path "venv" -Recurse -Force
    }
    
    Write-Info "Creating virtual environment..."
    try {
        & $PythonCmd -m venv venv
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Virtual environment created successfully"
        } else {
            Write-Error "Virtual environment creation failed"
            Write-Info "Troubleshooting:"
            Write-Info "  1. Check Python version: $PythonCmd --version"
            Write-Info "  2. Check disk space"
            Write-Info "  3. Check permissions"
            exit 1
        }
    }
    catch {
        Write-Error "Virtual environment creation failed: $_"
        exit 1
    }
    
    # Verify virtual environment
    if ((Test-Path "venv\Scripts\activate") -or (Test-Path "venv\bin\activate")) {
        Write-Success "Virtual environment verification passed"
    } else {
        Write-Error "Virtual environment creation failed - activation script not found"
        exit 1
    }
}

# Activate virtual environment
function Enable-VirtualEnvironment {
    Write-Step "Activating virtual environment..."
    
    if (Test-Path "venv\Scripts\activate") {
        & "venv\Scripts\activate"
        Write-Success "Virtual environment activated (Windows)"
    } elseif (Test-Path "venv\bin\activate") {
        & "venv\bin\activate"
        Write-Success "Virtual environment activated (WSL)"
    } else {
        Write-Error "Virtual environment activation failed"
        exit 1
    }
    
    # Verify activation
    if ($env:VIRTUAL_ENV -eq "$ProjectDir\venv") {
        Write-Success "Virtual environment activated successfully: $env:VIRTUAL_ENV"
    } else {
        Write-Error "Virtual environment activation failed"
        exit 1
    }
}

# Install Python dependencies
function Install-PythonDependencies {
    Write-Step "Installing Python dependencies..."
    
    # Upgrade pip
    Write-Info "Upgrading pip..."
    & $PipCmd install --upgrade pip
    
    # Install basic packages
    Write-Info "Installing basic packages..."
    & $PipCmd install wheel setuptools
    
    # Install project dependencies
    if (Test-Path "requirements.txt") {
        Write-Info "Installing project dependencies..."
        & $PipCmd install -r requirements.txt
        Write-Success "Project dependencies installation completed"
    } else {
        Write-Error "requirements.txt file not found"
        exit 1
    }
    
    # Install Playwright browser
    Write-Info "Installing Playwright browser..."
    & python -m playwright install chromium
    Write-Success "Playwright browser installation completed"
    
    # Verify installation
    Write-Info "Verifying Python package installation..."
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
    print('✅ All dependency packages verified successfully')
except ImportError as e:
    print(f'❌ Dependency package verification failed: {e}')
    sys.exit(1)
"@
    
    & python -c $pythonCode
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Dependency package verification failed"
        exit 1
    }
    
    Write-Success "Python environment configuration completed"
}

# Create configuration
function New-Configuration {
    Write-Step "Creating configuration..."
    
    # Create necessary directories
    $directories = @("logs", "data", "screenshots", "temp", "config")
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    # Create configuration file
    if (-not (Test-Path "config\settings.yaml")) {
        if (Test-Path "config\settings.example.yaml") {
            Copy-Item "config\settings.example.yaml" "config\settings.yaml"
            Write-Success "Configuration file created: config\settings.yaml"
        } else {
            # Create basic configuration file
            $configContent = @"
# Carousell Uploader Configuration File
# Please modify the following configuration according to your needs

# Browser settings
browser:
  headless: false
  timeout: 30
  retry_count: 3

# Logging settings
logging:
  level: INFO
  file: logs/carousell.log

# Upload settings
upload:
  delay_between_actions: 2
  max_retries: 3
  screenshot_on_error: true
"@
            $configContent | Out-File -FilePath "config\settings.yaml" -Encoding UTF8
            Write-Success "Basic configuration file created: config\settings.yaml"
        }
    } else {
        Write-Warning "Configuration file already exists: config\settings.yaml"
    }
}

# Create startup scripts
function New-StartupScripts {
    Write-Step "Creating startup scripts..."
    
    # Create activation script
    $activateScript = @"
# Carousell Uploader Virtual Environment Activation Script

`$ProjectDir = Split-Path -Parent `$MyInvocation.MyCommand.Path
`$VenvDir = "`$ProjectDir\venv"

Write-Host "🚀 Activating Carousell Uploader virtual environment..." -ForegroundColor Cyan

if (Test-Path "`$VenvDir\Scripts\activate") {
    & "`$VenvDir\Scripts\activate"
    Write-Host "✅ Virtual environment activated (Windows)" -ForegroundColor Green
} elseif (Test-Path "`$VenvDir\bin\activate") {
    & "`$VenvDir\bin\activate"
    Write-Host "✅ Virtual environment activated (WSL)" -ForegroundColor Green
} else {
    Write-Host "❌ Virtual environment not found: `$VenvDir" -ForegroundColor Red
    Write-Host "Please run the installation script first: .\install.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "📁 Project directory: `$ProjectDir" -ForegroundColor Blue
Write-Host "🐍 Python path: `$(Get-Command python).Source" -ForegroundColor Blue
Write-Host ""
Write-Host "💡 Usage instructions:" -ForegroundColor Cyan
Write-Host "  - Run program: python -m cli.main" -ForegroundColor White
Write-Host "  - Exit environment: deactivate" -ForegroundColor White
Write-Host "  - View help: python -m cli.main --help" -ForegroundColor White
"@
    
    $activateScript | Out-File -FilePath "activate_env.ps1" -Encoding UTF8
    Write-Success "Activation script created: activate_env.ps1"
    
    # Create quick start script
    $runScript = @"
# Carousell Uploader Quick Start Script

`$ProjectDir = Split-Path -Parent `$MyInvocation.MyCommand.Path
`$VenvDir = "`$ProjectDir\venv"

# Activate virtual environment
if (Test-Path "`$VenvDir\Scripts\activate") {
    & "`$VenvDir\Scripts\activate"
} elseif (Test-Path "`$VenvDir\bin\activate") {
    & "`$VenvDir\bin\activate"
} else {
    Write-Host "❌ Virtual environment not found, please run installation script first" -ForegroundColor Red
    exit 1
}

Write-Host "🚀 Starting Carousell Uploader..." -ForegroundColor Cyan
& python -m cli.main @args
"@
    
    $runScript | Out-File -FilePath "run.ps1" -Encoding UTF8
    Write-Success "Startup script created: run.ps1"
}

# Test installation
function Test-Installation {
    Write-Step "Testing installation..."
    
    # Test Python imports
    $pythonCode = @"
import sys
print('Python version:', sys.version)
print('Python path:', sys.executable)

try:
    import playwright
    print('✅ Playwright import successful')
except ImportError as e:
    print(f'❌ Playwright import failed: {e}')
    sys.exit(1)

try:
    import requests
    print('✅ Requests import successful')
except ImportError as e:
    print(f'❌ Requests import failed: {e}')
    sys.exit(1)

try:
    import yaml
    print('✅ PyYAML import successful')
except ImportError as e:
    print(f'❌ PyYAML import failed: {e}')
    sys.exit(1)

try:
    import pandas
    print('✅ Pandas import successful')
except ImportError as e:
    print(f'❌ Pandas import failed: {e}')
    sys.exit(1)

print('✅ All tests passed')
"@
    
    & python -c $pythonCode
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Installation test failed"
        exit 1
    }
    
    Write-Success "Installation test passed"
}

# Show usage instructions
function Show-Usage {
    Write-Host ""
    Write-Success "🎉 Installation completed!"
    Write-Host ""
    Write-Info "📁 Project directory: $ProjectDir"
    Write-Info "🐍 Virtual environment: $ProjectDir\venv"
    Write-Info "⚙️  Configuration file: $ProjectDir\config\settings.yaml"
    Write-Host ""
    
    Write-Info "🚀 Quick usage:"
    Write-Host ""
    Write-Host "1. Activate virtual environment:"
    Write-Host "   cd $ProjectDir"
    Write-Host "   .\activate_env.ps1"
    Write-Host ""
    Write-Host "2. Or run directly:"
    Write-Host "   cd $ProjectDir"
    Write-Host "   .\run.ps1"
    Write-Host ""
    Write-Host "3. Configuration settings:"
    Write-Host "   notepad $ProjectDir\config\settings.yaml"
    Write-Host ""
    
    Write-Info "📚 More information:"
    Write-Host "- Project documentation: README.md"
    Write-Host "- Configuration guide: config\settings.example.yaml"
    Write-Host "- Issue reporting: $RepoUrl/issues"
    Write-Host ""
    Write-Success "Installation completed! Start using Carousell Uploader now!"
}

# Main function
function Main {
    Write-Header
    
    # Environment check
    Get-SystemInfo
    Test-NetworkConnection
    Install-SystemDependencies
    Get-PythonEnvironment
    
    # Project setup
    Setup-ProjectDirectory
    New-VirtualEnvironment
    Enable-VirtualEnvironment
    Install-PythonDependencies
    
    # Configuration completion
    New-Configuration
    New-StartupScripts
    Test-Installation
    
    # Show usage instructions
    Show-Usage
}

# Error handling
trap {
    Write-Error "Error occurred during installation, please check the above output information"
    exit 1
}

# Run main function
Main