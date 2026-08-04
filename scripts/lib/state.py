"""State helpers for weekly Linear review repeat suppression."""

import json
import os
from pathlib import Path
from datetime import datetime, timezone


DEFAULT_STATE_PATH = "state/history.json"


def state_path():
    return Path(os.environ.get("AUDIT_STATE_PATH", DEFAULT_STATE_PATH))


def load_history():
    path = state_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def already_sent(history, issue_id, category, recipient):
    item = history.get(issue_id, {}).get(category)
    return bool(item and item.get("sent_to") == recipient)


def mark_sent(history, issue_id, category, recipient, sent_at=None):
    if not issue_id or not category or not recipient:
        return
    sent_at = sent_at or datetime.now(timezone.utc).isoformat()
    history.setdefault(issue_id, {})[category] = {
        "sent_to": recipient,
        "sent_at": sent_at,
    }


def save_history(history):
    path = state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(history, indent=2, sort_keys=True) + "\n", encoding="utf-8")
