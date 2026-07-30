"""`python -m deathbot` — launch the bot. `--check` — diagnose the setup."""
from __future__ import annotations

import asyncio
import sys

from .bot import doctor, run


def main() -> None:
    if "--check" in sys.argv[1:]:
        raise SystemExit(asyncio.run(doctor()))
    try:
        asyncio.run(run())
    except (KeyboardInterrupt, SystemExit) as exc:
        if isinstance(exc, SystemExit) and exc.code:
            raise
        print("DeathBot stopped.")


if __name__ == "__main__":
    main()
