"""Small shared utilities (async subprocess runner, formatting helpers)."""
from __future__ import annotations

import asyncio
import os
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


async def run_command(cmd: list[str], timeout: int = 120, *,
                      cwd: str | None = None, stdin: str | None = None,
                      env: dict[str, str] | None = None) -> CommandResult:
    """Run an external tool, capturing output with a hard timeout.

    ``cwd`` lets tools that write files land in a writable dir (the container's
    /app is read-only). ``stdin`` feeds input to tools that read from it.
    ``env`` merges on top of the current environment (e.g. to point pipx at a
    writable, non-default PIPX_HOME for runtime-installed tools).
    """
    if not cmd or not has_binary(cmd[0]):
        return CommandResult(False, "", f"{cmd[0] if cmd else '?'} not installed",
                             None, missing=True)
    full_env = {**os.environ, **env} if env else None
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE if stdin is not None else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
            env=full_env,
        )
    except OSError as exc:
        return CommandResult(False, "", str(exc), None, missing=True)

    try:
        out, err = await asyncio.wait_for(
            proc.communicate(stdin.encode() if stdin is not None else None),
            timeout=timeout,
        )
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


# --------------------------------------------------------------------------- #
# input validation
# --------------------------------------------------------------------------- #
import re  # noqa: E402

_DOMAIN_RE = re.compile(r"^(?=.{1,253}$)([a-zA-Z0-9](-?[a-zA-Z0-9])*\.)+[a-zA-Z]{2,}$")
_IPV4_RE = re.compile(r"^(\d{1,3})(\.\d{1,3}){3}$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_USERNAME_RE = re.compile(r"^@?[A-Za-z0-9._-]{1,64}$")
_PHONE_RE = re.compile(r"^\+?[0-9][0-9 ()\-]{5,19}$")

_HINTS = {
    "domain": "❌ Похоже, это не домен. Пример: <code>example.com</code>",
    "host": "❌ Нужен домен или IP. Пример: <code>example.com</code> или <code>8.8.8.8</code>",
    "ip": "❌ Похоже, это не IP-адрес. Пример: <code>8.8.8.8</code>",
    "email": "❌ Похоже, это не email. Пример: <code>user@example.com</code>",
    "url": "❌ Нужна ссылка или домен. Пример: <code>https://example.com</code>",
    "username": "❌ Похоже, это не юзернейм (буквы, цифры, . _ -).",
    "phone": "❌ Похоже, это не номер телефона. Пример: <code>+79161234567</code>",
}


def _strip_url(value: str) -> str:
    v = re.sub(r"^https?://", "", value.strip(), flags=re.I)
    return v.split("/")[0].split("?")[0]


def _is_ipv4(value: str) -> bool:
    m = _IPV4_RE.match(value)
    return bool(m) and all(0 <= int(o) <= 255 for o in value.split("."))


def _is_ip(value: str) -> bool:
    return _is_ipv4(value) or (":" in value and len(value) <= 45)


def _is_domain(value: str) -> bool:
    return bool(_DOMAIN_RE.match(value))


_EMAIL_FIND_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_PHONE_FIND_RE = re.compile(r"(?<!\d)(\+?\d[\d\s()\-]{7,17}\d)(?!\d)")


def extract_contacts(text: str) -> tuple[list[str], list[str]]:
    """Best-effort pull of emails and phone numbers out of free-form tool output."""
    emails = sorted({m.lower() for m in _EMAIL_FIND_RE.findall(text)})
    phones = []
    seen: set[str] = set()
    for raw in _PHONE_FIND_RE.findall(text):
        digits = re.sub(r"\D", "", raw)
        if 8 <= len(digits) <= 15 and digits not in seen:
            seen.add(digits)
            phones.append(("+" if raw.strip().startswith("+") else "") + digits)
    return emails, phones


def validate_input(kind: str, value: str) -> str | None:
    """Return an error message if ``value`` is not a valid ``kind``, else None."""
    v = value.strip()
    if not v:
        return "❌ Пустой ввод."
    ok = True
    if kind == "domain":
        ok = _is_domain(_strip_url(v))
    elif kind == "ip":
        ok = _is_ip(v)
    elif kind == "host":
        host = _strip_url(v)
        ok = _is_domain(host) or _is_ip(host)
    elif kind == "email":
        ok = bool(_EMAIL_RE.match(v))
    elif kind == "url":
        ok = v.lower().startswith(("http://", "https://")) or _is_domain(_strip_url(v))
    elif kind == "username":
        ok = bool(_USERNAME_RE.match(v))
    elif kind == "phone":
        ok = bool(_PHONE_RE.match(v))
    return None if ok else _HINTS.get(kind, "❌ Неверный формат ввода.")
