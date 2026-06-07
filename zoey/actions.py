"""The action protocol — how the agent edits its own memory.

The model persists things by emitting a fenced ```zoey block in its reply. The
runtime parses these out, executes them (writing to the workspace files), and
strips them from what the user sees. This is provider-agnostic (works with any
LLM, no function-calling API required) and fully legible — the agent's writes
are plain instructions you can read.

Supported actions (one per line inside a ```zoey fence):
    remember: <fact>            → append to curated MEMORY.md
    note: <text>                → append to today's raw daily log
    identity: Name=Zoey; Emoji=🪼   → set fields in IDENTITY.md
    user: Name=Sam; Timezone=PST    → set fields in USER.md
    done-bootstrap              → delete BOOTSTRAP.md (birth complete)
"""
from __future__ import annotations

import re
from pathlib import Path

from . import workspace as ws_mod

_FENCE = re.compile(r"```zoey\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)


def parse(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Return (text_without_action_blocks, [(verb, arg), ...])."""
    actions: list[tuple[str, str]] = []
    for block in _FENCE.findall(text):
        for raw in block.splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                verb, arg = line.split(":", 1)
                actions.append((verb.strip().lower(), arg.strip()))
            else:
                actions.append((line.lower(), ""))
    clean = _FENCE.sub("", text).strip()
    return clean, actions


def _parse_fields(arg: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for pair in arg.split(";"):
        if "=" in pair:
            k, v = pair.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def execute(ws: Path, actions: list[tuple[str, str]]) -> list[str]:
    """Run parsed actions against the workspace. Returns human-readable notes."""
    done: list[str] = []
    for verb, arg in actions:
        if verb == "remember" and arg:
            ws_mod.append_memory(ws, arg)
            done.append(f"📝 remembered: {arg}")
        elif verb == "note" and arg:
            ws_mod.append_daily(ws, "note", arg)
            done.append(f"🗒️  noted: {arg}")
        elif verb == "identity" and arg:
            ws_mod.set_fields(ws, "IDENTITY.md", _parse_fields(arg))
            done.append("🪞 updated IDENTITY.md")
        elif verb == "user" and arg:
            ws_mod.set_fields(ws, "USER.md", _parse_fields(arg))
            done.append("👤 updated USER.md")
        elif verb in ("done-bootstrap", "bootstrap-done", "done"):
            bp = ws / "BOOTSTRAP.md"
            if bp.exists():
                bp.unlink()
                done.append("🐣 bootstrap complete — deleted BOOTSTRAP.md")
    return done
