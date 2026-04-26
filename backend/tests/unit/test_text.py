from __future__ import annotations

from ai_notes.util.text import html_to_plain_text, preview_text


def test_html_strips() -> None:
    assert html_to_plain_text("<h1>Hi</h1>") == "Hi"
    p = preview_text("x" * 300, max_len=200)
    assert len(p) <= 201
    assert p.endswith("…")
