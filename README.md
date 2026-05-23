# 🔍 CyberIntel AI Platform

[![Build Status](https://github.com/YOUR_USERNAME/cyberintel-platform/workflows/CI/badge.svg)](https://github.com/YOUR_USERNAME/cyberintel-platform/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D20.0.0-brightgreen)](https://nodejs.org/)
[![Python Version](https://img.shields.io/badge/python-%3E%3D3.11-blue)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-required-2496ED?logo=docker)](https://www.docker.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

> **Enterprise-grade AI-powered cyber intelligence platform** combining OSINT, threat intelligence, graph analytics, and autonomous reconnaissance capabilities.

[🚀 Quick Start](#-quick-start) • [📖 Documentation](docs/index.html) • [🤝 Contributing](CONTRIBUTING.md) • [💬 Discussions](https://github.com/YOUR_USERNAME/cyberintel-platform/discussions)

---

## ✨ Key Features

🤖 **Autonomous AI Reconnaissance** - AI-powered OSINT collection with 20+ tool integrations  
🕸️ **Graph Intelligence Engine** - Entity relationship mapping with Neo4j  
🔐 **Breach Intelligence** - Exposure analysis and credential monitoring  
📊 **Visual Intelligence Reports** - AI-generated PDF/HTML reports  
💬 **AI Analyst Chat** - Natural language queries over your data  
📡 **Real-time Threat Feeds** - Continuous intelligence ingestion  
🤖 **Telegram Bot** - Mobile access and notifications  
⚡ **Distributed Architecture** - Scalable microservices design

## 🎯 Overview

Enterprise-grade AI-powered cyber intelligence platform combining OSINT, threat intelligence, graph analytics, and autonomous reconnaissance capabilities.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│              Dashboard | Graph | Intel Feed | Chat           │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    API Gateway (FastAPI)                     │
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

## 🚀 Quick Start

### One-Command Installation

After cloning the repository, run the automatic installation script:

**Linux/Mac:**
```bash
git clone https://github.com/YOUR_USERNAME/cyberintel-platform.git
cd cyberintel-platform
chmod +x scripts/install.sh
./scripts/install.sh
```

**Windows PowerShell:**
```powershell
git clone https://github.com/YOUR_USERNAME/cyberintel-platform.git
cd cyberintel-platform
.\scripts\install.ps1
```

**Windows CMD:**
```cmd
git clone https://github.com/YOUR_USERNAME/cyberintel-platform.git
cd cyberintel-platform
scripts\install.bat
```

The installation script will automatically:
- ✅ Check prerequisites (Node.js, Python, Docker)
- ✅ Install all Node.js dependencies
- ✅ Install all Python dependencies
- ✅ Build shared libraries
- ✅ Create `.env` configuration file
- ✅ Pull Docker images

### Configure & Start

1. **Add your API keys** to `.env`:
   ```bash
   nano .env  # or use your preferred editor
   ```

2. **Start infrastructure**:
   ```bash
   docker-compose up -d
   ```

3. **Start development servers**:
   ```bash
   npm run dev
   ```

4. **Access the platform**:
   - Frontend: http://localhost:3000
   - API Gateway: http://localhost:4000
   - Neo4j Browser: http://localhost:7474
   - Documentation: Open `docs/index.html`

📚 **New to the platform?** Check out [START_HERE.md](START_HERE.md) for a detailed walkthrough!

### Prerequisites

- **Node.js 20+** - [Download](https://nodejs.org/)
- **Python 3.11+** - [Download](https://www.python.org/)
- **Docker & Docker Compose** - [Download](https://www.docker.com/)
- **16GB+ RAM** recommended for full stack

### Production Deployment

```bash
# Build all services
npm run build

# Deploy with Docker
docker-compose -f docker-compose.prod.yml up -d
```

## 📦 Monorepo Structure

```
├── frontend/          # React + Vite UI
├── backend/           # Core API services
├── gateway/           # API Gateway + Auth
├── orchestrator/      # Task orchestration engine
├── agents/            # AI agent implementations
├── workers/           # Background job processors
├── integrations/      # OSINT provider integrations
├── graph-engine/      # Neo4j graph operations
├── ai-router/         # Multi-provider AI routing
├── auth/              # Authentication service
├── shared/            # Shared libraries
├── docker/            # Docker configurations
├── scripts/           # Automation scripts
└── docs/              # Documentation
```

## 🔑 Key Features

### 🔍 OSINT Intelligence
- **20+ integrated sources**: Shodan, VirusTotal, Censys, SecurityTrails, URLScan, and more
- **Automated enrichment**: Continuous data correlation and enhancement
- **Real-time ingestion**: Live threat feed processing
- **Historical tracking**: Timeline analysis and trend detection

### 🕸️ Graph Intelligence
- **Entity relationship mapping**: Visualize connections between domains, IPs, emails, and more
- **Attack chain detection**: Identify multi-stage attack patterns
- **Infrastructure pivoting**: Discover related infrastructure automatically
- **Temporal analysis**: Track entity evolution over time

### 🤖 AI Agents
- **Autonomous reconnaissance**: AI plans and executes OSINT workflows
- **Threat analysis**: Automated IOC correlation and risk scoring
- **Report generation**: AI-generated executive and technical reports
- **Natural language queries**: Chat with your intelligence data
- **Multi-provider support**: Anthropic, OpenAI, Groq, Ollama with automatic failover

### 🎯 Attack Surface Mapping
- **Subdomain enumeration**: Amass, Subfinder, Assetfinder integration
- **Port scanning**: Nmap, Naabu integration
- **Vulnerability detection**: Nuclei template scanning
- **SSL/TLS analysis**: Certificate transparency monitoring
- **DNS intelligence**: Comprehensive DNS record analysis

### ⚡ Real-time Operations
- **WebSocket streaming**: Live updates to frontend
- **Event-driven architecture**: Redis-based message queues
- **Async task execution**: Distributed worker pools
- **Live intelligence feeds**: RSS, CVE, IOC feed ingestion

### 🔐 Breach Intelligence
- **Exposure analysis**: HaveIBeenPwned, DeHashed integration
- **Credential monitoring**: Track leaked credentials (legal APIs only)
- **Risk scoring**: Automated exposure risk assessment
- **Timeline tracking**: Historical breach correlation

## 🔐 Security

- JWT-based authentication
- Role-based access control (RBAC)
- API rate limiting
- Audit logging
- Secrets management
- Environment isolation

## 📊 Data Stores

- **PostgreSQL**: Relational data, users, scans, IOCs
- **Neo4j**: Graph relationships, entity linking
- **Redis**: Caching, queues, sessions
- **Elasticsearch**: Full-text search, logs

## 🤖 AI Providers

- Ollama (local)
- OpenRouter
- Anthropic Claude
- DeepSeek
- Groq
- Automatic failover
- Cost optimization

## 📖 Documentation

📘 **[START_HERE.md](START_HERE.md)** - Complete getting started guide  
🏗️ **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture overview  
🔌 **[API.md](docs/API.md)** - REST API reference  
🤖 **[AGENTS.md](docs/AGENTS.md)** - AI agents documentation  
🔗 **[INTEGRATIONS.md](docs/INTEGRATIONS.md)** - OSINT tool integrations  
🚀 **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Production deployment guide  
🔧 **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common issues and solutions  
❓ **[FAQ.md](docs/FAQ.md)** - Frequently asked questions  
🌐 **[docs/index.html](docs/index.html)** - Beautiful web documentation

## 🛠️ Technology Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for blazing fast builds
- **Tailwind CSS** for styling
- **Zustand** for state management
- **React Flow** for graph visualization
- **Recharts** for data visualization

### Backend Services
- **Node.js 20** with TypeScript
- **Fastify** for high-performance APIs
- **Python 3.11** for AI agents
- **WebSocket** for real-time updates

### AI & Intelligence
- **Anthropic Claude** for advanced reasoning
- **OpenAI GPT** for general tasks
- **Groq** for fast inference
- **Ollama** for local models
- **LangChain** for agent orchestration

### Data Stores
- **PostgreSQL 15** - Relational data, users, scans, IOCs
- **Neo4j 5** - Graph relationships, entity linking
- **Redis 7** - Caching, queues, sessions, pub/sub
- **Elasticsearch 8** - Full-text search, logs, analytics

### OSINT Tools
- **Amass, Subfinder, Assetfinder** - Subdomain enumeration
- **Nuclei** - Vulnerability scanning
- **Sherlock, Holehe** - Username/email OSINT
- **TruffleHog** - Secret scanning
- **Shodan, Censys** - Internet-wide scanning
- **VirusTotal, URLScan** - Threat intelligence

## 🛠️ Development

### Available Commands

```bash
# Development
npm run dev              # Start all services in dev mode
npm run build            # Build all services for production
npm run test             # Run all tests
npm run lint             # Lint all code
npm run typecheck        # TypeScript type checking

# Database
npm run migrate          # Run database migrations
npm run seed             # Seed database with sample data

# Docker
docker-compose up -d     # Start infrastructure services
docker-compose down      # Stop all services
docker-compose logs -f   # View logs in real-time

# Individual services
npm run dev --workspace=frontend
npm run dev --workspace=backend
npm run dev --workspace=gateway
npm run dev --workspace=orchestrator
```

### Project Structure

```
cyberintel-platform/
├── frontend/              # React + Vite UI
│   ├── src/
│   │   ├── components/   # Reusable components
│   │   ├── pages/        # Page components
│   │   └── stores/       # State management
│   └── package.json
├── backend/              # Core API services
│   ├── src/
│   │   ├── routes/       # API routes
│   │   └── reports/      # Report generation
│   └── package.json
├── gateway/              # API Gateway + Auth
│   ├── src/
│   │   ├── middleware/   # Auth, rate limiting
│   │   └── routes/       # Gateway routes
│   └── package.json
├── orchestrator/         # Task orchestration
│   ├── src/
│   │   ├── queue/        # Redis queue management
│   │   └── ai-planner.ts # AI reconnaissance planner
│   └── package.json
├── agents/               # Python AI agents
│   ├── ai_recon_planner.py
│   ├── breach_intelligence_agent.py
│   ├── graph_agent.py
│   └── requirements.txt
├── workers/              # Background processors
│   ├── ingestion_worker.py
│   └── requirements.txt
├── integrations/         # OSINT integrations
│   ├── src/
│   │   ├── tools/        # Tool adapters
│   │   └── breach/       # Breach intelligence
│   └── package.json
├── graph-engine/         # Neo4j operations
│   ├── src/
│   │   └── intelligence.ts
│   └── package.json
├── ai-router/            # Multi-provider routing
│   ├── src/
│   │   └── providers/    # AI provider adapters
│   └── package.json
├── telegram-bot/         # Telegram integration
│   └── src/index.ts
├── shared/               # Shared TypeScript library
│   └── src/types/
├── docs/                 # Documentation
│   └── index.html        # Web documentation
├── scripts/              # Automation scripts
│   ├── install.sh        # Linux/Mac installer
│   ├── install.ps1       # Windows PowerShell installer
│   └── install.bat       # Windows CMD installer
└── docker/               # Docker configs
    └── postgres/init.sql
```

## 📝 Environment Variables

The platform uses environment variables for configuration. After running the installation script, edit `.env` to add your API keys.

### Required Variables

```bash
# Database Connections
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=cyberintel
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

REDIS_HOST=localhost
REDIS_PORT=6379

ELASTICSEARCH_NODE=http://localhost:9200

# Authentication
JWT_SECRET=your_jwt_secret_here
JWT_EXPIRES_IN=7d

# AI Providers (at least one required)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
OLLAMA_BASE_URL=http://localhost:11434
```

### Optional OSINT API Keys

```bash
# Threat Intelligence
VIRUSTOTAL_API_KEY=your_key
SHODAN_API_KEY=your_key
CENSYS_API_ID=your_id
CENSYS_API_SECRET=your_secret
SECURITYTRAILS_API_KEY=your_key
URLSCAN_API_KEY=your_key
ABUSEIPDB_API_KEY=your_key
GREYNOISE_API_KEY=your_key

# Breach Intelligence
HAVEIBEENPWNED_API_KEY=your_key
DEHASHED_EMAIL=your_email
DEHASHED_API_KEY=your_key

# Social Media OSINT
TELEGRAM_BOT_TOKEN=your_token

# Other Services
OPENROUTER_API_KEY=your_key
DEEPSEEK_API_KEY=your_key
```

See [`.env.example`](.env.example) for the complete list with descriptions.

## 🤝 Contributing

We welcome contributions from the community! Whether it's:

- 🐛 Bug fixes
- ✨ New features
- 📝 Documentation improvements
- 🔧 OSINT tool integrations
- 🤖 New AI agents
- 🎨 UI/UX enhancements

### Quick Contribution Guide

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/cyberintel-platform.git`
3. **Create** a branch: `git checkout -b feature/amazing-feature`
4. **Make** your changes
5. **Test** your changes: `npm test`
6. **Commit** your changes: `git commit -m 'Add amazing feature'`
7. **Push** to your fork: `git push origin feature/amazing-feature`
8. **Open** a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Areas We Need Help With

- [ ] Additional OSINT tool integrations (Maltego, SpiderFoot, etc.)
- [ ] AI agent improvements and new agent types
- [ ] Graph intelligence algorithms
- [ ] Performance optimizations
- [ ] Documentation and tutorials
- [ ] UI/UX improvements
- [ ] Test coverage
- [ ] Security enhancements

## 🐛 Bug Reports & Feature Requests

- **Bug Report**: [Create an issue](https://github.com/YOUR_USERNAME/cyberintel-platform/issues/new?template=bug_report.md)
- **Feature Request**: [Create an issue](https://github.com/YOUR_USERNAME/cyberintel-platform/issues/new?template=feature_request.md)
- **Integration Request**: [Create an issue](https://github.com/YOUR_USERNAME/cyberintel-platform/issues/new?template=integration_request.md)

## 💬 Community & Support

- **GitHub Discussions**: [Ask questions and share ideas](https://github.com/YOUR_USERNAME/cyberintel-platform/discussions)
- **GitHub Issues**: [Report bugs and request features](https://github.com/YOUR_USERNAME/cyberintel-platform/issues)
- **Documentation**: Check the [docs/](docs/) folder for guides

## 🗺️ Roadmap

### ✅ Completed (Phase 1-7)
- [x] Core platform architecture
- [x] 20+ OSINT tool integrations
- [x] AI reconnaissance planner
- [x] Graph intelligence engine
- [x] Breach intelligence subsystem
- [x] Telegram bot integration
- [x] Visual intelligence reports
- [x] Real-time feed ingestion

### 🚧 In Progress (Phase 8-10)
- [ ] Advanced search & correlation with OpenSearch
- [ ] Enhanced AI reasoning layer
- [ ] Enterprise architecture improvements
- [ ] Kubernetes deployment configs
- [ ] Advanced graph algorithms
- [ ] Machine learning for threat detection

### 🔮 Future Plans
- [ ] Mobile app (iOS/Android)
- [ ] Browser extension
- [ ] Slack/Discord integrations
- [ ] Custom plugin system
- [ ] Marketplace for community integrations
- [ ] SaaS offering

See [EXPANSION_SUMMARY.md](EXPANSION_SUMMARY.md) for detailed phase information.

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This platform integrates and builds upon many excellent open-source projects:

- **OSINT Tools**: Amass, Subfinder, Nuclei, Sherlock, TruffleHog, and many more
- **AI Providers**: Anthropic, OpenAI, Groq, Ollama
- **Databases**: PostgreSQL, Neo4j, Redis, Elasticsearch
- **Frameworks**: React, Fastify, LangChain

Special thanks to the cybersecurity and OSINT communities for their invaluable tools and knowledge.

## ⚠️ Legal Disclaimer

This platform is designed for **legal security research, penetration testing, and threat intelligence** purposes only. Users are responsible for:

- Obtaining proper authorization before scanning targets
- Complying with applicable laws and regulations
- Using the platform ethically and responsibly
- Not using the platform for malicious purposes

The developers assume no liability for misuse of this platform.

## 📊 Statistics

- **20+** OSINT tool integrations
- **9** specialized AI agents
- **11** microservices
- **4** database systems
- **6** AI provider integrations
- **100%** TypeScript/Python type coverage
- **Distributed** architecture ready for scale

## 🔗 Links

- **Documentation**: [docs/index.html](docs/index.html)
- **GitHub**: [https://github.com/YOUR_USERNAME/cyberintel-platform](https://github.com/YOUR_USERNAME/cyberintel-platform)
- **Issues**: [https://github.com/YOUR_USERNAME/cyberintel-platform/issues](https://github.com/YOUR_USERNAME/cyberintel-platform/issues)
- **Discussions**: [https://github.com/YOUR_USERNAME/cyberintel-platform/discussions](https://github.com/YOUR_USERNAME/cyberintel-platform/discussions)

---

<div align="center">

**Built with ❤️ by the cybersecurity community**

⭐ **Star this repo** if you find it useful!

[Report Bug](https://github.com/YOUR_USERNAME/cyberintel-platform/issues) • [Request Feature](https://github.com/YOUR_USERNAME/cyberintel-platform/issues) • [Contribute](CONTRIBUTING.md)

</div>
