# Frequently Asked Questions

## General

### What is CyberIntel Platform?

CyberIntel is an AI-powered cyber intelligence platform that combines OSINT, threat intelligence, graph analytics, and autonomous AI agents for comprehensive security analysis.

### Is it free?

Yes, the platform is open source under MIT license. However, some integrations require paid API keys.

### What are the system requirements?

- 16GB RAM minimum (32GB recommended)
- 50GB disk space
- Docker & Docker Compose
- Node.js 20+
- Python 3.11+

## Setup & Installation

### How do I get API keys?

Visit each provider's website:
- Shodan: https://account.shodan.io/
- VirusTotal: https://www.virustotal.com/gui/join-us
- AbuseIPDB: https://www.abuseipdb.com/register
- URLScan: https://urlscan.io/user/signup
- SecurityTrails: https://securitytrails.com/app/signup
- GreyNoise: https://viz.greynoise.io/signup
- AlienVault: https://otx.alienvault.com/

### Can I run without API keys?

Yes, but functionality will be limited. DNS, WHOIS, and local analysis will still work.

### How do I update the platform?

```bash
git pull
npm install
docker-compose build
docker-compose up -d
```

## Usage

### How do I create a scan?

1. Login to the platform
2. Click "New Scan"
3. Enter target (domain/IP)
4. Click "Start Scan"

### What targets are supported?

- Domains (example.com)
- IP addresses (1.2.3.4)
- URLs (https://example.com)
- Email addresses
- File hashes

### How long does a scan take?

Depends on:
- Target complexity
- Number of integrations
- API rate limits
- System resources

Typical scan: 2-10 minutes

### Can I scan multiple targets?

Yes, create multiple scans. They run in parallel based on worker capacity.

## AI Features

### Which AI providers are supported?

- Ollama (local)
- OpenAI
- Anthropic Claude
- OpenRouter
- Groq
- DeepSeek

### Do I need an AI API key?

Not if using Ollama locally. Other providers require API keys.

### How do I use local AI?

1. Ollama is included in docker-compose
2. Pull a model: `docker-compose exec ollama ollama pull llama3.1:8b`
3. Set `DEFAULT_AI_PROVIDER=ollama` in .env

### What can the AI analyst do?

- Analyze scan results
- Explain threats
- Correlate IOCs
- Generate reports
- Answer questions
- Provide recommendations

## Data & Privacy

### Where is data stored?

- PostgreSQL: Relational data
- Neo4j: Graph data
- Redis: Cache and queues
- Elasticsearch: Search and logs

### Is data encrypted?

- At rest: Configure database encryption
- In transit: Use HTTPS in production

### Can I export data?

Yes, via:
- API endpoints
- Database dumps
- Report exports

### How do I backup data?

See [Deployment Guide](DEPLOYMENT.md#backup)

## Performance

### How do I scale the platform?

- Increase worker instances
- Add more Redis nodes
- Scale PostgreSQL
- Use load balancer

### What's the maximum throughput?

Depends on:
- Hardware resources
- API rate limits
- Worker count
- Database performance

### How do I optimize performance?

1. Increase worker concurrency
2. Enable Redis persistence
3. Optimize database queries
4. Use connection pooling
5. Cache frequently accessed data

## Troubleshooting

### Services won't start

Check:
- Docker resources
- Port availability
- Service logs
- Environment variables

### Database connection errors

Verify:
- DATABASE_URL is correct
- PostgreSQL is running
- Credentials are valid
- Network connectivity

### Worker not processing tasks

Check:
- Redis connection
- Worker logs
- Queue status
- Task errors

### API rate limit errors

Solutions:
- Reduce scan frequency
- Upgrade API plans
- Enable caching
- Use multiple API keys

## Security

### Is it secure?

Security features:
- JWT authentication
- RBAC authorization
- Rate limiting
- Input validation
- Audit logging

### Should I use in production?

Yes, but:
- Change default credentials
- Use HTTPS
- Secure API keys
- Enable monitoring
- Regular updates

### How do I report security issues?

Email: security@cyberintel.local (or create private GitHub issue)

## Development

### How do I contribute?

See [CONTRIBUTING.md](../CONTRIBUTING.md)

### How do I add integrations?

See [Integration Guide](INTEGRATIONS.md#adding-new-integrations)

### How do I create custom agents?

See [Agent System](AGENTS.md#adding-new-agents)

### Where are the tests?

```bash
npm test                    # All tests
npm run test:unit          # Unit tests
npm run test:integration   # Integration tests
```

## Support

### Where can I get help?

- GitHub Issues
- Documentation
- Community Discord/Slack

### How do I report bugs?

Create a GitHub issue with:
- Description
- Steps to reproduce
- Expected behavior
- Actual behavior
- Logs/screenshots

### Can I request features?

Yes! Create a GitHub issue with:
- Feature description
- Use case
- Implementation ideas
