"""Tool registry — the single source of truth for the button UI.

Every capability the bot exposes is declared here once. The menu keyboards and
the input dispatcher are generated from this list, so adding a tool means adding
one entry — no new handler, no new command.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape, unescape
from typing import TYPE_CHECKING, Awaitable, Callable

_TAG_RE = re.compile(r"<[^>]+>")


def strip_html(text: str) -> str:
    """Turn the HTML we send to Telegram back into plain text for file exports."""
    return unescape(_TAG_RE.sub("", text))


_TRANSLIT = str.maketrans({
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
})


def _slug(title: str) -> str:
    """Filesystem-safe file stem — titles are Russian, so transliterate first."""
    stem = re.sub(r"[^a-z0-9]+", "-", title.lower().translate(_TRANSLIT))
    return stem.strip("-")[:40] or "report"

if TYPE_CHECKING:
    from .container import Container

# Category id -> button label (order defines the main-menu layout).
CATEGORIES: list[tuple[str, str]] = [
    ("workflows", "🧩 Комбайны"),
    ("osint", "🔎 OSINT"),
    ("pentest", "🛠 Пентест"),
    ("ai", "🤖 ИИ"),
    ("agents", "🧠 Агенты"),
    ("productivity", "📝 Заметки и задачи"),
    ("export", "📤 Экспорт"),
    ("custom", "🧩 Свои инструменты"),
    ("settings", "⚙️ Настройки"),
    ("admin", "🛡 Админ"),
]


@dataclass(slots=True)
class Result:
    text: str
    filename: str | None = None
    file_bytes: bytes | None = None
    report: dict | None = None        # rich report to remember for export (workflows)


@dataclass(slots=True)
class Tool:
    id: str
    label: str
    category: str
    module: str                       # access scope checked before running
    kind: str = "input"               # input | instant | chat | photo | apikey
    prompt: str | None = None
    run: Callable[["Container", int, str], Awaitable[Result]] | None = None
    desc: str = ""                    # one-line "what it does", shown on tap
    background: bool = False           # run via the task engine (slow tools)
    validate: str = ""                # expected input: domain|host|ip|email|url|username|phone
    subcategory: str = ""             # groups tools within a category into a tree, like the site


# --------------------------------------------------------------------------- #
# formatting helpers
# --------------------------------------------------------------------------- #
def _pre(text: str, limit: int = 3200) -> str:
    text = text if len(text) <= limit else text[:limit] + "\n… (обрезано)"
    return f"<pre>{escape(text)}</pre>"


# Field names come back from the tool modules in English; show them in Russian.
FIELD_LABELS: dict[str, str] = {
    "domain": "домен", "host": "хост", "query": "запрос", "url": "ссылка",
    "addresses": "адреса", "reverse": "обратная запись", "error": "ошибка",
    "subdomains": "поддомены", "count": "найдено", "checked": "проверено",
    "username": "юзернейм", "found": "найдено", "found_count": "найдено профилей",
    "email": "email", "valid_format": "формат верный", "gravatar": "gravatar",
    "hibp": "утечки (HIBP)", "breaches": "утечки", "available": "доступно",
    "input": "ввод", "digits": "цифры", "e164": "формат E.164",
    "country_guess": "страна (предположительно)", "length": "длина",
    "country": "страна", "regionName": "регион", "city": "город", "zip": "индекс",
    "lat": "широта", "lon": "долгота", "isp": "провайдер", "org": "организация",
    "as": "AS", "timezone": "часовой пояс", "map": "карта",
    "ports": "порты", "open_ports": "открытые порты", "hostnames": "имена хостов",
    "vulns": "уязвимости", "os": "ОС", "engine": "движок",
    "indicator": "индикатор", "sources": "источники", "listed": "в списках",
    "url_count": "ссылок", "urls": "ссылки", "abuse_score": "уровень угрозы",
    "total_reports": "всего жалоб", "source": "источник",
    "value": "значение", "type": "тип", "suggested_lookups": "что ещё проверить",
    "image_url": "ссылка на изображение", "engines": "поисковики",
    "format": "формат", "size": "размер", "camera": "камера",
    "datetime": "дата съёмки", "software": "софт", "gps": "GPS",
    "tool": "инструмент", "target": "цель", "installed": "установлен",
    "ok": "успешно", "output": "вывод", "raw": "ответ", "note": "примечание",
    "hint": "подсказка", "reason": "причина", "status": "статус",
    "tls_version": "версия TLS", "cipher": "шифр", "subject_cn": "выдан на",
    "issuer": "издатель", "valid_from": "действует с", "valid_until": "действует до",
    "days_until_expiry": "дней до истечения", "san": "альт. имена",
    "server": "сервер", "powered_by": "работает на", "frameworks": "фреймворки",
    "headers_of_interest": "заголовки", "security_headers": "заголовки безопасности",
    "port": "порт", "profiles": "профили", "sites": "сайты",
    "unavailable": "занято", "availableCount": "свободно", "unavailableCount": "занято",
    "id": "ID", "role": "роль", "notes": "заметки", "todos": "задачи",
    "since": "с", "pending_update_count": "апдейтов в очереди",
    "total_hits": "всего совпадений", "breaches": "утечки",
    "fields": "поля", "found": "найдено", "infected_machines": "заражённых устройств",
    "credentials_on_machine": "учёток на устройстве", "entries": "записи",
    "pattern": "паттерн почты", "organization": "организация",
    "email_count": "найдено email", "emails": "email-адреса", "confidence": "уверенность",
    "score": "оценка", "deliverable": "доставляемость", "disposable": "одноразовый",
    "webmail": "веб-почта", "mx_records": "MX-записи", "reputation": "репутация",
    "suspicious": "подозрительный", "references": "упоминаний",
    "blacklisted": "в чёрных списках", "malicious_activity": "вредоносная активность",
    "credentials_leaked": "учётки в утечках", "data_breach": "утечка данных",
    "spam": "спам", "first_seen": "впервые замечен", "last_seen": "последний раз замечен",
    "service": "сервис", "confidence": "уверенность", "match": "фрагмент",
    "line": "строка", "chars_scanned": "символов проверено",
    "label": "название", "spec": "источник", "binary": "бинарник", "tools": "инструменты",
}


def _label(key: str) -> str:
    return FIELD_LABELS.get(key, key)


def human(title: str, data: dict) -> str:
    """Render a result dict into readable Telegram HTML."""
    lines = [f"<b>{escape(title)}</b>"]
    raw_keys = ("raw", "output", "note", "hint", "reason")
    for key, value in data.items():
        if value in (None, "", [], {}):
            continue
        name = _label(key)
        if key in raw_keys:
            lines.append(_pre(str(value)))
        elif isinstance(value, dict):
            inner = "\n".join(f"  {escape(_label(str(k)))}: {escape(str(v))}"
                              for k, v in value.items() if v not in (None, ""))
            lines.append(f"<b>{escape(name)}</b>:\n{inner}")
        elif isinstance(value, list):
            if not value:
                continue
            if isinstance(value[0], dict):
                items = "\n".join("  • " + ", ".join(f"{_label(k)}={v}" for k, v in d.items())
                                  for d in value[:25])
            else:
                items = "\n".join(f"  • {escape(str(v))}" for v in value[:40])
            more = f"\n  … ещё {len(value) - 40}" if len(value) > 40 else ""
            lines.append(f"<b>{escape(name)}</b> ({len(value)}):\n{items}{more}")
        else:
            lines.append(f"<b>{escape(name)}</b>: {escape(str(value))}")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# run() implementations
# --------------------------------------------------------------------------- #
def _osint(method: str, title: str):
    async def _run(c: "Container", uid: int, arg: str) -> Result:
        data = await getattr(c.osint, method)(uid, arg)
        return Result(human(f"{title}: {arg}", data))
    return _run


def _pentest_native(method: str, title: str):
    async def _run(c: "Container", uid: int, arg: str) -> Result:
        data = await getattr(c.pentest, method)(uid, arg)
        return Result(human(f"{title}: {arg}", data))
    return _run


def _cli_result(title: str, arg: str, data: dict) -> Result:
    if data.get("installed") is False:
        return Result(f"<b>{escape(title)}</b>\n⚠️ {escape(data.get('hint', 'инструмент не установлен'))}")
    if data.get("error"):
        return Result(f"<b>{escape(title)}</b>\n⚠️ {escape(str(data['error']))}")
    # Render just the command output as a <pre> block (raw_keys → preformatted).
    return Result(human(f"{title}: {arg}", {"output": data.get("output", "(пусто)")}))


def _external(tool_id: str, title: str):
    async def _run(c: "Container", uid: int, arg: str) -> Result:
        return _cli_result(title, arg, await c.pentest.external(uid, tool_id, arg))
    return _run


def _osint_cli(tool_id: str, title: str):
    async def _run(c: "Container", uid: int, arg: str) -> Result:
        return _cli_result(title, arg, await c.osint.cli(uid, tool_id, arg))
    return _run


def _custom_cli(binary_path: str, title: str):
    """Run-builder for owner-installed tools (see services/plugins.py)."""
    async def _run(c: "Container", uid: int, arg: str) -> Result:
        from .util import run_command
        await c.repos.audit.log(uid, f"custom.{title}", arg)
        res = await run_command([binary_path, arg], timeout=180, cwd="/tmp")
        if res.missing:
            return Result(f"<b>{escape(title)}</b>\n⚠️ Бинарник пропал с диска "
                          f"(volume пересоздан?) — переустанови инструмент.")
        return _cli_result(title, arg, {
            "installed": True, "output": (res.stdout or res.stderr).strip() or "(пустой вывод)",
        })
    return _run


# --------------------------------------------------------------------------- #
# combine workflows — chain several tools into one report
# --------------------------------------------------------------------------- #
def _report(title: str, tags: list[str], sections: dict[str, str]) -> dict:
    return {
        "title": title,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tags": ["deathbot", *tags],
        "sections": sections,
    }


async def _collect(steps: list[tuple[str, Awaitable[dict]]]) -> dict[str, str]:
    """Run each step, rendering its result (or error) into a plain-text section."""
    sections: dict[str, str] = {}
    for name, coro in steps:
        try:
            data = await coro
            if data.get("installed") is False:
                sections[name] = data.get("hint", "инструмент не установлен")
            else:
                sections[name] = strip_html(human(name, data))
        except Exception as exc:  # noqa: BLE001
            sections[name] = f"ошибка: {exc}"
    return sections


def _wf_result(title: str, report: dict, sections: dict[str, str]) -> Result:
    summary = ("✅ <b>" + escape(title) + "</b>\nСобрано: "
               + ", ".join(sections.keys())
               + "\n\nНажми «📤 Сохранить как…», чтобы получить отчёт файлом.")
    return Result(summary, report=report)


async def _wf_domain(c: "Container", uid: int, arg: str) -> Result:
    d = arg.strip().lower()
    sections = await _collect([
        ("WHOIS", c.osint.whois(uid, d)),
        ("DNS", c.osint.dns(uid, d)),
        ("Поддомены", c.osint.subdomains(uid, d)),
        ("Почтовая защита (DMARC)", c.osint.cli(uid, "checkdmarc", d)),
        ("Технологии сайта", c.pentest.tech_detect(uid, d)),
    ])
    report = _report(f"Отчёт по домену {d}", ["домен", d], sections)
    return _wf_result(f"Отчёт по домену {d}", report, sections)


async def _wf_username(c: "Container", uid: int, arg: str) -> Result:
    u = arg.strip().lstrip("@")
    sections = await _collect([
        ("Профили (быстрая проверка)", c.osint.username(uid, u)),
        ("Maigret", c.osint.cli(uid, "maigret", u)),
    ])
    report = _report(f"Профиль по нику {u}", ["username", u], sections)
    return _wf_result(f"Профиль по нику {u}", report, sections)


async def _wf_ip(c: "Container", uid: int, arg: str) -> Result:
    ip = arg.strip()
    sections = await _collect([
        ("Геолокация", c.osint.geoip(uid, ip)),
        ("Репутация / угрозы", c.osint.threat_intel(uid, ip)),
        ("Shodan", c.osint.shodan(uid, ip)),
    ])
    report = _report(f"Досье по IP {ip}", ["ip", ip], sections)
    return _wf_result(f"Досье по IP {ip}", report, sections)


async def _wf_person(c: "Container", uid: int, arg: str) -> Result:
    """Identity dossier: pivot from a username through profiles → emails/phones →
    leaks → names, aggregating every open data point into one report."""
    from .util import extract_contacts

    u = arg.strip().lstrip("@")
    sections: dict[str, str] = {}
    pool = ""  # combined raw output to mine for emails/phones

    # 1) social footprint
    for name, tid in [("Maigret", "maigret"), ("Sherlock", "sherlock_cli"),
                      ("socialscan", "socialscan")]:
        try:
            d = await c.osint.cli(uid, tid, u)
            text = d.get("hint", "") if d.get("installed") is False else d.get("output", "")
            sections[name] = text or "(пусто)"
            if d.get("installed") is not False:
                pool += "\n" + text
        except Exception as exc:  # noqa: BLE001
            sections[name] = f"ошибка: {exc}"

    # 2) pivot: emails & phones surfaced in the profiles
    emails, phones = extract_contacts(pool)
    if emails:
        sections["📧 Найденные email"] = "\n".join(emails)
    if phones:
        sections["📱 Найденные телефоны"] = "\n".join(phones)

    # 3) email intelligence (where used + leaks) for the first few
    for em in emails[:3]:
        try:
            h = await c.osint.cli(uid, "holehe", em)
            sections[f"Holehe · {em}"] = (
                h.get("hint", "") if h.get("installed") is False else h.get("output", ""))
        except Exception as exc:  # noqa: BLE001
            sections[f"Holehe · {em}"] = f"ошибка: {exc}"
        sections[f"Утечки · {em}"] = strip_html(human("", await c.osint.leak(uid, em)))

    # 4) phone leaks
    for ph in phones[:3]:
        sections[f"Утечки · {ph}"] = strip_html(human("", await c.osint.leak(uid, ph)))

    # 5) ФИО — the profile pool often carries display names; give ready search
    #    links for the queried handle so the analyst can pin the real name.
    sections["Поиск по имени (ссылки)"] = strip_html(human("", await c.osint.name(uid, u)))

    sections["ℹ️ Заметка"] = (
        "Автопереход ник→email→телефон работает настолько, насколько инструменты "
        "(Maigret и др.) установлены и раскрыли контакты. Полные слитые записи и "
        "надёжный поиск телефона по утечкам требуют платного ключа (Dehashed/LeakCheck Pro).")

    report = _report(f"Досье по личности: {u}", ["person", u], sections)
    return _wf_result(f"Досье по личности: {u}", report, sections)


def _agent(agent_id: str, title: str):
    async def _run(c: "Container", uid: int, arg: str) -> Result:
        agent = c.agents[agent_id]
        user_keys = await c.ai.user_keys(uid)
        answer = await agent.run(arg, user_keys=user_keys)
        await c.repos.audit.log(uid, f"agent.{agent_id}", arg[:60])
        return Result(f"<b>{escape(title)}</b>\n\n{escape(answer)}")
    return _run


async def _ai_ask(c: "Container", uid: int, arg: str) -> Result:
    return Result(escape(await c.ai.ask(uid, arg)))


def _ai_mode(instruction: str, title: str):
    """One-shot AI utility (translate/summarize/review/…) — real model call,
    just a fixed instruction instead of a free-form question."""
    async def _run(c: "Container", uid: int, arg: str) -> Result:
        answer = await c.ai.run_mode(uid, instruction, arg)
        await c.repos.audit.log(uid, f"ai.mode.{title}", arg[:60])
        return Result(f"<b>{escape(title)}</b>\n\n{escape(answer)}")
    return _run


async def _ai_reset(c: "Container", uid: int, _: str) -> Result:
    await c.ai.reset(uid)
    return Result("🧹 История диалога очищена.")


async def _ai_providers(c: "Container", uid: int, _: str) -> Result:
    rows = await c.ai.provider_status(uid)
    lines = []
    for r in rows:
        mark = "✅" if r["available"] else "➖"
        lines.append(f"{mark} <b>{escape(r['name'])}</b> · {escape(r['model'])} · {escape(r['source'])}")
    has_any = any(r["available"] for r in rows)
    footer = ("" if has_any else
             "\n\nНи один провайдер не настроен. Добавь свой ключ через "
             "⚙️ Настройки → ➕ Добавить ключ (id: openai, openrouter, groq, "
             "deepseek, grok, claude, gemini) — или впиши ключ в .env владельцу бота.")
    return Result("<b>ИИ-провайдеры</b>\n" + "\n".join(lines) + footer)


async def _note_add(c: "Container", uid: int, arg: str) -> Result:
    nid = await c.notes.add(uid, arg)
    return Result(f"📝 Заметка #{nid} сохранена")


async def _note_list(c: "Container", uid: int, _: str) -> Result:
    notes = await c.notes.list(uid)
    if not notes:
        return Result("Заметок пока нет.")
    return Result("<b>Твои заметки</b>\n" + "\n".join(
        f"#{n['id']} {escape(n['title'] or 'без названия')}" for n in notes))


async def _todo_add(c: "Container", uid: int, arg: str) -> Result:
    tid = await c.todos.add(uid, arg)
    return Result(f"✅ Задача #{tid} добавлена")


async def _todo_list(c: "Container", uid: int, _: str) -> Result:
    todos = await c.todos.list(uid)
    if not todos:
        return Result("Задач пока нет.")
    return Result("<b>Твои задачи</b>\n" + "\n".join(
        f"{'☑️' if t['done'] else '⬜'} #{t['id']} {escape(t['text'])}" for t in todos))


async def _todo_done(c: "Container", uid: int, arg: str) -> Result:
    if not arg.strip().isdigit():
        return Result("Отправь номер задачи (число).")
    ok = await c.todos.done(uid, int(arg.strip()))
    return Result("☑️ Выполнено." if ok else "Не найдено.")


def _split_id_and_text(arg: str) -> tuple[int | None, str]:
    """Parse the "<id> | <new text>" convention shared by all *_edit tools."""
    id_part, sep, rest = arg.partition("|")
    id_part = id_part.strip()
    if not sep or not id_part.isdigit():
        return None, ""
    return int(id_part), rest.strip()


async def _note_view(c: "Container", uid: int, arg: str) -> Result:
    if not arg.strip().isdigit():
        return Result("Отправь номер заметки (число).")
    note = await c.notes.get(uid, int(arg.strip()))
    if note is None:
        return Result("Заметка не найдена.")
    title = escape(note["title"] or "без названия")
    body = escape(note["body"] or "")
    return Result(f"<b>#{note['id']} {title}</b>\n\n{body}" if body else f"<b>#{note['id']} {title}</b>")


async def _note_edit(c: "Container", uid: int, arg: str) -> Result:
    note_id, text = _split_id_and_text(arg)
    if note_id is None or not text:
        return Result("Формат: <code>id | новый текст (первая строка — заголовок)</code>")
    ok = await c.notes.edit(uid, note_id, text)
    return Result("✏️ Заметка обновлена." if ok else "Заметка не найдена.")


async def _note_delete(c: "Container", uid: int, arg: str) -> Result:
    if not arg.strip().isdigit():
        return Result("Отправь номер заметки (число).")
    ok = await c.notes.delete(uid, int(arg.strip()))
    return Result("🗑 Удалена." if ok else "Не найдена.")


async def _note_search(c: "Container", uid: int, arg: str) -> Result:
    if not arg.strip():
        return Result("Отправь слово или фразу для поиска.")
    notes = await c.notes.search(uid, arg.strip())
    if not notes:
        return Result("Ничего не найдено.")
    return Result(f"<b>Найдено ({len(notes)})</b>\n" + "\n".join(
        f"#{n['id']} {escape(n['title'] or 'без названия')}" for n in notes))


async def _todo_undo(c: "Container", uid: int, arg: str) -> Result:
    if not arg.strip().isdigit():
        return Result("Отправь номер задачи (число).")
    ok = await c.todos.undo(uid, int(arg.strip()))
    return Result("⬜ Возвращена в невыполненные." if ok else "Не найдена.")


async def _todo_edit(c: "Container", uid: int, arg: str) -> Result:
    todo_id, text = _split_id_and_text(arg)
    if todo_id is None or not text:
        return Result("Формат: <code>id | новый текст задачи</code>")
    ok = await c.todos.edit(uid, todo_id, text)
    return Result("✏️ Задача обновлена." if ok else "Задача не найдена.")


async def _todo_delete(c: "Container", uid: int, arg: str) -> Result:
    if not arg.strip().isdigit():
        return Result("Отправь номер задачи (число).")
    ok = await c.todos.delete(uid, int(arg.strip()))
    return Result("🗑 Удалена." if ok else "Не найдена.")


async def _todo_pending(c: "Container", uid: int, _: str) -> Result:
    todos = await c.todos.list(uid, include_done=False)
    if not todos:
        return Result("Невыполненных задач нет 🎉")
    return Result("<b>Невыполненные задачи</b>\n" + "\n".join(
        f"⬜ #{t['id']} {escape(t['text'])}" for t in todos))


async def _todo_clear_done(c: "Container", uid: int, _: str) -> Result:
    n = await c.todos.clear_done(uid)
    return Result(f"🧹 Удалено выполненных задач: {n}" if n else "Выполненных задач нет.")


async def _productivity_stats(c: "Container", uid: int, _: str) -> Result:
    notes_n = await c.notes.count(uid)
    pending, done = await c.todos.counts(uid)
    return Result(
        f"<b>📊 Статистика</b>\n"
        f"Заметок: {notes_n}\n"
        f"Задач невыполнено: {pending}\n"
        f"Задач выполнено: {done}"
    )


async def _profile(c: "Container", uid: int, _: str) -> Result:
    p = await c.users.profile(uid)
    if not p:
        return Result("Профиля пока нет.")
    return Result(human("Твой профиль", {
        "id": p["id"], "username": p["username"], "role": p["role"],
        "notes": p["notes"], "todos": p["todos"],
        "ключи ИИ": ", ".join(p["providers"]) or "—", "since": p["created_at"],
    }))


async def _keys_list(c: "Container", uid: int, _: str) -> Result:
    provs = await c.api_keys.list_providers(uid)
    return Result("🔑 Сохранённые ключи: " + (", ".join(provs) or "нет"))


async def _set_provider(c: "Container", uid: int, arg: str) -> Result:
    await c.settings_svc.set(uid, "ai_provider", arg.strip().lower())
    return Result(f"✅ Провайдер ИИ по умолчанию: {escape(arg.strip().lower())}")


async def _set_model(c: "Container", uid: int, arg: str) -> Result:
    if not arg.strip():
        return Result("Отправь название модели.")
    await c.settings_svc.set(uid, "ai_model", arg.strip())
    return Result(f"✅ Модель ИИ по умолчанию: {escape(arg.strip())}")


async def _del_key(c: "Container", uid: int, arg: str) -> Result:
    provider = arg.strip().lower()
    if not provider:
        return Result("Отправь id ключа (см. «🔑 Ключи»).")
    await c.api_keys.delete(uid, provider)
    return Result(f"🗑 Ключ «{escape(provider)}» удалён (если был).")


async def _my_settings(c: "Container", uid: int, _: str) -> Result:
    data = await c.settings_svc.all(uid)
    return Result(human("⚙️ Твои настройки", data))


async def _reset_settings(c: "Container", uid: int, _: str) -> Result:
    await c.settings_svc.reset(uid)
    return Result("🔄 Настройки сброшены на умолчания.")


async def _providers_help(c: "Container", uid: int, _: str) -> Result:
    from .services.ai import _AI_PROVIDER_IDS
    from .services.osint import OSINT_KEY_IDS
    return Result(
        "<b>Доступные id для «➕ Добавить ключ»</b>\n\n"
        f"<b>ИИ:</b> {', '.join(sorted(_AI_PROVIDER_IDS))}\n"
        f"<b>OSINT:</b> {', '.join(sorted(OSINT_KEY_IDS))}\n\n"
        "Свой ключ имеет приоритет над ключом в .env владельца бота."
    )


async def _wipe_me(c: "Container", uid: int, arg: str) -> Result:
    if arg.strip().upper() != "УДАЛИТЬ":
        return Result(
            "⚠️ Это удалит ВСЕ твои заметки, задачи, сохранённые ключи и настройки "
            "безвозвратно. Роль и доступ к боту не затронуты.\n\n"
            "Чтобы подтвердить, отправь заглавными: <code>УДАЛИТЬ</code>"
        )
    notes_n = await c.notes.delete_all(uid)
    todos_n = await c.todos.delete_all(uid)
    await c.api_keys.delete_all(uid)
    await c.settings_svc.reset(uid)
    await c.repos.audit.log(uid, "user.wipe_self", f"notes={notes_n} todos={todos_n}")
    return Result(f"🧹 Готово. Удалено: заметок — {notes_n}, задач — {todos_n}, все ключи и настройки.")


async def load_last_report(c: "Container", uid: int) -> dict | None:
    raw = await c.repos.cache.get(f"report:{uid}")
    return json.loads(raw) if raw else None


async def save_last_report(c: "Container", uid: int, report: dict) -> None:
    await c.repos.cache.set(f"report:{uid}", json.dumps(report), ttl_seconds=86400)


async def build_export(c: "Container", uid: int, fmt: str) -> Result:
    """Render the user's last tool result (or their notes/todos) into a file."""
    report = await load_last_report(c, uid)
    if report is None:
        notes = await c.notes.list(uid)
        todos = await c.todos.list(uid)
        report = c.report.build("Рабочее пространство DeathBot", {
            "Заметки": "\n".join(f"- {n['title']}: {n['body']}" for n in notes) or "нет",
            "Задачи": "\n".join(f"[{'x' if t['done'] else ' '}] {t['text']}" for t in todos) or "нет",
        })
        report["tags"] = ["deathbot", "workspace"]
    blob = c.export.render(report, fmt)
    ext = c.export.extension(fmt)
    safe = _slug(report["title"])
    return Result(f"📤 <b>{escape(report['title'])}</b> → {fmt.upper()}",
                  filename=f"{safe}.{ext}", file_bytes=blob)


def _export(fmt: str):
    async def _run(c: "Container", uid: int, _: str) -> Result:
        return await build_export(c, uid, fmt)
    return _run


async def _users(c: "Container", uid: int, _: str) -> Result:
    users = await c.users.list_users(30)
    return Result("<b>Пользователи</b>\n" + "\n".join(
        f"<code>{u['id']}</code> @{u['username'] or '—'} — {u['role']}"
        + (" 🚫" if u["is_banned"] else "") for u in users))


async def _grant(c: "Container", uid: int, arg: str) -> Result:
    parts = arg.split()
    from .core.roles import ROLE_ORDER
    if len(parts) != 2 or not parts[0].isdigit() or parts[1] not in ROLE_ORDER:
        return Result("Формат: <code>&lt;id пользователя&gt; &lt;роль&gt;</code>\n"
                      f"Роли: {', '.join(ROLE_ORDER)}")
    await c.access.grant(uid, int(parts[0]), parts[1])
    return Result(f"✅ {parts[0]} → {parts[1]}")


async def _ban(c: "Container", uid: int, arg: str) -> Result:
    if not arg.strip().isdigit():
        return Result("Отправь ID пользователя (число).")
    await c.access.ban(uid, int(arg.strip()), True)
    return Result("🚫 Забанен.")


async def _unban(c: "Container", uid: int, arg: str) -> Result:
    if not arg.strip().isdigit():
        return Result("Отправь ID пользователя (число).")
    await c.access.ban(uid, int(arg.strip()), False)
    return Result("✅ Разбанен.")


async def _audit(c: "Container", uid: int, _: str) -> Result:
    rows = await c.repos.audit.recent(25)
    if not rows:
        return Result("Записей в журнале нет.")
    return Result("<b>Последние действия</b>\n" + "\n".join(
        f"{r['created_at']} · {r['user_id']} · {r['action']} {r['detail'] or ''}" for r in rows))


async def _backup(c: "Container", uid: int, _: str) -> Result:
    if not c.access.is_owner(uid):
        return Result("⛔ Бэкап БД доступен только владельцу.")
    data = await c.db.snapshot()
    await c.repos.audit.log(uid, "db.backup", f"{len(data)} bytes")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return Result(f"💾 Бэкап базы ({len(data) // 1024} КБ). Содержит зашифрованные ключи — храни надёжно.",
                  filename=f"deathbot-backup-{stamp}.sqlite3", file_bytes=data)


async def _plugin_install(c: "Container", uid: int, arg: str) -> Result:
    if not c.access.is_owner(uid):
        return Result("⛔ Установка инструментов доступна только владельцу.")
    data = await c.plugins.install(uid, arg)
    return Result(human("Установка инструмента", data))


async def _plugin_list(c: "Container", uid: int, _: str) -> Result:
    data = await c.plugins.list_installed()
    return Result(human("🧩 Свои инструменты", data))


async def _plugin_remove(c: "Container", uid: int, arg: str) -> Result:
    if not c.access.is_owner(uid):
        return Result("⛔ Удаление инструментов доступно только владельцу.")
    data = await c.plugins.remove(arg.strip().lower())
    return Result(human("Удаление инструмента", data))


# --------------------------------------------------------------------------- #
# the registry
# --------------------------------------------------------------------------- #
def _t(**kw) -> Tool:
    return Tool(**kw)

TOOLS: dict[str, Tool] = {t.id: t for t in [
    # ---- Комбайны (несколько инструментов → один отчёт) ----
    _t(id="wf_domain", label="🌐 Отчёт по домену", category="workflows", module="osint",
       prompt="Отправь домен", run=_wf_domain, background=True, validate="domain",
       desc="WHOIS + DNS + поддомены + DMARC + технологии → один отчёт"),
    _t(id="wf_username", label="👤 Профиль по нику", category="workflows", module="osint",
       prompt="Отправь юзернейм", run=_wf_username, background=True, validate="username",
       desc="Поиск по сайтам + Maigret → один отчёт по нику"),
    _t(id="wf_ip", label="📍 Досье по IP", category="workflows", module="osint",
       prompt="Отправь IP-адрес", run=_wf_ip, background=True, validate="ip",
       desc="Геолокация + репутация + Shodan → досье по IP"),
    _t(id="wf_person", label="🕵️ Досье по личности", category="workflows", module="osint",
       prompt="Отправь юзернейм", run=_wf_person, background=True, validate="username",
       desc="Ник → соцсети → email → утечки/телефон → ФИО-ссылки → единый отчёт"),

    # ---- OSINT ----
    _t(id="whois", label="WHOIS", category="osint", module="osint",
       prompt="Отправь домен (например example.com)", run=_osint("whois", "WHOIS")),
    _t(id="dns", label="DNS", category="osint", module="osint",
       prompt="Отправь хост или домен", run=_osint("dns", "DNS")),
    _t(id="subdomains", label="Поддомены", category="osint", module="osint",
       prompt="Отправь домен — поищу поддомены (crt.sh)", run=_osint("subdomains", "Поддомены")),
    _t(id="username", label="Юзернейм", category="osint", module="osint",
       prompt="Отправь никнейм — поищу профили на сайтах", run=_osint("username", "Юзернейм")),
    _t(id="email", label="Почта", category="osint", module="osint",
       prompt="Отправь email-адрес", run=_osint("email", "Почта")),
    _t(id="phone", label="Телефон", category="osint", module="osint",
       prompt="Отправь номер телефона (+код страны…)", run=_osint("phone", "Телефон")),
    _t(id="geoip", label="GeoIP", category="osint", module="geoint",
       prompt="Отправь IP или хост", run=_osint("geoip", "GeoIP")),
    _t(id="shodan", label="Shodan", category="osint", module="osint",
       prompt="Отправь IP (нужен ключ Shodan)", run=_osint("shodan", "Shodan")),
    _t(id="threatintel", label="Threat Intel", category="osint", module="osint",
       prompt="Отправь IP, домен или ссылку", run=_osint("threat_intel", "Threat Intel")),
    _t(id="ioc", label="Индикатор", category="osint", module="osint",
       prompt="Отправь индикатор (IP, хеш, CVE, домен…)", run=_osint("ioc", "Индикатор")),
    _t(id="revimg", label="Поиск по фото", category="osint", module="image",
       prompt="Отправь ссылку на изображение", run=_osint("reverse_image", "Поиск по фото")),
    _t(id="exif", label="Метаданные", category="osint", module="image",
       kind="photo", prompt="Отправь фото (файлом — тогда EXIF сохранится полностью)"),
    _t(id="darknet", label="Даркнет", category="osint", module="osint",
       prompt="Отправь запрос", run=_osint("darknet", "Даркнет")),
    _t(id="leak", label="Утечки", category="osint", module="osint",
       prompt="Отправь email, ник или телефон", run=_osint("leak", "Утечки"),
       desc="В каких утечках засветился email/ник/телефон (LeakCheck)"),
    _t(id="fio", label="Поиск по ФИО", category="osint", module="osint",
       prompt="Отправь имя (ФИО)", run=_osint("name", "Поиск по ФИО"),
       desc="Готовые ссылки для поиска человека по имени (Google/VK/…)"),
    _t(id="hunter_domain", label="Hunter.io (домен)", category="osint", module="osint",
       prompt="Отправь домен компании", run=_osint("hunter_domain", "Hunter.io"),
       desc="Email-адреса и паттерн почты организации по домену"),
    _t(id="hunter_verify", label="Hunter.io (проверка)", category="osint", module="osint",
       prompt="Отправь email для проверки", run=_osint("hunter_verify", "Hunter.io verify"),
       desc="Проверка существования/доставляемости email"),
    _t(id="emailrep", label="EmailRep", category="osint", module="osint",
       prompt="Отправь email", run=_osint("emailrep", "EmailRep"),
       desc="Репутация email: подозрительность, утечки, спам-метки"),
    _t(id="secretscan", label="Поиск утёкших ключей", category="osint", module="osint",
       prompt="Вставь текст или код — найду похожее на настоящие API-ключи/токены",
       run=_osint("secretscan", "Поиск утёкших ключей"),
       desc="Офлайн-регекс сканер: AWS/GitHub/Stripe/OpenAI/Slack и другие форматы ключей — без обращения к внешним сервисам"),

    # ---- OSINT: реальные CLI-инструменты с GitHub ----
    _t(id="theharvester", label="theHarvester", category="osint", module="osint",
       prompt="Отправь домен", run=_osint_cli("theharvester", "theHarvester"),
       desc="Сбор email, поддоменов и хостов из открытых источников"),
    _t(id="sherlock_cli", label="Sherlock", category="osint", module="osint",
       prompt="Отправь юзернейм", run=_osint_cli("sherlock_cli", "Sherlock"),
       desc="Поиск юзернейма по сотням соцсетей и сайтов"),
    _t(id="holehe", label="Holehe", category="osint", module="osint",
       prompt="Отправь email", run=_osint_cli("holehe", "Holehe"),
       desc="Где зарегистрирован email (по восстановлению пароля)"),
    _t(id="maigret", label="Maigret", category="osint", module="osint",
       prompt="Отправь юзернейм", run=_osint_cli("maigret", "Maigret"),
       desc="Юзернейм на 2500+ сайтах + данные из профилей"),
    _t(id="socialscan", label="socialscan", category="osint", module="osint",
       prompt="Отправь email или юзернейм", run=_osint_cli("socialscan", "socialscan"),
       desc="Занятость email/username на популярных платформах"),
    _t(id="h8mail", label="h8mail", category="osint", module="osint",
       prompt="Отправь email", run=_osint_cli("h8mail", "h8mail"),
       desc="Поиск email в публичных утечках и дампах"),
    _t(id="dnstwist", label="dnstwist", category="osint", module="osint",
       prompt="Отправь домен", run=_osint_cli("dnstwist", "dnstwist"),
       desc="Домены-двойники: тайпсквоттинг и фишинг"),
    _t(id="dnsrecon", label="dnsrecon", category="osint", module="osint",
       prompt="Отправь домен", run=_osint_cli("dnsrecon", "dnsrecon"),
       desc="Перечисление DNS-записей, зон и поддоменов"),
    _t(id="sublist3r", label="Sublist3r", category="osint", module="osint",
       prompt="Отправь домен", run=_osint_cli("sublist3r", "Sublist3r"),
       desc="Поиск поддоменов через поисковые системы"),
    _t(id="checkdmarc", label="checkdmarc", category="osint", module="osint",
       prompt="Отправь домен", run=_osint_cli("checkdmarc", "checkdmarc"),
       desc="Почтовая защита домена: SPF / DKIM / DMARC"),
    _t(id="wafw00f", label="wafw00f", category="osint", module="web",
       prompt="Отправь ссылку/домен", run=_osint_cli("wafw00f", "wafw00f"),
       desc="Определение WAF / файрвола перед сайтом"),
    _t(id="metafinder", label="MetaFinder", category="osint", module="osint",
       prompt="Отправь домен", run=_osint_cli("metafinder", "MetaFinder"),
       desc="Метаданные (авторы, софт) из публичных документов домена"),
    _t(id="whatweb", label="WhatWeb", category="osint", module="web",
       prompt="Отправь ссылку/домен", run=_osint_cli("whatweb", "WhatWeb"),
       desc="Фингерпринт технологий, CMS и заголовков сайта"),
    _t(id="gau", label="gau", category="osint", module="osint",
       prompt="Отправь домен", run=_osint_cli("gau", "gau"),
       desc="Все известные URL домена (Wayback, OTX, CommonCrawl)"),
    _t(id="phoneinfoga", label="PhoneInfoga", category="osint", module="osint",
       prompt="Отправь номер телефона (+код…)", run=_osint_cli("phoneinfoga", "PhoneInfoga"),
       desc="OSINT по номеру телефона: оператор, тип, следы в сети"),

    # ---- Pentest ----
    _t(id="portscan", label="Скан портов", category="pentest", module="recon",
       prompt="Отправь хост (только с разрешения владельца)",
       run=_pentest_native("scan_ports", "Скан портов")),
    _t(id="sslscan", label="SSL-скан", category="pentest", module="recon",
       prompt="Отправь хост", run=_pentest_native("ssl_scan", "SSL-скан")),
    _t(id="techdetect", label="Технологии", category="pentest", module="web",
       prompt="Отправь ссылку", run=_pentest_native("tech_detect", "Технологии")),
    _t(id="subfinder", label="subfinder", category="pentest", module="recon",
       prompt="Отправь домен", run=_external("subfinder", "subfinder")),
    _t(id="amass", label="amass", category="pentest", module="recon",
       prompt="Отправь домен", run=_external("amass", "amass")),
    _t(id="httpx", label="httpx", category="pentest", module="recon",
       prompt="Отправь ссылку или хост", run=_external("httpx", "httpx")),
    _t(id="naabu", label="naabu", category="pentest", module="recon",
       prompt="Отправь хост", run=_external("naabu", "naabu")),
    _t(id="nuclei", label="nuclei", category="pentest", module="recon",
       prompt="Отправь ссылку (только с разрешения владельца)", run=_external("nuclei", "nuclei")),
    _t(id="katana", label="katana", category="pentest", module="recon",
       prompt="Отправь ссылку", run=_external("katana", "katana")),
    _t(id="masscan", label="masscan", category="pentest", module="recon",
       prompt="Отправь хост или подсеть (только с разрешения)", run=_external("masscan", "masscan")),
    _t(id="rustscan", label="rustscan", category="pentest", module="recon",
       prompt="Отправь хост", run=_external("rustscan", "rustscan")),
    _t(id="gobuster", label="gobuster", category="pentest", module="recon",
       prompt="Отправь домен", run=_external("gobuster", "gobuster")),
    _t(id="ffuf", label="ffuf", category="pentest", module="web",
       prompt="Отправь ссылку со словом FUZZ", run=_external("ffuf", "ffuf")),
    _t(id="ferox", label="feroxbuster", category="pentest", module="web",
       prompt="Отправь ссылку", run=_external("feroxbuster", "feroxbuster")),

    # ---- AI ----
    _t(id="ai_ask", label="Спросить ИИ", category="ai", module="ai",
       prompt="Задай вопрос", run=_ai_ask),
    _t(id="ai_chat", label="Режим диалога", category="ai", module="ai", kind="chat"),
    _t(id="ai_providers", label="Провайдеры", category="ai", module="ai",
       kind="instant", run=_ai_providers),
    _t(id="ai_reset", label="Очистить историю", category="ai", module="ai",
       kind="instant", run=_ai_reset),
    _t(id="ai_translate_en", label="🇬🇧 Перевод → английский", category="ai", module="ai",
       prompt="Отправь текст для перевода",
       run=_ai_mode("Переведи следующий текст на английский, сохрани смысл, тон и форматирование. "
                    "Выведи только перевод, без пояснений.", "Перевод → английский")),
    _t(id="ai_translate_ru", label="🇷🇺 Перевод → русский", category="ai", module="ai",
       prompt="Отправь текст для перевода",
       run=_ai_mode("Переведи следующий текст на русский, сохрани смысл и тон. "
                    "Выведи только перевод, без пояснений.", "Перевод → русский")),
    _t(id="ai_summarize", label="📋 Краткое содержание", category="ai", module="ai",
       prompt="Отправь текст для сжатия",
       run=_ai_mode("Сделай краткое содержание текста ниже: 3-6 пунктов, только суть.",
                    "Краткое содержание")),
    _t(id="ai_shorten", label="✂️ Сократить текст", category="ai", module="ai",
       prompt="Отправь текст, который нужно сократить",
       run=_ai_mode("Сократи текст до 2-3 предложений, сохрани главную мысль.",
                    "Сокращение текста")),
    _t(id="ai_rewrite", label="✍️ Переписать яснее", category="ai", module="ai",
       prompt="Отправь текст для рерайта",
       run=_ai_mode("Перепиши текст яснее и грамотнее, сохрани смысл и тон автора.",
                    "Рерайт текста")),
    _t(id="ai_explain_code", label="💡 Объяснить код", category="ai", module="ai",
       prompt="Вставь код",
       run=_ai_mode("Объясни, что делает этот код, простыми словами, по шагам.",
                    "Объяснение кода")),
    _t(id="ai_review_code", label="🔍 Ревью кода", category="ai", module="ai",
       prompt="Вставь код на ревью",
       run=_ai_mode("Проведи код-ревью: найди баги, проблемы безопасности, узкие места "
                    "и стиль. Дай конкретные, применимые замечания.", "Ревью кода")),
    _t(id="ai_explain_error", label="🐛 Объяснить ошибку", category="ai", module="ai",
       prompt="Вставь текст ошибки/трейсбек",
       run=_ai_mode("Объясни эту ошибку/трейсбек простыми словами и предложи, как это исправить.",
                    "Объяснение ошибки")),
    _t(id="ai_regex", label="🧵 Составить регулярку", category="ai", module="ai",
       prompt="Опиши, что должно совпадать (и что не должно)",
       run=_ai_mode("Составь регулярное выражение под описанную задачу. Дай сам паттерн "
                    "и короткое объяснение по частям.", "Регулярное выражение")),
    _t(id="ai_sql", label="🗄 Составить SQL", category="ai", module="ai",
       prompt="Опиши задачу (и диалект SQL, если важен)",
       run=_ai_mode("Составь SQL-запрос под описанную задачу. Если диалект не указан — "
                    "используй стандартный SQL и отметь это.", "SQL-запрос")),
    _t(id="ai_commit_msg", label="📦 Сообщение коммита", category="ai", module="ai",
       prompt="Опиши, что изменилось",
       run=_ai_mode("Составь короткое информативное сообщение коммита в стиле "
                    "Conventional Commits по описанию изменений.", "Сообщение коммита")),

    # ---- Agents ----
    _t(id="ag_general", label="Универсальный", category="agents", module="ai",
       prompt="Опиши задачу", run=_agent("general", "Универсальный ассистент")),
    _t(id="ag_osint", label="OSINT", category="agents", module="ai",
       prompt="Опиши цель", run=_agent("osint", "OSINT-агент")),
    _t(id="ag_recon", label="Разведка", category="agents", module="ai",
       prompt="Опиши цель", run=_agent("recon", "Агент разведки")),
    _t(id="ag_report", label="Отчёт", category="agents", module="ai",
       prompt="Вставь находки — соберу отчёт", run=_agent("report", "Агент отчётов")),
    _t(id="ag_threat", label="Threat Intel", category="agents", module="ai",
       prompt="Отправь индикаторы", run=_agent("threatintel", "Агент Threat Intel")),
    _t(id="ag_code", label="Код", category="agents", module="ai",
       prompt="Опиши задачу по коду", run=_agent("code", "Агент по коду")),
    _t(id="ag_research", label="Ресёрч", category="agents", module="ai",
       prompt="Задай исследовательский вопрос", run=_agent("research", "Агент-исследователь")),
    _t(id="ag_planner", label="Планировщик", category="agents", module="ai",
       prompt="Опиши цель — составлю план", run=_agent("planner", "Агент-планировщик")),
    _t(id="ag_incident", label="Инцидент-респонс", category="agents", module="ai",
       prompt="Опиши инцидент", run=_agent("incident", "Агент реагирования на инциденты")),
    _t(id="ag_devops", label="DevOps", category="agents", module="ai",
       prompt="Опиши задачу по инфраструктуре/CI-CD", run=_agent("devops", "DevOps-агент")),
    _t(id="ag_legal", label="Юрист (общее)", category="agents", module="ai",
       prompt="Опиши ситуацию", run=_agent("legal", "Юридический аналитик")),
    _t(id="ag_finance", label="Финансы", category="agents", module="ai",
       prompt="Опиши задачу / вставь цифры", run=_agent("finance", "Финансовый аналитик")),
    _t(id="ag_seo", label="SEO/Контент", category="agents", module="ai",
       prompt="Вставь текст или опиши задачу", run=_agent("seo", "SEO/контент-агент")),
    _t(id="ag_career", label="Карьера", category="agents", module="ai",
       prompt="Опиши ситуацию (резюме, собес, выбор)", run=_agent("career", "Карьерный коуч")),
    _t(id="ag_translator", label="Переводчик", category="agents", module="ai",
       prompt="Отправь текст для перевода", run=_agent("translator", "Агент-переводчик")),
    _t(id="ag_critique", label="Критик", category="agents", module="ai",
       prompt="Пришли план/идею/аргумент", run=_agent("critique", "Агент-критик")),

    # ---- Productivity ----
    _t(id="note_add", label="➕ Заметка", category="productivity", module="notes",
       prompt="Отправь текст заметки (первая строка — заголовок)", run=_note_add),
    _t(id="note_list", label="📋 Заметки", category="productivity", module="notes",
       kind="instant", run=_note_list),
    _t(id="todo_add", label="➕ Задача", category="productivity", module="todo",
       prompt="Отправь текст задачи", run=_todo_add),
    _t(id="todo_list", label="📋 Задачи", category="productivity", module="todo",
       kind="instant", run=_todo_list),
    _t(id="todo_done", label="☑️ Выполнить", category="productivity", module="todo",
       prompt="Отправь номер задачи", run=_todo_done),
    _t(id="note_view", label="🔎 Открыть заметку", category="productivity", module="notes",
       prompt="Отправь номер заметки", run=_note_view),
    _t(id="note_edit", label="✏️ Изменить заметку", category="productivity", module="notes",
       prompt="Формат: id | новый текст (первая строка — заголовок)", run=_note_edit),
    _t(id="note_delete", label="🗑 Удалить заметку", category="productivity", module="notes",
       prompt="Отправь номер заметки", run=_note_delete),
    _t(id="note_search", label="🔍 Поиск заметок", category="productivity", module="notes",
       prompt="Отправь слово или фразу", run=_note_search),
    _t(id="todo_undo", label="⬜ Вернуть задачу", category="productivity", module="todo",
       prompt="Отправь номер задачи", run=_todo_undo),
    _t(id="todo_edit", label="✏️ Изменить задачу", category="productivity", module="todo",
       prompt="Формат: id | новый текст задачи", run=_todo_edit),
    _t(id="todo_delete", label="🗑 Удалить задачу", category="productivity", module="todo",
       prompt="Отправь номер задачи", run=_todo_delete),
    _t(id="todo_pending", label="⏳ Только невыполненные", category="productivity", module="todo",
       kind="instant", run=_todo_pending),
    _t(id="todo_clear_done", label="🧹 Очистить выполненные", category="productivity", module="todo",
       kind="instant", run=_todo_clear_done),
    _t(id="productivity_stats", label="📊 Статистика", category="productivity", module="notes",
       kind="instant", run=_productivity_stats),

    # ---- Export ----
    _t(id="exp_pdf", label="PDF", category="export", module="reports", kind="instant", run=_export("pdf")),
    _t(id="exp_docx", label="DOCX", category="export", module="reports", kind="instant", run=_export("docx")),
    _t(id="exp_html", label="HTML", category="export", module="reports", kind="instant", run=_export("html")),
    _t(id="exp_md", label="Markdown", category="export", module="reports", kind="instant", run=_export("markdown")),
    _t(id="exp_csv", label="CSV", category="export", module="reports", kind="instant", run=_export("csv")),
    _t(id="exp_json", label="JSON", category="export", module="reports", kind="instant", run=_export("json")),

    # ---- Settings ----
    _t(id="profile", label="👤 Профиль", category="settings", module="profile",
       kind="instant", run=_profile),
    _t(id="keys", label="🔑 Ключи", category="settings", module="profile",
       kind="instant", run=_keys_list),
    _t(id="addkey", label="➕ Добавить ключ", category="settings", module="profile", kind="apikey"),
    _t(id="setprov", label="Сменить ИИ", category="settings", module="profile",
       prompt="Отправь название провайдера (openrouter, openai, claude, gemini…)",
       run=_set_provider),
    _t(id="setmodel", label="Модель ИИ по умолчанию", category="settings", module="profile",
       prompt="Отправь название модели (например gpt-4o-mini)", run=_set_model),
    _t(id="delkey", label="🗑 Удалить ключ", category="settings", module="profile",
       prompt="Отправь id ключа для удаления (см. «🔑 Ключи»)", run=_del_key),
    _t(id="my_settings", label="📋 Мои настройки", category="settings", module="profile",
       kind="instant", run=_my_settings),
    _t(id="reset_settings", label="🔄 Сбросить настройки", category="settings", module="profile",
       kind="instant", run=_reset_settings),
    _t(id="providers_help", label="❓ Какие id ключей бывают", category="settings", module="profile",
       kind="instant", run=_providers_help),
    _t(id="wipe_me", label="⚠️ Удалить все мои данные", category="settings", module="profile",
       prompt="Отправь <code>УДАЛИТЬ</code> заглавными, чтобы подтвердить", run=_wipe_me),

    # ---- Admin ----
    _t(id="users", label="Пользователи", category="admin", module="admin",
       kind="instant", run=_users),
    _t(id="grant", label="Выдать роль", category="admin", module="admin",
       prompt="Отправь: &lt;id пользователя&gt; &lt;роль&gt;", run=_grant),
    _t(id="ban", label="Забанить", category="admin", module="admin",
       prompt="Отправь ID пользователя для бана", run=_ban),
    _t(id="unban", label="Разбанить", category="admin", module="admin",
       prompt="Отправь ID пользователя для разбана", run=_unban),
    _t(id="audit", label="Журнал", category="admin", module="audit",
       kind="instant", run=_audit),
    _t(id="backup", label="💾 Бэкап БД", category="admin", module="admin",
       kind="instant", run=_backup, desc="Скачать снимок базы (только владелец)"),
    _t(id="plugin_install", label="➕ Установить инструмент", category="admin", module="admin",
       background=True, run=_plugin_install,
       prompt="Отправь: <code>id | pip-или-git-спецификатор | Название | Описание</code>\n"
              "Пример: <code>trufflehog | truffleHog3 | TruffleHog | поиск секретов в репо</code>\n"
              "Спецификатор — имя пакета PyPI или <code>git+https://github.com/автор/репо.git</code>.",
       desc="Поставить свой CLI-инструмент из PyPI/GitHub через pipx (только владелец, выполняет чужой код!)"),
    _t(id="plugin_list", label="🧩 Мои инструменты", category="admin", module="admin",
       kind="instant", run=_plugin_list, desc="Список установленных вручную инструментов"),
    _t(id="plugin_remove", label="🗑 Удалить инструмент", category="admin", module="admin",
       prompt="Отправь id установленного инструмента (см. «🧩 Мои инструменты»)",
       run=_plugin_remove, desc="Снести установленный вручную инструмент"),
]}

# Descriptions for the built-in tools (the GitHub CLIs above set desc inline).
# Attached after construction to keep the tool table above readable.
DESCRIPTIONS: dict[str, str] = {
    # OSINT (native)
    "whois": "Данные о домене: регистратор, даты, серверы имён",
    "dns": "A/AAAA-записи хоста и обратная запись (PTR)",
    "subdomains": "Поддомены домена через Certificate Transparency (crt.sh)",
    "username": "Быстрая проверка юзернейма по популярным сайтам",
    "email": "Проверка email: формат, Gravatar, утечки (HIBP)",
    "phone": "Разбор номера телефона: страна, формат E.164",
    "geoip": "Геолокация IP: страна, город, провайдер, координаты",
    "shodan": "Данные Shodan по IP: порты, сервисы, уязвимости",
    "threatintel": "Репутация индикатора (URLhaus, AbuseIPDB)",
    "ioc": "Определение типа индикатора и что с ним проверить",
    "revimg": "Ссылки для поиска по изображению (Google/Yandex/…)",
    "exif": "Метаданные и GPS из отправленного фото",
    "darknet": "Заглушка: краулинг даркнета отключён (безопасность)",
    # Pentest
    "portscan": "Скан открытых портов (nmap или встроенный)",
    "sslscan": "Информация о TLS-сертификате и сроках",
    "techdetect": "Технологии сайта по заголовкам и телу ответа",
    "subfinder": "Пассивный сбор поддоменов (ProjectDiscovery)",
    "amass": "Комбайн для картирования поверхности атаки",
    "httpx": "HTTP-пробинг: статусы, заголовки, заголовки",
    "naabu": "Быстрый сканер портов (ProjectDiscovery)",
    "nuclei": "Сканер уязвимостей по шаблонам",
    "katana": "Веб-краулер для сбора ссылок",
    "masscan": "Массовый сканер портов",
    "rustscan": "Очень быстрый сканер портов",
    "gobuster": "Брутфорс поддоменов и директорий",
    "ffuf": "Веб-фаззер (директории, параметры)",
    "ferox": "Рекурсивный поиск контента на сайте",
    # AI
    "ai_ask": "Одиночный вопрос к ИИ",
    "ai_chat": "Диалог с ИИ с сохранением контекста",
    "ai_providers": "Список доступных ИИ-провайдеров",
    "ai_reset": "Очистить историю диалога с ИИ",
    "ai_translate_en": "Перевод текста на английский",
    "ai_translate_ru": "Перевод текста на русский",
    "ai_summarize": "Краткое содержание текста (3-6 пунктов)",
    "ai_shorten": "Сократить текст до сути (2-3 предложения)",
    "ai_rewrite": "Переписать текст яснее и грамотнее",
    "ai_explain_code": "Объяснение кода простыми словами",
    "ai_review_code": "Код-ревью: баги, безопасность, стиль",
    "ai_explain_error": "Разбор ошибки/трейсбека + как исправить",
    "ai_regex": "Составить регулярное выражение по описанию",
    "ai_sql": "Составить SQL-запрос по описанию",
    "ai_commit_msg": "Сообщение коммита по описанию изменений",
    # Agents
    "ag_general": "Универсальный помощник",
    "ag_osint": "Агент планирует OSINT по цели",
    "ag_recon": "Агент строит план разведки",
    "ag_report": "Агент собирает отчёт из находок",
    "ag_threat": "Агент оценивает угрозу по индикаторам",
    "ag_code": "Агент пишет и ревьюит код",
    "ag_research": "Агент-исследователь с рассуждением",
    "ag_planner": "Агент составляет пошаговый план",
    "ag_incident": "План сдерживания и восстановления по инциденту",
    "ag_devops": "Помощь с Docker/CI-CD/инфраструктурой",
    "ag_legal": "Разбор рисков по цифровому праву (не консультация)",
    "ag_finance": "Разбор метрик, бюджетов, юнит-экономики",
    "ag_seo": "SEO/контент-правки: структура, заголовки, ключевые слова",
    "ag_career": "Резюме, подготовка к собеседованиям, карьера",
    "ag_translator": "Профессиональный перевод с сохранением тона",
    "ag_critique": "Жёсткий разбор слабых мест плана/идеи",
    # Productivity / settings / admin
    "note_add": "Сохранить заметку", "note_list": "Показать заметки",
    "todo_add": "Добавить задачу", "todo_list": "Показать задачи",
    "todo_done": "Отметить задачу выполненной",
    "note_view": "Открыть заметку целиком",
    "note_edit": "Изменить текст заметки",
    "note_delete": "Удалить заметку",
    "note_search": "Поиск по заголовкам и тексту заметок",
    "todo_undo": "Вернуть выполненную задачу в невыполненные",
    "todo_edit": "Изменить текст задачи",
    "todo_delete": "Удалить задачу",
    "todo_pending": "Только невыполненные задачи",
    "todo_clear_done": "Удалить все выполненные задачи разом",
    "productivity_stats": "Счётчики заметок и задач",
    "profile": "Твой профиль и статистика",
    "keys": "Список сохранённых API-ключей",
    "addkey": "Добавить зашифрованный API-ключ",
    "setprov": "Выбрать ИИ-провайдера по умолчанию",
    "setmodel": "Задать модель ИИ по умолчанию",
    "delkey": "Удалить сохранённый API-ключ",
    "my_settings": "Показать все свои настройки",
    "reset_settings": "Сбросить настройки на умолчания",
    "providers_help": "Справка: какие id ключей понимает бот",
    "wipe_me": "Удалить все свои заметки/задачи/ключи/настройки",
    "users": "Список пользователей", "grant": "Выдать пользователю роль",
    "ban": "Забанить пользователя", "unban": "Снять бан",
    "audit": "Последние действия из журнала",
    "backup": "Скачать снимок базы (только владелец)",
    "plugin_install": "Установить свой CLI-инструмент из PyPI/GitHub",
    "plugin_list": "Список установленных вручную инструментов",
    "plugin_remove": "Удалить установленный вручную инструмент",
    # Export
    "exp_pdf": "Последний результат → PDF", "exp_docx": "Последний результат → DOCX",
    "exp_html": "Последний результат → HTML", "exp_md": "Последний результат → Markdown",
    "exp_csv": "Последний результат → CSV", "exp_json": "Последний результат → JSON",
}
for _tid, _d in DESCRIPTIONS.items():
    if _tid in TOOLS:
        TOOLS[_tid].desc = _d

# Slow tools (external CLIs + crt.sh + port scan) run through the task engine so
# the chat isn't blocked for minutes.
_BACKGROUND = {
    "theharvester", "sherlock_cli", "holehe", "maigret", "socialscan", "h8mail",
    "dnstwist", "dnsrecon", "sublist3r", "checkdmarc", "wafw00f", "metafinder",
    "whatweb", "gau", "phoneinfoga",
    "subfinder", "amass", "httpx", "naabu", "nuclei", "katana", "masscan",
    "rustscan", "gobuster", "ffuf", "ferox",
    "subdomains", "portscan",
}
for _tid in _BACKGROUND:
    if _tid in TOOLS:
        TOOLS[_tid].background = True

# Expected input type per tool → validated before the tool runs.
_VALIDATE = {
    "whois": "domain", "dns": "host", "subdomains": "domain", "dnstwist": "domain",
    "dnsrecon": "domain", "sublist3r": "domain", "checkdmarc": "domain",
    "theharvester": "domain", "gau": "domain", "geoip": "host", "shodan": "ip",
    "email": "email", "holehe": "email", "h8mail": "email",
    "username": "username", "sherlock_cli": "username", "maigret": "username",
    "socialscan": "username", "phone": "phone", "phoneinfoga": "phone",
    "revimg": "url", "techdetect": "host", "whatweb": "host", "wafw00f": "host",
    "sslscan": "host", "portscan": "host",
    "hunter_domain": "domain", "hunter_verify": "email", "emailrep": "email",
}
for _tid, _v in _VALIDATE.items():
    if _tid in TOOLS:
        TOOLS[_tid].validate = _v

# OSINT has grown to 30+ tools — grouped into a category tree (like the
# catalog sites do: "Email и телефоны" -> Hunter.io / EmailRep / HIBP / ...)
# instead of one long flat button wall. Categories with no entries here just
# keep the old flat list.
SUBCATEGORY_LABELS: dict[str, str] = {
    "domains": "🌐 Домены и сайты",
    "contacts": "📧 Email и телефоны",
    "social": "👤 Юзернеймы и соцсети",
    "ipgeo": "📍 IP и геолокация",
    "images": "🖼 Изображения",
    "secrets": "🔑 Секреты и ключи",
    "other": "🕸 Прочее",
}
_SUBCATEGORY = {
    "whois": "domains", "dns": "domains", "subdomains": "domains",
    "dnstwist": "domains", "dnsrecon": "domains", "sublist3r": "domains",
    "checkdmarc": "domains", "theharvester": "domains", "gau": "domains",
    "metafinder": "domains", "whatweb": "domains", "wafw00f": "domains",
    "email": "contacts", "phone": "contacts", "holehe": "contacts",
    "h8mail": "contacts", "phoneinfoga": "contacts", "hunter_domain": "contacts",
    "hunter_verify": "contacts", "emailrep": "contacts", "leak": "contacts",
    "username": "social", "sherlock_cli": "social", "maigret": "social",
    "socialscan": "social", "fio": "social",
    "geoip": "ipgeo", "shodan": "ipgeo", "threatintel": "ipgeo", "ioc": "ipgeo",
    "revimg": "images", "exif": "images",
    "secretscan": "secrets",
    "darknet": "other",
}
for _tid, _sc in _SUBCATEGORY.items():
    if _tid in TOOLS:
        TOOLS[_tid].subcategory = _sc


def tools_in(category: str) -> list[Tool]:
    return [t for t in TOOLS.values() if t.category == category]


def subcategories_in(category: str) -> list[tuple[str, str]]:
    """Ordered (id, label) pairs for the subcategories present in a category.

    Empty when the category isn't grouped — callers fall back to the flat
    tools_in() list in that case.
    """
    present = {t.subcategory for t in TOOLS.values() if t.category == category and t.subcategory}
    return [(sc, label) for sc, label in SUBCATEGORY_LABELS.items() if sc in present]


def tools_in_sub(category: str, subcategory: str) -> list[Tool]:
    return [t for t in TOOLS.values()
            if t.category == category and t.subcategory == subcategory]


def get_tool(tool_id: str) -> Tool | None:
    return TOOLS.get(tool_id)


# --------------------------------------------------------------------------- #
# runtime plugin registration — tools the owner installs from a pip/git spec
# after the process has already started (see services/plugins.py). Reloaded
# from the DB on every boot so they survive a restart.
# --------------------------------------------------------------------------- #
def register_custom_tool(tool_id: str, label: str, desc: str, binary_path: str) -> None:
    TOOLS[tool_id] = _t(
        id=tool_id, label=label, category="custom", module="admin",
        prompt=f"Отправь аргумент для «{label}» (домен/ник/IP — смотря что ждёт инструмент)",
        run=_custom_cli(binary_path, label), desc=desc, background=True,
    )


def unregister_custom_tool(tool_id: str) -> None:
    TOOLS.pop(tool_id, None)
