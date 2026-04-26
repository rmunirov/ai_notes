from __future__ import annotations

import asyncio
import os
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

os.environ["LLM_API_KEY"] = "test-key-123"
os.environ["LLM_BASE_URL"] = "https://api.openai.com/v1"

from ai_notes.infrastructure.db.models import EMBED_DIM

FIXED_EMB = [0.01] * EMBED_DIM


@pytest.mark.asyncio
async def test_agent_query_happy_path_with_mocks(
    client: AsyncClient,
) -> None:
    """Embeddings + generation mocked; grader returns all results as relevant."""
    c = await client.post(
        "/notes",
        json={"title": "Mars", "body_html": "<p>Mars is a red planet in our solar system.</p>"},
    )
    assert c.status_code == 201, c.text
    await asyncio.sleep(0.6)

    async def all_relevant(
        _chat: object, q: str, results: list
    ) -> tuple[list, list[bool]]:
        return results, [True] * len(results)

    class FakeMsg:
        content = "Согласно заметкам, Mars — красная планета."

    class FakeLLM:
        async def ainvoke(self, *a: object, **k: object) -> FakeMsg:
            return FakeMsg()

    with (
        patch(
            "ai_notes.infrastructure.embeddings.provider.LangChainEmbeddingProvider.embed_query",
            new=AsyncMock(side_effect=lambda _t: FIXED_EMB),
        ),
        patch("ai_notes.agent.nodes.grade_relevance_of_chunks", new=all_relevant),
        patch(
            "ai_notes.infrastructure.llm.factory.LLMProviderFactory.chat_model",
            return_value=FakeLLM(),
        ),
    ):
        r = await client.post(
            "/agent/query",
            json={"question": "What do we know about Mars?"},
        )
    assert r.status_code == 200, r.text
    d = r.json()
    assert "thread_id" in d
    assert d.get("is_grounded") is not None
