"""PluginService — lets the owner install a real CLI tool at runtime, verify
it actually produced a working binary, and wire it live into the tool
registry. Two install modes, both landing on the persistent /data volume:

  - pipx: a PyPI package name or a `git+https://...` spec (Python tools).
  - url:  a direct link to a prebuilt binary or a .tar.gz/.zip release
    archive — the same shape as most Go/Rust CLI releases on GitHub. No Go
    toolchain, no pip, nothing except curl + tar/unzip (already in the image
    for feroxbuster/TruffleHog/masscan).

This runs third-party code with the bot's own permissions. There is no
sandboxing beyond process isolation — the registry restricts the install and
run buttons to the "admin" module (owner/trusted roles), but the operator is
still trusting whatever spec/URL they type in. Only install sources you trust.

Format accepted from the user: "id | spec | Название | Описание | бинарник"
— the last field is only needed for URL installs when the archive contains
more than one file and auto-detection can't guess which one is the tool.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from ..registry import TOOLS, register_custom_tool, unregister_custom_tool
from ..repositories import Repositories
from ..util import run_command

PIPX_HOME = "/data/pipx"
PIPX_BIN_DIR = "/data/pipx/bin"
PLUGINS_DIR = "/data/plugins"

_ID_RE = re.compile(r"^[a-z][a-z0-9_]{1,29}$")
_SPEC_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+@/:\-]{1,200}$")
_URL_RE = re.compile(r"^https?://[A-Za-z0-9][A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%\-]{3,500}$")
_RESERVED = {"custom", "install", "help"}
_SKIP_NAMES = {"license", "license.md", "license.txt", "notice", "notice.md",
              "changelog", "changelog.md", "changelog.txt"}


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


def _find_single_binary(plugin_dir: Path, hint: str) -> Path | None:
    if hint:
        candidate = plugin_dir / hint
        return candidate if candidate.is_file() else None
    candidates = [
        p for p in plugin_dir.iterdir()
        if p.is_file() and p.name.lower() not in _SKIP_NAMES
        and not p.name.lower().startswith("readme")
    ]
    return candidates[0] if len(candidates) == 1 else None


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
                      "method": r["method"],
                      "installed": Path(r["binary_path"]).exists()} for r in rows],
        }

    async def install(self, user_id: int, raw: str) -> dict:
        parts = [p.strip() for p in raw.split("|")]
        if len(parts) < 2 or not parts[0] or not parts[1]:
            return {"available": False, "reason": (
                "Формат: <code>id | спецификатор | Название | Описание | бинарник</code>\n"
                "Два режима, определяются по спецификатору:\n"
                "• <b>pipx</b> — имя пакета PyPI или "
                "<code>git+https://github.com/автор/репо.git</code>\n"
                "• <b>прямая ссылка</b> — <code>https://.../tool_linux_amd64.tar.gz</code> "
                "(.tar.gz/.zip или голый бинарник). Поле «бинарник» — только если в архиве "
                "больше одного файла и бот не смог угадать, какой из них запускать.\n\n"
                "Примеры:\n"
                "<code>dnstwist2 | dnstwist | dnstwist | тест</code>\n"
                "<code>subfinder2 | https://github.com/projectdiscovery/subfinder/releases/"
                "download/v2.9.0/subfinder_2.9.0_linux_amd64.zip | subfinder2</code>"
            )}
        tool_id, spec = parts[0].lower(), parts[1]
        label = parts[2] if len(parts) > 2 and parts[2] else tool_id
        desc = parts[3] if len(parts) > 3 and parts[3] else f"Установлен вручную ({spec})"
        binary_hint = parts[4].strip() if len(parts) > 4 and parts[4].strip() else ""

        if not _ID_RE.match(tool_id) or tool_id in _RESERVED:
            return {"available": False, "reason": (
                "id: 2-30 символов, строчные латинские буквы/цифры/_, начинается с буквы.")}
        if tool_id in TOOLS:
            return {"available": False,
                   "reason": f"id «{tool_id}» уже занят (встроенный или уже установленный)."}

        if spec.startswith(("http://", "https://")):
            return await self._install_from_url(user_id, tool_id, spec, label, desc, binary_hint)
        return await self._install_from_pipx(user_id, tool_id, spec, label, desc)

    async def _install_from_pipx(self, user_id: int, tool_id: str, spec: str,
                                 label: str, desc: str) -> dict:
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

        return await self._finish_install(user_id, tool_id, label, desc, spec,
                                          "pipx", package_name, binary_path, binary_name)

    async def _install_from_url(self, user_id: int, tool_id: str, url: str,
                                label: str, desc: str, binary_hint: str) -> dict:
        if not _URL_RE.match(url):
            return {"available": False, "reason": "Ссылка выглядит некорректно."}

        plugin_dir = Path(PLUGINS_DIR) / tool_id
        plugin_dir.mkdir(parents=True, exist_ok=True)
        download_path = plugin_dir / "download.bin"

        dl = await run_command(["curl", "-sSL", "-f", "-o", str(download_path), url], timeout=180)
        if dl.missing:
            shutil.rmtree(plugin_dir, ignore_errors=True)
            return {"available": False, "reason": "curl недоступен в этом образе."}
        if not dl.ok or not download_path.exists() or download_path.stat().st_size == 0:
            shutil.rmtree(plugin_dir, ignore_errors=True)
            reason = (dl.stderr or "").strip()[:300]
            return {"available": False,
                   "reason": f"Не удалось скачать файл. {reason or 'Проверь ссылку.'}"}

        lower = url.lower()
        is_archive = lower.endswith((".tar.gz", ".tgz", ".zip"))

        if not is_archive:
            # Raw binary download — the file itself IS the tool.
            binary_path = plugin_dir / (binary_hint or tool_id)
            download_path.rename(binary_path)
        else:
            if lower.endswith(".zip"):
                res = await run_command(
                    ["unzip", "-o", "-q", str(download_path), "-d", str(plugin_dir)], timeout=60)
            else:
                res = await run_command(
                    ["tar", "-xzf", str(download_path), "-C", str(plugin_dir)], timeout=60)
            download_path.unlink(missing_ok=True)
            if not res.ok:
                shutil.rmtree(plugin_dir, ignore_errors=True)
                reason = (res.stderr or "").strip()[:300]
                return {"available": False, "reason": f"Не удалось распаковать архив. {reason}"}

            found = _find_single_binary(plugin_dir, binary_hint)
            if found is None:
                shutil.rmtree(plugin_dir, ignore_errors=True)
                return {"available": False, "reason": (
                    "В архиве больше одного файла — не могу угадать, какой из них "
                    "запускать. Укажи имя пятым полем: "
                    "<code>id | ссылка | Название | Описание | имя_бинарника</code>")}
            binary_path = found

        if not binary_path.exists():
            shutil.rmtree(plugin_dir, ignore_errors=True)
            return {"available": False, "reason": "Файл после распаковки не найден."}

        binary_path.chmod(0o755)

        smoke = await run_command([str(binary_path), "--help"], timeout=15)
        if smoke.missing:
            shutil.rmtree(plugin_dir, ignore_errors=True)
            return {"available": False, "reason": "Скачанный файл не запускается."}

        return await self._finish_install(user_id, tool_id, label, desc, url,
                                          "url", str(plugin_dir), str(binary_path),
                                          binary_path.name)

    async def _finish_install(self, user_id: int, tool_id: str, label: str, desc: str,
                              spec: str, method: str, package_name: str,
                              binary_path: str, binary_name: str) -> dict:
        await self.repos.custom_tools.add(tool_id, label, desc, spec, method,
                                          package_name, binary_path, user_id)
        register_custom_tool(tool_id, label, desc, binary_path)
        return {
            "available": True, "id": tool_id, "label": label, "binary": binary_name,
            "note": "Установлен и уже виден в разделе «🧩 Свои инструменты» — можно запускать.",
        }

    async def remove(self, tool_id: str) -> dict:
        row = await self.repos.custom_tools.get(tool_id)
        if row is None:
            return {"available": False, "reason": f"«{tool_id}» не найден среди установленных."}
        if row["method"] == "url":
            shutil.rmtree(row["package_name"], ignore_errors=True)
        else:
            await run_command(["pipx", "uninstall", row["package_name"]], timeout=60, env=_env())
        await self.repos.custom_tools.delete(tool_id)
        unregister_custom_tool(tool_id)
        return {"available": True, "id": tool_id, "note": "Удалён."}
