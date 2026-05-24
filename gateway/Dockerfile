# ============================================================================
# Gateway Service - Monorepo-Aware Dockerfile
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

# Copy gateway package.json
COPY gateway/package*.json ./gateway/

# Install ALL workspace dependencies from root
# This resolves @cyberintel/shared correctly
RUN npm install --workspaces --if-present

# Copy shared library source code
COPY shared/ ./shared/

# Build shared library first (required by gateway)
RUN npm run build --workspace=shared

# Copy gateway source code
COPY gateway/ ./gateway/

# Build gateway service
RUN npm run build --workspace=gateway

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

# Copy gateway (built)
COPY --from=builder /monorepo/gateway/package*.json ./gateway/
COPY --from=builder /monorepo/gateway/dist ./gateway/dist

# Install production dependencies only
RUN npm install --workspace=gateway --omit=dev --ignore-scripts

WORKDIR /app/gateway

EXPOSE 8000

CMD ["node", "dist/index.js"]
