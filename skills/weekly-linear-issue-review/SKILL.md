---
name: weekly-linear-issue-review
description: Run a simple reusable weekly Linear SOP review for Bynd. Use when asked to fetch active Linear issues, run SOP checks, optionally use Azure OpenAI for gentle coaching notes, write the latest results folder, post a short Slack summary, or answer follow-ups from owner and issue reports.
---

# Weekly Linear Issue Review

## Overview

Use this skill to run a lightweight weekly Linear issue-management check. Keep Linear read-only.

The flow is:

1. Fetch active, non-archived Linear issues in `Backlog`, `Todo`, `In Progress`, and `In Review`.
2. Run local SOP checks.
3. If `AZURE_OPENAI_API_KEY` exists, send only flagged issues to Azure OpenAI in one batched call using the `luna` deployment.
4. Replace the contents of `results/` with the latest report.
5. Post only `results/summary.md` to Slack when explicitly asked or when the Thursday cron runs.

Read `references/sop-checks.md` before changing checks. Read `references/slack-workflow.md` before changing Slack behavior.

## Commands

From the repo root:

```bash
./run.sh
```

or:

```bash
skills/weekly-linear-issue-review/scripts/run.sh
```

To post the short summary:

```bash
./post.sh
```

or:

```bash
skills/weekly-linear-issue-review/scripts/post.sh
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
