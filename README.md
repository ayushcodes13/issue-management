# Weekly Linear Review

Simple weekly Linear issue review.

The run is read-only for Linear. It fetches active issues, asks Azure OpenAI to review them against the local SOP Markdown, writes the latest report and DM drafts into `results/`, and can post the short no-name summary to one Slack channel.

The source of truth is the repo copy of the SOP:

```text
docs/how-we-use-linear.md
```

Do not use the public Notion URL. Do not add rules that are not stated in that file.

For the broader Granola, Linear, GitHub, and Slack orchestration design, see:

```text
docs/central-work-orchestrator.md
```

## Files

```text
skills/weekly-linear-issue-review/SKILL.md
skills/weekly-linear-issue-review/scripts/run-review.sh
skills/weekly-linear-issue-review/scripts/post-summary.sh
docs/how-we-use-linear.md
docs/central-work-orchestrator.md
scripts/review.py
scripts/post.py
scripts/send_dms.py
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

DM sending also requires these Slack bot scopes:

```text
chat:write
im:write
users:read
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

To preview generated DMs without sending anything:

```bash
./send_dms.sh
```

To validate that draft recipients resolve to Slack users without sending:

```bash
./send_dms.sh --validate-users
```

To send one reviewed draft:

```bash
./send_dms.sh --recipient "Devayush Rout" --send --yes
```

To send every reviewed draft:

```bash
./send_dms.sh --send --yes
```

Successful DM sends update `state/history.json` for issue-level nudges. Dry-runs
never update state.

## End-to-End DM Workflow

DMs are implemented end to end, but they are not automatic by default.

1. `./run.sh`
   Fetches Linear issues, sends all active issues plus the SOP to Azure OpenAI,
   and generates:
   - `results/summary.md`
   - `results/dms/*.md`
   - `results/dm-drafts.json`
   - `results/report.md`

2. `./send_dms.sh`
   Previews generated DMs only. It shows who would receive messages and sends
   nothing.

3. `./send_dms.sh --validate-users`
   Checks Slack user resolution for draft recipients and sends nothing.

4. `./send_dms.sh --send --yes`
   Sends each generated DM draft, opens Slack DMs as needed, and updates
   `state/history.json` after successful issue-level DM sends.

To send only one person:

```bash
./send_dms.sh --recipient "Devayush Rout" --send --yes
```

Safety summary:

- `./run.sh` does not send DMs.
- `./post.sh` does not send DMs.
- Only `./send_dms.sh --send --yes` sends DMs.

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

Use `results/dms/` for per-person DM drafts. Issue-suggestion drafts are capped at three items. If someone has no issue-level nudge but the AI produced a useful owner note, the draft can be a light "no specific nudge this week" message.

If the AI has a positive owner note and no action item, the draft can simply say
good work this week and that there is nothing specific to clean up in Linear
from this review.

DM suggestions use two tiers:

- `should_have`: missing description, Definition of done, or Acceptance criteria
  on Todo/In Progress work; work that should move back to Backlog until scoped;
  or more than three In Progress items.
- `nice_to_have`: missing labels or missing priority.

Silence is acceptable when there is no genuinely useful nudge.

Use `owners.md` for owner-specific follow-ups, `issues.md` for issue-specific edits, `friction-notes.md` for repeat-suppression notes, and `report.md` for the full review.

`state/history.json` is committed and not replaced each run. It is used to suppress repeat DM items once actual DM sending starts updating state.

## GitHub Action

The GitHub Actions cron is disabled. The workflow can still be run manually from
the Actions tab:

```text
.github/workflows/weekly-review.yml
```

It writes the new `results/`, commits the updated results back to `main`, and uploads the same folder as an artifact.

Manual workflow runs use the `post_to_slack` input. Keep it `false` unless you
explicitly want the short summary posted to Slack.

## Safety

- No Linear mutations.
- No Linear comments.
- No auto-assignment.
- No status changes.
- Public Slack summary has no owner names.
- DM drafts are generated locally but not sent by `post.sh`.
- DM sending requires `./send_dms.sh --send --yes`.
