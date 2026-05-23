#!/bin/bash

echo "🚀 Setting up CyberIntel Platform..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed. Aborting." >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed. Aborting." >&2; exit 1; }

echo "✅ Prerequisites check passed"

# Copy environment file
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys"
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build shared library
echo "🔨 Building shared library..."
cd shared && npm run build && cd ..

# Start infrastructure
echo "🐳 Starting Docker containers..."
docker-compose up -d postgres redis neo4j elasticsearch

# Wait for services
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose exec -T postgres psql -U cyberintel -d cyberintel -f /docker-entrypoint-initdb.d/init.sql

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Run 'npm run dev' to start development servers"
echo "3. Access the platform at http://localhost:3000"
echo ""
echo "Default credentials:"
echo "  Email: admin@cyberintel.local"
echo "  Password: admin123"
