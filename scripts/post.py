import json
import os
from pathlib import Path

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def main():
    out_dir = Path(os.environ.get("AUDIT_OUT_DIR", "results"))
    text_path = out_dir / "summary.md"
    blocks_path = out_dir / "slack.json"

    token = os.environ.get("SLACK_BOT_TOKEN")
    channel = os.environ.get("SLACK_CHANNEL_ID")
    if not token:
        raise RuntimeError("SLACK_BOT_TOKEN is required")
    if not channel:
        raise RuntimeError("SLACK_CHANNEL_ID is required")
    if not text_path.exists():
        raise RuntimeError(f"Missing {text_path}; run scripts/review.py first")

    text = text_path.read_text(encoding="utf-8")
    blocks = None
    if blocks_path.exists():
        raw_blocks = json.loads(blocks_path.read_text(encoding="utf-8"))
        blocks = json.loads(raw_blocks) if isinstance(raw_blocks, str) else raw_blocks

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
        if exc.response.get("error") == "channel_not_found":
            raise RuntimeError("Slack could not access the configured channel; invite the bot or fix the channel ID") from exc
        raise
    print(f"Posted Slack summary to {channel}")


if __name__ == "__main__":
    main()
