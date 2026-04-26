from __future__ import annotations

from typing import Self

from pydantic import AliasChoices, Field, SecretStr, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="LLM_",
        extra="ignore",
    )

    base_url: str = Field(
        default="https://api.openai.com/v1",
        description="OpenAI-compatible API base URL (from config/env only).",
    )
    api_key: SecretStr = Field(default=SecretStr(""))
    model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    timeout: float = 30.0
    enabled: bool = True

    @computed_field
    def api_key_set(self) -> bool:
        v = self.api_key.get_secret_value().strip()
        return v not in {"", "sk-replace-me", "sk-placeholder"}


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env",),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    debug: bool = False
    port: int = 8765
    db_url: str = Field(
        default="postgresql+asyncpg://ai_notes:ai_notes@127.0.0.1:5432/ai_notes",
        validation_alias=AliasChoices("DB_URL", "db_url"),
    )
    checkpoint_url: str = Field(
        default="",
        description="Postgres URL for LangGraph. If empty, derived from DB_URL.",
        validation_alias=AliasChoices("CHECKPOINT_URL", "checkpoint_url"),
    )
    llm: LLMSettings = Field(default_factory=LLMSettings)

    @model_validator(mode="after")
    def sync_checkpoint_url(self) -> Self:
        if not self.checkpoint_url.strip():
            self.checkpoint_url = self.db_url.replace("postgresql+asyncpg://", "postgresql://", 1)
        return self


def get_settings() -> AppSettings:
    return AppSettings()
