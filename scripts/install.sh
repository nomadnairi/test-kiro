#!/bin/bash

# CyberIntel Platform - Automatic Installation Script
# This script automatically installs all dependencies

set -e  # Exit on error

echo "🚀 CyberIntel Platform - Automatic Installation"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Windows (Git Bash/WSL)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo -e "${YELLOW}⚠️  Detected Windows environment${NC}"
    IS_WINDOWS=true
else
    IS_WINDOWS=false
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print success message
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Function to print error message
print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to print info message
print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check prerequisites
echo "📋 Checking prerequisites..."
echo ""

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION installed"
else
    print_error "Node.js not found"
    echo "Please install Node.js 20+ from https://nodejs.org/"
    exit 1
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    print_success "npm $NPM_VERSION installed"
else
    print_error "npm not found"
    exit 1
fi

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    print_success "$PYTHON_VERSION installed"
elif command_exists python; then
    PYTHON_VERSION=$(python --version)
    print_success "$PYTHON_VERSION installed"
else
    print_error "Python not found"
    echo "Please install Python 3.11+ from https://www.python.org/"
    exit 1
fi

# Check pip
if command_exists pip3; then
    PIP_VERSION=$(pip3 --version)
    print_success "pip installed"
    PIP_CMD="pip3"
elif command_exists pip; then
    PIP_VERSION=$(pip --version)
    print_success "pip installed"
    PIP_CMD="pip"
else
    print_error "pip not found"
    exit 1
fi

# Check Docker
if command_exists docker; then
    DOCKER_VERSION=$(docker --version)
    print_success "$DOCKER_VERSION installed"
else
    print_info "Docker not found (optional, but recommended)"
fi

# Check Docker Compose
if command_exists docker-compose; then
    COMPOSE_VERSION=$(docker-compose --version)
    print_success "$COMPOSE_VERSION installed"
else
    print_info "Docker Compose not found (optional, but recommended)"
fi

echo ""
echo "📦 Installing dependencies..."
echo ""

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install
print_success "Node.js dependencies installed"

# Build shared library
echo "Building shared library..."
cd shared && npm run build && cd ..
print_success "Shared library built"

# Install Python dependencies for agents
echo "Installing Python dependencies for agents..."
cd agents
$PIP_CMD install -r requirements.txt
cd ..
print_success "Agent dependencies installed"

# Install Python dependencies for workers
echo "Installing Python dependencies for workers..."
cd workers
$PIP_CMD install -r requirements.txt
cd ..
print_success "Worker dependencies installed"

echo ""
echo "🔧 Setting up environment..."
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    print_success ".env file created"
    print_info "Please edit .env and add your API keys"
else
    print_info ".env file already exists"
fi

echo ""
echo "🐳 Docker setup..."
echo ""

if command_exists docker; then
    echo "Pulling Docker images..."
    docker-compose pull
    print_success "Docker images pulled"
else
    print_info "Skipping Docker setup (Docker not installed)"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Start infrastructure: docker-compose up -d"
echo "3. Start development: npm run dev"
echo "4. Access platform: http://localhost:3000"
echo ""
echo "For more information, see START_HERE.md"
echo ""
