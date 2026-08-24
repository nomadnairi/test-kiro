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
# Stage 1b: gobuild — compile amass, the one recon tool left needing an
# actual Go toolchain (see note below)
# ---------------------------------------------------------------------------
# Every other Go-based CLI here moved to a plain `curl`+`unzip`/`tar` download
# of the maintainer's own prebuilt release binary in the runtime stage — no
# Go toolchain, no build step, no toolchain-version surprises, just a file
# download (same idea as feroxbuster/TruffleHog/masscan below). amass is the
# lone holdout: its release-asset naming isn't a fixed, guessable pattern the
# way ProjectDiscovery's tools are, so `go install` is what's verified to work.
FROM golang:1.22-bookworm AS gobuild
ENV CGO_ENABLED=0 GOBIN=/out
RUN mkdir -p /out
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
        tini procps whois nmap whatweb git ca-certificates pipx unzip curl \
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

# phoneinfoga — same reasoning as TruffleHog above: no `go install` path
# (embeds a web client via go:embed that a plain install can't see). The
# upstream install script silently broke (it shells out to tooling the slim
# runtime image lacks); a direct release-asset download is deterministic.
ARG PHONEINFOGA_VERSION=2.11.0
RUN curl -sSL -o /tmp/phoneinfoga.tar.gz \
        "https://github.com/sundowndev/phoneinfoga/releases/download/v${PHONEINFOGA_VERSION}/phoneinfoga_Linux_x86_64.tar.gz" \
    && tar -xzf /tmp/phoneinfoga.tar.gz -C /usr/local/bin phoneinfoga \
    && rm -f /tmp/phoneinfoga.tar.gz \
    || echo "WARN: phoneinfoga download failed (tool will be reported as not installed)"

# ProjectDiscovery + community recon/pentest tools — every one of these
# publishes its own prebuilt Linux binary on GitHub Releases, so there is no
# need for `go install` (or the Go toolchain at all) here. Each asset URL and
# archive layout was verified for real before being wired in. Versions are
# pinned (not resolved via /releases/latest, which needs the GitHub API) —
# bump these occasionally.
ARG SUBFINDER_VERSION=2.9.0
ARG HTTPX_VERSION=1.9.0
ARG NAABU_VERSION=2.6.1
ARG NUCLEI_VERSION=3.9.0
ARG KATANA_VERSION=1.6.1
ARG GOBUSTER_VERSION=3.8.2
ARG FFUF_VERSION=2.2.1
ARG GAU_VERSION=2.2.4
RUN curl -sSL -o /tmp/subfinder.zip "https://github.com/projectdiscovery/subfinder/releases/download/v${SUBFINDER_VERSION}/subfinder_${SUBFINDER_VERSION}_linux_amd64.zip" \
        && unzip -o -q /tmp/subfinder.zip subfinder -d /usr/local/bin && rm -f /tmp/subfinder.zip \
    || echo "WARN: subfinder download failed (tool will be reported as not installed)"
RUN curl -sSL -o /tmp/httpx.zip "https://github.com/projectdiscovery/httpx/releases/download/v${HTTPX_VERSION}/httpx_${HTTPX_VERSION}_linux_amd64.zip" \
        && unzip -o -q /tmp/httpx.zip httpx -d /usr/local/bin && rm -f /tmp/httpx.zip \
    || echo "WARN: httpx download failed (tool will be reported as not installed)"
RUN curl -sSL -o /tmp/naabu.zip "https://github.com/projectdiscovery/naabu/releases/download/v${NAABU_VERSION}/naabu_${NAABU_VERSION}_linux_amd64.zip" \
        && unzip -o -q /tmp/naabu.zip naabu -d /usr/local/bin && rm -f /tmp/naabu.zip \
    || echo "WARN: naabu download failed (tool will be reported as not installed)"
RUN curl -sSL -o /tmp/nuclei.zip "https://github.com/projectdiscovery/nuclei/releases/download/v${NUCLEI_VERSION}/nuclei_${NUCLEI_VERSION}_linux_amd64.zip" \
        && unzip -o -q /tmp/nuclei.zip nuclei -d /usr/local/bin && rm -f /tmp/nuclei.zip \
    || echo "WARN: nuclei download failed (tool will be reported as not installed)"
RUN curl -sSL -o /tmp/katana.zip "https://github.com/projectdiscovery/katana/releases/download/v${KATANA_VERSION}/katana_${KATANA_VERSION}_linux_amd64.zip" \
        && unzip -o -q /tmp/katana.zip katana -d /usr/local/bin && rm -f /tmp/katana.zip \
    || echo "WARN: katana download failed (tool will be reported as not installed)"
RUN curl -sSL -o /tmp/gobuster.tar.gz "https://github.com/OJ/gobuster/releases/download/v${GOBUSTER_VERSION}/gobuster_Linux_x86_64.tar.gz" \
        && tar -xzf /tmp/gobuster.tar.gz -C /usr/local/bin gobuster && rm -f /tmp/gobuster.tar.gz \
    || echo "WARN: gobuster download failed (tool will be reported as not installed)"
RUN curl -sSL -o /tmp/ffuf.tar.gz "https://github.com/ffuf/ffuf/releases/download/v${FFUF_VERSION}/ffuf_${FFUF_VERSION}_linux_amd64.tar.gz" \
        && tar -xzf /tmp/ffuf.tar.gz -C /usr/local/bin ffuf && rm -f /tmp/ffuf.tar.gz \
    || echo "WARN: ffuf download failed (tool will be reported as not installed)"
RUN curl -sSL -o /tmp/gau.tar.gz "https://github.com/lc/gau/releases/download/v${GAU_VERSION}/gau_${GAU_VERSION}_linux_amd64.tar.gz" \
        && tar -xzf /tmp/gau.tar.gz -C /usr/local/bin gau && rm -f /tmp/gau.tar.gz \
    || echo "WARN: gau download failed (tool will be reported as not installed)"

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

# amass (the one tool still built via `go install` — see the gobuild stage
# comment above for why the others don't need this).
COPY --from=gobuild /out/ /usr/local/bin/

# ---------------------------------------------------------------------------
# H2/PHASE-3 build gate: the downloads above keep their `|| echo WARN` so a
# single flaky GitHub mirror can't kill the whole build, but a missing binary
# must never pass silently again (the 02.08 image shipped with 11 tools dead
# and nobody noticed). This step FAILS THE BUILD if any required tool is
# absent, listing exactly which ones — fix the network and rebuild instead of
# deploying a bot whose buttons report "не установлен".
# ---------------------------------------------------------------------------
ARG REQUIRED_TOOLS="subfinder httpx naabu nuclei katana gobuster ffuf gau amass trufflehog phoneinfoga feroxbuster sherlock holehe maigret socialscan h8mail dnstwist dnsrecon sublist3r checkdmarc wafw00f metafinder theHarvester whois masscan whatweb"
RUN missing=""; \
    for t in $REQUIRED_TOOLS; do \
        command -v "$t" >/dev/null 2>&1 || missing="$missing $t"; \
    done; \
    if [ -n "$missing" ]; then \
        echo "BUILD FAILED — required OSINT tools not installed:$missing" >&2; \
        exit 1; \
    fi; \
    echo "build gate: all required OSINT tools present"

# The Python `httpx` library installs a broken CLI shim into /opt/venv/bin
# that shadows ProjectDiscovery's httpx on PATH (the library needs the
# `[cli]` extra for its CLI, which we don't use — but the shim still wins
# name resolution). The bot uses httpx as a *library* only, so removing the
# shim leaves PD's recon binary as the one true `httpx`.
RUN rm -f /opt/venv/bin/httpx

# exiftool is optional (EXIF has an in-process PIL fallback) but wanted.
RUN command -v exiftool >/dev/null 2>&1 \
    || apt-get update && apt-get install -y --no-install-recommends libimage-exiftool-perl \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    # State (SQLite DB + AES master key) lives on a volume, not in the image.
    DATABASE_PATH=/data/deathbot.sqlite3 \
    SECRET_KEY_FILE=/data/.secret.key

COPY --from=builder /opt/venv /opt/venv

# The Python `httpx` library ships a CLI shim in the venv that shadows
# ProjectDiscovery's httpx recon binary on PATH (the shim needs the `[cli]`
# extra to actually work, which we don't install). Remove it AFTER the venv
# lands so PD's binary is the one true `httpx`. The library itself stays.
RUN rm -f /opt/venv/bin/httpx

WORKDIR /app
COPY deathbot/ ./deathbot/
COPY config.yaml smoke_test.py ./

# Unprivileged user; /app stays read-only to it, /data is the only writable path.
RUN useradd --create-home --uid 10001 deathbot \
    && mkdir -p /data /home/deathbot/.config/subfinder \
    && echo "# minimal subfinder config" > /home/deathbot/.config/subfinder/config.yaml \
    && chown -R deathbot:deathbot /data /home/deathbot/.config

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
