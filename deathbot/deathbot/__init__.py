"""DeathBot — a layered aiogram 3 Telegram assistant for OSINT, recon and AI.

Architecture (top to bottom):

    Telegram → Handlers → Services → Repositories → SQLite
                              +  AI Router (multi-provider)
                              +  Tool Engine (async task queue)
"""

__version__ = "0.1.0"
