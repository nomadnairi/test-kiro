# 🚀 Start Here - CyberIntel Platform

Welcome to the CyberIntel Platform! This guide will help you get started quickly.

## 📋 Prerequisites

Before you begin, ensure you have:

- **Node.js 20+** - [Download](https://nodejs.org/)
- **Python 3.11+** - [Download](https://www.python.org/)
- **Docker & Docker Compose** - [Download](https://www.docker.com/) (recommended)
- **Git** - [Download](https://git-scm.com/)

## ⚡ Quick Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/cyberintel-platform.git
cd cyberintel-platform
```

### Step 2: Run Automatic Installation

Choose the script for your operating system:

**Linux/Mac:**
```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

**Windows PowerShell:**
```powershell
.\scripts\install.ps1
```

**Windows CMD:**
```cmd
scripts\install.bat
```

The installation script will:
- ✅ Check all prerequisites
- ✅ Install Node.js dependencies
- ✅ Install Python dependencies
- ✅ Build shared libraries
- ✅ Create .env configuration file
- ✅ Pull Docker images

### Step 3: Configure API Keys

Edit the `.env` file and add your API keys:

```bash
# Required for basic functionality
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Optional integrations
VIRUSTOTAL_API_KEY=your_key_here
SHODAN_API_KEY=your_key_here
SECURITYTRAILS_API_KEY=your_key_here
```

### Step 4: Start Infrastructure

Start the required services (PostgreSQL, Neo4j, Redis, Elasticsearch):

```bash
docker-compose up -d
```

Wait for all services to be healthy (~30 seconds).

### Step 5: Start Development

```bash
npm run dev
```

This will start all microservices in development mode.

### Step 6: Access the Platform

Open your browser and navigate to:

- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:4000
- **Neo4j Browser**: http://localhost:7474
- **Documentation**: Open `docs/index.html` in your browser

## 🎯 First Steps

### 1. Create an Account

Navigate to http://localhost:3000 and create your first user account.

### 2. Run Your First Scan

```bash
# Using the API
curl -X POST http://localhost:4000/api/scans \
  -H "Content-Type: application/json" \
  -d '{
    "target": "example.com",
    "type": "domain",
    "depth": "standard"
  }'
```

Or use the web interface to start a scan.

### 3. Explore the Graph

Navigate to the Graph Explorer to visualize relationships between entities.

### 4. Chat with AI Analyst

Use the AI Chat feature to ask questions about your reconnaissance data.

## 📚 Learn More

### Documentation
- [Quick Start Guide](docs/QUICKSTART.md) - Detailed getting started guide
- [Architecture Overview](docs/ARCHITECTURE.md) - System architecture
- [API Documentation](docs/API.md) - REST API reference
- [Agent Documentation](docs/AGENTS.md) - AI agents overview
- [Integrations](docs/INTEGRATIONS.md) - OSINT tool integrations

### Key Features
- **Autonomous Reconnaissance** - AI-powered OSINT collection
- **Graph Intelligence** - Entity relationship mapping
- **Breach Intelligence** - Exposure analysis
- **AI Analyst** - Natural language queries
- **Visual Reports** - PDF/HTML report generation
- **Real-time Feeds** - Threat intelligence ingestion
- **Telegram Bot** - Mobile access

## 🛠️ Development

### Project Structure

```
cyberintel-platform/
├── frontend/          # React UI
├── backend/           # Main API
├── gateway/           # API Gateway
├── orchestrator/      # Task orchestration
├── ai-router/         # AI provider routing
├── graph-engine/      # Neo4j graph service
├── agents/            # Python AI agents
├── workers/           # Background workers
├── integrations/      # OSINT integrations
├── telegram-bot/      # Telegram service
└── shared/            # Shared libraries
```

### Available Commands

```bash
# Development
npm run dev              # Start all services in dev mode
npm run build            # Build all services
npm run test             # Run tests

# Docker
docker-compose up -d     # Start infrastructure
docker-compose down      # Stop infrastructure
docker-compose logs -f   # View logs

# Individual services
npm run dev --workspace=frontend
npm run dev --workspace=backend
npm run dev --workspace=gateway
```

### Environment Variables

Key environment variables in `.env`:

```bash
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
NEO4J_URI=bolt://localhost:7687
REDIS_HOST=localhost
ELASTICSEARCH_NODE=http://localhost:9200

# AI Providers
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GROQ_API_KEY=

# OSINT APIs
VIRUSTOTAL_API_KEY=
SHODAN_API_KEY=
SECURITYTRAILS_API_KEY=
HAVEIBEENPWNED_API_KEY=

# Telegram
TELEGRAM_BOT_TOKEN=
```

## 🐛 Troubleshooting

### Port Already in Use

If you see "port already in use" errors:

```bash
# Check what's using the port
netstat -ano | findstr :3000  # Windows
lsof -i :3000                 # Linux/Mac

# Kill the process or change the port in .env
```

### Docker Services Not Starting

```bash
# Check Docker status
docker ps

# View logs
docker-compose logs postgres
docker-compose logs neo4j

# Restart services
docker-compose restart
```

### Python Dependencies Issues

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r agents/requirements.txt
pip install -r workers/requirements.txt
```

### Node.js Dependencies Issues

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Rebuild shared library
cd shared && npm run build && cd ..
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📞 Getting Help

- **Documentation**: Check the `docs/` folder
- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/cyberintel-platform/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/cyberintel-platform/discussions)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 What's Next?

- Explore the [Architecture Documentation](docs/ARCHITECTURE.md)
- Learn about [AI Agents](docs/AGENTS.md)
- Check out [Integration Options](docs/INTEGRATIONS.md)
- Read the [API Documentation](docs/API.md)
- Join the community discussions

---

**Happy Hunting! 🎯**
