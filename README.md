# Weekly Linear Issue Review Skill

Reusable weekly Linear issue-management skill.

This repo is intentionally simple: a scheduled agent-style workflow fetches Linear issues, runs local SOP checks, optionally sends only flagged issues to OpenAI for gentle wording/suggestions, writes Markdown reports, and can post a short summary to Slack.

## What It Does

- Fetches active, non-archived Linear issues.
- Reviews `Backlog`, `Todo`, `In Progress`, and `In Review`.
- Checks SOP hygiene such as owners, priority, type labels, Definition of done, and Acceptance criteria.
- Optionally makes one batched OpenAI call for flagged issues only, not one call per issue.
- Writes audit artifacts for review.
- Posts a short owner-grouped summary to Slack when Slack secrets are configured.
- Keeps full details in Markdown files instead of dumping everything into Slack.

## Reusable Skill

The reusable skill instructions live in:

```text
skills/weekly-linear-issue-review/SKILL.md
```

Use that file when running this from Codex, Claude, or another agent.

## Thursday Cron

The workflow runs every Thursday at 9:00 AM IST:

```yaml
cron: "30 3 * * 4"
```

It can also be run manually from GitHub Actions with `workflow_dispatch`.

On scheduled runs, the workflow posts to Slack only when `SLACK_BOT_TOKEN` and `DEV_SMOKE_CHANNEL_ID` are configured. Otherwise it still generates artifacts.

## Required Secrets

Add secrets in:

```text
GitHub repo -> Settings -> Secrets and variables -> Actions -> New repository secret
```

Required to fetch Linear:

```text
LINEAR_API_KEY
```

Optional for AI-written coaching notes:

```text
OPENAI_API_KEY
```

Required for scheduled Slack posting:

```text
SLACK_BOT_TOKEN
DEV_SMOKE_CHANNEL_ID
```

Needed later for shadow/public rollout:

```text
SHADOW_CHANNEL_ID
ISSUE_MANAGEMENT_CHANNEL_ID
```

## Local Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and fill `LINEAR_API_KEY`.

If you want the AI-assisted notes, also fill `OPENAI_API_KEY`.

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
results/issues.json
results/audit.json
results/slack-blocks.json
```

Use `team-summary.md` for the short Slack-style message.
Use `full-report.md` for review with Mrinal.
Use `owner-details.md` when people ask what applies to them.
Use `issue-improvements.md` when someone asks how to improve a specific issue.

If `OPENAI_API_KEY` is not set, the reports still run using local checks only and mark the analysis source as fallback.

## Local Slack Posting

Use this for dev-smoke testing before relying on the Thursday cron.

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

## Follow-Up Answers

For v2, keep Slack simple: post the short weekly summary, then use the generated files for follow-up answers.

```text
results/owner-details.md
results/issue-improvements.md
results/full-report.md
```

If someone asks for `show Devayush`, answer from `owner-details.md`.
If someone asks for `improve BYN-67`, answer from `issue-improvements.md`.
If the team later wants a fully interactive Slackbot, add it as a separate layer on top of these JSON/Markdown artifacts.

## Safety

- No Linear mutations.
- No Linear comments.
- No auto-assignment.
- No auto-status changes.
- No Slack posting unless you run `./post_dev_smoke.sh` locally or the scheduled GitHub Action has Slack secrets configured.
