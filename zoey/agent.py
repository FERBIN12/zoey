"""The agent loop: turn input into a reply, persist memory, stay the same person.

One `respond()` handles a reactive turn. `heartbeat()` handles a proactive tick.
Both assemble the system prompt from the workspace, call the provider, parse and
execute any action block, and log the exchange to the daily memory file.
"""
from __future__ import annotations

from .config import Config
from . import actions, prompt, providers
from . import workspace as ws_mod


class Agent:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.ws = cfg.workspace
        self.history: list[dict] = []

    @property
    def bootstrapping(self) -> bool:
        return ws_mod.exists(self.ws, "BOOTSTRAP.md")

    def respond(self, user_text: str) -> tuple[str, list[str]]:
        """Reactive turn. Returns (reply_text, memory_notes)."""
        ws_mod.append_daily(self.ws, "user", user_text)
        self.history.append({"role": "user", "content": user_text})

        system = prompt.build_system(self.cfg, bootstrap=self.bootstrapping,
                                     heartbeat=False)
        raw = providers.complete(system, self.history, self.cfg)

        clean, acts = actions.parse(raw)
        notes = actions.execute(self.ws, acts)

        # Store the model's full reply (incl. action block) in conversation
        # history so it stays coherent, but log/show the clean text.
        self.history.append({"role": "assistant", "content": raw})
        if clean:
            ws_mod.append_daily(self.ws, "zoey", clean)
        return clean, notes

    def heartbeat(self) -> tuple[str | None, list[str]]:
        """Proactive tick. Returns (message_or_None, memory_notes)."""
        system = prompt.build_system(self.cfg, bootstrap=False, heartbeat=True)
        msgs = self.history + [{"role": "user", "content": "[heartbeat]"}]
        raw = providers.complete(system, msgs, self.cfg)
        clean, acts = actions.parse(raw)
        notes = actions.execute(self.ws, acts)
        if clean.strip().upper().startswith("HEARTBEAT_OK") or not clean.strip():
            return None, notes
        ws_mod.append_daily(self.ws, "zoey (heartbeat)", clean)
        return clean, notes
