#!/bin/bash

echo "🚀 Starting CyberIntel Platform (Development Mode)..."

# Start infrastructure
echo "🐳 Starting infrastructure services..."
docker-compose up -d postgres redis neo4j elasticsearch ollama

# Wait for services
echo "⏳ Waiting for services..."
sleep 5

# Start all services
echo "🎯 Starting application services..."
npm run dev
