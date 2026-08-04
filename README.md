# Issue Management

Weekly Linear SOP audit for issue hygiene.

This repo runs a read-only Linear audit, produces Slack-ready summaries, and can later post the approved summary to Slack. The first rollout mode is preview-only, so the GitHub Action does not post to Slack by default.

## What It Does

- Fetches active, non-archived Linear issues.
- Reviews `Backlog`, `Todo`, `In Progress`, and `In Review`.
- Checks SOP hygiene such as owners, priority, type labels, Definition of done, and Acceptance criteria.
- Writes audit artifacts for review.
- Can optionally post a short owner-grouped summary to Slack after approval.

## GitHub Action

The workflow runs every Thursday at 9:00 AM IST:

```yaml
cron: "30 3 * * 4"
```

It can also be run manually from GitHub Actions with `workflow_dispatch`.

## Required Secrets

Add secrets in:

```text
GitHub repo -> Settings -> Secrets and variables -> Actions -> New repository secret
```

Required for preview mode:

```text
LINEAR_API_KEY
```

Needed only when Slack posting is enabled:

```text
SLACK_BOT_TOKEN
DEV_SMOKE_CHANNEL_ID
```

Needed later for shadow/public rollout:

```text
SHADOW_CHANNEL_ID
ISSUE_MANAGEMENT_CHANNEL_ID
```

Needed only for the interactive local Slackbot, not for the weekly GitHub Action:

```text
SLACK_APP_TOKEN
```

## Local Preview

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and fill `LINEAR_API_KEY`.

Then run:

```bash
./run_manual.sh
```

This writes:

```text
results/team-summary.md
results/owner-details.md
results/issue-improvements.md
results/full-report.md
results/audit.json
results/slack-blocks.json
```

Use `team-summary.md` for the short Slack-style message.
Use `full-report.md` for review with Mrinal.
Use `owner-details.md` when people ask what applies to them.
Use `issue-improvements.md` when someone asks how to improve a specific issue.

## Slack Posting

Only enable this after reviewing the exact generated output.

For local dev-smoke posting, fill these values in `.env`:

```text
SLACK_BOT_TOKEN=<slack-bot-token>
DEV_SMOKE_CHANNEL_ID=<private-channel-id>
```

Then run:

```bash
./post_dev_smoke.sh
```

This posts only to `DEV_SMOKE_CHANNEL_ID`.

If Slack returns `channel_not_found`, invite the bot to the private channel first:

```text
/invite @issuemanagement
```

Then run `./post_dev_smoke.sh` again.

To verify bot access without sending the full audit:

```bash
.venv/bin/python check_slack_access.py
```

## Interactive Bot

The bot reads the latest `audit-output/audit.json`; it does not call Linear directly.

```bash
export SLACK_BOT_TOKEN="..."
export SLACK_APP_TOKEN="..."
python src/bot.py
```

Supported messages:

```text
show Devayush
improve BYN-67
examples
team themes
```

## Safety

- No Linear mutations.
- No Linear comments.
- No auto-assignment.
- No auto-status changes.
- No Slack posting unless `--post` and `POST_TO_SLACK=true` are both set.
