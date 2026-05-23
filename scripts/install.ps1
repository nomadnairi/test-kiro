# CyberIntel Platform - Automatic Installation Script (PowerShell)
# This script automatically installs all dependencies on Windows

$ErrorActionPreference = "Stop"

Write-Host "🚀 CyberIntel Platform - Automatic Installation" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if command exists
function Test-CommandExists {
    param($command)
    $null -ne (Get-Command $command -ErrorAction SilentlyContinue)
}

# Function to print success message
function Write-Success {
    param($message)
    Write-Host "✓ $message" -ForegroundColor Green
}

# Function to print error message
function Write-Error-Custom {
    param($message)
    Write-Host "✗ $message" -ForegroundColor Red
}

# Function to print info message
function Write-Info {
    param($message)
    Write-Host "ℹ $message" -ForegroundColor Yellow
}

# Check prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Cyan
Write-Host ""

# Check Node.js
if (Test-CommandExists node) {
    $nodeVersion = node --version
    Write-Success "Node.js $nodeVersion installed"
} else {
    Write-Error-Custom "Node.js not found"
    Write-Host "Please install Node.js 20+ from https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Check npm
if (Test-CommandExists npm) {
    $npmVersion = npm --version
    Write-Success "npm $npmVersion installed"
} else {
    Write-Error-Custom "npm not found"
    exit 1
}

# Check Python
if (Test-CommandExists python) {
    $pythonVersion = python --version
    Write-Success "$pythonVersion installed"
} elseif (Test-CommandExists python3) {
    $pythonVersion = python3 --version
    Write-Success "$pythonVersion installed"
} else {
    Write-Error-Custom "Python not found"
    Write-Host "Please install Python 3.11+ from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

# Check pip
if (Test-CommandExists pip) {
    $pipVersion = pip --version
    Write-Success "pip installed"
    $pipCmd = "pip"
} elseif (Test-CommandExists pip3) {
    $pipVersion = pip3 --version
    Write-Success "pip installed"
    $pipCmd = "pip3"
} else {
    Write-Error-Custom "pip not found"
    exit 1
}

# Check Docker
if (Test-CommandExists docker) {
    $dockerVersion = docker --version
    Write-Success "$dockerVersion installed"
} else {
    Write-Info "Docker not found (optional, but recommended)"
}

# Check Docker Compose
if (Test-CommandExists docker-compose) {
    $composeVersion = docker-compose --version
    Write-Success "$composeVersion installed"
} else {
    Write-Info "Docker Compose not found (optional, but recommended)"
}

Write-Host ""
Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
Write-Host ""

# Install Node.js dependencies
Write-Host "Installing Node.js dependencies..."
npm install
Write-Success "Node.js dependencies installed"

# Build shared library
Write-Host "Building shared library..."
Push-Location shared
npm run build
Pop-Location
Write-Success "Shared library built"

# Install Python dependencies for agents
Write-Host "Installing Python dependencies for agents..."
Push-Location agents
& $pipCmd install -r requirements.txt
Pop-Location
Write-Success "Agent dependencies installed"

# Install Python dependencies for workers
Write-Host "Installing Python dependencies for workers..."
Push-Location workers
& $pipCmd install -r requirements.txt
Pop-Location
Write-Success "Worker dependencies installed"

Write-Host ""
Write-Host "🔧 Setting up environment..." -ForegroundColor Cyan
Write-Host ""

# Create .env file if it doesn't exist
if (-not (Test-Path .env)) {
    Write-Host "Creating .env file..."
    Copy-Item .env.example .env
    Write-Success ".env file created"
    Write-Info "Please edit .env and add your API keys"
} else {
    Write-Info ".env file already exists"
}

Write-Host ""
Write-Host "🐳 Docker setup..." -ForegroundColor Cyan
Write-Host ""

if (Test-CommandExists docker) {
    Write-Host "Pulling Docker images..."
    docker-compose pull
    Write-Success "Docker images pulled"
} else {
    Write-Info "Skipping Docker setup (Docker not installed)"
}

Write-Host ""
Write-Host "✅ Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Edit .env file and add your API keys"
Write-Host "2. Start infrastructure: docker-compose up -d"
Write-Host "3. Start development: npm run dev"
Write-Host "4. Access platform: http://localhost:3000"
Write-Host ""
Write-Host "For more information, see START_HERE.md"
Write-Host ""
