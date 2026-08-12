# Issue Management

Read-only Linear and Granola workflows for keeping work context visible without automatically changing Linear.

## What This Repo Does

- Weekly Linear SOP review: fetches active Linear issues, reviews them against `docs/how-we-use-linear.md` with Azure OpenAI, and writes report/DM drafts locally.
- Daily Standup Memory: fetches today's Granola `Daily-Standup`, compares it with active Linear issues, and writes proposal/DM drafts locally.
- Slack posting and DM sending are always explicit. Dry-run is the default.
- Generated reports live under `results/` locally or as GitHub Actions artifacts. They are not committed to git.

Automation status:

- Both GitHub workflows are manual-only.
- There are no cron/schedule triggers in this repo.
- Daily Standup Memory can still wait for the Granola transcript to stabilize
  after a manual run starts.

## Source Of Truth

The Linear rules come from:

```text
docs/how-we-use-linear.md
```

Do not use the public Notion URL during runs. If the SOP changes, update this Markdown copy first.

For the broader Granola, Linear, GitHub, and Slack design, see:

```text
docs/central-work-orchestrator.md
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill `.env` with the secrets needed for the workflow you are running.

Core secrets:

```text
LINEAR_API_KEY
AZURE_OPENAI_API_KEY
```

Daily standup and work-memory secrets:

```text
GRANOLA_API_KEY
LINEAR_API_KEY
AZURE_OPENAI_API_KEY
```

Slack secrets:

```text
SLACK_BOT_TOKEN
SLACK_CHANNEL_ID
```

Slack DM sending also needs bot scopes:

```text
chat:write
im:write
users:read
```

Azure defaults:

```text
AZURE_OPENAI_4_1_MODELS_ENDPOINT=https://alerts-sweden-central.openai.azure.com/
AZURE_OPENAI_4_1_MODELS_VERSION=2025-03-01-preview
AZURE_OPENAI_4_1_MODELS_DEPLOYMENT=gpt-5.5
```

## Weekly Linear Review

This workflow is manual-only. Do not schedule it until the team decides where
these workflows should run reliably outside GitHub Actions.

Run locally:

```bash
./run.sh
```

Outputs:

```text
results/summary.md
results/owners.md
results/issues.md
results/report.md
results/dm-drafts.json
results/dms/*.md
results/friction-notes.md
```

Post only the short no-name summary to Slack:

```bash
./post.sh
```

Preview DM drafts without sending:

```bash
./send_dms.sh
```

Validate Slack user resolution without sending:

```bash
./send_dms.sh --validate-users
```

Send reviewed DM drafts:

```bash
./send_dms.sh --send --yes
```

Send one reviewed draft:

```bash
./send_dms.sh --recipient "Devayush Rout" --send --yes
```

Safety:

- `./run.sh` does not post to Slack.
- `./post.sh` posts only `results/summary.md`.
- `./post.sh` does not send DMs.
- Only `./send_dms.sh --send --yes` sends weekly review DMs.
- Successful weekly DM sends update `state/history.json` for repeat suppression.

## Daily Standup Memory

Run locally:

```bash
./run_daily_standup_memory.sh
```

Fast local smoke test:

```bash
./run_daily_standup_memory.sh --stable-seconds 0 --max-wait-seconds 0
```

List the Granola note titles visible to the current API key without fetching
transcripts:

```bash
set -a
source .env
set +a
python3 scripts/granola_preflight.py --date today --days 3
```

Flow:

```text
Granola API today's Daily-Standup transcript
  -> Linear GraphQL API active issues
  -> Azure OpenAI
  -> results/daily-standup-memory/*
```

Outputs:

```text
results/daily-standup-memory/summary.md
results/daily-standup-memory/report.md
results/daily-standup-memory/proposals.json
results/daily-standup-memory/raw-index.json
results/daily-standup-memory/dm-drafts.json
results/daily-standup-memory/dms/*.md
```

Preview Daily Standup DMs without sending:

```bash
./send_daily_standup_dms.sh
```

Validate Slack user resolution without sending:

```bash
./send_daily_standup_dms.sh --validate-users
```

Send only after review:

```bash
./send_daily_standup_dms.sh --send --yes
```

The GitHub workflow is manual-only. When manually dispatched, it can wait for
today's standup note to appear, then wait until the transcript has been
unchanged for 15 minutes before generating drafts. This is how the workflow
handles a standup with no fixed end time: "ended" means Granola stopped changing
the transcript for 15 minutes. It does not commit generated results back to the
repository.

The runner also requires at least `1000` transcript characters by default before processing, so it does not send DMs from an empty or barely-started note. Override with `DAILY_STANDUP_MIN_TRANSCRIPT_CHARS` only for unusually short standups.

The workflow sends DMs only when explicitly enabled on manual dispatch:

- Manual dispatch input: `send_slack_dms=true`

Default is off.

For a GitHub Actions smoke test that does not send Slack DMs and does not wait
15 minutes:

```bash
gh workflow run daily-standup-memory.yml \
  --repo ayushcodes13/issue-management \
  --ref main \
  -f date=today \
  -f send_slack_dms=false \
  -f stable_seconds=0 \
  -f max_wait_seconds=300
```

This validates Granola, Linear, Azure OpenAI, and artifact generation. The
normal manual run still uses the 15-minute transcript quiet period.

If the action fails before Linear/Azure, check the `Granola metadata preflight`
step first. It prints only note titles/timestamps and tells you whether the
configured `GRANOLA_API_KEY` can see a matching `Daily-Standup` for the target
date. If the note exists in the Granola app but not in this preflight, the
problem is API-key workspace/access or the title/date filter, not GitHub.

The Action is intentionally verbose. Read it like this:

```text
Preflight configuration
  Verifies required secrets exist and prints non-secret timing config.

Run today's Daily-Standup memory review
  Waits for the Granola note, waits for transcript stability, fetches Linear,
  calls Azure OpenAI, and writes local artifacts.

Validate generated draft outputs
  Fails early if expected files are missing or malformed.

Validate Slack recipients before sending
  Runs only when sending is enabled. Resolves every recipient before any DM is sent.

Optionally send Daily-Standup Slack DMs
  Runs only when `send_slack_dms=true` on manual dispatch.

Upload artifact
  Runs even on failure, so partial results/log context are easier to inspect.
```

If the Action appears to be "stuck" in the review step, it is usually waiting
for the transcript stability window. For a fast no-send health check, use
`stable_seconds=0`.

## General Work Memory API Runner

Use this for broader Granola note review. It is manual-only.

```bash
./run_work_memory_api.sh
```

Outputs:

```text
results/work-memory/summary.md
results/work-memory/report.md
results/work-memory/proposals.json
results/work-memory/raw-index.json
```

Optional Granola filters:

```text
GRANOLA_FOLDER_ID=
GRANOLA_FOLDER_IDS=
GRANOLA_TITLE_INCLUDE_REGEX=
GRANOLA_TITLE_EXCLUDE_REGEX=
GRANOLA_ATTENDEE_EMAIL_DOMAIN=
GRANOLA_OWNER_EMAIL=
```

## Standup Coverage Check

Check whether accessible Granola `Daily-Standup` notes cover recent weekdays:

```bash
./run_standup_coverage.sh
```

Outputs:

```text
results/standup-coverage/summary.md
results/standup-coverage/coverage.json
```

## GitHub Actions

Weekly review:

```text
.github/workflows/weekly-review.yml
```

Daily standup memory:

```text
.github/workflows/daily-standup-memory.yml
```

Both workflows upload generated `results/` content as artifacts. Neither workflow commits generated result files back to `main`.

## Safety Rules

- No Linear mutations.
- No Linear comments.
- No auto-assignment.
- No status changes.
- Public Slack summary has no owner names.
- DM drafts are generated but not sent unless the relevant `--send --yes` command or explicit workflow flag is used.
- `.env`, MCP tokens, virtualenvs, caches, and generated `results/` files stay out of git.
