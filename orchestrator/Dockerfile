# ============================================================================
# Orchestrator Service - Monorepo-Aware Dockerfile
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

# Copy orchestrator package.json
COPY orchestrator/package*.json ./orchestrator/

# Install ALL workspace dependencies from root
# This resolves @cyberintel/shared correctly
RUN npm ci --workspaces --if-present

# Copy shared library source code
COPY shared/ ./shared/

# Build shared library first (required by orchestrator)
RUN npm run build --workspace=shared

# Copy orchestrator source code
COPY orchestrator/ ./orchestrator/

# Build orchestrator service
RUN npm run build --workspace=orchestrator

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

# Copy orchestrator (built)
COPY --from=builder /monorepo/orchestrator/package*.json ./orchestrator/
COPY --from=builder /monorepo/orchestrator/dist ./orchestrator/dist

# Install production dependencies only
RUN npm ci --workspace=orchestrator --omit=dev --ignore-scripts

WORKDIR /app/orchestrator

EXPOSE 8002

CMD ["node", "dist/index.js"]
