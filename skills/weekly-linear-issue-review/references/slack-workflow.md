# Slack Workflow

Use Slack as the lightweight interface.

## Rollout

1. Dev smoke: private channel with Devayush and the bot.
2. Shadow: private review channel with Devayush/Mrinal.
3. Public: `#issue-management` only after review.

## Posting Rule

Post only `team-summary.md` to Slack. Keep detailed reports in artifacts or local files.

## Follow-Up Commands

Support these as conventions:

- `show <name>`: answer from `owner-details.md`
- `improve <issue id>`: answer from `issue-improvements.md`
- `examples`: show a good Linear issue shape

The simple Thursday cron generates the report and posts the summary. A continuously interactive bot requires Socket Mode and `SLACK_APP_TOKEN`; that is optional and not required for the weekly cron.
