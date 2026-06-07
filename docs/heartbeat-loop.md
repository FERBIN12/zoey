# The heartbeat loop

Most assistants are purely reactive: they do nothing until spoken to. A *companion* needs to be able to
reach out first. The heartbeat is how Zoey does that without becoming annoying or burning tokens.

## What a heartbeat is

The runtime sends the agent a periodic poll (say every ~30 minutes). The agent gets a turn to think, look
around, and decide: **is there anything worth saying right now?** Usually the answer is no, and it returns
a no-op signal (`HEARTBEAT_OK`) cheaply. Occasionally something matters, and it proactively reaches out.

```
on heartbeat_tick:
    state = read(memory/heartbeat-state.json)
    pick 1–2 checks that are due (inbox, calendar, mentions, ...)
    run them
    update state with timestamps
    if something genuinely matters and it's a reasonable hour:
        message the human
    else:
        return HEARTBEAT_OK   # say nothing, stay cheap
```

## The discipline: when to speak, when to stay quiet

The whole value of the loop is restraint. Reach out when:

- An important email or message arrived
- A calendar event is imminent (< ~2h)
- You found something genuinely interesting
- It's been a long while (> ~8h) and a light check-in fits

Stay quiet (`HEARTBEAT_OK`) when:

- It's late (e.g. 23:00–08:00) and nothing is urgent
- The human is clearly busy
- Nothing has changed since the last check
- You checked < 30 minutes ago

A companion that pings you about nothing gets muted. The default must be silence.

## Batching: why heartbeat beats N cron jobs

Heartbeats let you fold several fuzzy periodic checks (inbox + calendar + mentions) into **one** turn with
shared conversational context. That's far cheaper than a separate scheduled job per check, and the slight
timing drift doesn't matter for "check my inbox every so often."

## Heartbeat vs cron

| Use **heartbeat** when… | Use **cron** when… |
|--------------------------|--------------------|
| Several checks can batch together | Exact timing matters ("9:00 AM sharp") |
| You want recent conversational context | The task needs isolation from main history |
| Timing can drift (~30 min is fine) | You want a different model / thinking level |
| You're trying to reduce API calls | One-shot reminders, or output that delivers straight to a channel |

## State tracking

Keep a tiny `memory/heartbeat-state.json` so the agent remembers what it last looked at and doesn't
re-check the same thing every tick:

```json
{ "lastChecks": { "email": 1703275200, "calendar": 1703260800, "weather": null } }
```

That's it. A slow timer, a short checklist, and a strong bias toward silence — that's the entire loop.
