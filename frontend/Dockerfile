# syntax=docker/dockerfile:1.7
# ============================================================================
# Frontend Service — Vite build served by Nginx
# ----------------------------------------------------------------------------
# Build context is the monorepo ROOT (see docker-compose.yml). The frontend has
# no internal workspace dependencies, so only its own manifest is needed.
# ============================================================================

ARG NODE_VERSION=20-alpine
ARG NGINX_VERSION=1.27-alpine

# ---------------------------------------------------------------------------
# Stage 1: deps — install frontend dependencies (cached)
# ---------------------------------------------------------------------------
FROM node:${NODE_VERSION} AS deps
WORKDIR /monorepo

COPY package.json package-lock.json .npmrc ./
COPY frontend/package.json ./frontend/

RUN --mount=type=cache,target=/root/.npm \
    npm ci --ignore-scripts

# ---------------------------------------------------------------------------
# Stage 2: build — produce the static bundle
# ---------------------------------------------------------------------------
FROM node:${NODE_VERSION} AS build
WORKDIR /monorepo

COPY --from=deps /monorepo/node_modules ./node_modules
COPY package.json package-lock.json ./
COPY frontend/ ./frontend/

RUN npm run build --workspace=frontend

# ---------------------------------------------------------------------------
# Stage 3: runtime — Nginx serving the static assets
# ---------------------------------------------------------------------------
FROM nginx:${NGINX_VERSION} AS runtime

# Non-root hardening: let the unprivileged nginx user own the paths it writes.
RUN touch /var/run/nginx.pid \
    && chown -R nginx:nginx /var/run/nginx.pid /usr/share/nginx/html /var/cache/nginx

COPY --from=build /monorepo/frontend/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

USER nginx

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -q -O /dev/null http://127.0.0.1:3000/ || exit 1

CMD ["nginx", "-g", "daemon off;"]

LABEL org.opencontainers.image.title="cyberintel-frontend" \
      org.opencontainers.image.description="CyberIntel Platform web UI" \
      org.opencontainers.image.licenses="MIT"
