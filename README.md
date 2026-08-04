# Weekly Linear Review

Simple weekly Linear issue review.

The run is read-only for Linear. It fetches active issues, checks them against the SOP, writes the latest report into `results/`, and can post the short summary to one Slack channel.

The source of truth is the repo copy of the SOP:

```text
docs/how-we-use-linear.md
```

Do not use the public Notion URL or add checks that are not stated in that file.

## Files

```text
skills/weekly-linear-issue-review/SKILL.md
skills/weekly-linear-issue-review/scripts/run-review.sh
skills/weekly-linear-issue-review/scripts/post-summary.sh
docs/how-we-use-linear.md
scripts/review.py
scripts/post.py
results/
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

Optional:

```text
AZURE_OPENAI_API_KEY
SOP_DOC_PATH=docs/how-we-use-linear.md
```

Azure OpenAI uses the `gpt-5.5` deployment by default:

```text
AZURE_OPENAI_4_1_MODELS_ENDPOINT=https://alerts-sweden-central.openai.azure.com/
AZURE_OPENAI_4_1_MODELS_VERSION=2025-03-01-preview
AZURE_OPENAI_4_1_MODELS_DEPLOYMENT=gpt-5.5
```

If `AZURE_OPENAI_API_KEY` is missing, the review still runs with local checks only.

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

## Results

`results/` is committed to the repo. Each run replaces the folder contents with the latest report.

```text
results/summary.md
results/owners.md
results/issues.md
results/report.md
results/data.json
results/linear.json
results/slack.json
```

Use `summary.md` for Slack, `owners.md` for owner-specific follow-ups, `issues.md` for issue-specific edits, and `report.md` for the full review.

## GitHub Action

The workflow runs every Thursday at 9:00 AM IST:

```text
.github/workflows/weekly-review.yml
```

It writes the new `results/`, commits the updated results back to `main`, uploads the same folder as an artifact, and posts to Slack only when Slack secrets are configured.

## Safety

- No Linear mutations.
- No Linear comments.
- No auto-assignment.
- No status changes.
