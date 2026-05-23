# 🚀 Quick Command Reference

Essential commands for working with the CyberIntel Platform.

## 📦 Installation

```bash
# Automatic installation (recommended)
./scripts/install.sh              # Linux/Mac
.\scripts\install.ps1             # Windows PowerShell
scripts\install.bat               # Windows CMD

# Manual installation
npm install                       # Install Node.js dependencies
npm run setup:python              # Install Python dependencies
```

## 🐳 Docker Commands

```bash
# Start all infrastructure services
npm run docker:up
# or
docker-compose up -d

# Stop all services
npm run docker:down

# Restart services
npm run docker:restart

# View logs
npm run docker:logs

# Clean everything (removes volumes)
npm run docker:clean

# Production deployment
npm run docker:prod
```

## 🔧 Development

```bash
# Start all development servers
npm run dev

# Start all services (including graph-engine and ai-router)
npm run dev:all

# Start individual services
npm run dev:frontend              # React frontend (port 3000)
npm run dev:backend               # Backend API (port 5000)
npm run dev:gateway               # API Gateway (port 4000)
npm run dev:orchestrator          # Orchestrator (port 6000)
npm run dev:graph                 # Graph Engine (port 7000)
npm run dev:ai-router             # AI Router (port 8000)
```

## 🏗️ Build

```bash
# Build all services
npm run build

# Build shared library only
npm run build:shared

# Build specific workspace
npm run build --workspace=frontend
npm run build --workspace=backend
```

## 🧪 Testing

```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests for specific workspace
npm test --workspace=backend
npm test --workspace=frontend
```

## 🔍 Code Quality

```bash
# Lint all code
npm run lint

# Lint and auto-fix
npm run lint:fix

# Type checking
npm run typecheck

# Format code
npm run format

# Check formatting
npm run format:check

# Run all checks (typecheck + lint + test)
npm run check
```

## 🗄️ Database

```bash
# Run migrations
npm run migrate

# Create new migration
npm run migrate:create

# Seed database with sample data
npm run seed

# Reset database (WARNING: deletes all data)
npm run db:reset
```

## 🧹 Cleanup

```bash
# Clean build artifacts
npm run clean

# Clean everything including Docker volumes
npm run clean:all

# Remove node_modules
rm -rf node_modules
npm install
```

## 🐍 Python Commands

```bash
# Install Python dependencies
cd agents && pip install -r requirements.txt
cd workers && pip install -r requirements.txt

# Run Python agents
cd agents
python ai_recon_planner.py
python breach_intelligence_agent.py
python graph_agent.py

# Run Python workers
cd workers
python ingestion_worker.py
```

## 📊 Service URLs

After starting services, access them at:

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | React UI |
| API Gateway | http://localhost:4000 | Main API entry point |
| Backend | http://localhost:5000 | Backend API |
| Orchestrator | http://localhost:6000 | Task orchestration |
| Graph Engine | http://localhost:7000 | Neo4j operations |
| AI Router | http://localhost:8000 | AI provider routing |
| PostgreSQL | localhost:5432 | Database |
| Neo4j Browser | http://localhost:7474 | Graph database UI |
| Redis | localhost:6379 | Cache & queues |
| Elasticsearch | http://localhost:9200 | Search engine |

## 🔐 Environment Setup

```bash
# Copy example environment file
cp .env.example .env

# Edit environment variables
nano .env                         # Linux/Mac
notepad .env                      # Windows

# Generate secure secrets
openssl rand -base64 32           # For passwords
openssl rand -base64 64           # For JWT secret
```

## 📝 Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Stage changes
git add .

# Commit with conventional commit message
git commit -m "feat(agents): add new reconnaissance agent"

# Push to remote
git push origin feature/my-feature

# Update from main
git checkout main
git pull origin main
git checkout feature/my-feature
git rebase main
```

## 🔍 Debugging

```bash
# View Docker logs for specific service
docker-compose logs -f postgres
docker-compose logs -f neo4j
docker-compose logs -f redis

# Check service status
docker-compose ps

# Inspect container
docker exec -it cyberintel-postgres psql -U postgres
docker exec -it cyberintel-neo4j cypher-shell
docker exec -it cyberintel-redis redis-cli

# Check Node.js service logs
npm run dev:backend 2>&1 | tee backend.log
```

## 🚀 Production Deployment

```bash
# Build for production
npm run build

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# View production logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop production services
docker-compose -f docker-compose.prod.yml down
```

## 📦 Dependency Management

```bash
# Update all dependencies
npm update

# Check for outdated packages
npm outdated

# Audit for vulnerabilities
npm audit
npm audit fix

# Python dependency updates
pip list --outdated
pip install --upgrade -r agents/requirements.txt
```

## 🔧 Troubleshooting Commands

```bash
# Port already in use
lsof -i :3000                     # Linux/Mac
netstat -ano | findstr :3000      # Windows

# Clear npm cache
npm cache clean --force

# Rebuild node_modules
rm -rf node_modules package-lock.json
npm install

# Reset Docker
docker system prune -a
docker volume prune

# Check disk space
df -h                             # Linux/Mac
wmic logicaldisk get size,freespace,caption  # Windows
```

## 📚 Documentation Commands

```bash
# Generate API documentation
npm run docs:generate

# Serve documentation locally
npm run docs:serve

# Open documentation in browser
open docs/index.html              # Mac
xdg-open docs/index.html          # Linux
start docs/index.html             # Windows
```

## 🎯 Quick Start Workflow

```bash
# 1. Clone and install
git clone https://github.com/YOUR_USERNAME/cyberintel-platform.git
cd cyberintel-platform
./scripts/install.sh

# 2. Configure
cp .env.example .env
nano .env

# 3. Start infrastructure
npm run docker:up

# 4. Run migrations
npm run migrate

# 5. Start development
npm run dev

# 6. Access platform
open http://localhost:3000
```

## 💡 Tips

- Use `npm run dev:all` to start all services at once
- Use `docker-compose logs -f SERVICE_NAME` to debug specific services
- Run `npm run check` before committing to catch issues early
- Use `npm run format` to auto-format code before committing
- Check `docker-compose ps` to see which services are running
- Use `npm run db:reset` to start fresh with a clean database

## 🆘 Getting Help

```bash
# View available npm scripts
npm run

# View Docker Compose services
docker-compose config --services

# Check Node.js version
node --version

# Check Python version
python --version

# Check Docker version
docker --version
docker-compose --version
```

---

**Need more help?** Check [START_HERE.md](START_HERE.md) or [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
