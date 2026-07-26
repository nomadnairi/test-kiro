# DeathBot

A **button-driven** aiogram 3 Telegram assistant for OSINT, recon and AI.
There are no feature commands — the whole UI is inline buttons generated from a
single **tool registry** (59 tools / 8 categories) over a strict layered core
(Handlers → Services → Repositories → SQLite).

> This is a self-contained Python project living in `deathbot/`, independent of
> the TypeScript CyberIntel platform in the rest of the repository.

## Architecture

```
Telegram
   │  inline buttons only  (commands: just /start · /menu · /cancel)
   ▼
Handlers  handlers/menu.py ── Middlewares: logging · maintenance · auth · rate-limit
   │       keyboards.py · states/ (FSM) · registry.py  ← 59 tools / 8 categories
   ▼
Services  AccessControl · User · Notes · Todo · ApiKey · AI · OSINT · Pentest ·
   │       Report · Export · Settings · Notification
   ▼
Repositories  User · Access · Invite · Audit · ApiKey · Note · Todo ·
   │           Settings · History · Cache
   ▼
SQLite (aiosqlite)

   ├─ AI Router     OpenAI · OpenRouter · Groq · DeepSeek · Grok · LM Studio ·
   │                AnythingLLM · Claude · Gemini · Ollama   (graceful fallback)
   ├─ Tool Engine   async queue · workers · timeout · retry
   ├─ Agents        general · osint · recon · report · threatintel · code ·
   │                research · planner
   └─ Modules       modules/osint/ (13) · modules/pentest/ (14)
```

### Request flow

`tap category → tap tool → (FSM asks for input) → service → repository / module
→ formatted result → 📤 Export / Save as…`  Adding a capability is **one entry
in `registry.py`** — no new handler, no new command.

## Layout

| Path | Responsibility |
|------|----------------|
| `deathbot/registry.py` | **single source of truth** — every tool is one entry; menus and the input dispatch are generated from it |
| `deathbot/keyboards.py` | inline-keyboard builders (main menu, category submenus, export-format picker) |
| `deathbot/handlers/menu.py` | all button navigation + the FSM tool-runner (chat / text / photo-EXIF / API-key flows) |
| `deathbot/middlewares/` | logging · maintenance · auth · rate-limit |
| `deathbot/states/` · `filters/` | FSM state groups · role filters |
| `deathbot/services/` | business logic (12 services) |
| `deathbot/repositories/` | all SQL, one class per table group (10 repos) |
| `deathbot/modules/osint/` | 13 OSINT tools (whois, dns, subdomains, username, email, phone, geoip, shodan, threatintel, ioc, metadata/exif, reverse-image, darknet) |
| `deathbot/modules/pentest/` | 14 pentest tools (portscan, sslscan, techdetect + `external.py` CLI wrappers) |
| `deathbot/ai/` | provider abstraction + router (10 providers) |
| `deathbot/agents/` | 8 prompt-specialised AI agents |
| `deathbot/tools/engine.py` | async task-execution engine (queue · workers · retry) |
| `deathbot/services/export.py` | 8 export renderers (PDF · DOCX · Obsidian · MD · HTML · CSV · JSON · TXT) |
| `deathbot/core/` | AES-256-GCM crypto, role model |
| `deathbot/db/` | SQLite connection + schema |
| `deathbot/tasks/` | background jobs (cache cleanup) |
| `deathbot/config.py` · `util.py` | env + `config.yaml` loader · subprocess/format helpers |
| `deathbot/container.py` | composition root wiring every layer |
| `deathbot/bot.py` · `__main__.py` | Bot/Dispatcher assembly · `python -m deathbot` entrypoint |

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
  (🛡 Admin → Grant); the owner (`OWNER_ID`) is always active and bypasses
  every check.
- **Role matrix** (`config.yaml → roles`) maps roles to allowed module scopes;
  menu buttons are filtered by role and every tap is access-checked before it runs.
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
- **Export (8):** PDF (reportlab), DOCX (python-docx), Markdown, **Obsidian**
  (YAML frontmatter + tags + callouts), HTML, CSV, JSON, TXT. Every tool result
  gets a **📤 Export / Save as…** button — pick a format and the bot sends the
  file. The Export menu re-exports your last result (or your notes/todos).

Tools that need an API key (Shodan, HIBP, AbuseIPDB) or an external binary
(subfinder, nuclei…) degrade with a clear "needs key / not installed" message
and become fully functional once the key/binary is present. Network-dependent
lookups require the host to have outbound access to the relevant services.
