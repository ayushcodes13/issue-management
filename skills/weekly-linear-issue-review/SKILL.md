---
name: weekly-linear-issue-review
description: Run a reusable weekly Linear SOP review for Bynd. Use when asked to fetch active Linear issues, audit Linear hygiene, run weekly issue management checks, update the results folder, post a short Slack summary, or answer follow-ups like show Devayush, show Nikhil, improve BYN-123, improve BYN-67, examples, duplicate issues, stale issues, missing owners, missing priorities, or missing acceptance criteria.
---

# Weekly Linear Issue Review

## Overview

Use this skill to run a lightweight weekly Linear issue-management check. Keep Linear read-only.

The flow is:

1. Fetch active, non-archived Linear issues in `Backlog`, `Todo`, `In Progress`, and `In Review`.
2. Run deterministic local SOP checks.
3. If `AZURE_OPENAI_API_KEY` exists, send only flagged issues to Azure OpenAI in one batched call.
4. Replace the contents of `results/` with the latest report.
5. Post only `results/summary.md` to Slack when explicitly asked or when the Thursday cron runs.

The Azure deployment is `gpt-5.5`. It is configured through:

```text
AZURE_OPENAI_4_1_MODELS_ENDPOINT=https://alerts-sweden-central.openai.azure.com/
AZURE_OPENAI_4_1_MODELS_VERSION=2025-03-01-preview
AZURE_OPENAI_4_1_MODELS_DEPLOYMENT=gpt-5.5
```

Read `references/sop-checks.md` before changing checks. Read `references/slack-workflow.md` before changing Slack behavior.

## Required Environment

Required for every run:

```text
LINEAR_API_KEY
```

Required only for AI-assisted suggestions:

```text
AZURE_OPENAI_API_KEY
AZURE_OPENAI_4_1_MODELS_ENDPOINT
AZURE_OPENAI_4_1_MODELS_VERSION
AZURE_OPENAI_4_1_MODELS_DEPLOYMENT
```

Required only for Slack posting:

```text
SLACK_BOT_TOKEN
SLACK_CHANNEL_ID
```

Optional:

```text
AUDIT_MODE
AUDIT_OUT_DIR
```

If `AZURE_OPENAI_API_KEY` is missing, still run the review using deterministic checks and fallback wording.

## Commands

From the repo root:

```bash
./run.sh
```

or:

```bash
skills/weekly-linear-issue-review/scripts/run-review.sh
```

To post the short summary:

```bash
./post.sh
```

or:

```bash
skills/weekly-linear-issue-review/scripts/post-summary.sh
```

## Results

Each run replaces these files:

- `results/summary.md`
- `results/owners.md`
- `results/issues.md`
- `results/report.md`
- `results/data.json`
- `results/linear.json`
- `results/slack.json`

Use `owners.md` for `show <name>`.
Use `issues.md` for `improve <issue id>`.
Use `report.md` for the full review.

## Safety

- Do not mutate Linear.
- Do not comment on Linear issues.
- Do not auto-assign owners.
- Do not move issue statuses.
- Do not post detailed reports to Slack unless explicitly asked.
- Keep `.env` local and ignored by git.
