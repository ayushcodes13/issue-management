# SOP Checks

The only source of truth is:

```text
docs/how-we-use-linear.md
```

Do not add a check here unless that local SOP file states the rule.

Review active, non-archived Linear issues in:

- `Backlog`
- `Todo`
- `In Progress`
- `In Review`

Only issue-level findings are sent to Azure OpenAI. Owner-level findings remain in the deterministic report.

## Checks

- `missing_type_label`: `needs_fix`
  Issue has no SOP type label. Exactly one of `Bug`, `Feature`, `Improvement`, `Chore`, or `Spike` should be present.
- `multiple_type_labels`: `needs_fix`
  Issue has more than one SOP type label.
- `missing_owner`: `needs_fix`
  `Todo`, `In Progress`, or `In Review` issue has no assignee.
- `missing_priority`: `needs_fix`
  `Todo`, `In Progress`, or `In Review` issue has no priority.
- `missing_defined_outcome`: `should_improve`
  `Todo`, `In Progress`, or `In Review` issue lacks a clear Definition of done, goal, or outcome marker.
- `missing_acceptance_criteria`: `should_improve`
  `Todo`, `In Progress`, or `In Review` issue lacks Acceptance criteria or verification markers.
- `spike_missing_question`: `should_improve`
  `Spike` issue lacks a bounded question.
- `spike_missing_timebox`: `needs_fix`
  `Spike` issue lacks a timebox.
- `spike_missing_output`: `needs_fix`
  `Spike` issue lacks an expected output.
- `too_many_in_progress`: `needs_fix`
  Owner has more than three `In Progress` issues. This is owner-level and is not sent to Azure OpenAI as an issue rewrite request.

## Language

Use gentle language:

- `needs_fix`: objective field or status-readiness issue.
- `should_improve`: issue is usable but could be easier to verify.
- `gentle_suggestion`: subjective wording or scope suggestion tied directly to the SOP.

Avoid language like violation, non-compliant, wrong, invalid, bad issue, or failed.

When `AZURE_OPENAI_API_KEY` is configured, use the local checks as evidence and send only flagged issues plus `docs/how-we-use-linear.md` to Azure OpenAI. Do not send every Linear issue if it was not flagged.
