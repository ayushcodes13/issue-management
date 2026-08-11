import argparse
import json
import os
from pathlib import Path

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from lib.state import load_history, mark_sent, save_history


def main():
    args = parse_args()
    out_dir = Path(os.environ.get("AUDIT_OUT_DIR", "results"))
    drafts_path = out_dir / "dm-drafts.json"
    if not drafts_path.exists():
        raise RuntimeError(f"Missing {drafts_path}; run scripts/review.py first")

    drafts = json.loads(drafts_path.read_text(encoding="utf-8"))
    if args.recipient:
        drafts = [draft for draft in drafts if draft.get("recipient") == args.recipient]
        if not drafts:
            raise RuntimeError(f"No DM draft found for recipient: {args.recipient}")

    print(f"Loaded {len(drafts)} DM draft(s).")
    if not drafts:
        return

    if not args.send:
        print("Dry run only. No Slack messages will be sent and state will not be updated.")
        for draft in drafts:
            print(f"- would send to {draft.get('recipient')} ({draft.get('kind')}, {draft.get('itemCount')} item(s))")
        if args.validate_users:
            validate_slack_users(drafts)
        return

    if not args.yes:
        raise RuntimeError("Refusing to send without --yes. Use --send --yes after reviewing results/dms/")

    client = slack_client()
    user_map = slack_user_map(client)
    history = load_history()
    sent_count = 0

    for draft in drafts:
        recipient = draft.get("recipient")
        user_id = user_map.get(recipient)
        if not user_id:
            raise RuntimeError(f"Could not resolve Slack user for recipient: {recipient}")
        channel_id = open_dm(client, user_id)
        post_dm(client, channel_id, draft.get("text") or "")
        sent_count += 1
        for item in draft.get("items") or []:
            mark_sent(history, item.get("issueId"), item.get("category"), recipient)
        print(f"Sent DM to {recipient} ({user_id}).")

    save_history(history)
    print(f"Sent {sent_count} DM(s). Updated {os.environ.get('AUDIT_STATE_PATH', 'state/history.json')}.")


def parse_args():
    parser = argparse.ArgumentParser(description="Send generated Linear review DM drafts to Slack.")
    parser.add_argument("--send", action="store_true", help="Actually send DMs. Omit for dry-run preview.")
    parser.add_argument("--yes", action="store_true", help="Required with --send to prevent accidental sends.")
    parser.add_argument("--recipient", help="Only send/preview the exact recipient name.")
    parser.add_argument(
        "--validate-users",
        action="store_true",
        help="In dry-run, verify draft recipients can be resolved to Slack users. Does not send messages.",
    )
    return parser.parse_args()


def slack_client():
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        raise RuntimeError("SLACK_BOT_TOKEN is required")
    return WebClient(token=token)


def validate_slack_users(drafts):
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
    print("All draft recipients resolved to Slack users.")


def slack_user_map(client):
    users = []
    cursor = None
    while True:
        response = client.users_list(limit=200, cursor=cursor)
        users.extend(response.get("members", []))
        cursor = (response.get("response_metadata") or {}).get("next_cursor") or None
        if not cursor:
            break

    by_name = {}
    duplicates = set()
    for user in users:
        if user.get("deleted") or user.get("is_bot"):
            continue
        profile = user.get("profile") or {}
        names = {
            user.get("name") or "",
            user.get("real_name") or "",
            profile.get("real_name") or "",
            profile.get("display_name") or "",
            profile.get("real_name_normalized") or "",
            profile.get("display_name_normalized") or "",
        }
        for name in names:
            if not name:
                continue
            if name in by_name and by_name[name] != user.get("id"):
                duplicates.add(name)
            by_name[name] = user.get("id")
    if duplicates:
        raise RuntimeError(f"Duplicate Slack display names found: {', '.join(sorted(duplicates))}")
    return by_name


def open_dm(client, user_id):
    try:
        response = client.conversations_open(users=user_id)
    except SlackApiError as exc:
        raise RuntimeError(f"Failed to open DM with {user_id}: {exc.response.get('error')}") from exc
    return response["channel"]["id"]


def post_dm(client, channel_id, text):
    if not text.strip():
        raise RuntimeError("Refusing to send an empty DM")
    try:
        client.chat_postMessage(
            channel=channel_id,
            text=text,
            unfurl_links=True,
            unfurl_media=False,
        )
    except SlackApiError as exc:
        raise RuntimeError(f"Failed to post DM to {channel_id}: {exc.response.get('error')}") from exc


if __name__ == "__main__":
    main()
