"""Loads student-editable page copy from content/<lang>/<page>.md.

Each page's prose lives in content/<lang>/<page>.md (lang = 'en' or 'zh'), split
into named blocks by lines that start with '@' (e.g. '@tagline'). Section files
reference blocks by name via load("<page>"); the loader picks the language from
st.session_state["lang"] (set by the sidebar picker) and falls back to English
for any block a translation hasn't filled in yet — so a half-translated page is
still fully readable.

To change the WORDS, edit content/<lang>/<page>.md. To change layout or a number,
edit the section file. Blocks that show a live number keep their {placeholder}.
"""
from __future__ import annotations

import re
from pathlib import Path

import streamlit as st

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"
_MARKER = re.compile(r"^@(\w+)\s*$")


def _current_lang() -> str:
    try:
        lang = st.session_state.get("lang", "en")
    except Exception:
        lang = "en"
    return lang if lang in ("en", "zh") else "en"


def _read(path: Path) -> dict[str, str]:
    """Parse one content/<lang>/<page>.md into {block_name: markdown_text}."""
    if not path.exists():
        return {}
    blocks: dict[str, list[str]] = {}
    current: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = _MARKER.match(line)
        if m:
            current = m.group(1)
            blocks[current] = []
        elif current is not None:
            blocks[current].append(line)
    return {k: "\n".join(v).strip() for k, v in blocks.items()}


def load(page: str) -> dict[str, str]:
    """Return {block_name: markdown_text} for the current language (English fallback)."""
    en = _read(CONTENT_DIR / "en" / f"{page}.md")
    if _current_lang() == "en":
        return en
    translated = _read(CONTENT_DIR / _current_lang() / f"{page}.md")
    return {**en, **translated}  # translated blocks override; missing ones fall back to English
