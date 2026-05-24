# 🪶 Lightweight VPS Mode - Documentation

**Status**: ✅ ACTIVE (Current Configuration)  
**Target**: Low-resource VPS deployment  
**RAM Saved**: ~10 GB compared to FULL MODE

---

## 📊 Resource Requirements

### MINIMUM VPS Requirements (Current Mode)

**Hardware**:
- **CPU**: 2 vCPU
- **RAM**: 4 GB
- **Storage**: 20 GB SSD
- **Network**: 100 Mbps

**Software**:
- Docker 20.10+
- Docker Compose 2.0+
- Linux (Ubuntu 20.04+ recommended)

**Cost**: ~$10-20/month (DigitalOcean, Linode, Vultr)

### RECOMMENDED VPS Requirements

**Hardware**:
- **CPU**: 4 vCPU
- **RAM**: 8 GB
- **Storage**: 40 GB SSD
- **Network**: 1 Gbps

**Cost**: ~$40-60/month

### FULL MODE Requirements (For Comparison)

**Hardware**:
- **CPU**: 8+ vCPU
- **RAM**: 16+ GB (32 GB recommended)
- **Storage**: 100+ GB SSD
- **GPU**: NVIDIA GPU (for Ollama)
- **Network**: 1 Gbps

**Cost**: ~$200-400/month

---

## 📈 Estimated RAM Usage Per Service

### LIGHTWEIGHT MODE (Current)

| Service | RAM Limit | Actual Usage | Status |
|---------|-----------|--------------|--------|
| PostgreSQL | 512 MB | ~300 MB | ✅ Active |
| Neo4j | 512 MB | ~400 MB | ✅ Active (Reduced) |
| Redis | 256 MB | ~100 MB | ✅ Active |
| Gateway | 512 MB | ~200 MB | ✅ Active |
| Backend | 512 MB | ~250 MB | ✅ Active |
| Orchestrator | 256 MB | ~150 MB | ✅ Active |
| AI Router | 256 MB | ~150 MB | ✅ Active |
| Graph Engine | 512 MB | ~250 MB | ✅ Active |
| Workers | 512 MB | ~200 MB | ✅ Active |
| Frontend | 256 MB | ~150 MB | ✅ Active |
| Telegram Bot | 128 MB | ~80 MB | ✅ Active |
| Ingestion Worker | 256 MB | ~150 MB | ✅ Active |
| **TOTAL** | **~3.5 GB** | **~2.4 GB** | **✅ Fits in 4GB** |

### FULL MODE (Disabled Services)

| Service | RAM Usage | Status |
|---------|-----------|--------|
| Elasticsearch | ~2 GB | ❌ Disabled |
| Ollama | ~8 GB | ❌ Disabled |
| **TOTAL SAVED** | **~10 GB** | **💰 Cost Savings** |

---

## 🚀 Startup Instructions (Lightweight Mode)

### 1. Prerequisites

```bash
# Check Docker
docker --version
# Need: Docker 20.10+

docker compose --version
# Need: Docker Compose 2.0+

# Check available RAM
free -h
# Need: At least 4 GB available
```

### 2. Configure API Keys

```bash
# Copy environment template
cp .env.example .env

# Edit .env file
nano .env
```

**Required API Keys** (at least one):
```bash
# OpenAI (Recommended)
OPENAI_API_KEY=sk-...

# Or Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Or OpenRouter (Multiple models)
OPENROUTER_API_KEY=sk-or-...

# Or Groq (Fast inference)
GROQ_API_KEY=gsk_...
```

**Optional**:
```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...

# JWT Secret (change in production)
JWT_SECRET=your-secret-key-here
```

### 3. Start Platform

```bash
# Navigate to project
cd /path/to/cyberintel-platform

# Start all services
docker compose up -d

# Wait for initialization (60-90 seconds)
sleep 90

# Check status
docker compose ps
```

### 4. Verify Health

```bash
# Check all services
docker compose ps

# Check logs
docker compose logs -f

# Test API
curl http://localhost:8000/health
```

### 5. Access Platform

- **Frontend**: http://your-vps-ip:3000
- **API Gateway**: http://your-vps-ip:8000
- **Neo4j Browser**: http://your-vps-ip:7474

---

## 🔄 How to Re-Enable FULL MODE

### Step 1: Uncomment Heavy Services

Edit `docker-compose.yml`:

```yaml
# Find these sections and UNCOMMENT them:

# 1. Elasticsearch (lines ~100-130)
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.13.0
  # ... rest of config

# 2. Ollama (lines ~135-160)
ollama:
  image: ollama/ollama:latest
  # ... rest of config
```

### Step 2: Update Backend Dependencies

In `docker-compose.yml`, find `backend` service and uncomment:

```yaml
backend:
  # ...
  environment:
    # UNCOMMENT THIS:
    - ELASTICSEARCH_URL=http://elasticsearch:9200
  depends_on:
    # ... existing dependencies
    # UNCOMMENT THIS:
    elasticsearch:
      condition: service_healthy
```

### Step 3: Update AI Router Dependencies

In `docker-compose.yml`, find `ai-router` service and uncomment:

```yaml
ai-router:
  # ...
  environment:
    # UNCOMMENT THIS:
    - OLLAMA_URL=http://ollama:11434
  # No depends_on needed (Ollama is optional)
```

### Step 4: Restore Neo4j Plugins

In `docker-compose.yml`, find `neo4j` service and uncomment:

```yaml
neo4j:
  # ...
  environment:
    # UNCOMMENT THESE:
    NEO4J_PLUGINS: '["apoc", "graph-data-science"]'
    NEO4J_dbms_security_procedures_unrestricted: apoc.*,gds.*
    # UPDATE THESE:
    NEO4J_dbms_memory_heap_max__size: 2G  # Was 256M
```

### Step 5: Increase Resource Limits

Update resource limits for all services back to original values:

```yaml
# PostgreSQL
deploy:
  resources:
    limits:
      cpus: '2'      # Was 1
      memory: 2G     # Was 512M

# Neo4j
deploy:
  resources:
    limits:
      cpus: '2'      # Was 1
      memory: 3G     # Was 512M

# And so on for other services...
```

### Step 6: Restart Platform

```bash
# Stop all services
docker compose down

# Start with FULL MODE
docker compose up -d

# Wait longer for heavy services (2-3 minutes)
sleep 180

# Check status
docker compose ps
```

---

## 🔍 What's Different in Lightweight Mode

### Disabled Services

#### 1. Elasticsearch ❌
**Why Disabled**: Uses ~2 GB RAM  
**Impact**: No full-text search  
**Alternative**: PostgreSQL LIKE queries (slower but works)  
**When to Enable**: When you need advanced search capabilities

#### 2. Ollama ❌
**Why Disabled**: Uses ~8 GB RAM + requires GPU  
**Impact**: No local AI inference  
**Alternative**: API-based providers (OpenAI, Anthropic, Groq)  
**When to Enable**: When you have GPU and want privacy/no API costs

### Reduced Resources

#### 1. Neo4j Memory Reduced
**Before**: 3 GB RAM, APOC + GDS plugins  
**After**: 512 MB RAM, no plugins  
**Impact**: Slower graph operations, no advanced algorithms  
**Reason**: Graph database still needed for relationships

#### 2. PostgreSQL Memory Reduced
**Before**: 2 GB RAM  
**After**: 512 MB RAM  
**Impact**: Slower queries, smaller cache  
**Reason**: Still handles all data, just with less cache

#### 3. Redis Memory Reduced
**Before**: 512 MB  
**After**: 256 MB  
**Impact**: Smaller cache, more evictions  
**Reason**: Still handles queues and sessions

#### 4. All Services CPU Reduced
**Before**: 1-2 CPU per service  
**After**: 0.25-1 CPU per service  
**Impact**: Slower processing, longer response times  
**Reason**: VPS has limited CPU

---

## ⚠️ Limitations in Lightweight Mode

### Performance

- **Slower queries** - Reduced database cache
- **Slower graph operations** - No Neo4j plugins
- **Slower AI responses** - API latency vs local
- **Limited concurrency** - Fewer CPU cores

### Features

- **No full-text search** - Elasticsearch disabled
- **No local AI** - Ollama disabled
- **No advanced graph algorithms** - Neo4j plugins disabled
- **Smaller cache** - Redis memory reduced

### Scalability

- **Limited concurrent users** - ~10-20 users max
- **Limited scan throughput** - ~5-10 scans/hour
- **Limited data volume** - ~100K entities max

---

## 💡 Optimization Tips

### 1. Use API Providers Wisely

```bash
# Groq is fastest and cheapest for simple tasks
GROQ_API_KEY=gsk_...

# OpenAI for complex analysis
OPENAI_API_KEY=sk-...

# Anthropic for long context
ANTHROPIC_API_KEY=sk-ant-...
```

### 2. Monitor Resource Usage

```bash
# Check memory usage
docker stats

# Check disk usage
df -h

# Check logs for OOM errors
docker compose logs | grep -i "out of memory"
```

### 3. Tune PostgreSQL

Add to `docker-compose.yml` → `postgres` → `command`:

```yaml
postgres:
  command:
    - postgres
    - -c
    - shared_buffers=128MB
    - -c
    - effective_cache_size=256MB
    - -c
    - maintenance_work_mem=64MB
```

### 4. Tune Neo4j

Already optimized in lightweight mode:

```yaml
NEO4J_dbms_memory_heap_max__size: 256M
NEO4J_dbms_memory_pagecache_size: 128M
NEO4J_dbms_memory_transaction_max__size: 64M
```

### 5. Enable Swap (If Needed)

```bash
# Create 2GB swap file
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

**Warning**: Swap is slow, use only as emergency buffer.

---

## 📊 Monitoring

### Check Resource Usage

```bash
# Real-time stats
docker stats

# Memory usage
docker stats --format "table {{.Name}}\t{{.MemUsage}}"

# CPU usage
docker stats --format "table {{.Name}}\t{{.CPUPerc}}"
```

### Check Service Health

```bash
# All services
docker compose ps

# Specific service
docker compose logs gateway

# Follow logs
docker compose logs -f --tail=100
```

### Check Database Sizes

```bash
# PostgreSQL
docker exec cyberintel-postgres psql -U cyberintel -c "SELECT pg_size_pretty(pg_database_size('cyberintel'));"

# Neo4j
docker exec cyberintel-neo4j du -sh /data

# Redis
docker exec cyberintel-redis redis-cli INFO memory | grep used_memory_human
```

---

## 🆘 Troubleshooting

### Problem: Out of Memory

**Symptoms**: Services crashing, OOM errors in logs

**Solutions**:
1. Enable swap (see above)
2. Reduce concurrent scans
3. Restart services: `docker compose restart`
4. Upgrade VPS to 8 GB RAM

### Problem: Slow Performance

**Symptoms**: Long response times, timeouts

**Solutions**:
1. Check resource usage: `docker stats`
2. Reduce concurrent operations
3. Increase CPU limits in docker-compose.yml
4. Upgrade VPS to 4 vCPU

### Problem: Services Not Starting

**Symptoms**: Services stuck in "starting" state

**Solutions**:
1. Check logs: `docker compose logs <service>`
2. Increase start_period in healthchecks
3. Wait longer (databases need time)
4. Check disk space: `df -h`

### Problem: Database Connection Errors

**Symptoms**: "Connection refused" errors

**Solutions**:
1. Wait for databases to be healthy
2. Check health: `docker compose ps`
3. Restart databases: `docker compose restart postgres neo4j redis`
4. Check network: `docker network ls`

---

## 📈 Upgrade Path

### From 4 GB to 8 GB VPS

**Benefits**:
- 2x performance
- More concurrent users
- Larger cache
- Better stability

**Steps**:
1. Upgrade VPS plan
2. Increase resource limits in docker-compose.yml
3. Restart: `docker compose down && docker compose up -d`

### From 8 GB to 16 GB VPS (FULL MODE)

**Benefits**:
- Enable Elasticsearch (full-text search)
- Enable Ollama (local AI)
- Enable Neo4j plugins (advanced algorithms)
- Production-ready performance

**Steps**:
1. Upgrade VPS plan
2. Follow "How to Re-Enable FULL MODE" above
3. Restart: `docker compose down && docker compose up -d`

---

## 🎯 Recommended VPS Providers

### Budget ($10-20/month)

- **DigitalOcean**: Droplet 2 vCPU, 4 GB RAM
- **Linode**: Nanode 2 vCPU, 4 GB RAM
- **Vultr**: Cloud Compute 2 vCPU, 4 GB RAM
- **Hetzner**: CX21 2 vCPU, 4 GB RAM (Europe)

### Recommended ($40-60/month)

- **DigitalOcean**: Droplet 4 vCPU, 8 GB RAM
- **Linode**: Dedicated 4 vCPU, 8 GB RAM
- **Vultr**: High Frequency 4 vCPU, 8 GB RAM

### Full Mode ($200-400/month)

- **DigitalOcean**: CPU-Optimized 8 vCPU, 16 GB RAM
- **AWS**: t3.2xlarge 8 vCPU, 32 GB RAM
- **GCP**: n2-standard-8 8 vCPU, 32 GB RAM
- **Azure**: Standard_D8s_v3 8 vCPU, 32 GB RAM

---

## 📝 Summary

### Current Mode: LIGHTWEIGHT VPS ✅

**Resources**:
- RAM: ~3.5 GB (fits in 4 GB VPS)
- CPU: ~5 vCPU total (fits in 2 vCPU VPS)
- Storage: ~10 GB

**Services Active**: 12/14
- ✅ PostgreSQL, Neo4j, Redis
- ✅ Gateway, Backend, Orchestrator
- ✅ AI Router, Graph Engine
- ✅ Workers, Frontend, Telegram Bot, Ingestion Worker
- ❌ Elasticsearch (disabled)
- ❌ Ollama (disabled)

**Limitations**:
- No full-text search
- No local AI (use API providers)
- Reduced performance
- Limited scalability

**Best For**:
- Development
- Staging
- Small deployments
- Budget-conscious users
- API-based AI workflows

**Cost**: $10-20/month 💰

---

**To switch to FULL MODE**: See "How to Re-Enable FULL MODE" section above  
**Current Configuration**: `docker-compose.yml` (already in lightweight mode)  
**Validation**: `docker compose config` ✅ PASSED

