# Coverage Against Mrinal's Ask

## Asked: "make a skill that can run weekly on a cron (on thursdays)"

Covered by `.github/workflows/linear-sop-v2-audit.yml` with:

```yaml
cron: "30 3 * * 4"
```

This is Thursday 9:00 AM IST.

## Asked: "looks at all issues in Linear"

Covered by `src/audit.py`, which fetches active non-archived Linear issues via GraphQL and audits Backlog, Todo, In Progress, and In Review.

## Asked: "where should this skill run?"

Recommended:

- GitHub Actions for weekly audit and artifact generation.
- Slack Bolt for Python with Socket Mode for interactive bot testing.
- Later: small always-on host only if the interactive bot must be available 24/7.

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

Bot supports:

- `improve BYN-123`: gives a concrete next edit.
- `examples`: shows a good issue shape.
- `show <name>`: owner-specific suggestions.
- `team themes`: gives patterns without a giant dump.

## Asked: "not a large dump of text"

The weekly post is short and owner-grouped. Details are available through buttons/thread replies.

## Asked: "public accountability"

The final public-beta target is `#issue-management`, with grouped owner counts. No ranking or shaming language.

## Remaining Manual Setup

- Keep the leaked Slack token revoked/replaced.
- Store tokens as environment variables or GitHub secrets.
- Invite `issue-management` bot to the private test channel.
- Enable Socket Mode and create `SLACK_APP_TOKEN` only when running the interactive bot.
