from __future__ import annotations

import asyncio
import sys

from ai_notes.config import get_settings
from ai_notes.infrastructure.db.session import close_engine, get_session_maker, init_engine
from ai_notes.infrastructure.llm.factory import LLMProviderFactory
from ai_notes.services.indexing_service import IndexingService


async def _main() -> int:
    settings = get_settings()
    if not LLMProviderFactory.is_configured_for_remote(settings.llm):
        print("LLM is not configured (key / base_url / LLM_ENABLED).", file=sys.stderr)  # noqa: T201
        return 1
    init_engine(settings.db_url)
    try:
        sm = get_session_maker()
        async with sm() as session:
            n = await IndexingService(settings.llm).reindex_all_notes(session)
        print(f"Reindexed {n} note(s).")  # noqa: T201
    finally:
        await close_engine()
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(_main()))


if __name__ == "__main__":
    main()
