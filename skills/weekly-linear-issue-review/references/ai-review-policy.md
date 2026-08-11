# AI Review Policy

The only source of truth is:

```text
docs/how-we-use-linear.md
```

Do not use the public Notion URL during a run.

## Review Shape

- Fetch active, non-archived issues in `Backlog`, `Todo`, `In Progress`, and `In Review`.
- Send all fetched issues plus `docs/how-we-use-linear.md` to Azure OpenAI.
- Ask for useful suggestions only.
- Do not claim issues without suggestions are clean, compliant, or good.
- Keep the report framed as an AI-assisted helper, not a compliance report.
- Ask for one positive example issue when the model can identify one.
- Ask for the relevant SOP section on each suggestion so DM drafts can point
  people back to the rulebook.
- Silence is better than noise. Only return issue suggestions that are
  genuinely useful.

## Priority Tiers

Use two tiers:

- `should_have`: Todo or In Progress issues missing description, Definition of
  done, or Acceptance criteria; issues that should move back to Backlog until
  scoped; or more than three In Progress items for one owner.
- `nice_to_have`: missing labels or missing priority.

Future idea only: cross-reference GitHub activity against open tickets. Do not
create findings for this yet.

## Language

Use gentle language:

- `needs_fix`: objective SOP field/readiness gap the model is confident about.
- `should_improve`: likely helpful cleanup before someone starts or reviews work.
- `gentle_suggestion`: low-confidence or phrasing/scope suggestion tied directly to the SOP.

Avoid language like violation, non-compliant, wrong, invalid, bad issue, or failed.

Every suggestion should include a small next edit someone can make quickly.

If an owner has no useful issue-level nudge, do not create a DM for them.
Silence is better than a positive/no-action check-in.

DM suggestions should be one line each: inline issue link plus one concrete
next edit. Do not include separate "Noticed", "SOP reference", or explanatory
paragraphs in the DM.
