#!/bin/bash
find .github/workflows -type f -name "*.yml" -exec sed -i "s/cache: 'npm'/# cache: 'npm'/g" {} +
find .github/workflows -type f -name "*.yml" -exec sed -i "s/npm ci --workspaces --if-present/npm install/g" {} +
find .github/workflows -type f -name "*.yml" -exec sed -i "s/node-version: '20'/node-version: '22'/g" {} +
