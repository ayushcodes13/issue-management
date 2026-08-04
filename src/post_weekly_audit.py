import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from audit import audit_issues, fetch_active_issues
from slack_render import (
    render_full_report_markdown,
    render_issue_improvements_markdown,
    render_owner_details_markdown,
    render_weekly_blocks,
    render_weekly_text,
)


def main():
    parser = argparse.ArgumentParser(description="Run the Linear SOP weekly audit.")
    parser.add_argument("--preview", action="store_true", help="Write artifacts and print the Slack message without posting.")
    parser.add_argument("--post", action="store_true", help="Post to Slack, only if POST_TO_SLACK=true is also set.")
    args = parser.parse_args()

    mode = os.environ.get("AUDIT_MODE", "dev-smoke")
    out_dir = Path(os.environ.get("AUDIT_OUT_DIR", "audit-output"))

    issues = fetch_active_issues()
    findings = audit_issues(issues)
    text = render_weekly_text(issues, findings, mode)
    blocks = render_weekly_blocks(issues, findings, mode)

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "team-summary.md").write_text(f"{text}\n", encoding="utf-8")
    (out_dir / "owner-details.md").write_text(
        render_owner_details_markdown(issues, findings, mode),
        encoding="utf-8",
    )
    (out_dir / "issue-improvements.md").write_text(
        render_issue_improvements_markdown(findings, mode),
        encoding="utf-8",
    )
    (out_dir / "full-report.md").write_text(
        render_full_report_markdown(issues, findings, mode),
        encoding="utf-8",
    )
    (out_dir / "audit.json").write_text(
        json.dumps(
            {
                "runId": datetime.now(timezone.utc).isoformat(),
                "mode": mode,
                "issueCount": len(issues),
                "findings": findings,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (out_dir / "slack-blocks.json").write_text(json.dumps(blocks, indent=2), encoding="utf-8")

    print(text)
    print(f"\nWrote artifacts to {out_dir}")

    if args.preview or not args.post or os.environ.get("POST_TO_SLACK") != "true":
        print("Not posting to Slack. Use --post and POST_TO_SLACK=true after reviewing the exact output.")
        return

    post_to_slack(mode, text, blocks)


def post_to_slack(mode, text, blocks):
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError

    token = os.environ.get("SLACK_BOT_TOKEN")
    channel = channel_for_mode(mode)

    if not token:
        raise RuntimeError("SLACK_BOT_TOKEN is required when posting")
    if not channel:
        raise RuntimeError("DEV_SMOKE_CHANNEL_ID, SHADOW_CHANNEL_ID, or ISSUE_MANAGEMENT_CHANNEL_ID is required when posting")

    client = WebClient(token=token)
    try:
        client.chat_postMessage(
            channel=channel,
            text=text,
            blocks=blocks,
            unfurl_links=False,
            unfurl_media=False,
        )
    except SlackApiError as exc:
        error = exc.response.get("error")
        if error == "channel_not_found":
            raise RuntimeError(
                "Slack could not find or access DEV_SMOKE_CHANNEL_ID. "
                "Invite the issue-management bot to that private channel, or use a channel ID where the bot is already a member."
            ) from exc
        raise
    print(f"Posted {mode} audit to {channel}")


def channel_for_mode(mode):
    if mode == "public-beta":
        return os.environ.get("ISSUE_MANAGEMENT_CHANNEL_ID")
    if mode == "shadow":
        return os.environ.get("SHADOW_CHANNEL_ID")
    return os.environ.get("DEV_SMOKE_CHANNEL_ID") or os.environ.get("SHADOW_CHANNEL_ID")


if __name__ == "__main__":
    main()
