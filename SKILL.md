---
name: weekly-linear-issue-review
description: Run a simple weekly Linear SOP review and post a short owner-grouped summary to Slack.
---

# Weekly Linear Issue Review

Use this skill when asked to run the weekly Linear issue-management check.

## Goal

Every Thursday, review active Linear issues and post a short Slack summary that helps the team see:

- what needs ownership
- what is not ready to start
- what needs clearer scope
- what each owner should review

Keep it simple. This is a reusable agent workflow, not a production service.

## Scope

Review active, non-archived Linear issues in:

- `Backlog`
- `Todo`
- `In Progress`
- `In Review`

Do not edit Linear. Do not comment on Linear. Do not assign owners or move states.

## How To Run

From this repo:

```bash
./run_manual.sh
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

## Slack Message Shape

Post a short message only. Do not dump the full report into the channel.

Use this shape:

```text
Weekly Linear issue-management check

Reviewed <n> active issues.

Main themes:
- <theme 1>
- <theme 2>
- <theme 3>

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

If someone asks for the full report, point them to `results/full-report.md`.

## Tone

Keep language gentle and useful:

- "could be clearer"
- "consider adding"
- "this may be easier to pick up if"
- "if this is planned for this week"

Avoid:

- "violation"
- "non-compliant"
- "wrong"
- "invalid"
- "bad issue"
- "failed"

## Safety

This skill is read-only for Linear. The only write action is posting the generated summary to Slack when explicitly run or when the configured Thursday cron runs.
