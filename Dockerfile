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
# Stage 1b: gobuild — compile gau, and fetch the prebuilt phoneinfoga binary
# ---------------------------------------------------------------------------
# phoneinfoga embeds a web client (go:embed client/dist/*) that is not present
# in a plain `go install`, so it is downloaded as a release binary instead.
FROM golang:1.22-bookworm AS gobuild
ENV CGO_ENABLED=0 GOBIN=/out
RUN mkdir -p /out \
    && (go install github.com/lc/gau/v2/cmd/gau@latest \
        || echo "WARN: gau build failed (tool will be reported as not installed)")
RUN curl -sSL "https://raw.githubusercontent.com/sundowndev/phoneinfoga/master/support/scripts/install" \
        | bash -s -- -b /out \
    || echo "WARN: phoneinfoga download failed (tool will be reported as not installed)"

# ---------------------------------------------------------------------------
# Stage 2: runtime — minimal, non-root, signal-correct
# ---------------------------------------------------------------------------
FROM python:${PYTHON_VERSION} AS runtime

# System packages:
#   tini   → signal handling / zombie reaping for the long-running poller
#   procps → pgrep for the healthcheck
#   whois  → real WHOIS client (else the tool uses a TCP fallback)
#   nmap   → real Port Scan (else an asyncio fallback)
#   whatweb→ website fingerprint OSINT tool
#   git/pipx → install the Python OSINT CLIs in isolated environments
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tini procps whois nmap whatweb git ca-certificates pipx \
    && rm -rf /var/lib/apt/lists/*

# pipx installs each OSINT CLI into its own venv (no dependency clashes with the
# bot's runtime) and drops the entrypoints into /usr/local/bin (on PATH for all
# users). Kept in one layer; failures in a single tool don't abort the build.
ENV PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin
RUN for pkg in \
        theHarvester sherlock-project holehe maigret socialscan h8mail \
        dnstwist dnsrecon sublist3r checkdmarc wafw00f metafinder ; do \
        pipx install "$pkg" || echo "WARN: pipx install $pkg failed (tool will be reported as not installed)"; \
    done \
    && rm -rf /root/.cache

# Go / release OSINT binaries (whatever built successfully lands here).
COPY --from=gobuild /out/ /usr/local/bin/

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
