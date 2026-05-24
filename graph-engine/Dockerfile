# ============================================================================
# Graph Engine Service - Monorepo-Aware Dockerfile
# ============================================================================
# This Dockerfile properly handles npm workspace dependencies by copying
# the entire monorepo structure and using workspace-aware npm commands.
# ============================================================================

FROM node:20-alpine AS builder

# Set working directory to monorepo root
WORKDIR /monorepo

# Copy root package files for workspace configuration
COPY package*.json ./

# Copy shared library package.json first (dependency)
COPY shared/package*.json ./shared/

# Copy graph-engine package.json
COPY graph-engine/package*.json ./graph-engine/

# Install ALL workspace dependencies from root
# This resolves @cyberintel/shared correctly
RUN npm install --workspaces --if-present

# Copy shared library source code
COPY shared/ ./shared/

# Build shared library first (required by graph-engine)
RUN npm run build --workspace=shared

# Copy graph-engine source code
COPY graph-engine/ ./graph-engine/

# Build graph-engine service
RUN npm run build --workspace=graph-engine

# ============================================================================
# Production Stage
# ============================================================================
FROM node:20-alpine

WORKDIR /app

# Copy root package files
COPY --from=builder /monorepo/package*.json ./

# Copy shared library (built)
COPY --from=builder /monorepo/shared/package*.json ./shared/
COPY --from=builder /monorepo/shared/dist ./shared/dist

# Copy graph-engine (built)
COPY --from=builder /monorepo/graph-engine/package*.json ./graph-engine/
COPY --from=builder /monorepo/graph-engine/dist ./graph-engine/dist

# Install production dependencies only
RUN npm install --workspace=graph-engine --omit=dev --ignore-scripts

WORKDIR /app/graph-engine

EXPOSE 8003

CMD ["node", "dist/index.js"]
