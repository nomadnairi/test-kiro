# CyberIntel Platform API Documentation

## Base URL

```
http://localhost:8000/api
```

## Authentication

All API requests (except auth endpoints) require a JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

## Endpoints

### Authentication

#### POST /auth/register
Register a new user.

**Request:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123"
}
```

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "role": "analyst"
  },
  "token": "jwt-token"
}
```

#### POST /auth/login
Login with credentials.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "user": { ... },
  "token": "jwt-token"
}
```

### Scans

#### POST /scans
Create a new scan.

**Request:**
```json
{
  "target": "example.com",
  "targetType": "DOMAIN",
  "modules": ["dns", "whois", "shodan"],
  "depth": 2,
  "autoRecon": true
}
```

**Response:**
```json
{
  "scanId": "uuid",
  "status": "PENDING"
}
```

#### GET /scans
List all scans for the current user.

**Query Parameters:**
- `limit` (default: 50)
- `offset` (default: 0)

**Response:**
```json
{
  "scans": [
    {
      "id": "uuid",
      "target": "example.com",
      "status": "COMPLETED",
      "progress": 100,
      "entity_count": 42,
      "ioc_count": 5
    }
  ]
}
```

#### GET /scans/:scanId
Get scan details.

**Response:**
```json
{
  "id": "uuid",
  "target": "example.com",
  "status": "COMPLETED",
  "progress": 100,
  "entity_count": 42,
  "ioc_count": 5,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### GET /scans/:scanId/results
Get scan results including entities, IOCs, and relationships.

**Response:**
```json
{
  "scan": { ... },
  "entities": [ ... ],
  "iocs": [ ... ],
  "relationships": [ ... ]
}
```

### Entities

#### GET /entities
Search entities.

**Query Parameters:**
- `q` - Search query
- `type` - Entity type filter
- `limit` (default: 50)
- `offset` (default: 0)

**Response:**
```json
{
  "entities": [
    {
      "id": "uuid",
      "type": "IP",
      "value": "1.2.3.4",
      "threat_level": "MEDIUM",
      "first_seen": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### GET /entities/:entityId
Get entity details.

#### GET /entities/:entityId/relationships
Get entity relationships.

### IOCs

#### GET /iocs
Search IOCs.

**Query Parameters:**
- `q` - Search query
- `type` - IOC type filter
- `threatLevel` - Threat level filter
- `source` - Source filter
- `limit` (default: 50)
- `offset` (default: 0)

**Response:**
```json
{
  "iocs": [
    {
      "id": "uuid",
      "type": "IP",
      "value": "1.2.3.4",
      "source": "virustotal",
      "threat_level": "HIGH",
      "confidence": 95
    }
  ]
}
```

### Graph

#### POST /graph/query
Execute a Cypher query on the graph database.

**Request:**
```json
{
  "cypher": "MATCH (n:IP) RETURN n LIMIT 10",
  "params": {}
}
```

#### GET /graph/nodes/:nodeId/neighbors
Get neighboring nodes.

**Query Parameters:**
- `depth` (default: 1)

### AI Chat

#### POST /ai/chat
Send a chat message to the AI assistant.

**Request:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Analyze this IP: 1.2.3.4"
    }
  ],
  "provider": "ollama",
  "model": "llama3.1:8b"
}
```

**Response:**
```json
{
  "content": "AI response...",
  "model": "llama3.1:8b",
  "provider": "ollama"
}
```

## WebSocket

Connect to real-time updates:

```
ws://localhost:8000/ws?token=<jwt-token>
```

### Message Types

- `SCAN_UPDATE` - Scan progress updates
- `ENTITY_DISCOVERED` - New entity discovered
- `IOC_DETECTED` - IOC detected
- `TASK_UPDATE` - Task status update
- `AGENT_MESSAGE` - AI agent message
- `SYSTEM_ALERT` - System alert

## Error Responses

All errors follow this format:

```json
{
  "error": "Error message",
  "statusCode": 400,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Rate Limiting

- Default: 100 requests per 15 minutes per IP
- Authenticated: 1000 requests per 15 minutes per user
