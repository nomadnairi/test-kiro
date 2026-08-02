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
# Stage 1b: gobuild — compile the Go-based recon/pentest CLIs, and fetch the
# prebuilt phoneinfoga binary
# ---------------------------------------------------------------------------
# phoneinfoga embeds a web client (go:embed client/dist/*) that is not present
# in a plain `go install`, so it is downloaded as a release binary instead.
#
# `go install` auto-switches to whatever newer Go toolchain a module's go.mod
# demands (verified against this exact base: httpx/nuclei/katana/gobuster all
# pulled a newer 1.25/1.26 toolchain on demand and built clean) — the base
# image version below is just the floor, not a hard pin.
FROM golang:1.22-bookworm AS gobuild
ENV CGO_ENABLED=0 GOBIN=/out
RUN mkdir -p /out
RUN go install github.com/lc/gau/v2/cmd/gau@latest \
    || echo "WARN: gau build failed (tool will be reported as not installed)"
RUN curl -sSL "https://raw.githubusercontent.com/sundowndev/phoneinfoga/master/support/scripts/install" \
        | bash -s -- -b /out \
    || echo "WARN: phoneinfoga download failed (tool will be reported as not installed)"

# ProjectDiscovery + community recon/pentest tools — real binaries for the
# "Пентест" menu (these were registered as buttons but never actually built
# into the image before; every one of them build-verified here first).
RUN go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest \
    || echo "WARN: subfinder build failed (tool will be reported as not installed)"
RUN go install github.com/projectdiscovery/httpx/cmd/httpx@latest \
    || echo "WARN: httpx build failed (tool will be reported as not installed)"
RUN go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest \
    || echo "WARN: naabu build failed (tool will be reported as not installed)"
RUN go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest \
    || echo "WARN: nuclei build failed (tool will be reported as not installed)"
RUN go install github.com/projectdiscovery/katana/cmd/katana@latest \
    || echo "WARN: katana build failed (tool will be reported as not installed)"
RUN go install github.com/OJ/gobuster/v3@latest \
    || echo "WARN: gobuster build failed (tool will be reported as not installed)"
RUN go install github.com/ffuf/ffuf/v2@latest \
    || echo "WARN: ffuf build failed (tool will be reported as not installed)"
RUN go install github.com/owasp-amass/amass/v4/...@master \
    || echo "WARN: amass build failed (tool will be reported as not installed)"

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
#   unzip  → feroxbuster's official install script unpacks a .zip release
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tini procps whois nmap whatweb git ca-certificates pipx unzip \
    && rm -rf /var/lib/apt/lists/*

# masscan is packaged for Debian directly — kept in its own non-fatal layer
# (separate apt-get run) so a missing package on some future base image can't
# take the tini/nmap/etc install above down with it.
RUN apt-get update \
    && (apt-get install -y --no-install-recommends masscan \
        || echo "WARN: masscan apt install failed (tool will be reported as not installed)") \
    && rm -rf /var/lib/apt/lists/*

# feroxbuster ships prebuilt release binaries only (Rust, no `go install`
# equivalent) — official script, fixed release-asset URLs (no GitHub API
# call, so it isn't rate-limit-prone).
RUN curl -sSL "https://raw.githubusercontent.com/epi052/feroxbuster/main/install-nix.sh" \
        | bash -s -- /usr/local/bin \
    || echo "WARN: feroxbuster download failed (tool will be reported as not installed)"

# TruffleHog — `go install` does NOT work for this module: its go.mod carries
# replace directives, which Go's module system refuses for `go install
# module@version` on principle (not a network/proxy issue, fails identically
# everywhere). Only the prebuilt release binary works. Version pinned rather
# than resolved via /releases/latest (which needs the GitHub API — bump this
# tag occasionally): https://github.com/trufflesecurity/trufflehog/releases
ARG TRUFFLEHOG_VERSION=3.96.0
RUN curl -sSL "https://github.com/trufflesecurity/trufflehog/releases/download/v${TRUFFLEHOG_VERSION}/trufflehog_${TRUFFLEHOG_VERSION}_linux_amd64.tar.gz" \
        -o /tmp/trufflehog.tar.gz \
    && tar -xzf /tmp/trufflehog.tar.gz -C /usr/local/bin trufflehog \
    && rm -f /tmp/trufflehog.tar.gz \
    || echo "WARN: trufflehog download failed (tool will be reported as not installed)"

# pipx installs each OSINT CLI into its own venv (no dependency clashes with the
# bot's runtime) and drops the entrypoints into /usr/local/bin (on PATH for all
# users). Kept in one layer; failures in a single tool don't abort the build.
ENV PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin
RUN for pkg in \
        sherlock-project holehe maigret socialscan h8mail \
        dnstwist dnsrecon sublist3r checkdmarc wafw00f metafinder ; do \
        pipx install "$pkg" || echo "WARN: pipx install $pkg failed (tool will be reported as not installed)"; \
    done \
    # The "theHarvester" name on PyPI is a dead, ancient 0.0.1 stub with no
    # console script — installing it "succeeds" but leaves no theHarvester
    # binary on PATH, so the tool silently reports "not installed" forever.
    # The real project lives on GitHub only; the current tag (>=4.8.0) needs
    # Python 3.12+, which this image doesn't have, so pin the newest tag that
    # still supports 3.11 and has correct packaging metadata.
    && (pipx install "theHarvester @ git+https://github.com/laramies/theHarvester.git@4.7.1" \
        || echo "WARN: pipx install theHarvester failed (tool will be reported as not installed)") \
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
