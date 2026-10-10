"""Offline tests replace the paid LLM boundary, never the security decisions."""
import os
import sys
import types

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("DATABASE_SSL", "disable")


async def unavailable(*args, **kwargs):
    raise RuntimeError("No live providers in offline tests")


provider = types.ModuleType("core.llm_config")
provider.call_llm = unavailable
sys.modules["core.llm_config"] = provider
