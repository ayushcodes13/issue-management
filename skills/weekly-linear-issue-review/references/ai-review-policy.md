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

## Language

Use gentle language:

- `needs_fix`: objective SOP field/readiness gap the model is confident about.
- `should_improve`: likely helpful cleanup before someone starts or reviews work.
- `gentle_suggestion`: low-confidence or phrasing/scope suggestion tied directly to the SOP.

Avoid language like violation, non-compliant, wrong, invalid, bad issue, or failed.

Every suggestion should include a small next edit someone can make quickly.
