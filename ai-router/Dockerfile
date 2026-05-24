# ============================================================================
# AI Router Service - Monorepo-Aware Dockerfile
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

# Copy ai-router package.json
COPY ai-router/package*.json ./ai-router/

# Install ALL workspace dependencies from root
# This resolves @cyberintel/shared correctly
RUN npm ci --workspaces --if-present

# Copy shared library source code
COPY shared/ ./shared/

# Build shared library first (required by ai-router)
RUN npm run build --workspace=shared

# Copy ai-router source code
COPY ai-router/ ./ai-router/

# Build ai-router service
RUN npm run build --workspace=ai-router

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

# Copy ai-router (built)
COPY --from=builder /monorepo/ai-router/package*.json ./ai-router/
COPY --from=builder /monorepo/ai-router/dist ./ai-router/dist

# Install production dependencies only
RUN npm ci --workspace=ai-router --omit=dev --ignore-scripts

WORKDIR /app/ai-router

EXPOSE 8004

CMD ["node", "dist/index.js"]
