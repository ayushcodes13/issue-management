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
export LINEAR_API_KEY="..."
python src/post_weekly_audit.py --preview
```

This writes:

```text
audit-output/team-summary.md
audit-output/audit.json
audit-output/slack-blocks.json
```

## Slack Posting

Only enable this after reviewing the exact generated output.

```bash
export LINEAR_API_KEY="..."
export SLACK_BOT_TOKEN="..."
export DEV_SMOKE_CHANNEL_ID="..."
export POST_TO_SLACK=true
export AUDIT_MODE=dev-smoke
python src/post_weekly_audit.py --post
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
