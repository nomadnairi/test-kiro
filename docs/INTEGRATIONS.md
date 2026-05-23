# Integration Guide

## Overview

The CyberIntel Platform integrates with 20+ OSINT and threat intelligence providers.

## Supported Integrations

### Threat Intelligence

#### Shodan
- **Purpose**: Internet-connected device search
- **API Key**: Required
- **Rate Limit**: Varies by plan
- **Endpoints**: Host lookup, search
- **Setup**: Add `SHODAN_API_KEY` to .env

#### VirusTotal
- **Purpose**: File/URL/IP/domain reputation
- **API Key**: Required
- **Rate Limit**: 4 requests/minute (free)
- **Endpoints**: IP, domain, URL, hash analysis
- **Setup**: Add `VIRUSTOTAL_API_KEY` to .env

#### AbuseIPDB
- **Purpose**: IP reputation and abuse reports
- **API Key**: Required
- **Rate Limit**: 1000 requests/day (free)
- **Endpoints**: Check IP, report IP
- **Setup**: Add `ABUSEIPDB_API_KEY` to .env

#### URLScan
- **Purpose**: URL scanning and analysis
- **API Key**: Required
- **Rate Limit**: Varies
- **Endpoints**: Scan URL, search
- **Setup**: Add `URLSCAN_API_KEY` to .env

#### SecurityTrails
- **Purpose**: DNS intelligence and history
- **API Key**: Required
- **Rate Limit**: 50 requests/month (free)
- **Endpoints**: Domain details, subdomains, DNS history
- **Setup**: Add `SECURITYTRAILS_API_KEY` to .env

#### GreyNoise
- **Purpose**: Internet scanner classification
- **API Key**: Required
- **Rate Limit**: Varies
- **Endpoints**: IP lookup, context
- **Setup**: Add `GREYNOISE_API_KEY` to .env

#### AlienVault OTX
- **Purpose**: Open threat exchange
- **API Key**: Required
- **Rate Limit**: Generous
- **Endpoints**: IP/domain reputation, pulses
- **Setup**: Add `ALIENVAULT_API_KEY` to .env

### DNS & WHOIS

#### DNS Resolution
- **Purpose**: DNS record lookup
- **API Key**: Not required
- **Endpoints**: A, AAAA, MX, TXT, NS, CNAME records

#### WHOIS
- **Purpose**: Domain registration information
- **API Key**: Not required
- **Endpoints**: Domain WHOIS lookup

### Port Scanning

#### Censys
- **Purpose**: Internet-wide scanning data
- **API Key**: Required
- **Rate Limit**: Varies
- **Setup**: Add `CENSYS_API_ID` and `CENSYS_API_SECRET` to .env

## Adding New Integrations

### 1. Create Integration Class

```typescript
// integrations/src/myintegration.ts
import { BaseIntegration, IntegrationResult } from './base';

export class MyIntegration extends BaseIntegration {
  name = 'myintegration';
  private baseUrl = 'https://api.example.com';

  async lookup(target: string): Promise<IntegrationResult> {
    try {
      const response = await axios.get(`${this.baseUrl}/lookup/${target}`, {
        headers: { 'Authorization': `Bearer ${this.config.apiKey}` },
      });

      return this.createResult(response.data);
    } catch (error) {
      return this.handleError(error);
    }
  }
}
```

### 2. Register Integration

```typescript
// integrations/src/index.ts
export * from './myintegration';
```

### 3. Add to Agent

```python
# agents/threat_intel_agent.py
async def query_myintegration(self, target: str) -> Dict[str, Any]:
    # Call integration
    pass
```

### 4. Add Configuration

```env
# .env
MYINTEGRATION_API_KEY=your-api-key
```

### 5. Update Documentation

Add integration details to this file.

## Rate Limiting

All integrations respect rate limits:
- Automatic retry with exponential backoff
- Request queuing
- Rate limit tracking

## Error Handling

Integrations handle errors gracefully:
- Network errors
- API errors
- Rate limit errors
- Invalid responses

## Testing Integrations

```bash
# Test single integration
npm run test:integration -- --grep "MyIntegration"

# Test all integrations
npm run test:integration
```

## Best Practices

1. **API Keys**: Store in environment variables
2. **Rate Limits**: Respect provider limits
3. **Caching**: Cache responses when appropriate
4. **Error Handling**: Handle all error cases
5. **Logging**: Log all API calls
6. **Timeouts**: Set appropriate timeouts
7. **Retries**: Implement retry logic

## Integration Status

Check integration health:

```bash
curl http://localhost:8001/api/integrations/status
```

Response:
```json
{
  "integrations": [
    {
      "name": "shodan",
      "status": "healthy",
      "lastCheck": "2024-01-01T00:00:00Z"
    }
  ]
}
```
