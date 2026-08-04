"""State helpers for weekly Linear review repeat suppression."""

import json
import os
from pathlib import Path


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
