#!/usr/bin/env python3
"""Send Daily Standup Memory DM drafts to Slack.

Dry-run by default. Actual sends require both --send and --yes.
"""

import argparse
import json
import os
from pathlib import Path

from send_dms import open_dm, post_dm, slack_client, slack_user_map


def main():
    args = parse_args()
    out_dir = Path(os.environ.get("DAILY_STANDUP_OUT_DIR", "results/daily-standup-memory"))
    drafts_path = out_dir / "dm-drafts.json"
    if not drafts_path.exists():
        raise RuntimeError(f"Missing {drafts_path}; run the daily standup memory review first")

    drafts = json.loads(drafts_path.read_text(encoding="utf-8"))
    if args.recipient:
        drafts = [draft for draft in drafts if draft.get("recipient") == args.recipient]
        if not drafts:
            raise RuntimeError(f"No daily standup DM draft found for recipient: {args.recipient}")

    print(f"Loaded {len(drafts)} daily standup DM draft(s).")
    if not drafts:
        return 0

    if args.validate_users:
        validate_users(drafts)

    if not args.send:
        print("Dry run only. No Slack DMs were sent.")
        for draft in drafts:
            print(f"- would send to {draft.get('recipient')} ({draft.get('itemCount')} item(s))")
        return 0

    if not args.yes:
        raise RuntimeError("Refusing to send without --yes. Use --send --yes after reviewing results/daily-standup-memory/dms/")

    client = slack_client()
    user_map = slack_user_map(client)
    sent_count = 0
    for draft in drafts:
        recipient = draft.get("recipient")
        user_id = user_map.get(recipient)
        if not user_id:
            raise RuntimeError(f"Could not resolve Slack user for recipient: {recipient}")
        channel_id = open_dm(client, user_id)
        post_dm(client, channel_id, draft.get("text") or "")
        sent_count += 1
        print(f"Sent daily standup DM to {recipient} ({user_id}).")

    print(f"Sent {sent_count} daily standup DM(s).")
    return 0


def parse_args():
    parser = argparse.ArgumentParser(description="Send generated Daily Standup Memory DM drafts to Slack.")
    parser.add_argument("--send", action="store_true", help="Actually send DMs. Omit for dry-run preview.")
    parser.add_argument("--yes", action="store_true", help="Required with --send to prevent accidental sends.")
    parser.add_argument("--recipient", help="Only send/preview the exact recipient name.")
    parser.add_argument("--validate-users", action="store_true", help="Resolve recipients to Slack users without sending.")
    return parser.parse_args()


def validate_users(drafts):
    client = slack_client()
    user_map = slack_user_map(client)
    missing = []
    for draft in drafts:
        recipient = draft.get("recipient")
        if recipient in user_map:
            print(f"- resolved {recipient} -> {user_map[recipient]}")
        else:
            print(f"- missing Slack user for {recipient}")
            missing.append(recipient)
    if missing:
        raise RuntimeError(f"Could not resolve {len(missing)} recipient(s): {', '.join(missing)}")
    print("All daily standup draft recipients resolved to Slack users.")


if __name__ == "__main__":
    raise SystemExit(main())
