# Coverage Against Mrinal's Ask

## Asked: "make a skill that can run weekly on a cron (on thursdays)"

Covered by `.github/workflows/linear-sop-v2-audit.yml` with:

```yaml
cron: "30 3 * * 4"
```

This is Thursday 9:00 AM IST.

## Asked: "looks at all issues in Linear"

Covered by `scripts/main.py` and `scripts/lib/linear_client.py`, which fetch active non-archived Linear issues via GraphQL and audit Backlog, Todo, In Progress, and In Review.

## Asked: "where should this skill run?"

Recommended:

- GitHub Actions for weekly audit and artifact generation.
- Later: Slack Bolt or a small service only if the team wants interactive follow-ups directly inside Slack.

## Asked: "where should this skill post its results?"

Rollout:

1. Private channel with only Devayush + bot for dev smoke test (`DEV_SMOKE_CHANNEL_ID`).
2. Devayush/Mrinal private channel for shadow review.
3. Public `#issue-management` channel after Mrinal approves.

## Asked: "how strict should the skill be?"

Implemented severity split:

- `needs_fix` for objective SOP rules.
- `should_improve` for readiness/verification quality.
- `gentle_suggestion` for subjective phrasing and scope.

## Asked: "how should it flag deviations gently?"

Message language avoids:

- violation
- non-compliant
- wrong
- bad issue
- failed

It uses:

- could be clearer
- consider adding
- this may be easier to pick up if
- if this is planned for this week

## Asked: "how does it help people improve?"

Generated reports support:

- `results/issue-improvements.md`: concrete next edits per issue.
- `results/owner-details.md`: owner-specific suggestions.
- `results/full-report.md`: team themes and audit details without putting a giant dump in Slack.

## Asked: "not a large dump of text"

The weekly post is short and owner-grouped. Details are available in generated Markdown files; interactive buttons/thread replies can be added later.

## Asked: "public accountability"

The final public-beta target is `#issue-management`, with grouped owner counts. No ranking or shaming language.

## Remaining Manual Setup

- Keep the leaked Slack token revoked/replaced.
- Store tokens as environment variables or GitHub secrets.
- Invite `issue-management` bot to the private test channel.
- Add `OPENAI_API_KEY` if AI-written coaching notes are wanted instead of local fallback wording.
