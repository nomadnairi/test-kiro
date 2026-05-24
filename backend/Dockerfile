# ============================================================================
# Backend Service - Monorepo-Aware Dockerfile
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

# Copy backend package.json
COPY backend/package*.json ./backend/

# Copy integrations package.json (if backend depends on it)
COPY integrations/package*.json ./integrations/

# Install ALL workspace dependencies from root
# This resolves @cyberintel/shared and other internal packages correctly
RUN npm install --workspaces --if-present

# Copy shared library source code
COPY shared/ ./shared/

# Build shared library first (required by backend)
RUN npm run build --workspace=shared

# Copy integrations source code (if needed)
COPY integrations/ ./integrations/

# Build integrations if it has a build step
RUN npm run build --workspace=integrations --if-present

# Copy backend source code
COPY backend/ ./backend/

# Build backend service
RUN npm run build --workspace=backend

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

# Copy integrations (built)
COPY --from=builder /monorepo/integrations/package*.json ./integrations/
COPY --from=builder /monorepo/integrations/dist ./integrations/dist
COPY --from=builder /monorepo/integrations/src ./integrations/src

# Copy backend (built)
COPY --from=builder /monorepo/backend/package*.json ./backend/
COPY --from=builder /monorepo/backend/dist ./backend/dist

# Install production dependencies only
RUN npm install --workspace=backend --omit=dev --ignore-scripts

WORKDIR /app/backend

EXPOSE 8001

CMD ["node", "dist/index.js"]
