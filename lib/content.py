"""Loads student-editable page copy from content/<page>.md.

Each page's prose lives in content/<page>.md, split into named blocks by lines
that start with '@' (e.g. '@tagline'). The section files (sections/*.py) keep
layout, numbers, and logic; they reference blocks by name via load("<page>").

So: to change the WORDS, edit content/<page>.md. To change the layout or a
number, edit the section file. Blocks that show a live number contain a
{placeholder} the section fills in with .format(...) — leave the {braces} intact.

Not cached, so editing a .md and re-running the app (press 'R') shows the change.
"""
from __future__ import annotations

import re
from pathlib import Path

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"
_MARKER = re.compile(r"^@(\w+)\s*$")


def load(page: str) -> dict[str, str]:
    """Return {block_name: markdown_text} for content/<page>.md."""
    path = CONTENT_DIR / f"{page}.md"
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
