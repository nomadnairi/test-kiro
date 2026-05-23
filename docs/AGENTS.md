# AI Agent System

## Overview

The CyberIntel Platform uses a multi-agent architecture where specialized AI agents handle different aspects of cyber intelligence analysis.

## Agent Types

### 1. Recon Agent
**Purpose**: Initial reconnaissance and asset discovery

**Capabilities**:
- DNS enumeration
- Subdomain discovery
- WHOIS lookups
- Port scanning integration
- Asset inventory

**Workflow**:
1. Receive target (domain/IP)
2. Enumerate DNS records
3. Discover subdomains
4. Gather WHOIS data
5. Identify related assets
6. Return entity list

### 2. DNS Agent
**Purpose**: Deep DNS intelligence gathering

**Capabilities**:
- DNS record analysis
- Historical DNS data
- DNS security checks
- Nameserver analysis
- Zone transfer attempts

### 3. Threat Intel Agent
**Purpose**: Gather threat intelligence from multiple sources

**Capabilities**:
- Multi-source reputation checks
- IOC correlation
- Threat actor attribution
- Campaign identification
- Risk scoring

**Integrations**:
- VirusTotal
- AbuseIPDB
- GreyNoise
- AlienVault OTX
- URLScan

### 4. IOC Agent
**Purpose**: Detect and correlate indicators of compromise

**Capabilities**:
- IOC extraction
- Pattern identification
- Temporal analysis
- Attack chain reconstruction
- False positive filtering

### 5. Graph Analysis Agent
**Purpose**: Analyze entity relationships and network structure

**Capabilities**:
- Cluster identification
- Centrality analysis
- Path finding
- Community detection
- Attack chain visualization

### 6. Entity Resolution Agent
**Purpose**: Link and deduplicate entities

**Capabilities**:
- Entity matching
- Relationship inference
- Confidence scoring
- Conflict resolution
- Identity linking

### 7. Attack Surface Agent
**Purpose**: Map and analyze attack surface

**Capabilities**:
- Exposed asset identification
- Vulnerability correlation
- Risk assessment
- Entry point analysis
- Mitigation recommendations

### 8. Report Agent
**Purpose**: Generate comprehensive intelligence reports

**Capabilities**:
- Executive summaries
- Technical findings
- Threat assessments
- Recommendations
- Export formats (PDF, JSON, HTML)

## Agent Communication

Agents communicate through:
- **Task Queue**: Redis-based task distribution
- **Event Bus**: Real-time event publishing
- **Shared State**: PostgreSQL + Neo4j
- **AI Router**: Centralized AI API access

## Agent Workflow

```
1. Orchestrator creates workflow
2. Tasks enqueued in priority order
3. Workers pick tasks from queue
4. Workers invoke appropriate agents
5. Agents execute logic
6. Agents call integrations
7. Agents use AI for analysis
8. Results stored in databases
9. Events published to subscribers
10. Frontend receives updates
```

## Adding New Agents

1. Create agent class extending `BaseAgent`
2. Implement `execute()` method
3. Add agent to worker registry
4. Update orchestrator workflows
5. Add tests
6. Document capabilities

Example:

```python
from base_agent import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self, ai_router_url: str):
        super().__init__("CUSTOM", ai_router_url)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Your logic here
        return results
```

## Agent Configuration

Agents are configured via environment variables:

```env
AI_ROUTER_URL=http://localhost:8003
NEO4J_URI=bolt://localhost:7687
DATABASE_URL=postgresql://...
```

## Best Practices

1. **Idempotency**: Agents should be idempotent
2. **Error Handling**: Graceful failure and retry
3. **Logging**: Structured logging with context
4. **Performance**: Async operations, connection pooling
5. **Testing**: Unit tests and integration tests
