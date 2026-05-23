# ⚡ Quick Start - Get Running in 5 Minutes

## Prerequisites

- Docker & Docker Compose
- Node.js 20+
- Python 3.11+

## 1. Clone & Install

```bash
git clone <repo>
cd cyberintel-platform

# Run automatic installation
./scripts/install.sh  # Linux/Mac
.\scripts\install.ps1  # Windows
```

## 2. Configure

```bash
# Copy environment file
cp .env.example .env

# Edit .env and add at minimum:
# - JWT_SECRET=your-secret-here
# - ANTHROPIC_API_KEY or OPENAI_API_KEY (for AI features)
```

## 3. Start Infrastructure

```bash
docker-compose up -d postgres redis neo4j elasticsearch
```

Wait 30 seconds for databases to initialize.

## 4. Start Services

```bash
# Option A: All services at once
npm run dev

# Option B: Individual services
npm run dev --workspace=gateway
npm run dev --workspace=backend
npm run dev --workspace=orchestrator
npm run dev --workspace=ai-router
npm run dev --workspace=graph-engine
npm run dev --workspace=frontend
```

## 5. Verify

```bash
# Check all services are healthy
./scripts/check-health.sh  # Linux/Mac
.\scripts\check-health.ps1  # Windows

# Or manually:
curl http://localhost:8000/health  # Gateway
curl http://localhost:8001/health  # Backend
curl http://localhost:8002/health  # Orchestrator
curl http://localhost:8003/health  # AI Router
curl http://localhost:8004/health  # Graph Engine
```

## 6. Access

- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **Neo4j Browser**: http://localhost:7474 (user: neo4j, pass: cyberintel)

## Troubleshooting

### Services won't start

```bash
# Check Docker services
docker-compose ps

# View logs
docker-compose logs postgres
docker-compose logs redis
docker-compose logs neo4j

# Restart infrastructure
docker-compose restart
```

### Port already in use

```bash
# Find what's using the port
netstat -ano | findstr :3000  # Windows
lsof -i :3000                 # Linux/Mac

# Change port in .env or kill the process
```

### Database connection errors

```bash
# Wait for databases to be ready
docker-compose ps

# Check health
docker-compose exec postgres pg_isready
docker-compose exec redis redis-cli ping
```

## What's Running?

| Service | Port | Purpose |
|---------|------|---------|
| Frontend | 3000 | React UI |
| Gateway | 8000 | API Gateway |
| Backend | 8001 | Main API |
| Orchestrator | 8002 | Task Management |
| AI Router | 8003 | AI Providers |
| Graph Engine | 8004 | Neo4j Operations |
| PostgreSQL | 5432 | Main Database |
| Neo4j | 7474/7687 | Graph Database |
| Redis | 6379 | Cache & Queues |
| Elasticsearch | 9200 | Search |

## Next Steps

1. Create an account at http://localhost:3000
2. Start your first scan
3. Explore the graph
4. Check out the docs in `docs/`

## Need Help?

- Check `TROUBLESHOOTING.md` in docs/
- Review logs: `docker-compose logs -f`
- Open an issue on GitHub
