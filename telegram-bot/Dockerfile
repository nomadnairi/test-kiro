# ============================================================================
# Telegram Bot Service - Monorepo-Aware Dockerfile
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

# Copy telegram-bot package.json
COPY telegram-bot/package*.json ./telegram-bot/

# Install ALL workspace dependencies from root
# This resolves @cyberintel/shared correctly
RUN npm install --workspaces --if-present

# Copy shared library source code
COPY shared/ ./shared/

# Build shared library first (required by telegram-bot)
RUN npm run build --workspace=shared

# Copy telegram-bot source code
COPY telegram-bot/ ./telegram-bot/

# Build telegram-bot service
RUN npm run build --workspace=telegram-bot

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

# Copy telegram-bot (built)
COPY --from=builder /monorepo/telegram-bot/package*.json ./telegram-bot/
COPY --from=builder /monorepo/telegram-bot/dist ./telegram-bot/dist

# Install production dependencies only
RUN npm install --workspace=telegram-bot --omit=dev --ignore-scripts

WORKDIR /app/telegram-bot

CMD ["node", "dist/index.js"]
