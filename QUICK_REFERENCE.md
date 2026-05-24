# ⚡ Quick Reference - CyberIntel Platform

**Last Updated**: May 24, 2026  
**Version**: 1.0.0

---

## 🚀 Quick Start (5 Minutes)

```powershell
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/cyberintel-platform.git
cd cyberintel-platform

# 2. Install dependencies
npm install
npm run build:shared

# 3. Configure environment
Copy-Item .env.example .env
# Edit .env with your API keys

# 4. Start Docker services
docker-compose up -d

# 5. Start development
npm run dev

# 6. Open browser
# Frontend: http://localhost:3000
# API: http://localhost:8000
# Neo4j: http://localhost:7474
```

---

## 📋 Essential Commands

### Docker Management
```powershell
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View service status
docker-compose ps

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs gateway
docker-compose logs backend
docker-compose logs postgres

# Restart a service
docker-compose restart gateway

# Full reset (WARNING: deletes data)
docker-compose down -v
docker-compose up -d
```

### Development
```powershell
# Start all services
npm run dev

# Start specific service
npm run dev:frontend
npm run dev:backend
npm run dev:gateway
npm run dev:orchestrator
npm run dev:graph
npm run dev:ai-router

# Build all services
npm run build

# Build specific service
npm run build --workspace=frontend

# Run tests
npm run test

# Run linting
npm run lint

# Run type checking
npm run typecheck

# Run all checks
npm run check

# Format code
npm run format
```

### Database Operations
```powershell
# Connect to PostgreSQL
docker-compose exec postgres psql -U cyberintel -d cyberintel

# Connect to Neo4j
docker-compose exec neo4j cypher-shell -u neo4j -p cyberintel

# Connect to Redis
docker-compose exec redis redis-cli

# View database logs
docker-compose logs postgres
docker-compose logs neo4j
docker-compose logs redis
```

### Python Services
```powershell
# Install Python dependencies
pip install -r agents/requirements.txt
pip install -r workers/requirements.txt

# Run Python linting
cd agents && flake8 . && cd ..

# Run Python syntax check
python -m py_compile agents/*.py
```

---

## 🌐 API Endpoints

### Health Check
```bash
GET http://localhost:8000/health
```

### Authentication
```bash
# Register
POST http://localhost:8000/api/auth/register
{
  "email": "user@example.com",
  "password": "Password123!",
  "name": "User Name"
}

# Login
POST http://localhost:8000/api/auth/login
{
  "email": "user@example.com",
  "password": "Password123!"
}
```

### Scans
```bash
# Create scan
POST http://localhost:8000/api/scans
{
  "target": "example.com",
  "type": "domain",
  "depth": "standard"
}

# Get scans
GET http://localhost:8000/api/scans

# Get scan details
GET http://localhost:8000/api/scans/{scanId}

# Get scan results
GET http://localhost:8000/api/scans/{scanId}/results
```

### Entities
```bash
# Get entities
GET http://localhost:8000/api/entities

# Get entity details
GET http://localhost:8000/api/entities/{entityId}

# Search entities
GET http://localhost:8000/api/entities/search?query=example.com
```

### IOCs
```bash
# Get IOCs
GET http://localhost:8000/api/iocs

# Get IOC details
GET http://localhost:8000/api/iocs/{iocId}

# Search IOCs
GET http://localhost:8000/api/iocs/search?query=192.168.1.1
```

---

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=cyberintel
POSTGRES_PASSWORD=cyberintel
POSTGRES_DB=cyberintel

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=cyberintel

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Elasticsearch (if enabled)
ELASTICSEARCH_URL=http://localhost:9200

# AI Providers
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key
GROQ_API_KEY=your_key
DEEPSEEK_API_KEY=your_key
OPENROUTER_API_KEY=your_key

# JWT
JWT_SECRET=your_secret_key

# Telegram (optional)
TELEGRAM_BOT_TOKEN=your_token

# OSINT APIs (optional)
VIRUSTOTAL_API_KEY=your_key
SHODAN_API_KEY=your_key
SECURITYTRAILS_API_KEY=your_key
HAVEIBEENPWNED_API_KEY=your_key
```

### Service Ports
| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend | 8001 | http://localhost:8001 |
| Gateway | 8000 | http://localhost:8000 |
| Orchestrator | 8002 | http://localhost:8002 |
| Graph Engine | 8003 | http://localhost:8003 |
| AI Router | 8004 | http://localhost:8004 |
| PostgreSQL | 5432 | localhost:5432 |
| Neo4j | 7687 | bolt://localhost:7687 |
| Neo4j Browser | 7474 | http://localhost:7474 |
| Redis | 6379 | localhost:6379 |
| Elasticsearch | 9200 | http://localhost:9200 |
| Ollama | 11434 | http://localhost:11434 |

---

## 🐛 Troubleshooting

### Port Already in Use
```powershell
# Find process using port
netstat -ano | findstr :3000

# Kill process
taskkill /PID <PID> /F

# Or change port in .env
PORT=3001
```

### Docker Services Not Starting
```powershell
# Check Docker status
docker ps

# View logs
docker-compose logs

# Restart Docker
docker-compose restart

# Full reset
docker-compose down -v
docker-compose up -d
```

### Node Dependencies Issues
```powershell
# Clear cache
rm -r node_modules package-lock.json

# Reinstall
npm install

# Rebuild shared
npm run build:shared
```

### Python Dependencies Issues
```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r agents/requirements.txt
pip install -r workers/requirements.txt
```

### Database Connection Issues
```powershell
# Test PostgreSQL
docker-compose exec postgres psql -U cyberintel -d cyberintel -c "SELECT 1"

# Test Neo4j
docker-compose exec neo4j cypher-shell -u neo4j -p cyberintel "RETURN 1"

# Test Redis
docker-compose exec redis redis-cli ping

# View database logs
docker-compose logs postgres
docker-compose logs neo4j
docker-compose logs redis
```

### API Not Responding
```powershell
# Check gateway logs
docker-compose logs gateway

# Test health endpoint
curl http://localhost:8000/health

# Restart gateway
docker-compose restart gateway
```

---

## 📚 Documentation

### Getting Started
- [START_HERE.md](START_HERE.md) - Complete getting started guide
- [COMMANDS.md](COMMANDS.md) - All available commands
- [PRE_LAUNCH_CHECKLIST.md](PRE_LAUNCH_CHECKLIST.md) - Launch checklist

### Architecture
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture
- [docs/AGENTS.md](docs/AGENTS.md) - AI agents documentation
- [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md) - OSINT integrations

### Operations
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - Production deployment
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Common issues
- [docs/SECURITY.md](docs/SECURITY.md) - Security policy

### Configuration
- [LIGHTWEIGHT_MODE.md](LIGHTWEIGHT_MODE.md) - VPS mode setup
- [docker-compose.yml](docker-compose.yml) - Docker configuration
- [.env.example](.env.example) - Environment variables

---

## 🎯 Common Tasks

### Create New User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "Password123!",
    "name": "New User"
  }'
```

### Start a Scan
```bash
curl -X POST http://localhost:8000/api/scans \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "target": "example.com",
    "type": "domain",
    "depth": "standard"
  }'
```

### Get Scan Results
```bash
curl http://localhost:8000/api/scans/{scanId}/results \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Search Entities
```bash
curl "http://localhost:8000/api/entities/search?query=example.com" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### View Graph Data
```bash
# Access Neo4j Browser
# http://localhost:7474
# Login: neo4j / cyberintel
# Run Cypher queries
```

---

## 🔐 Security

### Change Default Passwords
```bash
# PostgreSQL
docker-compose exec postgres psql -U cyberintel -d cyberintel
ALTER USER cyberintel WITH PASSWORD 'new_password';

# Neo4j
docker-compose exec neo4j cypher-shell -u neo4j -p cyberintel
ALTER USER neo4j SET PASSWORD 'new_password';
```

### Generate JWT Secret
```powershell
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### Check for Secrets in Code
```powershell
git grep -i "password\|secret\|key" -- "*.ts" "*.js" | grep -v "node_modules"
```

### Run Security Audit
```powershell
npm audit
```

---

## 📊 Monitoring

### View Service Status
```powershell
docker-compose ps
```

### View Service Logs
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f gateway
docker-compose logs -f backend
docker-compose logs -f postgres
```

### Check Resource Usage
```powershell
docker stats
```

### Monitor Database
```powershell
# PostgreSQL
docker-compose exec postgres psql -U cyberintel -d cyberintel -c "SELECT * FROM pg_stat_activity;"

# Neo4j
docker-compose exec neo4j cypher-shell -u neo4j -p cyberintel "CALL dbms.queryJmx('org.neo4j:instance=kernel#0,name=Transactions');"

# Redis
docker-compose exec redis redis-cli info
```

---

## 🚀 Deployment

### Development
```powershell
npm run dev
```

### Staging
```powershell
docker-compose up -d
npm run build
```

### Production
```powershell
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📞 Getting Help

### Check Logs
```powershell
docker-compose logs -f
```

### Read Documentation
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- [docs/FAQ.md](docs/FAQ.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)

### Report Issues
- GitHub Issues: https://github.com/YOUR_USERNAME/cyberintel-platform/issues
- GitHub Discussions: https://github.com/YOUR_USERNAME/cyberintel-platform/discussions

---

## 🎯 Quick Checklist

Before launching:
- [ ] Node.js v20+ installed
- [ ] Python 3.11+ installed
- [ ] Docker Desktop running
- [ ] Repository cloned
- [ ] Dependencies installed
- [ ] .env configured
- [ ] Docker services running
- [ ] All services healthy
- [ ] Frontend accessible
- [ ] API responding

---

**Status**: ✅ Ready to Use  
**Last Updated**: May 24, 2026

