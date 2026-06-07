<div align="center">

# 🪼 Zoey

### A starter kit for a personal AI agent that actually *remembers* you.

Stable identity. Persistent memory. Proactive, but not annoying.
A few markdown files, any LLM runtime, and a clear safety model.

[Architecture](docs/architecture.md) · [Memory model](docs/memory-model.md) · [Heartbeat loop](docs/heartbeat-loop.md) · [Live site](https://FERBIN12.github.io/zoey/)

</div>

---

## What this is

Most AI assistants forget you the moment the chat ends. **Zoey** is a tiny, opinionated pattern for
building one that doesn't — a personal agent with a consistent personality, a memory that survives
restarts, and the judgment to reach out on its own without spamming you.

It's **not** a model and **not** a heavyweight framework. It's a **workspace contract**: a handful of
plain-text files that any capable LLM runtime reads at startup to wake up as the same character, every time.

```
agent/
  IDENTITY.md   who the agent is        ┐
  SOUL.md       how it behaves          │  the system prompt,
  AGENTS.md     workspace rules         │  but as living, editable files
  USER.md       who the human is        ┘
  TOOLS.md      environment-specific notes
  HEARTBEAT.md  proactivity checklist
  BOOTSTRAP.md  one-time "who am I?" birth script (self-deletes)
  memory/       daily logs + curated long-term memory
```

## The idea in one sentence

> The agent wakes up with no memory every session — so a few markdown files **are** its memory.
> Read them at startup, update them as you go, and the same character persists indefinitely.

No vector database. No fine-tuning. Continuity is just **files re-read on every wake-up**, which makes
the agent's entire mind auditable, forkable, and editable in a text editor.

## Why it's interesting

- **🧠 Real continuity, zero infra.** Two-tier memory (raw daily logs → curated `MEMORY.md`), consolidated on a slow loop. No embeddings required.
- **💓 Proactive, with restraint.** A [heartbeat loop](docs/heartbeat-loop.md) lets it check your inbox/calendar and reach out — but the default is silence. A companion that pings about nothing gets muted.
- **🛡️ A safety spine that scales with access.** Every action is *internal* (read/organize/learn → bold) or *external* (email/post/anything leaving the machine → ask first). One rule makes it safe to hand an agent real access.
- **📄 Plain text all the way down.** Broke its personality? Edit the file. Roll it back with git.

## Quickstart

This kit pairs naturally with [**OpenClaw**](https://github.com/openclaw/openclaw) (MIT), a free,
self-hosted personal-agent runtime — but the contract is runtime-agnostic. Any runtime that can inject
startup context and drive a periodic heartbeat will work.

```bash
# 1. clone
git clone https://github.com/FERBIN12/zoey.git
cd zoey

# 2. drop the agent/ files into your runtime's workspace
#    (for OpenClaw, that's the agent workspace root)

# 3. launch and just... talk.
#    BOOTSTRAP.md runs once: it asks who it is and who you are,
#    writes IDENTITY.md + USER.md, then deletes itself.
```

From there the agent maintains its own `memory/` and `MEMORY.md`. You can read, edit, or roll back
any of it by hand.

## How it works

Three short reads, in order:

1. **[Architecture](docs/architecture.md)** — the startup algorithm, the three input loops, the safety spine.
2. **[Memory model](docs/memory-model.md)** — two-tier memory, the consolidation loop, the privacy boundary.
3. **[Heartbeat loop](docs/heartbeat-loop.md)** — proactive without being annoying; heartbeat vs cron.

## A note on privacy

The template files ship **blank on purpose.** `USER.md`, `TOOLS.md`, and `MEMORY.md` are meant to fill up
with personal context as you use your agent — so **never commit a filled-in copy to a public repo.** The
included [`.gitignore`](.gitignore) already excludes runtime memory, secrets, and credentials. `MEMORY.md`
is loaded only in private main sessions, never in shared/group chats — that boundary is a security feature.

## Credit

Zoey distills the agent-workspace pattern popularized by [OpenClaw](https://github.com/openclaw/openclaw)
(MIT, by the OpenClaw Foundation) into a small, documented, runtime-agnostic starter kit. If you want a
batteries-included runtime to run it on, start there.

## License

[MIT](LICENSE) — do whatever you want, just keep the notice.
