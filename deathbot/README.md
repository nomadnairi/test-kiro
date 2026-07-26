<h1 align="center">💀 DeathBot</h1>

<p align="center">
  <b>A button-driven Telegram bot for OSINT, recon & AI.</b><br>
  Tap a menu — no commands to memorize. 59 tools, 10 AI providers, 8 export formats.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white">
  <img alt="aiogram" src="https://img.shields.io/badge/aiogram-3-2CA5E0?logo=telegram&logoColor=white">
  <img alt="SQLite" src="https://img.shields.io/badge/storage-SQLite-003B57?logo=sqlite&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green">
</p>

---

## What is it

DeathBot turns a Telegram chat into an OSINT / reconnaissance / AI console.
Everything is driven by **inline buttons** — you tap a category, tap a tool, and
the bot asks for the one thing it needs (a domain, an IP, a question) and returns
a clean result you can **export to PDF, Obsidian, DOCX and more**.

Built on a strict layered architecture (Handlers → Services → Repositories →
SQLite) with role-based access, encrypted API keys and an audit log.

## Highlights

- 🧭 **No commands** — the whole UI is buttons. Only `/start`, `/menu`, `/cancel` exist.
- 🧰 **59 tools** in 8 categories, all generated from one registry.
- 🤖 **10 AI providers** with automatic fallback.
- 📤 **8 export formats** — any result → a file, in one tap.
- 🔐 **Secure by default** — whitelist, roles, AES-256-GCM key storage, audit trail.
- 🧪 **Verifiable** — `smoke_test.py` checks every layer offline (no token needed).

## Quick start

```bash
cd deathbot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # set BOT_TOKEN and OWNER_ID (your Telegram id)
python -m deathbot          # start the bot
```

Send `/start` in Telegram → the menu appears → tap away.
Verify the build without a token: `python smoke_test.py`.

## How it works

```
tap category → tap tool → bot asks for input → result → 📤 Export / Save as…
```

Adding a new tool is **one entry in `registry.py`** — the menus and input handling
are generated automatically. No new command, no new handler.

## Tools

### 🔎 OSINT (13)
| Tool | Does | Needs |
|---|---|---|
| WHOIS · DNS · Subdomains | domain intel (crt.sh for subs) | — |
| Username · Email · Phone | account / contact footprint | HIBP key for breaches |
| GeoIP · Shodan | IP location & exposure | Shodan key |
| Threat Intel · IOC | reputation & indicator triage | AbuseIPDB key |
| Reverse Image · EXIF · Darknet | image OSINT & metadata | — |

### 🛠 Pentest (14) · *authorised targets only*
| Native (always work) | External CLIs (run if installed) |
|---|---|
| Port Scan · SSL Scan · Tech Detect | subfinder · amass · httpx · naabu · nuclei · katana · masscan · rustscan · gobuster · ffuf · feroxbuster |

### 🤖 AI (10 providers)
`OpenAI` · `Claude` · `Gemini` · `OpenRouter` · `Groq` · `DeepSeek` · `Grok` ·
`Ollama` · `LM Studio` · `AnythingLLM` — the router tries your default, then
falls back to whatever is configured. One-shot **Ask** or a **Chat** mode.

### 🧠 Agents (8)
`General` · `OSINT` · `Recon` · `Report` · `Threat Intel` · `Code` · `Research` · `Planner`

### 📤 Export (8)
`PDF` · `DOCX` · `Obsidian` (YAML frontmatter + tags) · `Markdown` · `HTML` ·
`CSV` · `JSON` · `TXT`. Every result gets a **📤 Export / Save as…** button.

> Tools needing a key or an external binary say so clearly and start working the
> moment it's present. Network lookups need the host to have internet access.

## Security

| Layer | What it does |
|---|---|
| **Whitelist** | new users are *pending* until an admin activates them (🛡 Admin → Grant) |
| **Roles** | `owner · admin · analyst · user · guest` — buttons are filtered per role, every tap is access-checked |
| **Encrypted keys** | per-user API keys stored AES-256-GCM, bound to the user id |
| **Audit log** | every privileged action is recorded |
| **Owner override** | `OWNER_ID` is always active and bypasses every gate |

## Project structure

```
deathbot/
├─ registry.py        ← every tool = one entry (menus generated from it)
├─ keyboards.py       inline-keyboard builders
├─ handlers/menu.py   all button navigation + FSM input runner
├─ services/          business logic (12 services)
├─ repositories/      all SQL, one class per table (10)
├─ modules/
│  ├─ osint/          13 OSINT tools
│  └─ pentest/        14 pentest tools
├─ ai/                provider abstraction + router (10 providers)
├─ agents/            8 AI agents
├─ tools/engine.py    async task queue (workers · timeout · retry)
├─ middlewares/       logging · maintenance · auth · rate-limit
├─ core/              AES-256-GCM crypto · roles
├─ db/                SQLite connection + schema
├─ container.py       composition root (wires every layer)
└─ bot.py             Bot/Dispatcher · `python -m deathbot`
```

## Configuration

- **`.env`** — secrets: `BOT_TOKEN`, `OWNER_ID`, and optional provider/OSINT keys
  (OpenAI, Claude, Shodan, HIBP…). Copy from `.env.example`.
- **`config.yaml`** — non-secret settings: rate limits, the role→module matrix,
  default AI provider, feature flags.

---

<p align="center"><sub>MIT · for authorised security research and OSINT only.</sub></p>
