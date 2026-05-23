#!/bin/bash

echo "🧪 Running CyberIntel Platform Tests..."

# Run TypeScript tests
echo "📝 Running TypeScript tests..."
npm run test

# Run Python tests
echo "🐍 Running Python tests..."
cd agents && python -m pytest && cd ..
cd workers && python -m pytest && cd ..

# Run integration tests
echo "🔗 Running integration tests..."
npm run test:integration

# Run linting
echo "🔍 Running linters..."
npm run lint

echo "✅ All tests complete!"
