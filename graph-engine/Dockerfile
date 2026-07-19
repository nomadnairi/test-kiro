# syntax=docker/dockerfile:1.7
# ============================================================================
# Graph Engine Service — monorepo-aware, multi-stage, production-hardened
# ----------------------------------------------------------------------------
# Build context is the monorepo ROOT (see docker-compose.yml). Only the
# graph-engine service and its `shared` dependency are compiled.
# ============================================================================

ARG NODE_VERSION=20-alpine

# ---------------------------------------------------------------------------
# Stage 1: deps — install the workspace dependency graph (cached)
# ---------------------------------------------------------------------------
FROM node:${NODE_VERSION} AS deps
WORKDIR /monorepo

COPY package.json package-lock.json .npmrc ./
COPY shared/package.json ./shared/
COPY graph-engine/package.json ./graph-engine/

# `--ignore-scripts` stops the root postinstall (which builds `shared`) from
# firing before the source exists; the build stage compiles it explicitly.
RUN --mount=type=cache,target=/root/.npm \
    npm ci --ignore-scripts

# ---------------------------------------------------------------------------
# Stage 2: build — compile shared then the service
# ---------------------------------------------------------------------------
FROM node:${NODE_VERSION} AS build
WORKDIR /monorepo

COPY --from=deps /monorepo/node_modules ./node_modules
COPY package.json package-lock.json ./

COPY shared/ ./shared/
RUN npm run build --workspace=shared

COPY graph-engine/ ./graph-engine/
RUN npm run build --workspace=graph-engine

RUN --mount=type=cache,target=/root/.npm \
    npm prune --omit=dev

# ---------------------------------------------------------------------------
# Stage 3: runtime — minimal, non-root, signal-correct
# ---------------------------------------------------------------------------
FROM node:${NODE_VERSION} AS runtime

RUN apk add --no-cache tini

ENV NODE_ENV=production \
    GRAPH_ENGINE_PORT=8004

WORKDIR /app

# The /app layout mirrors /monorepo so workspace symlinks stay valid.
COPY --from=build /monorepo/node_modules ./node_modules
COPY --from=build /monorepo/package.json ./package.json
COPY --from=build /monorepo/shared/package.json ./shared/package.json
COPY --from=build /monorepo/shared/dist ./shared/dist
COPY --from=build /monorepo/graph-engine/package.json ./graph-engine/package.json
COPY --from=build /monorepo/graph-engine/dist ./graph-engine/dist

USER node

EXPOSE 8004

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD node -e "require('http').get('http://127.0.0.1:'+(process.env.GRAPH_ENGINE_PORT||8004)+'/health',r=>process.exit(r.statusCode===200?0:1)).on('error',()=>process.exit(1))"

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "graph-engine/dist/index.js"]

LABEL org.opencontainers.image.title="cyberintel-graph-engine" \
      org.opencontainers.image.description="CyberIntel Platform graph analytics engine" \
      org.opencontainers.image.licenses="MIT"
