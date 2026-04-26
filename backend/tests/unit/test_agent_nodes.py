from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest

from ai_notes.agent import nodes
from ai_notes.config import AppSettings, LLMSettings
from ai_notes.domain.search import SearchResultItem


@pytest.mark.asyncio
async def test_grade_relevance_keeps_relevant() -> None:
    mock = MagicMock()

    async def ainvoke(msgs: list) -> MagicMock:  # noqa: ANN001
        out = MagicMock()
        out.content = "yes"
        return out

    mock.ainvoke = ainvoke
    r1 = SearchResultItem(
        note_id=uuid.uuid4(), note_title="A", chunk_text="alpha", similarity_score=0.9
    )
    r2 = SearchResultItem(
        note_id=uuid.uuid4(), note_title="B", chunk_text="beta", similarity_score=0.8
    )
    rel, flags = await nodes.grade_relevance_of_chunks(mock, "Q?", [r1, r2])
    assert flags == [True, True]
    assert len(rel) == 2


@pytest.mark.asyncio
async def test_grade_relevance_none_when_all_no() -> None:
    mock = MagicMock()

    async def ainvoke(msgs: list) -> MagicMock:  # noqa: ANN001
        out = MagicMock()
        out.content = "no"
        return out

    mock.ainvoke = ainvoke
    r1 = SearchResultItem(
        note_id=uuid.uuid4(), note_title="A", chunk_text="x", similarity_score=0.5
    )
    rel, flags = await nodes.grade_relevance_of_chunks(mock, "Q?", [r1])
    assert flags == [False]
    assert rel == []


def test_infer_grounded() -> None:
    assert nodes.infer_grounded("недостаточно информации") is False
    assert nodes.infer_grounded("заметки не содержат такой информации") is False
    assert nodes.infer_grounded("Mars is the fourth planet") is True


@pytest.mark.asyncio
async def test_generate_insufficient_without_results() -> None:
    s = AppSettings(
        db_url="postgresql+asyncpg://u:p@127.0.0.1:1/db",
        llm=LLMSettings(
            base_url="https://api.openai.com/v1",
            api_key="k",
        ),
    )
    out = await nodes.run_generate_llm(s, "Q", [])
    assert out["confidence"] == "none"
    assert out["is_grounded"] is False
