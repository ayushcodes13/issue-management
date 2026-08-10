---
name: weekly-linear-issue-review
description: Run a reusable weekly Linear SOP review for Bynd. Use when asked to fetch active Linear issues, review Linear hygiene against the local How we use Linear SOP with Azure OpenAI, update the results folder, generate no-name Slack summaries, draft per-person DMs, track repeat suggestions, post a short Slack summary, or answer follow-ups like show Devayush, show Nikhil, improve BYN-123, improve BYN-67, examples, missing owners, missing priorities, missing type labels, missing definitions of done, missing acceptance criteria, or Spike shape.
---

# Weekly Linear Issue Review

## Overview

Use this skill to run a lightweight weekly Linear issue-management check. Keep Linear read-only.

The only source of truth is the repo copy of the Notion SOP:

```text
docs/how-we-use-linear.md
```

Do not use the public Notion URL during a run. Do not add checks unless they are stated in `docs/how-we-use-linear.md`.

The flow is:

1. Fetch active, non-archived Linear issues in `Backlog`, `Todo`, `In Progress`, and `In Review`.
2. Read `docs/how-we-use-linear.md`.
3. Send all active issues plus the local SOP text to Azure OpenAI in one batched call.
4. Ask Azure OpenAI to return useful suggestions only, without treating omitted issues as clean.
5. Replace the local `results/` artifacts with the latest report and DM drafts.
6. Read `state/history.json` to suppress repeated DM draft items.
7. Post only `results/summary.md` to Slack when explicitly asked or when a send flag is enabled.

The Azure deployment is `gpt-5.5`. It is configured through:

```text
AZURE_OPENAI_4_1_MODELS_ENDPOINT=https://alerts-sweden-central.openai.azure.com/
AZURE_OPENAI_4_1_MODELS_VERSION=2025-03-01-preview
AZURE_OPENAI_4_1_MODELS_DEPLOYMENT=gpt-5.5
```

Read `references/ai-review-policy.md` before changing review behavior. Read `references/slack-workflow.md` before changing Slack behavior. Read `references/state-tracking.md` before changing repeat suppression.

## Required Environment

Required for every run:

```text
LINEAR_API_KEY
```

Required for review generation:

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
AUDIT_STATE_PATH
SOP_DOC_PATH
```

If `AZURE_OPENAI_API_KEY` is missing, write a "no AI review" report instead of producing deterministic hygiene results.

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

To preview generated DMs without sending:

```bash
./send_dms.sh
```

To validate Slack user resolution without sending:

```bash
./send_dms.sh --validate-users
```

or:

```bash
skills/weekly-linear-issue-review/scripts/send-dms.sh --validate-users
```

To send after human review:

```bash
./send_dms.sh --send --yes
```

or:

```bash
skills/weekly-linear-issue-review/scripts/send-dms.sh --send --yes
```

End-to-end DM workflow:

1. `./run.sh` fetches Linear issues, sends all active issues plus the SOP to
   Azure OpenAI, and generates `results/summary.md`, `results/dms/*.md`,
   `results/dm-drafts.json`, and `results/report.md`.
2. `./send_dms.sh` previews generated DMs and sends nothing.
3. `./send_dms.sh --validate-users` checks Slack user resolution and sends
   nothing.
4. `./send_dms.sh --send --yes` sends generated DM drafts and updates
   `state/history.json` after successful issue-level DM sends.

Important: `./run.sh` does not send DMs. `./post.sh` does not send DMs. Only
`./send_dms.sh --send --yes` sends DMs.

## Results

Each run replaces these generated files locally:

- `results/summary.md`
- `results/dms/*.md`
- `results/dm-drafts.json`
- `results/friction-notes.md`
- `results/owners.md`
- `results/issues.md`
- `results/report.md`
- `results/data.json`
- `results/linear.json`
- `results/slack.json`

Use `owners.md` for `show <name>`.
Use `issues.md` for `improve <issue id>`.
Use `results/dms/` for per-person DM drafts. Some drafts may be light owner-note
messages when there is no specific issue-level nudge.
Use `report.md` for the full review.

DM suggestions use two tiers:

- `should_have`: missing description, Definition of done, or Acceptance criteria
  on Todo/In Progress work; work that should move back to Backlog until scoped;
  or more than three In Progress items.
- `nice_to_have`: missing labels or missing priority.

`state/history.json` is not replaced during normal runs. It is reserved for
tracking successfully sent DM suggestions so the same issue/category is not
nudge-sent to the same person twice.

Generated `results/` artifacts are ignored by git. GitHub Actions should upload
them as build artifacts, not commit them back to `main`.

Do not describe this as a deterministic compliance report. It is an AI-assisted review prompt grounded in the local SOP.

## Safety

- Do not mutate Linear.
- Do not comment on Linear issues.
- Do not auto-assign owners.
- Do not move issue statuses.
- Do not post detailed reports or DMs to Slack unless explicitly asked.
- DM sending must use `./send_dms.sh --send --yes`; dry-run is the default.
- Public Slack summaries must not name owners or DM recipients.
- Keep `.env` local and ignored by git.
