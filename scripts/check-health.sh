#!/bin/bash

# Health Check Script - Verify all services are running

echo "🏥 CyberIntel Platform - Health Check"
echo "======================================"
echo ""

SERVICES=(
  "Gateway:8000"
  "Backend:8001"
  "Orchestrator:8002"
  "AI-Router:8003"
  "Graph-Engine:8004"
)

FAILED=0

for service in "${SERVICES[@]}"; do
  NAME="${service%%:*}"
  PORT="${service##*:}"
  
  echo -n "Checking $NAME (port $PORT)... "
  
  if curl -sf "http://localhost:$PORT/health" > /dev/null 2>&1; then
    echo "✅ OK"
  else
    echo "❌ FAILED"
    FAILED=$((FAILED + 1))
  fi
done

echo ""
echo "======================================"

if [ $FAILED -eq 0 ]; then
  echo "✅ All services healthy!"
  exit 0
else
  echo "❌ $FAILED service(s) failed health check"
  exit 1
fi
