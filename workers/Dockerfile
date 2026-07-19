# syntax=docker/dockerfile:1.7
# ============================================================================
# Workers Service — Python background worker (also used by ingestion-worker)
# ----------------------------------------------------------------------------
# Build context is ./workers (see docker-compose.yml). The image is shared by
# the `workers` and `ingestion-worker` services; docker-compose overrides the
# command for the latter.
# ============================================================================

FROM python:3.11-slim AS runtime

# - PYTHONUNBUFFERED: stream logs straight to the container (no buffering)
# - PYTHONDONTWRITEBYTECODE: no .pyc clutter in the layer
# - PIP_NO_CACHE_DIR / PIP_DISABLE_PIP_VERSION_CHECK: smaller, quieter builds
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# `procps` provides pgrep for the liveness healthcheck; `tini` gives correct
# signal handling / zombie reaping for the long-running worker loop.
RUN apt-get update \
    && apt-get install -y --no-install-recommends procps tini \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies first so the layer is cached until requirements change.
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Application code.
COPY . .

# Run as an unprivileged user.
RUN useradd --create-home --uid 10001 worker \
    && chown -R worker:worker /app
USER worker

# The worker has no HTTP surface, so liveness is a process check. `worker.py`
# matches both `worker.py` and `ingestion_worker.py` command overrides.
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD pgrep -f "worker.py" > /dev/null || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "worker.py"]

LABEL org.opencontainers.image.title="cyberintel-workers" \
      org.opencontainers.image.description="CyberIntel Platform background workers" \
      org.opencontainers.image.licenses="MIT"
