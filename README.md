# Weekly Linear Review

Simple weekly Linear issue review.

The run is read-only for Linear. It fetches active issues, asks Azure OpenAI to review them against the local SOP Markdown, writes the latest report and DM drafts into `results/`, and can post the short no-name summary to one Slack channel.

The source of truth is the repo copy of the SOP:

```text
docs/how-we-use-linear.md
```

Do not use the public Notion URL. Do not add rules that are not stated in that file.

## Files

```text
skills/weekly-linear-issue-review/SKILL.md
skills/weekly-linear-issue-review/scripts/run-review.sh
skills/weekly-linear-issue-review/scripts/post-summary.sh
docs/how-we-use-linear.md
scripts/review.py
scripts/post.py
results/
state/history.json
```

## Secrets

Required:

```text
LINEAR_API_KEY
```

Required only for Slack posting:

```text
SLACK_BOT_TOKEN
SLACK_CHANNEL_ID
```

Required for review generation:

```text
AZURE_OPENAI_API_KEY
```

Optional:

```text
SOP_DOC_PATH=docs/how-we-use-linear.md
```

Azure OpenAI uses the `gpt-5.5` deployment by default:

```text
AZURE_OPENAI_4_1_MODELS_ENDPOINT=https://alerts-sweden-central.openai.azure.com/
AZURE_OPENAI_4_1_MODELS_VERSION=2025-03-01-preview
AZURE_OPENAI_4_1_MODELS_DEPLOYMENT=gpt-5.5
```

If `AZURE_OPENAI_API_KEY` is missing, the run writes a "no AI review" report instead of pretending local checks are enough.

## Local Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill `.env`, then run:

```bash
./run.sh
```

To post the latest summary to Slack:

```bash
./post.sh
```

`./post.sh` posts only `results/summary.md`. It does not send DM drafts.

## Results

`results/` is committed to the repo. Each run replaces the folder contents with the latest report.

```text
results/summary.md
results/dms/*.md
results/dm-drafts.json
results/friction-notes.md
results/owners.md
results/issues.md
results/report.md
results/data.json
results/linear.json
results/slack.json
```

Use `summary.md` for the public/shadow Slack post. It contains aggregate counts only and no owner names.

Use `results/dms/` for per-person DM drafts. Each draft is capped at three items.

Use `owners.md` for owner-specific follow-ups, `issues.md` for issue-specific edits, `friction-notes.md` for repeat-suppression notes, and `report.md` for the full review.

`state/history.json` is committed and not replaced each run. It is used to suppress repeat DM items once actual DM sending starts updating state.

## GitHub Action

The workflow runs every Thursday at 9:00 AM IST:

```text
.github/workflows/weekly-review.yml
```

It writes the new `results/`, commits the updated results back to `main`, and uploads the same folder as an artifact.

Scheduled runs are dry-run by default. To allow scheduled Slack posting, set repository variable:

```text
POST_WEEKLY_TO_SLACK=true
```

Manual workflow runs still use the `post_to_slack` input.

## Safety

- No Linear mutations.
- No Linear comments.
- No auto-assignment.
- No status changes.
- Public Slack summary has no owner names.
- DM drafts are generated locally but not sent by `post.sh`.
