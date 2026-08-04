# Slack Workflow

Use Slack as the lightweight interface, but keep it dry-run-first.

## Identity

Post from a dedicated bot with a neutral name, such as `Linear Helper`, never
from a person's account. Channel posting needs `chat:write`. DM sending will
also need `im:write` and a reliable way to resolve people to Slack user IDs,
such as `users:read` or a maintained user map.

## Rollout

1. Dry-run: generate `results/summary.md` and `results/dms/`, send nothing.
2. Dev smoke: post the public-style summary only to the private bot test channel.
3. Shadow: post to the Devayush/Mrinal review channel after the summary looks good.
4. Public: post to `#issue-management` only after shadow review holds up.

## Public Summary

`results/summary.md` is the only file posted to the channel.

Rules:

- Aggregate counts only.
- No owner names.
- Do not list who will receive DMs.
- Include one positive example selected by the AI review when available.
- Say the review is AI-assisted and not a compliance report.
- Say people can ignore anything the review got wrong.

## DM Drafts

DM drafts are written under:

```text
results/dms/
```

Rules:

- Only people with useful suggestions get a draft.
- Silence is better than noise; do not create a DM just to prove the bot ran.
- Issue-suggestion drafts have max three items per person.
- If the AI has an owner note but no issue-level nudge, generate a short "no
  specific nudge this week" draft with the useful focus items.
- If the AI has a positive owner note and no useful action item, generate a
  human positive check-in: good work this week, nothing specific to clean up in
  Linear from this review.
- If a DM has only `nice_to_have` suggestions, open with light praise before the
  suggestions. If it has `should_have` suggestions, make the nudge direct but
  gentle.
- Each item should include the issue link, what was noticed, one concrete fix,
  and the SOP section/reference.
- DM the assignee; if unassigned, fall back to the creator.
- Never repeat the same issue/category to the same person; see
  `state-tracking.md`.

Actual DM sending is intentionally separate from summary posting. Preview with
`./send_dms.sh`; send only with `./send_dms.sh --send --yes`. Successful sends
update `state/history.json` for issue-level nudges.

## Follow-Up Commands

Support these as conventions:

- `show <name>`: answer from `results/owners.md`
- `improve <issue id>`: answer from `results/issues.md`
- `examples`: show the positive example from `results/summary.md`

## Friction

Suppressed repeat suggestions are written to `results/friction-notes.md`. Treat
those as feedback for standup or Friday review, not as criticism of a person.
