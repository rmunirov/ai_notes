from __future__ import annotations

# Minimal LangGraph placeholder: a compiled graph with MemorySaver is created when needed.
# Full RAG state machine lives in `services/agent_service.py` (retrieve + LLM generate).
from langgraph.checkpoint.memory import MemorySaver


def memory_checkpointer() -> MemorySaver:
    return MemorySaver()
