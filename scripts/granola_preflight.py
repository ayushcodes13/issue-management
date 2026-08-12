#!/usr/bin/env python3
"""Print Granola note metadata visible to the configured API key.

This deliberately prints titles and timestamps only. It does not fetch or print
transcripts. It is meant for GitHub Actions/debug preflight so failures are easy
to understand before the expensive Linear/Azure steps run.
"""

import argparse
import os
import re
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from lib.granola import list_notes


DEFAULT_TITLE_REGEX = r"^Daily[- ]Stand[- ]?up$|^Daily-Standup$"


def main():
    args = parse_args()
    tz = ZoneInfo(args.timezone)
    target_date = parse_target_date(args.date, tz)
    created_after = (
        datetime.combine(target_date - timedelta(days=args.days - 1), time.min, tzinfo=tz)
        .astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )

    notes = list_notes(created_after=created_after, page_size=args.page_size, max_pages=args.max_pages)
    pattern = re.compile(args.title_regex, re.IGNORECASE)
    matches = [note for note in notes if is_target_standup(note, target_date, tz, pattern)]

    print("Granola metadata preflight")
    print(f"target_date={target_date.isoformat()}")
    print(f"created_after={created_after}")
    print(f"notes_visible={len(notes)}")
    print(f"matching_daily_standups={len(matches)}")
    print("")
    print("Visible note titles:")
    for note in notes[: args.limit]:
        print(f"- {local_created_at(note, tz)} | {(note.get('title') or 'Untitled').strip()}")
    if len(notes) > args.limit:
        print(f"- ...and {len(notes) - args.limit} more")

    if not matches:
        print("")
        print("No matching Daily-Standup note is visible to this Granola API key for the target date.")
        print("If a standup exists in Granola, check the API key workspace/access or the title/date filter.")


def parse_args():
    parser = argparse.ArgumentParser(description="List accessible Granola note metadata for debug preflight.")
    parser.add_argument("--date", default=os.environ.get("DAILY_STANDUP_DATE", "today"))
    parser.add_argument("--timezone", default=os.environ.get("DAILY_STANDUP_TIMEZONE", "Asia/Kolkata"))
    parser.add_argument("--days", type=int, default=int(os.environ.get("GRANOLA_PREFLIGHT_DAYS", "3")))
    parser.add_argument("--page-size", type=int, default=int(os.environ.get("GRANOLA_PAGE_SIZE", "30")))
    parser.add_argument("--max-pages", type=int, default=int(os.environ.get("GRANOLA_MAX_PAGES", "10")))
    parser.add_argument("--limit", type=int, default=int(os.environ.get("GRANOLA_PREFLIGHT_LIMIT", "20")))
    parser.add_argument("--title-regex", default=os.environ.get("DAILY_STANDUP_TITLE_REGEX", DEFAULT_TITLE_REGEX))
    return parser.parse_args()


def parse_target_date(value, tz):
    if value == "today":
        return datetime.now(tz).date()
    return datetime.fromisoformat(value).date()


def is_target_standup(note, target_date, tz, pattern):
    title = (note.get("title") or "").strip()
    if not pattern.search(title):
        return False
    created_at = note.get("created_at") or note.get("createdAt")
    if not created_at:
        return False
    created = datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(tz)
    return created.date() == target_date


def local_created_at(note, tz):
    created_at = note.get("created_at") or note.get("createdAt") or ""
    if not created_at:
        return "unknown-time"
    try:
        return datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(tz).strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return created_at


if __name__ == "__main__":
    raise SystemExit(main())
