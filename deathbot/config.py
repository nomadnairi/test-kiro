"""Configuration loader: merges `.env` (secrets) with `config.yaml` (static).

Kept dependency-light on purpose — plain dataclasses over environment and YAML,
no pydantic-settings, so the config layer never fights the rest of the stack.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _as_int(value: str | None, default: int) -> int:
    try:
        return int(value) if value not in (None, "") else default
    except (TypeError, ValueError):
        return default


@dataclass(slots=True)
class AIProviderKeys:
    openai: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    anthropic: str = ""
    openrouter: str = ""
    groq: str = ""
    gemini: str = ""
    deepseek: str = ""
    grok: str = ""
    anythingllm: str = ""
    anythingllm_base_url: str = "http://localhost:3001/api/v1/openai"
    ollama_base_url: str = "http://localhost:11434"
    lmstudio_base_url: str = "http://localhost:1234/v1"


@dataclass(slots=True)
class Settings:
    # --- Telegram / runtime ---
    bot_token: str = ""
    owner_id: int = 0
    env: str = "development"
    log_level: str = "INFO"
    database_path: str = "deathbot.sqlite3"
    secret_key: str = ""
    secret_key_file: str = ""

    # --- Static config (from config.yaml) ---
    raw: dict[str, Any] = field(default_factory=dict)
    ai_keys: AIProviderKeys = field(default_factory=AIProviderKeys)
    osint_keys: dict[str, str] = field(default_factory=dict)

    # ---- Convenience accessors into the yaml tree ----
    @property
    def bot_name(self) -> str:
        return self.raw.get("bot", {}).get("name", "DeathBot")

    @property
    def parse_mode(self) -> str:
        return self.raw.get("bot", {}).get("parse_mode", "HTML")

    @property
    def whitelist_only(self) -> bool:
        return bool(self.raw.get("bot", {}).get("whitelist_only", True))

    @property
    def maintenance(self) -> bool:
        return bool(self.raw.get("bot", {}).get("maintenance", False))

    @property
    def ratelimit(self) -> dict[str, Any]:
        return self.raw.get("ratelimit", {"window_seconds": 10, "max_requests": 20})

    @property
    def ai(self) -> dict[str, Any]:
        return self.raw.get("ai", {})

    @property
    def role_matrix(self) -> dict[str, list[str]]:
        return self.raw.get("roles", {})

    def module_enabled(self, name: str) -> bool:
        return bool(self.raw.get("modules", {}).get(name, True))

    def absolute_db_path(self) -> Path:
        p = Path(self.database_path)
        return p if p.is_absolute() else PROJECT_ROOT / p

    def absolute_key_path(self) -> Path:
        """Where the AES master key lives.

        Defaults to sitting next to the database, so in a container both pieces
        of state land in the same mounted volume — losing the key would make
        every stored API key undecryptable.
        """
        if self.secret_key_file:
            p = Path(self.secret_key_file)
            return p if p.is_absolute() else PROJECT_ROOT / p
        return self.absolute_db_path().parent / ".secret.key"


def load_settings(
    env_file: str | os.PathLike[str] | None = None,
    config_file: str | os.PathLike[str] | None = None,
) -> Settings:
    """Build a :class:`Settings` from the environment and YAML config."""
    load_dotenv(env_file or (PROJECT_ROOT / ".env"), override=False)

    cfg_path = Path(config_file) if config_file else PROJECT_ROOT / "config.yaml"
    raw: dict[str, Any] = {}
    if cfg_path.exists():
        raw = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}

    ai_keys = AIProviderKeys(
        openai=os.getenv("OPENAI_API_KEY", ""),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        anthropic=os.getenv("ANTHROPIC_API_KEY", ""),
        openrouter=os.getenv("OPENROUTER_API_KEY", ""),
        groq=os.getenv("GROQ_API_KEY", ""),
        gemini=os.getenv("GEMINI_API_KEY", ""),
        deepseek=os.getenv("DEEPSEEK_API_KEY", ""),
        grok=os.getenv("GROK_API_KEY", "") or os.getenv("XAI_API_KEY", ""),
        anythingllm=os.getenv("ANYTHINGLLM_API_KEY", ""),
        anythingllm_base_url=os.getenv(
            "ANYTHINGLLM_BASE_URL", "http://localhost:3001/api/v1/openai"
        ),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        lmstudio_base_url=os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1"),
    )

    osint_keys = {
        "shodan": os.getenv("SHODAN_API_KEY", ""),
        "virustotal": os.getenv("VIRUSTOTAL_API_KEY", ""),
        "abuseipdb": os.getenv("ABUSEIPDB_API_KEY", ""),
        "hibp": os.getenv("HIBP_API_KEY", ""),
        "hunter": os.getenv("HUNTER_API_KEY", ""),
        "securitytrails": os.getenv("SECURITYTRAILS_API_KEY", ""),
    }

    return Settings(
        bot_token=os.getenv("BOT_TOKEN", ""),
        owner_id=_as_int(os.getenv("OWNER_ID"), 0),
        env=os.getenv("DEATHBOT_ENV", "development"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        database_path=os.getenv("DATABASE_PATH", "deathbot.sqlite3"),
        secret_key=os.getenv("SECRET_KEY", ""),
        secret_key_file=os.getenv("SECRET_KEY_FILE", ""),
        raw=raw,
        ai_keys=ai_keys,
        osint_keys=osint_keys,
    )
