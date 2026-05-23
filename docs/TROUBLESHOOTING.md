# Troubleshooting Guide

## Common Issues

### Services Won't Start

**Symptom**: Docker containers fail to start

**Solutions**:
1. Check Docker resources
```bash
docker info
docker system df
```

2. Check port conflicts
```bash
netstat -tulpn | grep -E '3000|8000|5432|7687|6379|9200'
```

3. View service logs
```bash
docker-compose logs <service-name>
```

4. Restart Docker
```bash
sudo systemctl restart docker
```

### Database Connection Errors

**Symptom**: "Connection refused" or "Authentication failed"

**Solutions**:
1. Verify service is running
```bash
docker-compose ps
```

2. Check connection string
```bash
echo $DATABASE_URL
```

3. Test connection
```bash
docker-compose exec postgres psql -U cyberintel -d cyberintel -c "SELECT 1"
```

4. Reset database
```bash
docker-compose down -v
docker-compose up -d postgres
```

### Neo4j Connection Issues

**Symptom**: "ServiceUnavailable" or "AuthenticationError"

**Solutions**:
1. Check Neo4j logs
```bash
docker-compose logs neo4j
```

2. Verify credentials
```bash
docker-compose exec neo4j cypher-shell -u neo4j -p cyberintel "RETURN 1"
```

3. Increase memory
```yaml
# docker-compose.yml
NEO4J_dbms_memory_heap_max__size: 4G
```

### Worker Not Processing Tasks

**Symptom**: Tasks stuck in queue

**Solutions**:
1. Check Redis connection
```bash
docker-compose exec redis redis-cli ping
```

2. View queue
```bash
docker-compose exec redis redis-cli ZRANGE cyberintel:tasks 0 -1
```

3. Check worker logs
```bash
docker-compose logs workers
```

4. Restart workers
```bash
docker-compose restart workers
```

### Frontend Build Errors

**Symptom**: Vite build fails

**Solutions**:
1. Clear cache
```bash
cd frontend
rm -rf node_modules dist .vite
npm install
```

2. Check Node version
```bash
node --version  # Should be 20+
```

3. Update dependencies
```bash
npm update
```

### API Rate Limit Errors

**Symptom**: 429 Too Many Requests

**Solutions**:
1. Check rate limit config
```env
RATE_LIMIT_MAX=1000
RATE_LIMIT_WINDOW=15m
```

2. Implement caching
3. Upgrade API plans
4. Use multiple API keys

### Memory Issues

**Symptom**: Out of memory errors

**Solutions**:
1. Check memory usage
```bash
docker stats
```

2. Increase Docker memory
```bash
# Docker Desktop: Settings > Resources > Memory
```

3. Optimize services
```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
```

### Disk Space Issues

**Symptom**: No space left on device

**Solutions**:
1. Check disk usage
```bash
df -h
docker system df
```

2. Clean Docker
```bash
docker system prune -a
docker volume prune
```

3. Clean logs
```bash
docker-compose logs --tail=0 -f > /dev/null
```

## Performance Issues

### Slow Scans

**Causes**:
- API rate limits
- Network latency
- Insufficient workers
- Database performance

**Solutions**:
1. Increase workers
```yaml
workers:
  deploy:
    replicas: 10
```

2. Optimize database
```sql
-- PostgreSQL
VACUUM ANALYZE;
CREATE INDEX idx_entities_value ON entities(value);
```

3. Enable caching
```env
CACHE_TTL=3600
```

### High CPU Usage

**Solutions**:
1. Identify process
```bash
docker stats
```

2. Limit CPU
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
```

3. Optimize queries
4. Scale horizontally

## Debugging

### Enable Debug Logging

```env
LOG_LEVEL=debug
```

### View Detailed Logs

```bash
# All services
docker-compose logs -f --tail=100

# Specific service
docker-compose logs -f gateway

# Follow logs
docker-compose logs -f | grep ERROR
```

### Inspect Container

```bash
docker-compose exec gateway sh
```

### Check Environment

```bash
docker-compose exec gateway env
```

## Getting Help

1. Check documentation
2. Search GitHub issues
3. Enable debug logging
4. Collect logs
5. Create GitHub issue with:
   - Description
   - Steps to reproduce
   - Logs
   - Environment details
