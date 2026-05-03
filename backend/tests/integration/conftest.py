from __future__ import annotations

import re
import socket
from unittest.mock import AsyncMock, patch

import pytest
from ai_notes.infrastructure.db.models import EMBED_DIM
from tests.conftest import TEST_DB_URL

_match = re.search(r"@[^:]+:(\d+)/", TEST_DB_URL)
_test_port = int(_match.group(1)) if _match else 5432


def _pg_up() -> bool:
    try:
        with socket.create_connection(("127.0.0.1", _test_port), timeout=1.0):
            return True
    except OSError:
        return False


pytestmark = pytest.mark.skipif(
    not _pg_up(),
    reason=(
        f"PostgreSQL not reachable on 127.0.0.1:{_test_port} "
        "(set TEST_DB_URL; docker compose up -d)"
    ),
)

FIXED_VEC = [0.01] * EMBED_DIM


@pytest.fixture(autouse=True)
def _no_real_openai_embeddings() -> object:
    """Integration tests must not call the real OpenAI API for embeddings."""
    with (
        patch(
            "ai_notes.infrastructure.embeddings.provider.LangChainEmbeddingProvider.embed_query",
            new=AsyncMock(return_value=FIXED_VEC),
        ),
        patch(
            "ai_notes.infrastructure.embeddings.provider.LangChainEmbeddingProvider.embed_documents",
            new=AsyncMock(
                side_effect=lambda texts: [[0.01] * EMBED_DIM for _ in texts],
            ),
        ),
    ):
        yield
