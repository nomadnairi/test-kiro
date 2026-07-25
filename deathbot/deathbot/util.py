"""Small shared utilities (async subprocess runner, formatting helpers)."""
from __future__ import annotations

import asyncio
import shutil
from dataclasses import dataclass


@dataclass(slots=True)
class CommandResult:
    ok: bool
    stdout: str
    stderr: str
    code: int | None
    missing: bool = False  # binary not installed


def has_binary(name: str) -> bool:
    return shutil.which(name) is not None


async def run_command(cmd: list[str], timeout: int = 120) -> CommandResult:
    """Run an external tool, capturing output with a hard timeout."""
    if not cmd or not has_binary(cmd[0]):
        return CommandResult(False, "", f"{cmd[0] if cmd else '?'} not installed",
                             None, missing=True)
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except OSError as exc:
        return CommandResult(False, "", str(exc), None, missing=True)

    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        return CommandResult(False, "", f"timed out after {timeout}s", None)

    return CommandResult(
        ok=proc.returncode == 0,
        stdout=out.decode(errors="replace"),
        stderr=err.decode(errors="replace"),
        code=proc.returncode,
    )


def truncate(text: str, limit: int = 3500) -> str:
    return text if len(text) <= limit else text[:limit] + "\n… (truncated)"
