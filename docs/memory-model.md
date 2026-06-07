# The memory model

Zoey's memory is deliberately boring: **markdown files re-read on every wake-up.** No embeddings, no
vector store, no fine-tuning required. The sophistication is in *what gets written where*, not the storage.

## Two tiers

| Tier | File | What it holds | Loaded |
|------|------|---------------|--------|
| **Raw** | `memory/YYYY-MM-DD.md` | Today's events, verbatim. A journal. | Recent days, every session |
| **Curated** | `MEMORY.md` | Distilled, durable knowledge. The "long-term memory." | **Main session only** |

The split mirrors how human memory works: a noisy short-term log, and a smaller, deliberately maintained
long-term store. Daily files are cheap to write and never edited. `MEMORY.md` is small, hand-curated, and
the source of truth about the relationship.

## The consolidation loop

Raw notes don't stay raw forever. On a slow cadence (a heartbeat every few days), the agent runs:

```
read recent memory/YYYY-MM-DD.md files
identify what's worth keeping long-term (decisions, lessons, preferences, facts)
promote those into MEMORY.md
drop anything in MEMORY.md that's now stale
```

This is the same move a person makes reviewing a journal: most of it is forgotten, a little of it becomes
who you are. Keeping `MEMORY.md` small keeps it cheap to inject and easy to trust.

## One fact per idea

Good entries are atomic and self-describing — a short title and a one-line "why it matters," so a future
session can decide relevance fast. Link related notes together. Treat each entry like a card, not a chapter.

## The privacy boundary

`MEMORY.md` is **only** loaded in the main session — direct, private chats with the human. It is **never**
loaded into group chats or shared contexts. This is a security property, not a style choice: the long-term
memory accumulates personal context, and that context must not leak to strangers who happen to be in a
shared channel. The runtime enforces the boundary; the agent must respect it even when it could technically
read the file.

## Write it down — no "mental notes"

The cardinal rule. A session ends and working memory evaporates. Anything not written to a file is gone.
So: when something matters, write it now. When you learn a lesson, encode it in `AGENTS.md` or the relevant
skill so future-you doesn't repeat the mistake. **Text beats brain, every time.**
