# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│              Dashboard | Graph | Intel Feed | Chat           │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    API Gateway (Fastify)                     │
│              Auth | Rate Limit | WebSocket Proxy             │
└─────────┬──────────────────────────────────────┬────────────┘
          │                                      │
┌─────────▼─────────┐                 ┌─────────▼──────────┐
│   Orchestrator    │◄────────────────►│    AI Router       │
│  (Task Manager)   │                 │ (Multi-Provider)   │
└─────────┬─────────┘                 └────────────────────┘
          │
┌─────────▼─────────────────────────────────────────────────┐
│                      Agent System                          │
│  Recon | DNS | Threat | IOC | Graph | Entity | Report     │
└─────────┬─────────────────────────────────────────────────┘
          │
┌─────────▼─────────────────────────────────────────────────┐
│                    Integration Layer                       │
│  Shodan | VT | Censys | URLScan | SecurityTrails | etc.   │
└─────────┬─────────────────────────────────────────────────┘
          │
┌─────────▼─────────────────────────────────────────────────┐
│                      Data Layer                            │
│  PostgreSQL | Neo4j | Redis | Elasticsearch               │
└───────────────────────────────────────────────────────────┘
```

## Components

### Frontend
- **Technology**: React + Vite + TypeScript
- **State Management**: Zustand
- **Data Fetching**: React Query
- **Styling**: Tailwind CSS
- **Graph Visualization**: Cytoscape.js
- **Real-time**: WebSocket

### API Gateway
- **Technology**: Fastify (Node.js)
- **Responsibilities**:
  - Authentication & Authorization
  - Rate limiting
  - Request routing
  - WebSocket management
  - API aggregation

### Orchestrator
- **Technology**: Fastify (Node.js)
- **Responsibilities**:
  - Task queue management
  - Workflow orchestration
  - Agent coordination
  - Task scheduling
  - Retry logic

### AI Router
- **Technology**: Fastify (Node.js)
- **Responsibilities**:
  - Multi-provider AI routing
  - Fallback handling
  - Usage tracking
  - Cost optimization
  - Streaming support

### Agents (Python)
- **Recon Agent**: Initial reconnaissance
- **DNS Agent**: DNS intelligence
- **Threat Intel Agent**: Threat intelligence gathering
- **IOC Agent**: IOC detection and correlation
- **Graph Agent**: Graph analysis
- **Entity Resolution Agent**: Entity linking
- **Attack Surface Agent**: Attack surface mapping
- **Report Agent**: Report generation

### Workers (Python)
- **Technology**: Python + asyncio
- **Responsibilities**:
  - Task execution
  - Agent invocation
  - Result persistence
  - Error handling

### Graph Engine
- **Technology**: Fastify + Neo4j
- **Responsibilities**:
  - Graph operations
  - Relationship management
  - Path finding
  - Graph queries

### Integrations
- **Technology**: TypeScript
- **Providers**:
  - Shodan
  - VirusTotal
  - AbuseIPDB
  - URLScan
  - SecurityTrails
  - GreyNoise
  - AlienVault OTX
  - DNS/WHOIS

## Data Flow

### Scan Workflow

1. **User initiates scan** → Frontend
2. **Create scan request** → API Gateway
3. **Authenticate & validate** → API Gateway
4. **Create scan record** → PostgreSQL
5. **Create workflow** → Orchestrator
6. **Enqueue tasks** → Redis Queue
7. **Workers pick tasks** → Workers
8. **Execute agents** → Agents
9. **Call integrations** → Integration Layer
10. **Store results** → PostgreSQL + Neo4j
11. **Publish updates** → Redis Pub/Sub
12. **WebSocket broadcast** → Frontend

### AI Analysis Flow

1. **Agent needs AI** → Agent
2. **Send request** → AI Router
3. **Select provider** → AI Router
4. **Call AI API** → Provider (Ollama/OpenAI/etc)
5. **Return response** → Agent
6. **Process result** → Agent

## Data Stores

### PostgreSQL
- Users
- Scans
- Entities
- IOCs
- Timeline events
- Audit logs

### Neo4j
- Entity nodes
- Relationships
- Graph structure
- Attack chains

### Redis
- Task queue
- Caching
- Session storage
- Pub/Sub messaging

### Elasticsearch
- Full-text search
- Log aggregation
- Analytics

## Security

### Authentication
- JWT-based authentication
- Token expiration
- Refresh tokens

### Authorization
- Role-based access control (RBAC)
- Resource-level permissions
- Audit logging

### API Security
- Rate limiting
- Input validation
- SQL injection prevention
- XSS protection

## Scalability

### Horizontal Scaling
- Multiple worker instances
- Load-balanced API gateway
- Distributed caching

### Vertical Scaling
- Database optimization
- Connection pooling
- Query optimization

### Async Processing
- Task queues
- Event-driven architecture
- Non-blocking I/O

## Monitoring

### Metrics
- Request rates
- Response times
- Error rates
- Queue depth
- Resource usage

### Logging
- Structured logging
- Log levels
- Correlation IDs
- Centralized aggregation

### Alerting
- Service health
- Error thresholds
- Performance degradation
- Resource exhaustion
