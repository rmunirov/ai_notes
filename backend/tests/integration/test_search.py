from __future__ import annotations

import os
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from ai_notes.infrastructure.db.models import EMBED_DIM

os.environ["LLM_API_KEY"] = "test-key-123"
os.environ["LLM_BASE_URL"] = "https://api.openai.com/v1"


@pytest.mark.asyncio
async def test_search_returns_note_after_indexing(client: AsyncClient) -> None:
    fixed = [0.01] * EMBED_DIM

    async def fake_embed_query(_: str) -> list[float]:
        return fixed

    with patch(
        "ai_notes.infrastructure.embeddings.provider.LangChainEmbeddingProvider.embed_query",
        new=AsyncMock(side_effect=fake_embed_query),
    ):
        c = await client.post(
            "/notes",
            json={"title": "Planets", "body_html": "<p>Mars and Venus</p>"},
        )
        assert c.status_code == 201, c.text
        # background reindex may run — wait briefly for chunk in test env
        import asyncio

        for _ in range(20):
            s = await client.post("/search", json={"query": "Mars space", "limit": 5})
            if s.status_code == 200 and s.json().get("total", 0) > 0:
                break
            await asyncio.sleep(0.1)
        s = await client.post("/search", json={"query": "Mars space", "limit": 5})
        assert s.status_code == 200, s.text
        data = s.json()
        assert data["total"] >= 1
        assert any("Mars" in (x.get("chunk_text") or "") for x in data.get("results", []))
