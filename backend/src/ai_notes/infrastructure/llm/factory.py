from __future__ import annotations

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from ai_notes.config import LLMSettings


class LLMProviderFactory:
    @staticmethod
    def chat_model(settings: LLMSettings) -> BaseChatModel:
        key = settings.api_key.get_secret_value()
        return ChatOpenAI(
            model=settings.model,
            base_url=settings.base_url,
            api_key=key or "dummy",  # noqa: S105
            timeout=settings.timeout,
        )

    @staticmethod
    def embeddings(settings: LLMSettings) -> Embeddings:
        key = settings.api_key.get_secret_value()
        return OpenAIEmbeddings(
            model=settings.embedding_model,
            base_url=settings.base_url,
            api_key=key or "dummy",  # noqa: S105
            dimensions=settings.embedding_dimensions,
        )

    @staticmethod
    def is_configured_for_remote(settings: LLMSettings) -> bool:
        k = settings.api_key.get_secret_value().strip()
        has_key = k not in {"", "sk-replace-me", "sk-placeholder"}
        return has_key and bool(settings.base_url) and settings.enabled
