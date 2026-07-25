# DeathBot

A layered **aiogram 3** Telegram assistant for OSINT, recon and AI — built to
the DeathBot roadmap (Handlers → Services → Repositories → SQLite, with an AI
router and an async tool engine on the side).

> This is a self-contained Python project living in `deathbot/`, independent of
> the TypeScript CyberIntel platform in the rest of the repository.

## Architecture

```
Telegram
   │
   ▼
Handlers ── Middlewares (logging · maintenance · auth · rate-limit) · FSM
   │
   ▼
Services ── AccessControl · User · Notes · Todo · ApiKey · AI · OSINT · Pentest
   │         Report · Export · Settings · Notification
   ▼
Repositories ── User · Access · Invite · Audit · ApiKey · Note · Todo
   │             Settings · History · Cache
   ▼
SQLite (aiosqlite)

        +  AI Router  (OpenAI · OpenRouter · Groq · DeepSeek · Ollama)
        +  Tool Engine (async queue · workers · timeout · retry)
        +  Agents (general · osint · recon · report)
```

## Layout

| Path | Responsibility |
|------|----------------|
| `deathbot/config.py` | env + `config.yaml` loader |
| `deathbot/db/` | SQLite connection + schema |
| `deathbot/core/` | AES-256-GCM crypto, role model |
| `deathbot/repositories/` | all SQL, one class per table group |
| `deathbot/services/` | business logic |
| `deathbot/ai/` | provider abstraction + router |
| `deathbot/middlewares/` `filters/` `states/` `handlers/` | aiogram layer |
| `deathbot/modules/` | OSINT (whois/dns) & pentest (portscan) |
| `deathbot/tools/` | async task execution engine |
| `deathbot/agents/` | prompt-specialised AI agents |
| `deathbot/container.py` | composition root wiring every layer |

## Quick start

```bash
cd deathbot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env          # set BOT_TOKEN and OWNER_ID
python -m deathbot            # start polling
```

Run the offline verification (no Telegram token needed):

```bash
python smoke_test.py
```

## Security model

- **Whitelist gate** — new users are *pending* until an admin activates them
  (`/grant`); the owner (`OWNER_ID`) is always active and bypasses every check.
- **Role matrix** (`config.yaml → roles`) maps roles to allowed module scopes;
  every handler passes through an access guard.
- **Encrypted API keys** — per-user provider keys are stored AES-256-GCM
  encrypted, bound to the user id via the AEAD associated data.
- **Audit log** — privileged actions are recorded in `audit_logs`.

## Interface — buttons, not commands

There are **no feature commands**. Everything is reached by tapping inline
buttons. Only three commands exist to bootstrap/reset the UI: `/start`,
`/menu`, `/cancel`. Tapping a tool that needs input puts the chat into a short
FSM prompt ("Send a domain…"), then returns the result with Back / Menu buttons.

The whole button surface is generated from a single **tool registry**
(`deathbot/registry.py`) — one entry per tool, ~59 tools across 8 categories.
Adding a tool is one dataclass entry; no new handler, no new command.

Menu → **OSINT · Pentest · AI · Agents · Notes & Todo · Export · Settings · Admin**

## Tools (all implemented)

- **OSINT (13):** WHOIS, DNS, Subdomains (crt.sh), Username search, Email
  (Gravatar + HIBP), Phone, GeoIP (ip-api), Shodan, Threat Intel
  (URLhaus + AbuseIPDB), IOC classify, Reverse-image search, Metadata/EXIF
  (Pillow), Darknet (safe stub).
- **Pentest (14):** Port scan (nmap/asyncio), SSL scan (native), Tech detect,
  plus CLI wrappers run through the tool engine: subfinder, amass, httpx,
  naabu, nuclei, katana, masscan, rustscan, gobuster, ffuf, feroxbuster.
- **AI providers (10):** OpenAI, OpenRouter, Groq, DeepSeek, Grok, LM Studio,
  AnythingLLM, Claude (Anthropic), Gemini, Ollama — with graceful fallback.
- **Agents (8):** General, OSINT, Recon, Report, Threat Intel, Code, Research,
  Planner.
- **Export (6):** JSON, Markdown, HTML, CSV, PDF (reportlab), DOCX (python-docx).

Tools that need an API key (Shodan, HIBP, AbuseIPDB) or an external binary
(subfinder, nuclei…) degrade with a clear "needs key / not installed" message
and become fully functional once the key/binary is present. Network-dependent
lookups require the host to have outbound access to the relevant services.
