# Architecture

Zoey is not a model and not a chatbot. It's a **thin, file-based personality layer** that sits on top of
any capable LLM runtime and gives it three things a raw model doesn't have: a **stable identity**, a
**persistent memory**, and **proactive behavior**.

The whole design fits in one idea:

> The agent wakes up with no memory every session. A handful of markdown files **are** its memory.
> Read them at startup, update them as you go, and the same character persists indefinitely.

## The pieces

```
                 ┌─────────────────────────────────────────────┐
                 │                  RUNTIME                      │
                 │   (gateway · scheduler · channel adapters)    │
                 └───────────────┬───────────────────────────────┘
                                 │  injects at startup
                                 ▼
   ┌──────────────────────────────────────────────────────────────────┐
   │                          WORKSPACE                                 │
   │                                                                    │
   │   IDENTITY.md   who the agent is        ┐                          │
   │   SOUL.md       how it behaves          │  the "system prompt",    │
   │   AGENTS.md     workspace rules         │  but as living files     │
   │   USER.md       who the human is        ┘                          │
   │                                                                    │
   │   TOOLS.md      environment-specific notes                         │
   │   HEARTBEAT.md  proactivity checklist                              │
   │   BOOTSTRAP.md  one-time birth script (self-deletes)               │
   │                                                                    │
   │   memory/                                                          │
   │     YYYY-MM-DD.md   raw daily logs                                 │
   │     heartbeat-state.json                                           │
   │   MEMORY.md     curated long-term memory (private, main session)   │
   └──────────────────────────────────────────────────────────────────┘
                                 ▲
                                 │  three input loops
        ┌────────────────────────┼────────────────────────┐
        │                        │                         │
   user message              heartbeat tick            cron fire
   (reactive)            (slow batched proactive)   (exact-time, isolated)
```

## The startup algorithm

Every session, the runtime does roughly this:

```
on session_start:
    context = load(IDENTITY, SOUL, AGENTS)        # identity + behavior + rules
    if main_session:
        context += load(USER, MEMORY)             # private context, main session only
    context += load(recent memory/YYYY-MM-DD.md)  # what happened lately
    if exists(BOOTSTRAP.md):
        run_bootstrap()                           # first run only; deletes itself when done
    inject(context) into the model's system prompt
```

That's the entire "magic." There's no vector database required, no fine-tuning. Continuity is just
**plain files re-read on every wake-up**, which means it's auditable, forkable, and editable by hand.

## The three input loops

A personal agent needs more than request/response. Zoey runs three loops:

1. **Reactive** — a user message arrives, the agent responds. Standard.
2. **Heartbeat (proactive)** — a slow timer (~every 30 min) hands the agent a chance to check things
   (inbox, calendar, mentions) and reach out *only if something matters*. Batched to save tokens.
   See [heartbeat-loop.md](./heartbeat-loop.md).
3. **Cron (scheduled)** — exact-time, isolated tasks ("9:00 AM Monday: summarize the week"). Runs
   outside the main session so it can use a different model/thinking level and deliver straight to a channel.

**Heartbeat vs cron:** batch fuzzy, drift-tolerant checks into the heartbeat; use cron when the *time*
matters or the task needs isolation.

## The safety spine: internal vs external

Every action is classified:

- **Internal** (read, organize, learn, work in the workspace) → do it boldly, no permission needed.
- **External** (email, posts, anything that leaves the machine) → ask first unless durably authorized.

This single rule is what makes it safe to hand an agent real access. It can be maximally useful inside
its sandbox while staying conservative at every boundary with the outside world. The rule lives in
`SOUL.md` and `AGENTS.md` so it's enforced on every single turn.

## Why files instead of a database

- **Auditable** — you can read your agent's entire mind in a text editor.
- **Forkable** — copy the workspace, get a clone.
- **Portable** — runtime-agnostic; the files don't care which LLM or gateway runs them.
- **Repairable** — broke its personality? Edit the file. Roll back with git.

## Runtime

This kit ships the **workspace contract** (the files above) and the architecture, not a runtime.
It's designed for [OpenClaw](https://github.com/openclaw/openclaw) (MIT) and works with any runtime
that can inject startup context and drive heartbeat/cron loops. See the [README](../README.md) to wire it up.
