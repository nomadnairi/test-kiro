"""PluginService — lets the owner install a real CLI tool at runtime from a
pip/git spec (pipx, isolated venv on the persistent /data volume), verify it
actually produced a working binary, and wire it live into the tool registry.

This runs third-party code with the bot's own permissions. There is no
sandboxing beyond pipx's venv isolation — the registry restricts the install
and run buttons to the "admin" module (owner/trusted roles), but the operator
is still trusting whatever spec they type in. Only install sources you trust.

Format accepted from the user: "id | spec | Название | Описание" — spec is
either a bare PyPI package name or a `git+https://...` URL (pip/pipx syntax).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from ..registry import TOOLS, register_custom_tool, unregister_custom_tool
from ..repositories import Repositories
from ..util import run_command

PIPX_HOME = "/data/pipx"
PIPX_BIN_DIR = "/data/pipx/bin"

_ID_RE = re.compile(r"^[a-z][a-z0-9_]{1,29}$")
_SPEC_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+@/:\-]{1,200}$")
_RESERVED = {"custom", "install", "help"}


def _env() -> dict[str, str]:
    return {"PIPX_HOME": PIPX_HOME, "PIPX_BIN_DIR": PIPX_BIN_DIR}


def _venv_apps(list_json_text: str) -> dict[str, list[str]]:
    """venv name -> app (binary) names, from `pipx list --json`."""
    try:
        data = json.loads(list_json_text or "{}")
    except ValueError:
        return {}
    out: dict[str, list[str]] = {}
    for venv_name, venv in (data.get("venvs") or {}).items():
        apps = (venv.get("metadata", {}) or {}).get("main_package", {}).get("apps") or []
        out[venv_name] = apps
    return out


class PluginService:
    def __init__(self, repos: Repositories) -> None:
        self.repos = repos

    async def bootstrap(self) -> None:
        """Re-register every previously installed tool after a process restart."""
        for row in await self.repos.custom_tools.list_all():
            if Path(row["binary_path"]).exists():
                register_custom_tool(row["id"], row["label"], row["description"],
                                     row["binary_path"])

    async def list_installed(self) -> dict:
        rows = await self.repos.custom_tools.list_all()
        if not rows:
            return {"count": 0, "note": "Пока ничего не установлено."}
        return {
            "count": len(rows),
            "tools": [{"id": r["id"], "label": r["label"], "spec": r["spec"],
                      "installed": Path(r["binary_path"]).exists()} for r in rows],
        }

    async def install(self, user_id: int, raw: str) -> dict:
        parts = [p.strip() for p in raw.split("|")]
        if len(parts) < 2 or not parts[0] or not parts[1]:
            return {"available": False, "reason": (
                "Формат: <code>id | спецификатор | Название | Описание</code>\n"
                "id — короткий код латиницей, спецификатор — имя пакета PyPI "
                "или <code>git+https://github.com/автор/репо.git</code>.\n"
                "Пример: <code>dnstwist2 | dnstwist | dnstwist | ещё одна копия для теста</code>"
            )}
        tool_id, spec = parts[0].lower(), parts[1]
        label = parts[2] if len(parts) > 2 and parts[2] else tool_id
        desc = parts[3] if len(parts) > 3 and parts[3] else f"Установлен вручную ({spec})"

        if not _ID_RE.match(tool_id) or tool_id in _RESERVED:
            return {"available": False, "reason": (
                "id: 2-30 символов, строчные латинские буквы/цифры/_, начинается с буквы.")}
        if tool_id in TOOLS:
            return {"available": False,
                   "reason": f"id «{tool_id}» уже занят (встроенный или уже установленный)."}
        if not _SPEC_RE.match(spec):
            return {"available": False, "reason": "Спецификатор содержит недопустимые символы."}

        Path(PIPX_BIN_DIR).mkdir(parents=True, exist_ok=True)

        before = await run_command(["pipx", "list", "--json"], timeout=30, env=_env())
        if before.missing:
            return {"available": False, "reason": "pipx недоступен в этом образе."}
        venvs_before = set(_venv_apps(before.stdout))

        # Force the pip backend explicitly where supported: newer pipx defaults
        # to uv *whenever uv happens to be on PATH*, which makes the outcome
        # depend on unrelated dev tooling on the host rather than the package
        # itself. Older pipx (Debian's apt package) doesn't know --backend at
        # all and always used pip anyway, so fall back to the plain form for it.
        install_res = await run_command(
            ["pipx", "install", "--backend", "pip", spec], timeout=420, env=_env())
        if not install_res.ok and "unrecognized arguments" in (install_res.stderr or ""):
            install_res = await run_command(["pipx", "install", spec], timeout=420, env=_env())
        if not install_res.ok:
            reason = (install_res.stderr or install_res.stdout).strip()[:500]
            return {"available": False, "reason": f"Установка не удалась: {reason or 'см. логи'}"}

        after = await run_command(["pipx", "list", "--json"], timeout=30, env=_env())
        apps_after = _venv_apps(after.stdout)
        new_venvs = set(apps_after) - venvs_before
        if not new_venvs:
            # Package spec matched something already installed under pipx.
            new_venvs = set(apps_after)
        package_name = sorted(new_venvs)[0] if new_venvs else spec
        apps = apps_after.get(package_name, [])
        if not apps:
            return {"available": False, "reason": (
                f"Пакет «{package_name}» установился, но не предоставляет "
                f"исполняемый файл (console script) — его нельзя запускать как CLI.")}
        binary_name = apps[0]
        binary_path = f"{PIPX_BIN_DIR}/{binary_name}"
        if not Path(binary_path).exists():
            return {"available": False, "reason": (
                f"pipx сообщил про бинарник «{binary_name}», но файла нет на диске "
                f"по пути {binary_path}.")}

        smoke = await run_command([binary_path, "--help"], timeout=15)
        if smoke.missing:
            return {"available": False,
                   "reason": "Бинарник не запускается (пропал сразу после установки)."}

        await self.repos.custom_tools.add(tool_id, label, desc, spec, package_name,
                                          binary_path, user_id)
        register_custom_tool(tool_id, label, desc, binary_path)
        return {
            "available": True, "id": tool_id, "label": label, "binary": binary_name,
            "note": "Установлен и уже виден в разделе «🧩 Свои инструменты» — можно запускать.",
        }

    async def remove(self, tool_id: str) -> dict:
        row = await self.repos.custom_tools.get(tool_id)
        if row is None:
            return {"available": False, "reason": f"«{tool_id}» не найден среди установленных."}
        await run_command(["pipx", "uninstall", row["package_name"]], timeout=60, env=_env())
        await self.repos.custom_tools.delete(tool_id)
        unregister_custom_tool(tool_id)
        return {"available": True, "id": tool_id, "note": "Удалён."}
