# syntax=docker/dockerfile:1.7
# ============================================================================
# Backend Service — monorepo-aware, multi-stage, production-hardened
# ----------------------------------------------------------------------------
# Build context is the monorepo ROOT (see docker-compose.yml). Layers are
# ordered so dependency installation stays cached until a manifest or the
# lockfile changes.
# ============================================================================

ARG NODE_VERSION=20-alpine

# ---------------------------------------------------------------------------
# Stage 1: deps — install the full workspace dependency graph (cached)
# ---------------------------------------------------------------------------
FROM node:${NODE_VERSION} AS deps
WORKDIR /monorepo

# Only manifests + lockfile are needed to resolve dependencies, so copy them
# first: `npm ci` is re-run only when dependencies actually change.
COPY package.json package-lock.json .npmrc ./
COPY shared/package.json ./shared/
COPY integrations/package.json ./integrations/
COPY backend/package.json ./backend/

# `--ignore-scripts` stops the root postinstall (which builds `shared`) from
# firing before the source exists; the build stage compiles it explicitly.
RUN --mount=type=cache,target=/root/.npm \
    npm ci --ignore-scripts

# ---------------------------------------------------------------------------
# Stage 2: build — compile shared, integrations and the backend
# ---------------------------------------------------------------------------
FROM node:${NODE_VERSION} AS build
WORKDIR /monorepo

COPY --from=deps /monorepo/node_modules ./node_modules
COPY package.json package-lock.json ./

# Build in dependency order.
COPY shared/ ./shared/
RUN npm run build --workspace=shared

COPY integrations/ ./integrations/
RUN npm run build --workspace=integrations --if-present

COPY backend/ ./backend/
RUN npm run build --workspace=backend

# Reduce node_modules to production-only for the runtime copy.
RUN --mount=type=cache,target=/root/.npm \
    npm prune --omit=dev

# ---------------------------------------------------------------------------
# Stage 3: runtime — minimal, non-root, signal-correct
# ---------------------------------------------------------------------------
FROM node:${NODE_VERSION} AS runtime

# tini reaps zombies and forwards signals so the container stops cleanly.
RUN apk add --no-cache tini

ENV NODE_ENV=production \
    BACKEND_PORT=8001

WORKDIR /app

# Pruned production dependency tree + compiled output. The /app layout mirrors
# /monorepo so the workspace symlinks in node_modules stay valid.
COPY --from=build /monorepo/node_modules ./node_modules
COPY --from=build /monorepo/package.json ./package.json
COPY --from=build /monorepo/shared/package.json ./shared/package.json
COPY --from=build /monorepo/shared/dist ./shared/dist
COPY --from=build /monorepo/integrations/package.json ./integrations/package.json
COPY --from=build /monorepo/integrations/dist ./integrations/dist
COPY --from=build /monorepo/backend/package.json ./backend/package.json
COPY --from=build /monorepo/backend/dist ./backend/dist

# Drop privileges to the built-in unprivileged `node` user.
USER node

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD node -e "require('http').get('http://127.0.0.1:'+(process.env.BACKEND_PORT||8001)+'/health',r=>process.exit(r.statusCode===200?0:1)).on('error',()=>process.exit(1))"

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "backend/dist/index.js"]

LABEL org.opencontainers.image.title="cyberintel-backend" \
      org.opencontainers.image.description="CyberIntel Platform backend service" \
      org.opencontainers.image.licenses="MIT"
