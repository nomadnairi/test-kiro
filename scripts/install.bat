@echo off
REM CyberIntel Platform - Automatic Installation Script (Windows CMD)
REM This script automatically installs all dependencies on Windows

echo.
echo ========================================
echo CyberIntel Platform - Installation
echo ========================================
echo.

REM Check Node.js
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js not found
    echo Please install Node.js 20+ from https://nodejs.org/
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo [OK] Node.js %NODE_VERSION% installed

REM Check npm
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] npm not found
    exit /b 1
)
for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i
echo [OK] npm %NPM_VERSION% installed

REM Check Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found
    echo Please install Python 3.11+ from https://www.python.org/
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] %PYTHON_VERSION% installed

REM Check pip
where pip >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] pip not found
    exit /b 1
)
echo [OK] pip installed

REM Check Docker (optional)
where docker >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=*" %%i in ('docker --version') do set DOCKER_VERSION=%%i
    echo [OK] Docker installed
) else (
    echo [INFO] Docker not found (optional, but recommended)
)

echo.
echo Installing dependencies...
echo.

REM Install Node.js dependencies
echo Installing Node.js dependencies...
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install Node.js dependencies
    exit /b 1
)
echo [OK] Node.js dependencies installed

REM Build shared library
echo Building shared library...
cd shared
call npm run build
cd ..
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to build shared library
    exit /b 1
)
echo [OK] Shared library built

REM Install Python dependencies for agents
echo Installing Python dependencies for agents...
cd agents
pip install -r requirements.txt
cd ..
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install agent dependencies
    exit /b 1
)
echo [OK] Agent dependencies installed

REM Install Python dependencies for workers
echo Installing Python dependencies for workers...
cd workers
pip install -r requirements.txt
cd ..
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install worker dependencies
    exit /b 1
)
echo [OK] Worker dependencies installed

echo.
echo Setting up environment...
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo [OK] .env file created
    echo [INFO] Please edit .env and add your API keys
) else (
    echo [INFO] .env file already exists
)

echo.
echo Docker setup...
echo.

where docker >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Pulling Docker images...
    docker-compose pull
    echo [OK] Docker images pulled
) else (
    echo [INFO] Skipping Docker setup (Docker not installed)
)

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file and add your API keys
echo 2. Start infrastructure: docker-compose up -d
echo 3. Start development: npm run dev
echo 4. Access platform: http://localhost:3000
echo.
echo For more information, see START_HERE.md
echo.

pause
