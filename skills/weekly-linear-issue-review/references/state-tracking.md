# State Tracking

## Purpose

Do not DM the same person about the same issue/category twice. A repeated
suggestion is a signal for standup or Friday review, not another automated
nudge.

## File

```text
state/history.json
```

This file is committed to the repo and is not replaced when `results/` is
regenerated.

## Current Behavior

- Dry runs read `state/history.json` and suppress repeat DM draft items.
- Dry runs do not write to `state/history.json`.
- Actual DM sending is still a later step; when that is implemented, it should
  write to `state/history.json` only after a DM send succeeds.
- Suppressed repeats are written to `results/friction-notes.md`.

## Shape

```json
{
  "BYN-59": {
    "missing_priority": {
      "sent_to": "Devayush Rout",
      "sent_at": "2026-08-06"
    }
  }
}
```

Use issue ID plus AI suggestion category as the repeat key.
