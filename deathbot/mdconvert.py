"""Best-effort Markdown -> Telegram HTML converter for raw LLM output.

Telegram's HTML parse mode understands a small fixed tag set (b, i, u, s,
code, pre, a, tg-spoiler) and has no concept of Markdown at all. Models
default to Markdown-style formatting (**bold**, ## headers, `code`, fenced
blocks, "| table |" rows), so without converting it that syntax shows up as
literal asterisks/hashes/pipes in the chat — exactly the symptom this fixes.

Designed to fail safe: any delimiter that never finds its closing partner is
left as plain (escaped) text instead of becoming a stray/unbalanced HTML tag
that would make Telegram reject the whole message.
"""
from __future__ import annotations

import re
from html import escape as _escape

_FENCE_RE = re.compile(r"```[ \t]*\w*\n(.*?)```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*|__(.+?)__")
_ITALIC_RE = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)|(?<!_)_([^_\n]+)_(?!_)")
_HEADER_RE = re.compile(r"^#{1,6}[ \t]+(.+?)[ \t]*#*$", re.MULTILINE)
_BULLET_RE = re.compile(r"^[ \t]*[-*+][ \t]+", re.MULTILINE)
_HR_RE = re.compile(r"^[ \t]*-{3,}[ \t]*$\n?", re.MULTILINE)
_TABLE_SEP_RE = re.compile(r"^:?-{2,}:?$")


def _table_row(line: str) -> str | None:
    """Turn a "| a | b |" row into "• a — b", or "" to drop a separator row."""
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|") and len(stripped) > 1):
        return None
    cells = [c.strip() for c in stripped[1:-1].split("|")]
    if all(_TABLE_SEP_RE.match(c) for c in cells if c) and any(cells):
        return ""
    non_empty = [c for c in cells if c]
    return "• " + " — ".join(non_empty) if non_empty else ""


def md_to_html(text: str) -> str:
    """Convert Markdown-ish text into Telegram-safe HTML. Never raises."""
    if not text or not text.strip():
        return text

    try:
        return _convert(text)
    except Exception:  # noqa: BLE001 — formatting must never break delivery
        return _escape(text)


def _convert(text: str) -> str:
    # 1) Fenced code blocks are pulled out first so nothing inside them is
    #    touched by the line/inline substitutions below.
    blocks: list[str] = []

    def _stash(m: re.Match) -> str:
        blocks.append(m.group(1).strip("\n"))
        return f"\x00{len(blocks) - 1}\x00"

    text = _FENCE_RE.sub(_stash, text)

    # 2) Line-level rewrites (headers -> bold, "- x" -> "• x", tables -> bullets).
    out_lines = []
    for line in text.split("\n"):
        row = _table_row(line)
        if row is not None:
            out_lines.append(row)
            continue
        out_lines.append(line)
    text = "\n".join(out_lines)

    text = _HR_RE.sub("", text)
    text = _HEADER_RE.sub(lambda m: f"**{m.group(1).strip()}**", text)
    text = _BULLET_RE.sub("• ", text)

    # 3) Escape what remains as plain text, *then* turn surviving markdown
    #    delimiters into real tags — order matters: our own generated tags
    #    must never pass back through html.escape().
    text = _escape(text)
    text = _INLINE_CODE_RE.sub(lambda m: f"<code>{m.group(1)}</code>", text)
    text = _BOLD_RE.sub(lambda m: f"<b>{m.group(1) or m.group(2)}</b>", text)
    text = _ITALIC_RE.sub(lambda m: f"<i>{m.group(1) or m.group(2)}</i>", text)

    # 4) Put fenced code blocks back as their own <pre> blocks.
    def _unstash(m: re.Match) -> str:
        return f"<pre>{_escape(blocks[int(m.group(1))])}</pre>"

    text = re.sub(r"\x00(\d+)\x00", _unstash, text)

    return text.strip()
