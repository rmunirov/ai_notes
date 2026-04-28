from __future__ import annotations

import asyncio
import os
from typing import Any

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

os.environ["LLM_API_KEY"] = "test-key-123"
os.environ["LLM_BASE_URL"] = "https://api.openai.com/v1"

from ai_notes.domain.agent import AgentAnswer  # noqa: E402
from ai_notes.infrastructure.db.models import EMBED_DIM  # noqa: E402

FIXED_EMB = [0.01] * EMBED_DIM


class _StubAgent:
    """Minimal stand-in for the compiled `create_agent` graph used in tests.

    Bypasses real tool-calling; returns a canned `structured_response` mirroring
    what a real LLM would produce after invoking `search_notes`.
    """

    def __init__(self, answer: AgentAnswer) -> None:
        self._answer = answer

    async def ainvoke(
        self,
        _payload: Any,
        *,
        config: Any = None,
        context: Any = None,
    ) -> dict[str, Any]:
        return {"messages": [], "structured_response": self._answer}


@pytest.mark.asyncio
async def test_agent_query_happy_path_with_mocks(
    app_and_client: tuple[FastAPI, AsyncClient],
) -> None:
    """End-to-end /agent/query with the LangChain v1 agent stubbed.

    The real `create_agent` graph is replaced with a stub returning a fixed
    structured AgentAnswer. We verify the API response shape, persistence of
    the dialog (thread_id), and AgentAnswer→AgentQueryResponse mapping.
    """
    app, client = app_and_client

    c = await client.post(
        "/notes",
        json={"title": "Mars", "body_html": "<p>Mars is a red planet in our solar system.</p>"},
    )
    assert c.status_code == 201, c.text
    await asyncio.sleep(0.6)

    canned = AgentAnswer(
        answer="Согласно заметкам, Mars — красная планета.",
        confidence="high",
        is_grounded=True,
        source_notes=[],
    )
    app.state.agent = _StubAgent(canned)

    r = await client.post(
        "/agent/query",
        json={"question": "What do we know about Mars?"},
    )
    assert r.status_code == 200, r.text
    d = r.json()
    assert "thread_id" in d
    assert d["is_grounded"] is True
    assert d["confidence"] == "high"
    assert d["answer"].startswith("Согласно")
