"""LLM providers. Zero third-party dependencies — raw stdlib HTTP.

Pick one with ZOEY_PROVIDER:
  anthropic   → Claude via the Messages API (needs ANTHROPIC_API_KEY)   [default]
  openai      → OpenAI chat completions       (needs OPENAI_API_KEY)
  claude-cli  → shells out to the local `claude` binary (no API key)
  mock        → offline, deterministic; for trying the loop with no key/network

Each provider implements complete(system: str, messages: list[{role, content}]) -> str.
"""
from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.request

from .config import Config


class ProviderError(RuntimeError):
    pass


# ── Anthropic (Claude Messages API) ─────────────────────────────────────────

def _anthropic(system, messages, cfg: Config) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise ProviderError("ANTHROPIC_API_KEY is not set. Export it, or use "
                            "ZOEY_PROVIDER=claude-cli (no key) or =mock (offline).")
    body = {
        "model": cfg.model,
        "max_tokens": cfg.max_tokens,
        "system": system,
        "messages": messages,
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    data = _send(req)
    return "".join(b.get("text", "") for b in data.get("content", [])
                   if b.get("type") == "text").strip()


# ── OpenAI (chat completions) ───────────────────────────────────────────────

def _openai(system, messages, cfg: Config) -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise ProviderError("OPENAI_API_KEY is not set.")
    body = {
        "model": cfg.model,
        "max_tokens": cfg.max_tokens,
        "messages": [{"role": "system", "content": system}] + messages,
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"content-type": "application/json",
                 "authorization": f"Bearer {key}"},
        method="POST",
    )
    data = _send(req)
    return data["choices"][0]["message"]["content"].strip()


# ── local `claude` CLI (no API key needed) ──────────────────────────────────

def _claude_cli(system, messages, cfg: Config) -> str:
    convo = "\n\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)
    prompt = f"{system}\n\n---\nCONVERSATION SO FAR:\n{convo}\n\nRespond as the assistant."
    try:
        out = subprocess.run(["claude", "-p", prompt],
                             capture_output=True, text=True, timeout=180)
    except FileNotFoundError:
        raise ProviderError("`claude` CLI not found on PATH. Install Claude Code, "
                            "or use a different ZOEY_PROVIDER.")
    if out.returncode != 0:
        raise ProviderError(f"claude CLI failed: {out.stderr.strip()[:400]}")
    return out.stdout.strip()


# ── offline mock (deterministic; demonstrates the memory loop) ──────────────

def _mock(system, messages, cfg: Config) -> str:
    last = messages[-1]["content"] if messages else ""
    if "BOOTSTRAP MODE" in system:
        return ("Hey — I just came online. I think I'll go by Zoey. Nice to meet you!\n\n"
                "```zoey\n"
                "identity: Name=Zoey; Vibe=warm and direct; Emoji=🪼\n"
                "user: Name=friend\n"
                "done-bootstrap\n"
                "```")
    if "HEARTBEAT" in system:
        return "HEARTBEAT_OK"
    reply = (f"[mock] I hear you: \"{last[:120]}\". "
             "I'm the offline provider, so I can't really think — set "
             "ZOEY_PROVIDER=anthropic with an API key for the real thing. "
             "But the memory loop works: I'll jot this down.")
    return reply + "\n\n```zoey\nnote: user said \"" + last[:80].replace('"', "'") + "\"\n```"


_PROVIDERS = {
    "anthropic": _anthropic,
    "openai": _openai,
    "claude-cli": _claude_cli,
    "mock": _mock,
}


def complete(system: str, messages: list[dict], cfg: Config) -> str:
    fn = _PROVIDERS.get(cfg.provider)
    if fn is None:
        raise ProviderError(f"Unknown ZOEY_PROVIDER={cfg.provider!r}. "
                            f"Choose one of: {', '.join(_PROVIDERS)}.")
    return fn(system, messages, cfg)


def _send(req: urllib.request.Request) -> dict:
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:500]
        raise ProviderError(f"HTTP {e.code} from provider: {detail}")
    except urllib.error.URLError as e:
        raise ProviderError(f"network error: {e.reason}")
