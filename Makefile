.PHONY: help install dev build start stop clean test backup

help:
	@echo "CyberIntel Platform - Available Commands:"
	@echo "  make install    - Install all dependencies"
	@echo "  make dev        - Start development environment"
	@echo "  make build      - Build all services"
	@echo "  make start      - Start production environment"
	@echo "  make stop       - Stop all services"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make test       - Run all tests"
	@echo "  make backup     - Create database backups"
	@echo "  make logs       - View service logs"

install:
	@echo "📦 Installing dependencies..."
	npm install
	cd agents && pip install -r requirements.txt
	cd workers && pip install -r requirements.txt

dev:
	@echo "🚀 Starting development environment..."
	docker-compose up -d postgres redis neo4j elasticsearch
	npm run dev

build:
	@echo "🔨 Building all services..."
	npm run build
	docker-compose build

start:
	@echo "🚀 Starting production environment..."
	docker-compose -f docker-compose.prod.yml up -d

stop:
	@echo "🛑 Stopping all services..."
	docker-compose down

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf */dist */build */node_modules
	docker-compose down -v

test:
	@echo "🧪 Running tests..."
	./scripts/test.sh

backup:
	@echo "📦 Creating backups..."
	./scripts/backup.sh

logs:
	@echo "📋 Viewing logs..."
	docker-compose logs -f
