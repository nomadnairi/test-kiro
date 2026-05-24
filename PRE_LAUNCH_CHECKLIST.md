# 🚀 Pre-Launch Checklist - CyberIntel Platform

**Status**: Ready for Launch  
**Date**: May 24, 2026  
**Version**: 1.0.0

---

## 📋 Prerequisites Installation

### Windows Setup

#### Step 1: Install Node.js
- [ ] Download Node.js v20+ from https://nodejs.org/
- [ ] Run installer and follow prompts
- [ ] Verify installation:
  ```powershell
  node --version  # Should show v20.x.x
  npm --version   # Should show 10.x.x
  ```

#### Step 2: Install Python
- [ ] Download Python 3.11+ from https://www.python.org/
- [ ] Run installer
- [ ] **IMPORTANT**: Check "Add Python to PATH"
- [ ] Verify installation:
  ```powershell
  python --version  # Should show 3.11.x or higher
  ```

#### Step 3: Install Docker Desktop
- [ ] Download Docker Desktop from https://www.docker.com/products/docker-desktop
- [ ] Run installer and follow prompts
- [ ] Restart computer if prompted
- [ ] Verify installation:
  ```powershell
  docker --version        # Should show Docker version
  docker compose version  # Should show Compose version
  ```

#### Step 4: Install Git
- [ ] Download Git from https://git-scm.com/
- [ ] Run installer with default settings
- [ ] Verify installation:
  ```powershell
  git --version  # Should show git version
  ```

### Verification Script
- [ ] Run validation script:
  ```powershell
  .\scripts\validate.ps1
  ```
- [ ] All checks should pass (green ✅)
- [ ] Fix any failed checks (red ❌)

---

## 🔧 Repository Setup

### Step 1: Clone Repository
- [ ] Open PowerShell or Command Prompt
- [ ] Navigate to desired directory
- [ ] Clone repository:
  ```powershell
  git clone https://github.com/YOUR_USERNAME/cyberintel-platform.git
  cd cyberintel-platform
  ```

### Step 2: Install Dependencies
- [ ] Run installation script:
  ```powershell
  .\scripts\install.ps1
  ```
- [ ] Or manually install:
  ```powershell
  npm install
  npm run build:shared
  pip install -r agents/requirements.txt
  pip install -r workers/requirements.txt
  ```

### Step 3: Configure Environment
- [ ] Copy example environment file:
  ```powershell
  Copy-Item .env.example .env
  ```
- [ ] Edit `.env` file with your settings:
  ```bash
  # Required API Keys
  ANTHROPIC_API_KEY=your_key_here
  OPENAI_API_KEY=your_key_here
  
  # Optional API Keys
  VIRUSTOTAL_API_KEY=your_key_here
  SHODAN_API_KEY=your_key_here
  SECURITYTRAILS_API_KEY=your_key_here
  
  # JWT Secret (generate with: node -e "console.log(require('crypto').randomBytes(32).toString('hex'))")
  JWT_SECRET=your_generated_secret_here
  
  # Telegram (optional)
  TELEGRAM_BOT_TOKEN=your_token_here
  ```

---

## 🐳 Docker Configuration

### Step 1: Verify Docker Setup
- [ ] Docker Desktop is running
- [ ] Check Docker status:
  ```powershell
  docker ps  # Should show running containers (or empty list)
  ```

### Step 2: Validate Docker Compose
- [ ] Validate configuration:
  ```powershell
  docker compose config
  ```
- [ ] Should output valid YAML without errors

### Step 3: Choose Deployment Mode

#### Option A: Lightweight VPS Mode (Recommended for Testing)
- [ ] Current configuration is already in lightweight mode
- [ ] Services: Frontend, Backend, Gateway, PostgreSQL, Neo4j, Redis
- [ ] Resources: 2 vCPU, 4 GB RAM
- [ ] Start services:
  ```powershell
  docker-compose up -d
  ```

#### Option B: Full Mode (Advanced)
- [ ] Edit `docker-compose.yml`
- [ ] Uncomment Elasticsearch section
- [ ] Uncomment Ollama section
- [ ] Update Backend to include Elasticsearch
- [ ] Update AI Router to include Ollama
- [ ] Resources needed: 8+ vCPU, 16+ GB RAM
- [ ] Start services:
  ```powershell
  docker-compose up -d
  ```

### Step 4: Wait for Services to Start
- [ ] Wait 30-60 seconds for all services to initialize
- [ ] Check service health:
  ```powershell
  docker-compose ps
  ```
- [ ] All services should show "healthy" or "running"

---

## ✅ Service Verification

### Step 1: Check Database Connectivity

#### PostgreSQL
- [ ] Test connection:
  ```powershell
  docker-compose exec postgres psql -U cyberintel -d cyberintel -c "SELECT 1"
  ```
- [ ] Should return: `1`

#### Neo4j
- [ ] Test connection:
  ```powershell
  docker-compose exec neo4j cypher-shell -u neo4j -p cyberintel "RETURN 1"
  ```
- [ ] Should return: `1`

#### Redis
- [ ] Test connection:
  ```powershell
  docker-compose exec redis redis-cli ping
  ```
- [ ] Should return: `PONG`

### Step 2: Check Service Logs
- [ ] View all logs:
  ```powershell
  docker-compose logs -f
  ```
- [ ] Look for errors (red text)
- [ ] Services should show "listening on port X"

### Step 3: Start Development Services
- [ ] Open new PowerShell window
- [ ] Start all services:
  ```powershell
  npm run dev
  ```
- [ ] Or start individual services in separate terminals:
  ```powershell
  # Terminal 1
  npm run dev:frontend
  
  # Terminal 2
  npm run dev:backend
  
  # Terminal 3
  npm run dev:gateway
  
  # Terminal 4
  npm run dev:orchestrator
  ```

---

## 🌐 Web Interface Access

### Step 1: Access Frontend
- [ ] Open browser and navigate to: http://localhost:3000
- [ ] Should see CyberIntel Platform login page
- [ ] Check browser console for errors (F12)

### Step 2: Access API Gateway
- [ ] Test API health:
  ```powershell
  curl http://localhost:8000/health
  ```
- [ ] Should return JSON with status "ok"

### Step 3: Access Neo4j Browser
- [ ] Open browser and navigate to: http://localhost:7474
- [ ] Login with:
  - Username: `neo4j`
  - Password: `cyberintel`
- [ ] Should see Neo4j browser interface

### Step 4: Access Documentation
- [ ] Open `docs/index.html` in browser
- [ ] Should see beautiful documentation site
- [ ] All links should work

---

## 👤 User Account Setup

### Step 1: Create Test Account
- [ ] Go to http://localhost:3000
- [ ] Click "Sign Up" or "Register"
- [ ] Fill in registration form:
  - Email: `test@example.com`
  - Password: `TestPassword123!`
  - Name: `Test User`
- [ ] Click "Register"
- [ ] Should see success message

### Step 2: Login
- [ ] Use credentials from Step 1
- [ ] Should see dashboard
- [ ] Should see navigation menu

### Step 3: Verify Dashboard
- [ ] Dashboard should load without errors
- [ ] Should see widgets/cards
- [ ] Should see navigation options

---

## 🔍 First Scan Test

### Step 1: Create Scan via Web UI
- [ ] Click "New Scan" or similar button
- [ ] Enter target: `example.com`
- [ ] Select scan type: `Domain`
- [ ] Select depth: `Standard`
- [ ] Click "Start Scan"
- [ ] Should see scan in progress

### Step 2: Monitor Scan Progress
- [ ] Watch scan progress bar
- [ ] Should see status updates
- [ ] Should complete within 2-5 minutes

### Step 3: View Results
- [ ] Click on completed scan
- [ ] Should see discovered entities
- [ ] Should see relationships in graph
- [ ] Should see IOCs and vulnerabilities

### Step 4: Test API Directly (Optional)
- [ ] Create scan via API:
  ```powershell
  $headers = @{
    "Content-Type" = "application/json"
  }
  
  $body = @{
    target = "example.com"
    type = "domain"
    depth = "standard"
  } | ConvertTo-Json
  
  curl -X POST http://localhost:8000/api/scans `
    -Headers $headers `
    -Body $body
  ```
- [ ] Should return scan ID

---

## 🧪 Code Quality Checks

### Step 1: Run Linting
- [ ] Run ESLint:
  ```powershell
  npm run lint
  ```
- [ ] Should show no errors (warnings are OK)

### Step 2: Run Type Checking
- [ ] Run TypeScript check:
  ```powershell
  npm run typecheck
  ```
- [ ] Should show no errors

### Step 3: Run Tests
- [ ] Run test suite:
  ```powershell
  npm run test
  ```
- [ ] Should show test results
- [ ] Most tests may be skipped (OK for now)

### Step 4: Run All Checks
- [ ] Run comprehensive check:
  ```powershell
  npm run check
  ```
- [ ] Should complete without critical errors

---

## 🐳 Docker Validation

### Step 1: Validate Compose File
- [ ] Validate configuration:
  ```powershell
  docker compose config > $null
  ```
- [ ] Should complete without errors

### Step 2: Check Service Health
- [ ] View service status:
  ```powershell
  docker compose ps
  ```
- [ ] All services should show "healthy" or "running"

### Step 3: View Service Logs
- [ ] View specific service logs:
  ```powershell
  docker compose logs postgres
  docker compose logs neo4j
  docker compose logs redis
  ```
- [ ] Should show startup messages
- [ ] Should not show critical errors

### Step 4: Test Service Restart
- [ ] Restart a service:
  ```powershell
  docker compose restart gateway
  ```
- [ ] Service should restart and become healthy
- [ ] Should take ~10 seconds

---

## 📊 GitHub Actions Validation

### Step 1: Check Workflow Files
- [ ] Verify workflow files exist:
  - [ ] `.github/workflows/ci.yml`
  - [ ] `.github/workflows/docker.yml`
  - [ ] `.github/workflows/code-quality.yml`
  - [ ] `.github/workflows/pages.yml`

### Step 2: Validate YAML Syntax
- [ ] Each workflow file should be valid YAML
- [ ] No syntax errors

### Step 3: Check Workflow Configuration
- [ ] CI workflow should:
  - [ ] Run on push to main/develop
  - [ ] Run on pull requests
  - [ ] Have setup, lint, typecheck, test, build jobs
  - [ ] Have Python services validation
  - [ ] Have Docker build validation

### Step 4: Verify npm Workspace Commands
- [ ] Check that workflows use:
  - [ ] `npm ci --workspaces --if-present`
  - [ ] `npm run build --workspace=shared`
  - [ ] `npm run lint --workspaces --if-present`
  - [ ] `npm run test --workspaces --if-present`

---

## 🔐 Security Verification

### Step 1: Check Secrets
- [ ] Verify `.env` is in `.gitignore`
- [ ] Verify no secrets in code:
  ```powershell
  git grep -i "password\|secret\|key" -- "*.ts" "*.js" | grep -v "node_modules"
  ```
- [ ] Should return no results (or only comments)

### Step 2: Check Dependencies
- [ ] Run security audit:
  ```powershell
  npm audit
  ```
- [ ] Review any vulnerabilities
- [ ] Fix critical issues if found

### Step 3: Verify Input Validation
- [ ] Check that API routes validate input
- [ ] Test with invalid data:
  ```powershell
  curl -X POST http://localhost:8000/api/scans `
    -H "Content-Type: application/json" `
    -d '{"invalid": "data"}'
  ```
- [ ] Should return validation error

### Step 4: Verify Error Handling
- [ ] Test with invalid endpoint:
  ```powershell
  curl http://localhost:8000/api/invalid
  ```
- [ ] Should return 404 error
- [ ] Should not expose stack trace

---

## 📚 Documentation Review

### Step 1: Check Main Documentation
- [ ] Review `README.md`
- [ ] Review `START_HERE.md`
- [ ] Review `COMMANDS.md`

### Step 2: Check Architecture Documentation
- [ ] Review `docs/ARCHITECTURE.md`
- [ ] Review `docs/AGENTS.md`
- [ ] Review `docs/INTEGRATIONS.md`

### Step 3: Check Operational Documentation
- [ ] Review `docs/DEPLOYMENT.md`
- [ ] Review `docs/TROUBLESHOOTING.md`
- [ ] Review `docs/SECURITY.md`

### Step 4: Check Configuration Documentation
- [ ] Review `LIGHTWEIGHT_MODE.md`
- [ ] Review `.env.example`
- [ ] Review `docker-compose.yml` comments

---

## 🎯 Final Verification

### Step 1: System Health Check
- [ ] All services running: `docker-compose ps`
- [ ] All services healthy: All show "healthy" or "running"
- [ ] No critical errors in logs: `docker-compose logs`

### Step 2: Functionality Check
- [ ] Frontend loads: http://localhost:3000
- [ ] API responds: http://localhost:8000/health
- [ ] Database connected: Can query PostgreSQL
- [ ] Graph database connected: Can query Neo4j
- [ ] Cache working: Can ping Redis

### Step 3: User Experience Check
- [ ] Can create account
- [ ] Can login
- [ ] Can create scan
- [ ] Can view results
- [ ] Can access documentation

### Step 4: Code Quality Check
- [ ] Linting passes: `npm run lint`
- [ ] Type checking passes: `npm run typecheck`
- [ ] Tests pass: `npm run test`
- [ ] No security issues: `npm audit`

---

## 🚀 Launch Readiness

### Final Checklist
- [ ] All prerequisites installed
- [ ] Repository cloned and configured
- [ ] .env file created with API keys
- [ ] Docker services running and healthy
- [ ] All services accessible
- [ ] Test account created
- [ ] First scan completed
- [ ] Code quality checks pass
- [ ] GitHub Actions configured
- [ ] Documentation reviewed
- [ ] Security verified
- [ ] No critical errors in logs

### Go/No-Go Decision
- [ ] **GO**: All items checked ✅ → Ready to launch
- [ ] **NO-GO**: Some items unchecked ❌ → Fix issues before launch

---

## 📞 Troubleshooting

### If Services Won't Start
1. Check Docker is running: `docker ps`
2. Check logs: `docker-compose logs`
3. Restart services: `docker-compose restart`
4. Full reset: `docker-compose down -v && docker-compose up -d`

### If Frontend Won't Load
1. Check frontend service: `docker-compose logs frontend`
2. Check port 3000 is available: `netstat -ano | findstr :3000`
3. Restart frontend: `docker-compose restart frontend`

### If API Won't Respond
1. Check gateway service: `docker-compose logs gateway`
2. Check database connection: `docker-compose logs backend`
3. Restart gateway: `docker-compose restart gateway`

### If Database Won't Connect
1. Check PostgreSQL: `docker-compose logs postgres`
2. Check Neo4j: `docker-compose logs neo4j`
3. Verify credentials in .env
4. Restart databases: `docker-compose restart postgres neo4j`

---

## ✅ Success Criteria

Your platform is ready when:

1. ✅ All prerequisites installed
2. ✅ Repository cloned and dependencies installed
3. ✅ .env configured with API keys
4. ✅ Docker services running and healthy
5. ✅ Frontend accessible at http://localhost:3000
6. ✅ API Gateway responding at http://localhost:8000
7. ✅ Database connections working
8. ✅ User account created successfully
9. ✅ First scan completed successfully
10. ✅ Code quality checks passing
11. ✅ No critical errors in logs
12. ✅ Documentation reviewed

---

## 🎉 Ready to Launch!

Once all items are checked, your CyberIntel Platform is ready for:

- **Development**: Local testing and feature development
- **Staging**: Pre-production testing and validation
- **Production**: Live deployment and monitoring

---

## 📊 Quick Reference

### Important URLs
- Frontend: http://localhost:3000
- API Gateway: http://localhost:8000
- Neo4j Browser: http://localhost:7474
- Documentation: `docs/index.html`

### Important Commands
```powershell
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Start development
npm run dev

# Run checks
npm run check

# Validate
.\scripts\validate.ps1
```

### Important Files
- Configuration: `.env`
- Docker: `docker-compose.yml`
- Package: `package.json`
- Documentation: `docs/`

---

**Status**: ✅ Ready for Launch  
**Last Updated**: May 24, 2026  
**Next Step**: Follow the checklist above

