"""Scaffolded modules from the roadmap.

Each command is wired through the same access guard and layered structure as the
implemented ones, but returns a "planned" notice. This keeps the command surface
and permission matrix complete while the heavy integrations are built out.
"""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from ..container import Container
from ._guard import guard

router = Router(name="stubs")

# command -> (module scope used for the access check, human label)
_PLANNED = {
    "image": ("image", "Image / EXIF / reverse-image OSINT"),
    "geoint": ("geoint", "Geospatial intelligence"),
    "crypto": ("crypto", "Crypto address / transaction intel"),
    "network": ("network", "Network analysis"),
    "web": ("web", "Web tech / fingerprinting"),
    "recon": ("recon", "Recon orchestration (subfinder/amass/httpx)"),
    "malware": ("osint", "Malware / sample intel"),
    "sandbox": ("osint", "Sandbox detonation"),
    "reports": ("reports", "Report builder & export"),
}


def _make(command: str, module: str, label: str):
    @router.message(Command(command))
    async def _handler(message: Message, container: Container) -> None:  # noqa: N807
        if not await guard(message, container, module):
            return
        await message.answer(f"🧩 <b>{label}</b> is scaffolded and planned — not wired up yet.")
    return _handler


for _cmd, (_mod, _label) in _PLANNED.items():
    _make(_cmd, _mod, _label)
