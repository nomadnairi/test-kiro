# Quick Start Guide

## Prerequisites

- Docker & Docker Compose
- Node.js 20+
- Python 3.11+
- 16GB RAM minimum
- 50GB disk space

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd cyberintel-platform
```

### 2. Environment Setup

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Required for basic functionality
JWT_SECRET=your-super-secret-jwt-key-change-in-production

# Optional: Add API keys for integrations
SHODAN_API_KEY=your-shodan-key
VIRUSTOTAL_API_KEY=your-virustotal-key
ABUSEIPDB_API_KEY=your-abuseipdb-key
```

### 3. Run Setup Script

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

This will:
- Check prerequisites
- Install dependencies
- Start infrastructure services
- Initialize databases

### 4. Start Development

```bash
npm run dev
```

This starts all services:
- Frontend: http://localhost:3000
- API Gateway: http://localhost:8000
- Neo4j Browser: http://localhost:7474

## First Steps

### 1. Login

Navigate to http://localhost:3000

Default credentials:
- Email: `admin@cyberintel.local`
- Password: `admin123`

**⚠️ Change these in production!**

### 2. Create Your First Scan

1. Click "New Scan" button
2. Enter a target (e.g., `example.com`)
3. Click "Start Scan"
4. Watch real-time progress

### 3. Explore Results

- **Dashboard**: Overview of all scans
- **Scans**: List of all scans and their status
- **Graph**: Visualize entity relationships
- **IOCs**: Browse detected indicators
- **Entities**: View discovered entities
- **AI Chat**: Ask AI analyst questions

## Common Tasks

### Start Services

```bash
# Development mode
npm run dev

# Production mode
./scripts/start-prod.sh
```

### Stop Services

```bash
docker-compose down
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f gateway
```

### Reset Database

```bash
docker-compose down -v
docker-compose up -d postgres
docker-compose exec postgres psql -U cyberintel -d cyberintel -f /docker-entrypoint-initdb.d/init.sql
```

### Pull Ollama Models

```bash
docker-compose exec ollama ollama pull llama3.1:8b
```

## Troubleshooting

### Services Won't Start

```bash
# Check Docker resources
docker info

# Check port availability
netstat -an | grep -E '3000|8000|5432|7687|6379|9200'

# View service logs
docker-compose logs <service-name>
```

### Database Connection Errors

```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check connection
docker-compose exec postgres psql -U cyberintel -d cyberintel -c "SELECT 1"
```

### Neo4j Connection Issues

```bash
# Verify Neo4j is running
docker-compose ps neo4j

# Check logs
docker-compose logs neo4j
```

### Worker Not Processing Tasks

```bash
# Check Redis
docker-compose exec redis redis-cli ping

# Check worker logs
docker-compose logs workers
```

## Next Steps

- [Architecture Guide](ARCHITECTURE.md)
- [API Documentation](API.md)
- [Agent System](AGENTS.md)
- [Integration Guide](INTEGRATIONS.md)
- [Deployment Guide](DEPLOYMENT.md)

## Getting Help

- GitHub Issues: Report bugs and request features
- Documentation: Check docs/ folder
- Community: Join our Discord/Slack

## Security Notes

1. **Change default credentials** immediately
2. **Set strong JWT_SECRET** in production
3. **Use HTTPS** in production
4. **Secure API keys** properly
5. **Enable audit logging**
6. **Configure rate limiting**
7. **Regular backups**

## Performance Tips

1. **Increase worker instances** for faster processing
2. **Configure Redis persistence** for reliability
3. **Optimize PostgreSQL** connection pooling
4. **Use SSD storage** for databases
5. **Monitor resource usage**

## Development Tips

1. **Hot reload** is enabled for all services
2. **TypeScript** compilation is automatic
3. **Logs** are structured JSON in production
4. **Tests** run with `npm test`
5. **Linting** with `npm run lint`
