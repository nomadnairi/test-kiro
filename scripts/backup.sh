#!/bin/bash

BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📦 Creating backups..."

# PostgreSQL backup
echo "Backing up PostgreSQL..."
docker-compose exec -T postgres pg_dump -U cyberintel cyberintel > "$BACKUP_DIR/postgres.sql"

# Neo4j backup
echo "Backing up Neo4j..."
docker-compose exec neo4j neo4j-admin database dump neo4j --to-path=/backups
docker cp $(docker-compose ps -q neo4j):/backups/neo4j.dump "$BACKUP_DIR/neo4j.dump"

# Redis backup
echo "Backing up Redis..."
docker-compose exec redis redis-cli --rdb "$BACKUP_DIR/redis.rdb" BGSAVE

echo "✅ Backups complete: $BACKUP_DIR"
