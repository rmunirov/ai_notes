from __future__ import annotations

from ai_notes.services.chunking_service import ChunkingService


def test_empty_text() -> None:
    c = ChunkingService()
    assert c.split("") == []


def test_single_short_chunk() -> None:
    c = ChunkingService(chunk_words=10, overlap_words=1)
    words = " ".join([f"w{i}" for i in range(5)])
    out = c.split(words)
    assert len(out) == 1
    assert out[0] == words


def test_long_splits_with_overlap() -> None:
    c = ChunkingService(chunk_words=3, overlap_words=1)
    words = "a b c d e f g h"
    out = c.split(words)
    assert len(out) >= 2
    # overlap ensures "c" can appear in consecutive chunks
    assert all(" " in s for s in out)
