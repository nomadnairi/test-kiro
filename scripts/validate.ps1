# ============================================================================
# CyberIntel Platform - Deployment Validation Script
# ============================================================================
# This script validates that all prerequisites and configurations are correct
# before launching the platform.
#
# Usage: .\scripts\validate.ps1
# ============================================================================

param(
    [switch]$Verbose = $false,
    [switch]$SkipDocker = $false,
    [switch]$SkipNode = $false,
    [switch]$SkipPython = $false
)

# Color output
function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Magenta
    Write-Host "  $Message" -ForegroundColor Magenta
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Magenta
}

# Initialize counters
$passed = 0
$failed = 0
$warnings = 0

# ============================================================================
# 1. Check Node.js
# ============================================================================
Write-Header "1. Checking Node.js Installation"

if (-not $SkipNode) {
    try {
        $nodeVersion = node --version 2>$null
        if ($nodeVersion) {
            $nodeMajor = [int]($nodeVersion -replace 'v(\d+)\..*', '$1')
            if ($nodeMajor -ge 20) {
                Write-Success "Node.js $nodeVersion installed"
                $passed++
            } else {
                Write-Error "Node.js version $nodeVersion is too old (need v20+)"
                $failed++
            }
        } else {
            Write-Error "Node.js not found"
            $failed++
        }
    } catch {
        Write-Error "Failed to check Node.js: $_"
        $failed++
    }
} else {
    Write-Info "Skipping Node.js check"
}

# ============================================================================
# 2. Check npm
# ============================================================================
Write-Header "2. Checking npm Installation"

if (-not $SkipNode) {
    try {
        $npmVersion = npm --version 2>$null
        if ($npmVersion) {
            $npmMajor = [int]($npmVersion -split '\.')[0]
            if ($npmMajor -ge 10) {
                Write-Success "npm $npmVersion installed"
                $passed++
            } else {
                Write-Error "npm version $npmVersion is too old (need v10+)"
                $failed++
            }
        } else {
            Write-Error "npm not found"
            $failed++
        }
    } catch {
        Write-Error "Failed to check npm: $_"
        $failed++
    }
} else {
    Write-Info "Skipping npm check"
}

# ============================================================================
# 3. Check Python
# ============================================================================
Write-Header "3. Checking Python Installation"

if (-not $SkipPython) {
    try {
        $pythonVersion = python --version 2>$null
        if ($pythonVersion) {
            $pythonMajor = [int]($pythonVersion -replace 'Python (\d+)\..*', '$1')
            $pythonMinor = [int]($pythonVersion -replace 'Python \d+\.(\d+)\..*', '$1')
            if ($pythonMajor -ge 3 -and $pythonMinor -ge 11) {
                Write-Success "Python $pythonVersion installed"
                $passed++
            } else {
                Write-Warning "Python version $pythonVersion is older than recommended (need v3.11+)"
                $warnings++
            }
        } else {
            Write-Warning "Python not found (optional for Node.js-only setup)"
            $warnings++
        }
    } catch {
        Write-Warning "Failed to check Python: $_"
        $warnings++
    }
} else {
    Write-Info "Skipping Python check"
}

# ============================================================================
# 4. Check Docker
# ============================================================================
Write-Header "4. Checking Docker Installation"

if (-not $SkipDocker) {
    try {
        $dockerVersion = docker --version 2>$null
        if ($dockerVersion) {
            Write-Success "Docker installed: $dockerVersion"
            $passed++
        } else {
            Write-Error "Docker not found"
            $failed++
        }
    } catch {
        Write-Error "Failed to check Docker: $_"
        $failed++
    }

    # Check Docker daemon
    try {
        $dockerPs = docker ps 2>$null
        if ($?) {
            Write-Success "Docker daemon is running"
            $passed++
        } else {
            Write-Error "Docker daemon is not running"
            $failed++
        }
    } catch {
        Write-Error "Failed to connect to Docker daemon: $_"
        $failed++
    }

    # Check Docker Compose
    try {
        $composeVersion = docker compose version 2>$null
        if ($composeVersion) {
            Write-Success "Docker Compose installed: $composeVersion"
            $passed++
        } else {
            Write-Error "Docker Compose not found"
            $failed++
        }
    } catch {
        Write-Error "Failed to check Docker Compose: $_"
        $failed++
    }
} else {
    Write-Info "Skipping Docker check"
}

# ============================================================================
# 5. Check Git
# ============================================================================
Write-Header "5. Checking Git Installation"

try {
    $gitVersion = git --version 2>$null
    if ($gitVersion) {
        Write-Success "Git installed: $gitVersion"
        $passed++
    } else {
        Write-Error "Git not found"
        $failed++
    }
} catch {
    Write-Error "Failed to check Git: $_"
    $failed++
}

# ============================================================================
# 6. Check Repository Structure
# ============================================================================
Write-Header "6. Checking Repository Structure"

$requiredDirs = @(
    "frontend",
    "backend",
    "gateway",
    "orchestrator",
    "agents",
    "workers",
    "integrations",
    "graph-engine",
    "ai-router",
    "telegram-bot",
    "shared",
    "docs",
    ".github/workflows"
)

foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Write-Success "Directory exists: $dir"
        $passed++
    } else {
        Write-Error "Directory missing: $dir"
        $failed++
    }
}

# ============================================================================
# 7. Check Configuration Files
# ============================================================================
Write-Header "7. Checking Configuration Files"

$requiredFiles = @(
    "package.json",
    "docker-compose.yml",
    ".env.example",
    ".gitignore",
    "README.md",
    "START_HERE.md"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Success "File exists: $file"
        $passed++
    } else {
        Write-Error "File missing: $file"
        $failed++
    }
}

# ============================================================================
# 8. Check .env Configuration
# ============================================================================
Write-Header "8. Checking .env Configuration"

if (Test-Path ".env") {
    Write-Success ".env file exists"
    $passed++
    
    # Check for required keys
    $envContent = Get-Content ".env" -Raw
    $requiredKeys = @(
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "JWT_SECRET"
    )
    
    foreach ($key in $requiredKeys) {
        if ($envContent -match $key) {
            Write-Success ".env contains $key"
            $passed++
        } else {
            Write-Warning ".env missing $key (optional)"
            $warnings++
        }
    }
} else {
    Write-Warning ".env file not found (copy from .env.example)"
    $warnings++
}

# ============================================================================
# 9. Check npm Workspaces
# ============================================================================
Write-Header "9. Checking npm Workspaces Configuration"

if (Test-Path "package.json") {
    try {
        $packageJson = Get-Content "package.json" | ConvertFrom-Json
        if ($packageJson.workspaces) {
            Write-Success "npm workspaces configured"
            $passed++
            
            foreach ($workspace in $packageJson.workspaces) {
                if (Test-Path $workspace) {
                    Write-Success "Workspace exists: $workspace"
                    $passed++
                } else {
                    Write-Error "Workspace missing: $workspace"
                    $failed++
                }
            }
        } else {
            Write-Error "npm workspaces not configured in package.json"
            $failed++
        }
    } catch {
        Write-Error "Failed to parse package.json: $_"
        $failed++
    }
}

# ============================================================================
# 10. Check Docker Compose Configuration
# ============================================================================
Write-Header "10. Checking Docker Compose Configuration"

if (-not $SkipDocker) {
    if (Test-Path "docker-compose.yml") {
        try {
            $composeCheck = docker compose config 2>&1
            if ($?) {
                Write-Success "docker-compose.yml is valid"
                $passed++
            } else {
                Write-Error "docker-compose.yml validation failed: $composeCheck"
                $failed++
            }
        } catch {
            Write-Error "Failed to validate docker-compose.yml: $_"
            $failed++
        }
    } else {
        Write-Error "docker-compose.yml not found"
        $failed++
    }
}

# ============================================================================
# 11. Check GitHub Actions Workflows
# ============================================================================
Write-Header "11. Checking GitHub Actions Workflows"

$workflows = @(
    ".github/workflows/ci.yml",
    ".github/workflows/docker.yml",
    ".github/workflows/code-quality.yml",
    ".github/workflows/pages.yml"
)

foreach ($workflow in $workflows) {
    if (Test-Path $workflow) {
        Write-Success "Workflow exists: $workflow"
        $passed++
    } else {
        Write-Warning "Workflow missing: $workflow"
        $warnings++
    }
}

# ============================================================================
# 12. Check Installation Scripts
# ============================================================================
Write-Header "12. Checking Installation Scripts"

$scripts = @(
    "scripts/install.ps1",
    "scripts/install.sh",
    "scripts/install.bat"
)

foreach ($script in $scripts) {
    if (Test-Path $script) {
        Write-Success "Script exists: $script"
        $passed++
    } else {
        Write-Warning "Script missing: $script"
        $warnings++
    }
}

# ============================================================================
# 13. Check Documentation
# ============================================================================
Write-Header "13. Checking Documentation"

$docs = @(
    "docs/ARCHITECTURE.md",
    "docs/API.md",
    "docs/AGENTS.md",
    "docs/INTEGRATIONS.md",
    "docs/DEPLOYMENT.md",
    "docs/SECURITY.md",
    "CONTRIBUTING.md",
    "COMMANDS.md"
)

foreach ($doc in $docs) {
    if (Test-Path $doc) {
        Write-Success "Documentation exists: $doc"
        $passed++
    } else {
        Write-Warning "Documentation missing: $doc"
        $warnings++
    }
}

# ============================================================================
# Summary
# ============================================================================
Write-Header "Validation Summary"

$total = $passed + $failed + $warnings
Write-Info "Total checks: $total"
Write-Success "Passed: $passed"
if ($failed -gt 0) {
    Write-Error "Failed: $failed"
}
if ($warnings -gt 0) {
    Write-Warning "Warnings: $warnings"
}

Write-Host ""

if ($failed -eq 0) {
    Write-Success "✅ All critical checks passed!"
    Write-Info "Your platform is ready to launch."
    Write-Host ""
    Write-Info "Next steps:"
    Write-Info "1. Configure .env with your API keys"
    Write-Info "2. Run: docker-compose up -d"
    Write-Info "3. Run: npm install"
    Write-Info "4. Run: npm run dev"
    Write-Info "5. Open: http://localhost:3000"
    exit 0
} else {
    Write-Error "❌ Some critical checks failed!"
    Write-Info "Please fix the issues above before launching."
    exit 1
}
