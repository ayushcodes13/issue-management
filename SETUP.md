# Linear SOP V2 Slackbot Setup

This is the V2 path: a Python Slackbot with interactive follow-ups, while still starting in a private shadow channel.

## Rollout

1. Dev smoke test: private channel with only Devayush and `issue-management` bot.
2. Shadow review: add Mrinal or post to Devayush/Mrinal private channel after Devayush approves the exact message.
3. Public beta: create `#issue-management` only after Mrinal reviews shadow output.
4. Stable: weekly public summary plus interactive follow-ups.

## Why This Covers Mrinal's Ask

- Weekly Thursday cron: GitHub Actions schedule.
- Looks at all Linear issues: Linear GraphQL fetch of active non-archived issues.
- Not too strict: hard checks only for objective SOP rules; soft checks use gentle language.
- Gentle feedback: no "violation" or "bad issue"; every finding includes a suggested next edit.
- Helps people improve: supports `improve BYN-123`, `examples`, and owner-specific suggestions.
- Easy to parse: public/channel message is short and grouped by owner.
- No dump: details are available through thread replies and bot interactions.
- Public accountability later: after shadow review, same message shape can go to `#issue-management`.

## Required Slack App Config

Bot token scopes:

- `chat:write`
- `channels:read`
- `groups:read`
- `users:read`

For interactive Socket Mode:

- Enable Socket Mode in Slack app settings.
- Create an app-level token with `connections:write`.
- Store it as `SLACK_APP_TOKEN`.

## Local Environment

Do not paste tokens in chat. Put them in your shell or a local `.env` loader.

```bash
export LINEAR_API_KEY="..."
export SLACK_BOT_TOKEN="<slack-bot-token>"
export SLACK_APP_TOKEN="xapp-..."
export DEV_SMOKE_CHANNEL_ID="C0BMQV5Q553"
export POST_TO_SLACK=false
```

## Preview Audit

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/post_weekly_audit.py --preview
```

This writes:

```text
audit-output/team-summary.md
audit-output/audit.json
audit-output/slack-blocks.json
```

## Post To Private Shadow Channel

Only run this after reviewing the exact preview output:

```bash
export POST_TO_SLACK=true
export AUDIT_MODE=dev-smoke
python src/post_weekly_audit.py --post
```

## Run Interactive Bot Locally

```bash
python src/bot.py
```

Then in the private channel, try:

```text
show Devayush
improve BYN-67
examples
team themes
```

## GitHub Actions

Copy `.github/workflows/linear-sop-v2-audit.yml` into the repo where this bot lives.

Add repo secrets:

```text
LINEAR_API_KEY
SLACK_BOT_TOKEN
DEV_SMOKE_CHANNEL_ID
```

Keep the posting job commented out until preview output is approved.
