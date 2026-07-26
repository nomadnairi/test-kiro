# ============================================================================
# DeathBot — Telegram OSINT / recon / AI bot
# ----------------------------------------------------------------------------
# Multi-stage: dependencies are installed into a virtualenv in the builder and
# copied into a slim runtime, so no build tooling or pip cache ships in the
# final image. Runs as an unprivileged user; all mutable state lives in /data.
# ============================================================================

ARG PYTHON_VERSION=3.11-slim

# ---------------------------------------------------------------------------
# Stage 1: builder — resolve dependencies into a self-contained venv
# ---------------------------------------------------------------------------
FROM python:${PYTHON_VERSION} AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore

WORKDIR /build

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy only the manifest first so this layer stays cached until deps change.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Stage 2: runtime — minimal, non-root, signal-correct
# ---------------------------------------------------------------------------
FROM python:${PYTHON_VERSION} AS runtime

# tini  → correct signal handling / zombie reaping for the long-running poller
# procps→ pgrep for the healthcheck
# whois → makes the WHOIS tool use the real client instead of the TCP fallback
# nmap  → makes the Port Scan tool use nmap instead of the asyncio fallback
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tini procps whois nmap ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    # State (SQLite DB + AES master key) lives on a volume, not in the image.
    DATABASE_PATH=/data/deathbot.sqlite3 \
    SECRET_KEY_FILE=/data/.secret.key

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY deathbot/ ./deathbot/
COPY config.yaml smoke_test.py ./

# Unprivileged user; /app stays read-only to it, /data is the only writable path.
RUN useradd --create-home --uid 10001 deathbot \
    && mkdir -p /data \
    && chown -R deathbot:deathbot /data

USER deathbot
VOLUME ["/data"]

# The bot has no HTTP surface (it long-polls Telegram), so liveness is a
# process check — if polling dies the process exits and this goes unhealthy.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD pgrep -f "python -m deathbot" > /dev/null || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "-m", "deathbot"]

LABEL org.opencontainers.image.title="deathbot" \
      org.opencontainers.image.description="Button-driven Telegram bot for OSINT, recon and AI" \
      org.opencontainers.image.licenses="MIT"
