# 🛡️ CyberIntel Platform - Hardening Implementation Plan

**Status**: IN PROGRESS  
**Timeline**: 3-4 weeks  
**Priority**: CRITICAL

---

## 📋 Overview

This document outlines the step-by-step plan to transform the CyberIntel Platform from a functional prototype into a production-grade system.

---

## PHASE 1: CRITICAL INFRASTRUCTURE (Week 1, Days 1-2)

### ✅ Task 1.1: Add Health Checks to All Services

**Status**: IN PROGRESS

**Services to Update**:
- [x] Gateway - Add `/health` endpoint
- [x] Backend - Add `/health` endpoint  
- [ ] Orchestrator - Add `/health` endpoint
- [ ] AI Router - Add `/health` endpoint
- [ ] Graph Engine - Add `/health` endpoint
- [ ] Telegram Bot - Add `/health` endpoint

**Implementation**:
```typescript
// Standard health check endpoint
fastify.get('/health', async () => {
  return {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'service-name',
    version: '1.0.0',
    uptime: process.uptime(),
  };
});
```

**Docker Healthcheck**:
```yaml
healthcheck:
  test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:PORT/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Task 1.2: Fix Docker Startup Dependencies

**Status**: IN PROGRESS

**Changes**:
- Replace `depends_on` with `depends_on: condition: service_healthy`
- Add restart policies: `restart: unless-stopped`
- Add proper networks configuration
- Add resource limits

**Example**:
```yaml
depends_on:
  postgres:
    condition: service_healthy
  redis:
    condition: service_healthy
```

### Task 1.3: Add Global Error Handlers

**Status**: PENDING

**Implementation for Each Service**:
```typescript
// Global error handler
fastify.setErrorHandler((error, request, reply) => {
  logger.error('Unhandled error', error, {
    requestId: request.id,
    path: request.url,
    method: request.method,
  });

  const statusCode = error.statusCode || 500;
  const message = statusCode === 500 
    ? 'Internal server error' 
    : error.message;

  reply.status(statusCode).send({
    error: {
      message,
      code: error.code || 'INTERNAL_ERROR',
      requestId: request.id,
    },
  });
});
```

---

## PHASE 2: SECURITY HARDENING (Week 1, Days 3-5)

### Task 2.1: Add Input Validation

**Status**: PENDING

**Implementation**:
- Use Zod schemas for all API inputs
- Validate query parameters
- Validate request bodies
- Sanitize user inputs

**Example**:
```typescript
import { z } from 'zod';

const CreateScanSchema = z.object({
  target: z.string().min(1).max(255),
  targetType: z.nativeEnum(EntityType),
  modules: z.array(z.string()).optional(),
  depth: z.number().min(1).max(5).optional(),
});

fastify.post('/api/scans', async (request, reply) => {
  const validated = CreateScanSchema.parse(request.body);
  // ... rest of logic
});
```

### Task 2.2: Fix SQL Injection Vulnerabilities

**Status**: PENDING

**Changes**:
- Replace string concatenation with parameterized queries
- Use ORM/query builder properly
- Validate all inputs

**Before**:
```typescript
// VULNERABLE
const query = `SELECT * FROM users WHERE email = '${email}'`;
```

**After**:
```typescript
// SAFE
const query = 'SELECT * FROM users WHERE email = $1';
const result = await pool.query(query, [email]);
```

### Task 2.3: Add Rate Limiting

**Status**: PARTIAL (Gateway only)

**Implementation**:
- Add rate limiting to all public endpoints
- Different limits for different endpoint types
- Store limits in Redis

**Example**:
```typescript
await fastify.register(rateLimit, {
  max: 100,
  timeWindow: '15 minutes',
  redis,
  keyGenerator: (request) => {
    return request.headers['x-real-ip'] || request.ip;
  },
});
```

### Task 2.4: Add Request Timeouts

**Status**: PENDING

**Implementation**:
- Add timeouts to all external HTTP requests
- Add timeouts to database queries
- Add timeouts to AI provider calls

**Example**:
```typescript
const response = await axios.get(url, {
  timeout: 30000, // 30 seconds
  signal: AbortSignal.timeout(30000),
});
```

### Task 2.5: Add CORS Configuration

**Status**: PARTIAL

**Implementation**:
- Proper CORS configuration
- Whitelist allowed origins
- Handle preflight requests

---

## PHASE 3: ERROR HANDLING & RETRY LOGIC (Week 1-2)

### Task 3.1: Add Retry Logic for External Calls

**Status**: PENDING

**Implementation**:
```typescript
import pRetry from 'p-retry';

async function callExternalAPI(url: string) {
  return pRetry(
    async () => {
      const response = await axios.get(url);
      if (response.status >= 500) {
        throw new Error('Server error');
      }
      return response.data;
    },
    {
      retries: 3,
      factor: 2,
      minTimeout: 1000,
      maxTimeout: 10000,
      onFailedAttempt: (error) => {
        logger.warn(`Attempt ${error.attemptNumber} failed`, {
          retriesLeft: error.retriesLeft,
        });
      },
    }
  );
}
```

### Task 3.2: Add Circuit Breakers

**Status**: PENDING

**Implementation**:
```typescript
import CircuitBreaker from 'opossum';

const breaker = new CircuitBreaker(callExternalAPI, {
  timeout: 30000,
  errorThresholdPercentage: 50,
  resetTimeout: 30000,
});

breaker.fallback(() => {
  return { cached: true, data: getCachedData() };
});
```

### Task 3.3: Add Dead Letter Queues

**Status**: PENDING

**Implementation**:
- Failed tasks go to DLQ
- Retry logic for DLQ
- Manual intervention for persistent failures

---

## PHASE 4: OBSERVABILITY (Week 2)

### Task 4.1: Add Prometheus Metrics

**Status**: PENDING

**Metrics to Track**:
- HTTP request duration
- HTTP request count by status code
- Active connections
- Queue depth
- Task processing time
- AI provider latency
- Database query time
- Cache hit/miss ratio

**Implementation**:
```typescript
import promClient from 'prom-client';

const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
});

// Middleware
fastify.addHook('onResponse', (request, reply, done) => {
  const duration = reply.getResponseTime() / 1000;
  httpRequestDuration
    .labels(request.method, request.routerPath, reply.statusCode.toString())
    .observe(duration);
  done();
});
```

### Task 4.2: Add Request ID Tracking

**Status**: PENDING

**Implementation**:
```typescript
import { v4 as uuidv4 } from 'uuid';

fastify.addHook('onRequest', (request, reply, done) => {
  request.id = request.headers['x-request-id'] || uuidv4();
  reply.header('x-request-id', request.id);
  done();
});
```

### Task 4.3: Structured Logging

**Status**: PARTIAL (Logger exists)

**Enhancement**:
- Add request ID to all logs
- Add user ID to all logs
- Add scan ID to all logs
- JSON format for production

---

## PHASE 5: DATABASE & QUEUE RELIABILITY (Week 2-3)

### Task 5.1: Add Database Migrations

**Status**: PENDING

**Tool**: node-pg-migrate or Prisma

**Implementation**:
```bash
npm install node-pg-migrate
```

```javascript
// migrations/001_initial_schema.js
exports.up = (pgm) => {
  pgm.createTable('users', {
    id: { type: 'uuid', primaryKey: true },
    email: { type: 'varchar(255)', notNull: true, unique: true },
    // ... rest of schema
  });
};

exports.down = (pgm) => {
  pgm.dropTable('users');
};
```

### Task 5.2: Add Connection Pooling

**Status**: PARTIAL

**Enhancement**:
- Configure pool size
- Add connection timeout
- Add idle timeout
- Monitor pool metrics

### Task 5.3: Add Queue Reliability

**Status**: PENDING

**Features**:
- Task persistence
- Idempotency keys
- Distributed locks
- Worker heartbeats
- Task cancellation

---

## PHASE 6: TESTING (Week 3)

### Task 6.1: Unit Tests

**Status**: PENDING

**Coverage Target**: >70%

**Framework**: Jest or Vitest

**Example**:
```typescript
describe('TaskQueue', () => {
  it('should add task to queue', async () => {
    const queue = new TaskQueue(redis);
    const taskId = await queue.addTask({
      type: 'scan',
      payload: { target: 'example.com' },
    });
    expect(taskId).toBeDefined();
  });
});
```

### Task 6.2: Integration Tests

**Status**: PENDING

**Tests**:
- API endpoint tests
- Database integration tests
- Queue integration tests
- WebSocket tests

### Task 6.3: E2E Tests

**Status**: PENDING

**Scenarios**:
- Complete scan workflow
- User registration and login
- Graph exploration
- Report generation

---

## PHASE 7: PERFORMANCE OPTIMIZATION (Week 3-4)

### Task 7.1: Add Caching

**Status**: PENDING

**Implementation**:
- Cache API responses
- Cache database queries
- Cache AI responses
- TTL configuration

### Task 7.2: Optimize Database Queries

**Status**: PENDING

**Actions**:
- Add indexes
- Optimize N+1 queries
- Use connection pooling
- Add query timeouts

### Task 7.3: Add Pagination

**Status**: PENDING

**Implementation**:
- Cursor-based pagination
- Limit/offset pagination
- Default page size: 50
- Max page size: 1000

---

## PHASE 8: PRODUCTION READINESS (Week 4)

### Task 8.1: Environment Configuration

**Status**: PENDING

**Files**:
- `.env.example` - Complete template
- `.env.development` - Dev defaults
- `.env.production` - Prod template
- `.env.test` - Test configuration

### Task 8.2: Production Docker Compose

**Status**: PARTIAL

**Enhancements**:
- Remove volume mounts
- Use built images
- Add resource limits
- Add logging configuration
- Add secrets management

### Task 8.3: Deployment Scripts

**Status**: PENDING

**Scripts**:
- `scripts/deploy.sh` - Deploy to production
- `scripts/backup.sh` - Backup databases
- `scripts/restore.sh` - Restore from backup
- `scripts/rollback.sh` - Rollback deployment

### Task 8.4: Monitoring Setup

**Status**: PENDING

**Tools**:
- Prometheus for metrics
- Grafana for dashboards
- Loki for logs (optional)
- Alertmanager for alerts

---

## 📊 Progress Tracking

### Week 1 Progress

- [x] Audit complete
- [x] Hardening plan created
- [ ] Health checks added (50%)
- [ ] Docker dependencies fixed (50%)
- [ ] Error handlers added (0%)
- [ ] Input validation added (0%)
- [ ] SQL injection fixed (0%)

### Week 2 Progress

- [ ] Retry logic added
- [ ] Circuit breakers added
- [ ] Metrics added
- [ ] Request tracking added
- [ ] Database migrations added

### Week 3 Progress

- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Caching added
- [ ] Performance optimized

### Week 4 Progress

- [ ] Production config complete
- [ ] Deployment scripts ready
- [ ] Monitoring setup
- [ ] Documentation updated

---

## 🎯 Success Criteria

### Must Have (P0)

- [x] All services have health checks
- [ ] All services handle errors gracefully
- [ ] All inputs are validated
- [ ] No SQL injection vulnerabilities
- [ ] All external calls have retries
- [ ] All external calls have timeouts
- [ ] Docker compose works end-to-end

### Should Have (P1)

- [ ] Test coverage >70%
- [ ] Prometheus metrics exposed
- [ ] Request ID tracking
- [ ] Database migrations
- [ ] Production docker-compose
- [ ] Deployment scripts

### Nice to Have (P2)

- [ ] Circuit breakers
- [ ] Distributed tracing
- [ ] Grafana dashboards
- [ ] E2E tests
- [ ] Performance benchmarks

---

## 📝 Next Steps

1. **Today**: Complete health checks for all services
2. **Tomorrow**: Fix Docker dependencies and add error handlers
3. **Day 3**: Add input validation and fix SQL injection
4. **Day 4-5**: Add retry logic and timeouts
5. **Week 2**: Observability and database reliability
6. **Week 3**: Testing
7. **Week 4**: Production readiness

---

**Last Updated**: 2024-12-XX  
**Next Review**: Daily during hardening phase
