"""`python -m deathbot` — launch the bot."""
from __future__ import annotations

import asyncio

from .bot import run


def main() -> None:
    try:
        asyncio.run(run())
    except (KeyboardInterrupt, SystemExit) as exc:
        if isinstance(exc, SystemExit) and exc.code:
            raise
        print("DeathBot stopped.")


if __name__ == "__main__":
    main()
