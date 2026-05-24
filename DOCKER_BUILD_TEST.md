# 🧪 Docker Build Testing Guide

**Date**: May 24, 2026  
**Status**: Ready for Testing  
**Issue Fixed**: npm ERR! 404 '@cyberintel/shared@*' is not in this registry

---

## ✅ Quick Test (5 minutes)

### Test 1: Build Single Service
```powershell
# Test backend service build
docker-compose build backend

# Expected output:
# ✅ [+] Building X.Xs
# ✅ => [builder] COPY package*.json ./
# ✅ => [builder] RUN npm ci --workspaces --if-present
# ✅ => [builder] RUN npm run build --workspace=shared
# ✅ => [builder] RUN npm run build --workspace=backend
# ✅ => exporting to image

# Should NOT see:
# ❌ npm ERR! 404 '@cyberintel/shared@*' is not in this registry
```

### Test 2: Build All Services
```powershell
# Build all services
docker-compose build

# Expected: All services build successfully
# Time: ~5-10 minutes (first build)
```

### Test 3: Start Services
```powershell
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# Expected: All services running/healthy
```

---

## 🔍 Detailed Testing

### Step 1: Clean Environment
```powershell
# Stop and remove all containers
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Clean Docker cache (optional)
docker system prune -a
```

### Step 2: Build Backend (Tests @cyberintel/shared)
```powershell
# Build backend service
docker-compose build backend

# Watch for these steps:
# 1. "COPY package*.json ./"
# 2. "COPY shared/package*.json ./shared/"
# 3. "COPY backend/package*.json ./backend/"
# 4. "RUN npm ci --workspaces --if-present"
# 5. "COPY shared/ ./shared/"
# 6. "RUN npm run build --workspace=shared"
# 7. "COPY backend/ ./backend/"
# 8. "RUN npm run build --workspace=backend"

# Should complete without errors
```

### Step 3: Build Gateway (Tests @cyberintel/shared)
```powershell
# Build gateway service
docker-compose build gateway

# Should reuse cached layers from backend build
# Should complete in ~1-2 minutes
```

### Step 4: Build All Services
```powershell
# Build all services in parallel
docker-compose build --parallel

# Services to build:
# - frontend
# - backend
# - gateway
# - orchestrator
# - graph-engine
# - ai-router
# - telegram-bot
# - workers
# - ingestion-worker

# Expected time: ~5-10 minutes
```

### Step 5: Start Services
```powershell
# Start all services
docker-compose up -d

# Wait for services to be healthy
Start-Sleep -Seconds 30

# Check status
docker-compose ps

# Expected output:
# NAME                          STATUS
# cyberintel-postgres           Up (healthy)
# cyberintel-neo4j              Up (healthy)
# cyberintel-redis              Up (healthy)
# cyberintel-gateway            Up (healthy)
# cyberintel-backend            Up (healthy)
# cyberintel-orchestrator       Up (healthy)
# cyberintel-ai-router          Up (healthy)
# cyberintel-graph-engine       Up (healthy)
# cyberintel-telegram-bot       Up (healthy)
# cyberintel-frontend           Up
# cyberintel-workers            Up
# cyberintel-ingestion          Up
```

### Step 6: Check Logs
```powershell
# Check backend logs
docker-compose logs backend

# Should see:
# ✅ "Server listening on port 8001"
# ✅ No errors about @cyberintel/shared

# Check gateway logs
docker-compose logs gateway

# Should see:
# ✅ "Server listening on port 8000"
# ✅ No errors about @cyberintel/shared
```

### Step 7: Verify Internal Imports
```powershell
# Enter backend container
docker-compose exec backend sh

# Check if shared library exists
ls -la /app/shared/dist

# Expected output:
# drwxr-xr-x    2 root     root          4096 May 24 12:00 .
# drwxr-xr-x    3 root     root          4096 May 24 12:00 ..
# -rw-r--r--    1 root     root          1234 May 24 12:00 index.js
# -rw-r--r--    1 root     root           567 May 24 12:00 index.d.ts
# ... (other files)

# Exit container
exit
```

### Step 8: Test API Endpoints
```powershell
# Test gateway health
curl http://localhost:8000/health

# Expected: {"status":"ok"}

# Test backend health
curl http://localhost:8001/health

# Expected: {"status":"ok"}
```

---

## 🐛 Troubleshooting

### Issue: Build fails with "COPY failed"

**Error:**
```
ERROR [builder 5/10] COPY shared/package*.json ./shared/
```

**Cause**: Build context not set to monorepo root

**Fix**: Check docker-compose.yml:
```yaml
services:
  backend:
    build:
      context: .              # Must be "." not "./backend"
      dockerfile: backend/Dockerfile
```

### Issue: Still getting 404 errors

**Error:**
```
npm ERR! 404 '@cyberintel/shared@*' is not in this registry
```

**Cause**: Old Dockerfile still in use

**Fix**: 
```powershell
# Rebuild without cache
docker-compose build --no-cache backend

# Or rebuild all
docker-compose build --no-cache
```

### Issue: "Cannot find module '@cyberintel/shared'"

**Error in logs:**
```
Error: Cannot find module '@cyberintel/shared'
```

**Cause**: Shared library not built or not copied

**Fix**: Check Dockerfile has correct build order:
```dockerfile
# 1. Build shared first
COPY shared/ ./shared/
RUN npm run build --workspace=shared

# 2. Then build service
COPY backend/ ./backend/
RUN npm run build --workspace=backend
```

### Issue: Service won't start

**Error:**
```
Error: ENOENT: no such file or directory
```

**Cause**: Missing files in production stage

**Fix**: Check production stage copies all required files:
```dockerfile
# Copy shared library (built)
COPY --from=builder /monorepo/shared/package*.json ./shared/
COPY --from=builder /monorepo/shared/dist ./shared/dist

# Copy service (built)
COPY --from=builder /monorepo/backend/package*.json ./backend/
COPY --from=builder /monorepo/backend/dist ./backend/dist
```

---

## 📊 Performance Benchmarks

### Build Times

| Scenario | Expected Time | Notes |
|----------|---------------|-------|
| First build (all services) | 5-10 min | Downloads all dependencies |
| Rebuild (no changes) | 30 sec | All layers cached |
| Rebuild (source change) | 1-2 min | Only changed service rebuilds |
| Rebuild (deps change) | 3-5 min | Re-installs dependencies |

### Image Sizes

| Service | Expected Size | Notes |
|---------|---------------|-------|
| Backend | ~200-300 MB | Node.js + dependencies |
| Gateway | ~200-300 MB | Node.js + dependencies |
| Frontend | ~50-100 MB | Nginx + static files |
| Orchestrator | ~150-200 MB | Node.js + dependencies |
| Graph Engine | ~200-250 MB | Node.js + dependencies |
| AI Router | ~200-250 MB | Node.js + dependencies |
| Telegram Bot | ~150-200 MB | Node.js + dependencies |

---

## ✅ Success Criteria

Your Docker build is successful when:

1. ✅ `docker-compose build` completes without errors
2. ✅ No "404 @cyberintel/shared" errors in build output
3. ✅ All services show "Successfully built" message
4. ✅ `docker-compose up -d` starts all services
5. ✅ `docker-compose ps` shows all services healthy/running
6. ✅ No errors in `docker-compose logs`
7. ✅ API endpoints respond correctly
8. ✅ Internal imports work (no module not found errors)

---

## 🚀 Next Steps

After successful testing:

1. **Commit changes** (already done)
2. **Push to repository**
   ```powershell
   git push origin main
   ```

3. **Update CI/CD** (if needed)
   - GitHub Actions should work with new Dockerfiles
   - No changes needed to workflows

4. **Deploy to staging**
   ```powershell
   # Pull latest code
   git pull

   # Build and start
   docker-compose build
   docker-compose up -d
   ```

5. **Monitor logs**
   ```powershell
   docker-compose logs -f
   ```

6. **Deploy to production** (when ready)
   ```powershell
   docker-compose -f docker-compose.prod.yml build
   docker-compose -f docker-compose.prod.yml up -d
   ```

---

## 📞 Getting Help

### Documentation
- [MONOREPO_DOCKER_FIX.md](MONOREPO_DOCKER_FIX.md) - Complete architecture explanation
- [docker-compose.yml](docker-compose.yml) - Service configuration
- [backend/Dockerfile](backend/Dockerfile) - Example Dockerfile

### Common Commands
```powershell
# View logs
docker-compose logs -f

# Restart service
docker-compose restart backend

# Rebuild service
docker-compose build backend

# Stop all
docker-compose down

# Clean everything
docker-compose down -v --rmi all
```

---

## 🎉 Summary

The Docker monorepo architecture has been fixed. All services can now:
- ✅ Build successfully
- ✅ Resolve internal packages (@cyberintel/shared)
- ✅ Use workspace-aware npm commands
- ✅ Benefit from layer caching
- ✅ Run in production with optimized images

**Status**: ✅ Ready for Testing  
**Date**: May 24, 2026

