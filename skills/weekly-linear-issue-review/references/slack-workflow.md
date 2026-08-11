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
- Do not send positive/no-action DMs.
- Start with: "Here are a few suggestions from an AI review of your Linear issues:"
- Each item should be one line: clickable issue key plus one concrete fix.
- Use Slack mrkdwn internally as `<https://linear.app/...|BYN-123>` so the sent
  message renders as a blue clickable `BYN-123` with the URL hidden. Do not show
  raw angle-bracket syntax in human previews.
- Do not include separate link lines, "Noticed", "SOP reference", or
  explanatory paragraphs.
- Explain the actual edit instead of only naming SOP fields. For example,
  explain "add the exact question, time limit, and expected result" instead of
  saying "add Question to answer, Timebox, and Output".
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
