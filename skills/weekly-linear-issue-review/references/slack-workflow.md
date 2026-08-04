# Slack Workflow

Use Slack as the lightweight interface.

## Rollout

1. Dev smoke: private channel with Devayush and the bot.
2. Shadow: private review channel with Devayush/Mrinal.
3. Public: `#issue-management` only after review.

## Posting Rule

Post only `results/summary.md` to Slack. Keep detailed reports in `results/`.

## Follow-Up Commands

Support these as conventions:

- `show <name>`: answer from `results/owners.md`
- `improve <issue id>`: answer from `results/issues.md`
- `examples`: show a good Linear issue shape

The simple Thursday cron generates the report, commits the latest `results/` folder, and posts the summary when Slack secrets are configured.
