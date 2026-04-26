from __future__ import annotations


class ChunkingService:
    """Split note body text into overlapping word-based chunks (per data model)."""

    def __init__(self, chunk_words: int = 500, overlap_words: int = 50) -> None:
        self.chunk_words = chunk_words
        self.overlap_words = overlap_words

    def split(self, body_text: str) -> list[str]:
        words = body_text.split()
        if not words:
            return []
        if len(words) <= self.chunk_words:
            return [" ".join(words)]
        chunks: list[str] = []
        i = 0
        step = self.chunk_words - self.overlap_words
        while i < len(words):
            part = words[i : i + self.chunk_words]
            chunks.append(" ".join(part))
            i += step
        return chunks
