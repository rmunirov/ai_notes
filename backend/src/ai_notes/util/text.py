from __future__ import annotations

from bs4 import BeautifulSoup


def html_to_plain_text(html: str) -> str:
    if not html.strip():
        return ""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text("\n", strip=True)


def preview_text(text: str, max_len: int = 200) -> str:
    t = text.replace("\n", " ").strip()
    if len(t) <= max_len:
        return t
    return t[: max_len - 1] + "…"
