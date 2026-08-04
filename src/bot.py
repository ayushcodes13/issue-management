import json
import os
import re
from pathlib import Path

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from slack_render import (
    render_examples,
    render_issue_improvement,
    render_owner_detail,
    render_team_themes,
)


app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


def latest_audit():
    path = Path(os.environ.get("AUDIT_JSON_PATH", "audit-output/audit.json"))
    return json.loads(path.read_text(encoding="utf-8"))


@app.event("app_mention")
def handle_app_mention(event, say):
    response = respond_to_prompt(event.get("text", ""))
    say(text=response, thread_ts=event.get("ts"))


@app.message(re.compile(r"^show me$", re.IGNORECASE))
def handle_show_me(message, say):
    say(
        text="I need Slack user-to-Linear owner mapping before `show me` can be exact. Try `show Devayush` for now.",
        thread_ts=message.get("ts"),
    )


@app.message(re.compile(r"^show (.+)$", re.IGNORECASE))
def handle_show_owner(message, context, say):
    audit = latest_audit()
    owner_name = context["matches"][0]
    say(text=render_owner_detail(audit.get("findings", []), owner_name), thread_ts=message.get("ts"))


@app.message(re.compile(r"^improve (BYN-\d+)$", re.IGNORECASE))
def handle_improve_issue(message, context, say):
    audit = latest_audit()
    issue_id = context["matches"][0]
    say(text=render_issue_improvement(audit.get("findings", []), issue_id), thread_ts=message.get("ts"))


@app.message(re.compile(r"^examples$", re.IGNORECASE))
def handle_examples(message, say):
    say(text=render_examples(), thread_ts=message.get("ts"))


@app.message(re.compile(r"^team themes$", re.IGNORECASE))
def handle_team_themes(message, say):
    audit = latest_audit()
    say(text=render_team_themes(audit.get("findings", [])), thread_ts=message.get("ts"))


@app.action("show_me")
def action_show_me(ack, body, client):
    ack()
    client.chat_postEphemeral(
        channel=body["channel"]["id"],
        user=body["user"]["id"],
        text="For now, use `show <name>` in the thread. User-to-Linear owner mapping is the next setup step.",
    )


@app.action("team_themes")
def action_team_themes(ack, body, client):
    ack()
    audit = latest_audit()
    client.chat_postMessage(
        channel=body["channel"]["id"],
        thread_ts=body["message"]["ts"],
        text=render_team_themes(audit.get("findings", [])),
    )


@app.action("examples")
def action_examples(ack, body, client):
    ack()
    client.chat_postMessage(
        channel=body["channel"]["id"],
        thread_ts=body["message"]["ts"],
        text=render_examples(),
    )


def respond_to_prompt(text):
    audit = latest_audit()

    improve_match = re.search(r"improve\s+(BYN-\d+)", text, re.IGNORECASE)
    if improve_match:
        return render_issue_improvement(audit.get("findings", []), improve_match.group(1))

    show_match = re.search(r"show\s+([a-zA-Z ]+)", text, re.IGNORECASE)
    if show_match:
        return render_owner_detail(audit.get("findings", []), show_match.group(1).strip())

    if re.search(r"examples", text, re.IGNORECASE):
        return render_examples()

    if re.search(r"team themes", text, re.IGNORECASE):
        return render_team_themes(audit.get("findings", []))

    return "Try: `show Devayush`, `improve BYN-67`, `examples`, or `team themes`."


if __name__ == "__main__":
    app_token = os.environ.get("SLACK_APP_TOKEN")
    if not app_token:
        raise RuntimeError("SLACK_APP_TOKEN is required to run the Socket Mode bot")
    SocketModeHandler(app, app_token).start()
