---
name: weekly-linear-issue-review
description: Run a simple reusable weekly Linear SOP review for Bynd. Use when asked to fetch active Linear issues, check issue hygiene against the Linear SOP, generate owner-grouped Markdown reports, post a short Slack shadow-channel summary, or support follow-up prompts like show a person and improve an issue id.
---

# Weekly Linear Issue Review

## Overview

Use this skill to run a lightweight weekly Linear issue-management check. The workflow is intentionally simple: fetch active Linear issues, generate Markdown reports, and post a short Slack summary to the configured shadow channel.

This is not a production service. Keep Linear read-only and use Slack only for the short summary.

## Workflow

1. Fetch active, non-archived Linear issues in `Backlog`, `Todo`, `In Progress`, and `In Review`.
2. Check issue hygiene against the Linear SOP.
3. Write Markdown and JSON artifacts.
4. Post only the short summary to Slack when explicitly running the post command or when the configured Thursday cron runs.
5. Use detailed Markdown files for follow-up answers.

Read `references/sop-checks.md` before changing the checks. Read `references/slack-workflow.md` before changing Slack behavior.

## Commands

From the repo root, or by using the skill wrapper scripts:

```bash
./run_manual.sh
```

or:

```bash
skills/weekly-linear-issue-review/scripts/run-review.sh
```

This writes:

- `results/team-summary.md`
- `results/full-report.md`
- `results/owner-details.md`
- `results/issue-improvements.md`
- `results/issues.json`
- `results/audit.json`
- `results/slack-blocks.json`

To post the short summary to the configured Slack shadow channel:

```bash
./post_dev_smoke.sh
```

or:

```bash
skills/weekly-linear-issue-review/scripts/post-summary.sh
```

## Slack Message

Post only the short summary. Do not paste the full report into Slack.

Good shape:

```text
Weekly Linear issue-management check

Reviewed <n> active issues.

Main themes:
- <theme>
- <theme>
- <theme>

Suggestions by owner:
- <Owner>: <n> issues, <n> suggestions

Reply with:
- show <name>
- improve <issue id>
- examples
```

## Follow-Ups

If someone asks `show <name>`, answer from `results/owner-details.md`.

If someone asks `improve <issue id>`, answer from `results/issue-improvements.md`.

If someone asks for the full report, use `results/full-report.md`.

## Safety

- Do not mutate Linear.
- Do not comment on Linear issues.
- Do not auto-assign owners.
- Do not move issue statuses.
- Do not post detailed owner reports to Slack unless explicitly asked.
- Keep `.env` local and ignored by git.
