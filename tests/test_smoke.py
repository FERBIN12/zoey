"""End-to-end smoke test of the memory loop using the offline mock provider.

No API key or network needed. Run with: python -m pytest, or just `python tests/test_smoke.py`.
"""
import os
import tempfile
from pathlib import Path


def _cfg(ws):
    os.environ["ZOEY_PROVIDER"] = "mock"
    os.environ["ZOEY_WORKSPACE"] = str(ws)
    from zoey.config import Config
    return Config.load()


def test_bootstrap_memory_and_persistence():
    with tempfile.TemporaryDirectory() as d:
        ws = Path(d) / "ws"
        from zoey import workspace as w
        from zoey.agent import Agent

        # init scaffolds the template, including BOOTSTRAP.md
        w.init(ws)
        assert w.is_initialized(ws)
        assert w.exists(ws, "BOOTSTRAP.md")

        # first turn runs bootstrap: writes identity/user, deletes BOOTSTRAP.md
        agent = Agent(_cfg(ws))
        assert agent.bootstrapping
        reply, notes = agent.respond("(startup) say hi")
        assert reply                              # clean text, action block stripped
        assert "```zoey" not in reply
        assert not w.exists(ws, "BOOTSTRAP.md")   # birth complete
        assert "Zoey" in w.read(ws, "IDENTITY.md")

        # a normal turn records to the daily log
        agent.respond("I like trail running")
        today = w.read_recent_daily(ws, 1)
        assert "trail running" in today

        # a fresh agent on the same workspace is NOT bootstrapping (memory persists)
        agent2 = Agent(_cfg(ws))
        assert not agent2.bootstrapping


def test_action_protocol_remember():
    with tempfile.TemporaryDirectory() as d:
        ws = Path(d) / "ws"
        from zoey import workspace as w, actions
        w.init(ws)
        clean, acts = actions.parse("Sure thing.\n```zoey\nremember: prefers tea over coffee\n```")
        assert clean == "Sure thing."
        actions.execute(ws, acts)
        assert "prefers tea over coffee" in w.read_memory(ws)


if __name__ == "__main__":
    test_bootstrap_memory_and_persistence()
    test_action_protocol_remember()
    print("✓ all smoke tests passed")
