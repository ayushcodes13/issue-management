import os
from pathlib import Path

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def load_env():
    env_path = Path(".env")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip().strip('"').strip("'")


def main():
    load_env()
    token = os.environ.get("SLACK_BOT_TOKEN")
    channel = os.environ.get("SLACK_CHANNEL_ID")
    print("SLACK_BOT_TOKEN:", "set" if token else "missing")
    print("SLACK_CHANNEL_ID:", "set" if channel else "missing")
    if channel:
        print("channel_prefix:", channel[:1])
        print("channel_length:", len(channel))
    if not token:
        return

    client = WebClient(token=token)

    try:
        auth = client.auth_test()
        print("auth_test: ok")
        print("workspace:", auth.get("team"))
        print("bot_user:", auth.get("user"))
        print("bot_id:", auth.get("bot_id"))
    except SlackApiError as exc:
        print("auth_test:", exc.response.get("error"))
        return

    if not channel:
        return

    try:
        info = client.conversations_info(channel=channel)
        ch = info.get("channel", {})
        print("conversations_info: ok")
        print("channel_name:", ch.get("name"))
        print("is_member:", ch.get("is_member"))
        print("is_private:", ch.get("is_private"))
    except SlackApiError as exc:
        print("conversations_info:", exc.response.get("error"))

    try:
        client.chat_postMessage(
            channel=channel,
            text="Issue-management smoke test: Slack access check.",
            unfurl_links=False,
            unfurl_media=False,
        )
        print("post_test: ok")
    except SlackApiError as exc:
        print("post_test:", exc.response.get("error"))
        if exc.response.get("error") == "channel_not_found":
            print("next_step: confirm the exact channel ID and invite @issuemanagement in that same channel")


if __name__ == "__main__":
    main()
