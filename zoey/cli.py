"""`zoey` command line: init · chat · heartbeat · doctor · version."""
from __future__ import annotations

import argparse
import sys

from . import __version__
from .agent import Agent
from .config import Config
from .providers import ProviderError
from . import workspace as ws_mod


def _c(s: str, code: str) -> str:
    return f"\033[{code}m{s}\033[0m" if sys.stdout.isatty() else s


def cmd_init(cfg: Config, args) -> int:
    written = ws_mod.init(cfg.workspace, force=args.force)
    print(f"🪼  Workspace: {cfg.workspace}")
    if written:
        print("    created: " + ", ".join(written))
    else:
        print("    already initialized (use --force to overwrite templates)")
    print("\nNext: " + _c("zoey chat", "1") + "  — it'll ask who it is on first run.")
    return 0


def cmd_chat(cfg: Config, args) -> int:
    if not ws_mod.is_initialized(cfg.workspace):
        print("No workspace yet. Run " + _c("zoey init", "1") + " first.")
        return 1
    agent = Agent(cfg)
    banner = "🪼  Zoey" + (" — first run, let's get acquainted" if agent.bootstrapping else "")
    print(_c(banner, "95"))
    print(_c(f"   provider={cfg.provider} model={cfg.model}  (Ctrl-D or 'exit' to quit)\n", "90"))

    # On a fresh bootstrap, let the agent open the conversation.
    if agent.bootstrapping:
        try:
            reply, notes = agent.respond("(I just started you up. Say hi.)")
            _print_reply(reply, notes)
        except ProviderError as e:
            print(_c(f"⚠  {e}", "91"))
            return 2

    while True:
        try:
            user = input(_c("you ▸ ", "96"))
        except (EOFError, KeyboardInterrupt):
            print("\n🪼  bye.")
            return 0
        if user.strip().lower() in {"exit", "quit"}:
            print("🪼  bye.")
            return 0
        if not user.strip():
            continue
        try:
            reply, notes = agent.respond(user)
        except ProviderError as e:
            print(_c(f"⚠  {e}", "91"))
            continue
        _print_reply(reply, notes)


def cmd_heartbeat(cfg: Config, args) -> int:
    if not ws_mod.is_initialized(cfg.workspace):
        print("No workspace yet. Run `zoey init` first.")
        return 1
    agent = Agent(cfg)
    try:
        msg, notes = agent.heartbeat()
    except ProviderError as e:
        print(_c(f"⚠  {e}", "91"))
        return 2
    if msg:
        _print_reply(msg, notes)
    else:
        print(_c("· heartbeat: nothing to say (HEARTBEAT_OK)", "90"))
        for n in notes:
            print(_c("   " + n, "90"))
    return 0


def cmd_doctor(cfg: Config, args) -> int:
    import os
    print(_c("🪼  zoey doctor", "1"))
    print(f"  version       {__version__}")
    print(f"  provider      {cfg.provider}")
    print(f"  model         {cfg.model}")
    print(f"  workspace     {cfg.workspace}  ({'ok' if ws_mod.is_initialized(cfg.workspace) else 'NOT initialized — run zoey init'})")
    key_env = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY"}.get(cfg.provider)
    if key_env:
        print(f"  {key_env:<13} {'set ✓' if os.environ.get(key_env) else 'MISSING ✗'}")
    if ws_mod.is_initialized(cfg.workspace):
        bp = "yes (first run pending)" if ws_mod.exists(cfg.workspace, 'BOOTSTRAP.md') else "no (already born)"
        print(f"  bootstrap     {bp}")
        print(f"  long-term mem {'present' if ws_mod.read_memory(cfg.workspace).strip() else 'empty'}")
    return 0


def _print_reply(reply: str, notes: list[str]) -> None:
    print(_c("zoey ▸ ", "95") + reply)
    for n in notes:
        print(_c("   " + n, "90"))
    print()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="zoey", description="A personal AI agent that remembers you.")
    p.add_argument("--version", action="version", version=f"zoey {__version__}")
    sub = p.add_subparsers(dest="cmd")

    sp = sub.add_parser("init", help="scaffold the workspace from the template")
    sp.add_argument("--force", action="store_true", help="overwrite existing template files")
    sp.set_defaults(fn=cmd_init)

    sub.add_parser("chat", help="talk to your agent").set_defaults(fn=cmd_chat)
    sub.add_parser("heartbeat", help="run one proactive check-in").set_defaults(fn=cmd_heartbeat)
    sub.add_parser("doctor", help="show config and health").set_defaults(fn=cmd_doctor)

    args = p.parse_args(argv)
    if not getattr(args, "fn", None):
        p.print_help()
        return 0
    return args.fn(Config.load(), args)


if __name__ == "__main__":
    sys.exit(main())
