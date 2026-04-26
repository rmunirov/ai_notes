from __future__ import annotations

import os
import socket

import pytest

_TEST_DB = os.environ.get(
    "TEST_DB_URL", "postgresql+asyncpg://ai_notes:ai_notes@127.0.0.1:5432/ai_notes"
)


def _pg_up() -> bool:
    try:
        with socket.create_connection(("127.0.0.1", 5432), timeout=1.0):
            return True
    except OSError:
        return False


pytestmark = pytest.mark.skipif(
    not _pg_up(),
    reason="PostgreSQL not reachable on 127.0.0.1:5432 (start: docker compose up -d)",
)
