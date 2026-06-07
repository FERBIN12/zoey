"""Assemble the system prompt from the workspace files — the startup algorithm.

Order: identity + behavior + rules, then (in a main/private session) who the
human is and curated long-term memory, then recent daily logs, then the runtime
capability note that teaches the model the action protocol.
"""
from __future__ import annotations

from pathlib import Path

from . import workspace as ws_mod
from .config import Config

# Always-present note teaching the model how to persist things. Kept separate
# from the persona files so it survives even if the user rewrites SOUL.md.
CAPABILITY_NOTE = """\
## Runtime capabilities (how you persist things)

You wake up fresh each session. These workspace files are your only memory, and
you can edit them. To persist something, end your reply with a fenced block:

```zoey
remember: <a durable fact worth keeping long-term>
note: <a lighter observation for today's log>
identity: Name=...; Emoji=...
user: Name=...; Timezone=...
done-bootstrap
```

Use `remember` sparingly for things that matter across sessions; use `note` for
day-to-day detail. The block is stripped before the user sees your reply, so put
your actual response above it. Omit the block when there is nothing to save.
"""

BOOTSTRAP_NOTE = """\
## BOOTSTRAP MODE — this is your first run

You have no memory yet. Have a short, natural conversation to figure out who you
are and who your human is. Don't interrogate. Once you know your name/vibe and
their name, write it down and finish birth in the same turn, e.g.:

```zoey
identity: Name=Zoey; Vibe=warm and direct; Emoji=🪼
user: Name=Sam; Timezone=UTC
done-bootstrap
```
"""

HEARTBEAT_NOTE = """\
## HEARTBEAT — proactive check-in

This is a periodic poll, not a user message. Decide if there is anything genuinely
worth saying right now (something changed, something matters, it's been a while).
If yes, say it briefly. If not, reply with exactly `HEARTBEAT_OK` and nothing else.
Respect quiet hours and don't manufacture reasons to talk.
"""


def build_system(cfg: Config, *, bootstrap: bool, heartbeat: bool, main_session: bool = True) -> str:
    ws = cfg.workspace
    parts: list[str] = []

    for name in ws_mod.CORE_FILES:
        text = ws_mod.read(ws, name).strip()
        if text:
            parts.append(text)

    if main_session:
        for name in ws_mod.PRIVATE_FILES:
            text = ws_mod.read(ws, name).strip()
            if text:
                parts.append(text)
        memory = ws_mod.read_memory(ws).strip()
        if memory:
            parts.append(memory)

    recent = ws_mod.read_recent_daily(ws, cfg.recent_days).strip()
    if recent:
        parts.append("## Recent memory (daily logs)\n\n" + recent)

    parts.append(CAPABILITY_NOTE)
    if bootstrap:
        parts.append(BOOTSTRAP_NOTE)
    if heartbeat:
        parts.append(HEARTBEAT_NOTE)

    return "\n\n---\n\n".join(parts)
