from __future__ import annotations

from typing import Protocol, runtime_checkable

from langchain_core.embeddings import Embeddings


@runtime_checkable
class EmbeddingProvider(Protocol):
    async def embed_query(self, text: str) -> list[float]: ...
    async def embed_documents(self, texts: list[str]) -> list[list[float]]: ...


class LangChainEmbeddingProvider:
    def __init__(self, inner: Embeddings) -> None:
        self._inner = inner

    async def embed_query(self, text: str) -> list[float]:
        return await self._inner.aembed_query(text)

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return await self._inner.aembed_documents(texts)
