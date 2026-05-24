# ============================================================================
# Frontend Service - Monorepo-Aware Dockerfile
# ============================================================================
# Frontend doesn't depend on @cyberintel/shared, but we use the same
# monorepo pattern for consistency and future-proofing.
# ============================================================================

FROM node:20-alpine AS builder

# Set working directory to monorepo root
WORKDIR /monorepo

# Copy root package files for workspace configuration
COPY package*.json ./

# Copy frontend package.json
COPY frontend/package*.json ./frontend/

# Install ALL workspace dependencies from root
RUN npm ci --workspaces --if-present

# Copy frontend source code
COPY frontend/ ./frontend/

# Build frontend service
RUN npm run build --workspace=frontend

# ============================================================================
# Production Stage - Nginx
# ============================================================================
FROM nginx:alpine

COPY --from=builder /monorepo/frontend/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
