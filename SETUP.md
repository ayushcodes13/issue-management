# Setup

This repo is a simple reusable weekly Linear issue-review skill.

## Local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill `.env`:

```text
LINEAR_API_KEY=<linear-api-key>
SLACK_BOT_TOKEN=<slack-bot-token>
DEV_SMOKE_CHANNEL_ID=<private-channel-id>
```

Run preview:

```bash
./run_manual.sh
```

Post to the private dev-smoke channel:

```bash
./post_dev_smoke.sh
```

## GitHub Secrets

Add these in GitHub Actions secrets:

```text
LINEAR_API_KEY
SLACK_BOT_TOKEN
DEV_SMOKE_CHANNEL_ID
```

The Thursday cron posts to Slack only when the Slack secrets exist. If Slack secrets are missing, it still runs and uploads report artifacts.

## Outputs

```text
team-summary.md
full-report.md
owner-details.md
issue-improvements.md
issues.json
audit.json
slack-blocks.json
```

Use `team-summary.md` for Slack. Use the detailed Markdown files for follow-ups.
