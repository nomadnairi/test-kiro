#!/bin/bash

echo "🚀 Starting CyberIntel Platform (Production Mode)..."

# Build all services
echo "🔨 Building services..."
npm run build

# Start all containers
echo "🐳 Starting all services..."
docker-compose up -d

echo "✅ Platform started!"
echo ""
echo "Services:"
echo "  Frontend: http://localhost:3000"
echo "  API Gateway: http://localhost:8000"
echo "  Neo4j Browser: http://localhost:7474"
echo ""
echo "View logs: docker-compose logs -f"
