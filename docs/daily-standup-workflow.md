# Daily Standup Workflow

This workflow is for Granola notes titled `Daily-Standup`.

## Coverage Check

Run:

```bash
./run_standup_coverage.sh --days 60
```

Outputs:

- `results/standup-coverage/summary.md`
- `results/standup-coverage/coverage.json`

The checker only reads note metadata. It does not fetch transcripts.

## Standup To Linear Drafts

Run:

```bash
./run_daily_standup_memory.sh
```

This processes exactly one standup: the target date's `Daily-Standup` note.
By default the target date is today in `Asia/Kolkata`.

The runner:

1. Lists notes created since local midnight for the target date.
2. Filters to notes titled `Daily-Standup`.
3. Waits for a matching note if it is not available yet.
4. Fetches transcript detail.
5. Waits until the note signature is stable before sending it to the model.
6. Reviews the one standup against active Linear issues.

The run is read-only against Granola and Linear. It writes draft proposal files
locally and does not send Slack messages or mutate Linear.

For local testing without waiting:

```bash
./run_daily_standup_memory.sh --stable-seconds 0 --max-wait-seconds 0
```

## Schedule

The GitHub workflow is:

```text
.github/workflows/daily-standup-memory.yml
```

It runs Monday-Friday at `11:15 IST`, then waits up to four hours for today's
standup note to appear and stabilize. This avoids processing a partial
transcript if standup runs late.
