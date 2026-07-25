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

## Command surface

`/start /help /menu /profile` · `/note /notes /delnote` · `/todo /todos /done`
· `/ai /chat /reset /providers` · `/whois /dns` · `/scan` ·
`/settings /setprovider /addkey /keys` · `/users /grant /ban /unban /audit /tools`

Planned/scaffolded modules (respond as "planned"): `/image /geoint /crypto
/network /web /recon /malware /sandbox /reports`.

## What's implemented vs scaffolded

**Working end-to-end:** config, SQLite + all repositories, RBAC + whitelist +
audit, notes/todo CRUD, encrypted API keys, AI router with graceful fallback,
OSINT whois/dns, port scanning (nmap or asyncio fallback), export
(md/json/html/csv), tool engine, background cache cleanup.

**Scaffolded (structure in place, integrations pending):** the extended OSINT
sources (Shodan/HIBP/VirusTotal…), full pentest toolchain (amass/nuclei/httpx…),
PDF/DOCX export (optional deps), and the roadmap's remaining handler modules.
