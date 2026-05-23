# Deployment Guide

## Prerequisites

- Docker & Docker Compose
- Node.js 20+
- Python 3.11+
- 16GB+ RAM
- 50GB+ disk space

## Quick Start

### Development

```bash
# Clone repository
git clone <repo-url>
cd cyberintel-platform

# Setup
./scripts/setup.sh

# Start development
./scripts/start-dev.sh
```

### Production

```bash
# Build and start
./scripts/start-prod.sh
```

## Manual Setup

### 1. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 2. Install Dependencies

```bash
npm install
cd agents && pip install -r requirements.txt
cd ../workers && pip install -r requirements.txt
```

### 3. Start Infrastructure

```bash
docker-compose up -d postgres redis neo4j elasticsearch
```

### 4. Initialize Database

```bash
docker-compose exec postgres psql -U cyberintel -d cyberintel -f /docker-entrypoint-initdb.d/init.sql
```

### 5. Start Services

```bash
# Terminal 1: Gateway
cd gateway && npm run dev

# Terminal 2: Backend
cd backend && npm run dev

# Terminal 3: Orchestrator
cd orchestrator && npm run dev

# Terminal 4: AI Router
cd ai-router && npm run dev

# Terminal 5: Graph Engine
cd graph-engine && npm run dev

# Terminal 6: Workers
cd workers && python worker.py

# Terminal 7: Frontend
cd frontend && npm run dev
```

## Docker Deployment

### Build Images

```bash
docker-compose build
```

### Start All Services

```bash
docker-compose up -d
```

### View Logs

```bash
docker-compose logs -f
```

### Stop Services

```bash
docker-compose down
```

## Production Considerations

### Security

1. **Change default credentials**
   - Update JWT_SECRET
   - Change database passwords
   - Update default admin password

2. **Enable HTTPS**
   - Use reverse proxy (nginx/traefik)
   - Configure SSL certificates

3. **API Rate Limiting**
   - Configure appropriate limits
   - Use Redis for distributed rate limiting

4. **Secrets Management**
   - Use environment variables
   - Consider HashiCorp Vault or AWS Secrets Manager

### Performance

1. **Database Optimization**
   - Configure PostgreSQL connection pooling
   - Optimize Neo4j memory settings
   - Enable Redis persistence

2. **Scaling**
   - Run multiple worker instances
   - Use load balancer for API gateway
   - Scale horizontally with Kubernetes

3. **Monitoring**
   - Set up Prometheus metrics
   - Configure log aggregation
   - Enable health checks

### Backup

1. **PostgreSQL**
```bash
docker-compose exec postgres pg_dump -U cyberintel cyberintel > backup.sql
```

2. **Neo4j**
```bash
docker-compose exec neo4j neo4j-admin dump --database=neo4j --to=/backups/neo4j.dump
```

3. **Redis**
```bash
docker-compose exec redis redis-cli BGSAVE
```

## Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests.

```bash
kubectl apply -f k8s/
```

## Monitoring

### Prometheus

Access metrics at:
- Gateway: http://localhost:8000/metrics
- Orchestrator: http://localhost:8002/metrics

### Grafana

Import dashboards from `monitoring/grafana/`

### Logs

Centralized logging with ELK stack:
```bash
docker-compose -f docker-compose.elk.yml up -d
```

## Troubleshooting

### Services won't start

1. Check Docker resources
2. Verify port availability
3. Check logs: `docker-compose logs <service>`

### Database connection errors

1. Verify DATABASE_URL
2. Check PostgreSQL is running
3. Verify credentials

### Neo4j connection issues

1. Check NEO4J_URI
2. Verify authentication
3. Check memory settings

### Worker not processing tasks

1. Check Redis connection
2. Verify queue name
3. Check worker logs

## Health Checks

All services expose `/health` endpoint:

```bash
curl http://localhost:8000/health  # Gateway
curl http://localhost:8001/health  # Backend
curl http://localhost:8002/health  # Orchestrator
curl http://localhost:8003/health  # AI Router
curl http://localhost:8004/health  # Graph Engine
```

## Updating

```bash
git pull
npm install
docker-compose build
docker-compose up -d
```
