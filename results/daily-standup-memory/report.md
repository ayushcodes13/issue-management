# Work Memory API Report

Mode: `daily-standup-read-only`
Since: `2026-08-09T18:30:00Z`
Analysis source: `azure-openai`

This is the schedulable production path. It does not depend on Codex CLI or MCP OAuth.

## Counts

- Granola notes listed: 1
- Granola notes selected after filters: 1
- Granola notes inspected: 1
- Active Linear issues reviewed: 75
- Draft proposals: 6

## Linear Status Mix

- Backlog: 42
- In Progress: 15
- In Review: 1
- Todo: 17

## Proposal Categories

- add_context_to_existing_issue: 2
- already_in_linear: 1
- create_new_linear_issue: 2
- needs_human_review: 1

## Relevance Filters

Only selected notes are fetched in detail and sent to Azure OpenAI.

- Input notes: today-only lookup
- Selected notes: 1
- Active filters: targetDate=2026-08-10, titleRegex=^Daily[- ]Stand[- ]?up$|^Daily-Standup$

## Limitations

- Only one Granola detail record was provided, and the transcript text is truncated.
- Some Linear issue descriptions are truncated in the input, so a few overlaps may be hidden.
- The output is a draft proposal set for human approval; no Linear or Slack action is implied.

No Slack messages were sent and no Linear changes were made.
