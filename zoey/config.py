"""Runtime configuration, resolved from environment variables with sane defaults.

Nothing here is secret. API keys are read from the environment by the provider
layer (ANTHROPIC_API_KEY / OPENAI_API_KEY), never stored in config or on disk.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_WORKSPACE = Path(os.path.expanduser("~/.zoey/workspace"))


@dataclass
class Config:
    provider: str          # anthropic | openai | claude-cli | mock
    model: str
    workspace: Path
    max_tokens: int
    recent_days: int       # how many days of daily logs to load at startup

    @classmethod
    def load(cls) -> "Config":
        ws = os.environ.get("ZOEY_WORKSPACE")
        return cls(
            provider=os.environ.get("ZOEY_PROVIDER", "anthropic").strip(),
            # Defaults to the most capable model; override with ZOEY_MODEL.
            # For OpenAI set e.g. ZOEY_MODEL=gpt-4o; for a cheaper Claude, claude-haiku-4-5.
            model=os.environ.get("ZOEY_MODEL", "claude-opus-4-8").strip(),
            workspace=Path(ws).expanduser() if ws else DEFAULT_WORKSPACE,
            max_tokens=int(os.environ.get("ZOEY_MAX_TOKENS", "4096")),
            recent_days=int(os.environ.get("ZOEY_RECENT_DAYS", "2")),
        )
