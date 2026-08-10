#!/usr/bin/env python3
"""Check whether accessible Granola Daily-Standup notes cover weekdays."""

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from lib.granola import list_notes, safe_note_metadata


DEFAULT_OUT_DIR = "results/standup-coverage"


def main():
    args = parse_args()
    out_dir = Path(args.out_dir)
    prepare_out_dir(out_dir)

    tz = ZoneInfo(args.timezone)
    end_date = datetime.now(tz).date()
    start_date = end_date - timedelta(days=args.days)
    since_iso = (
        datetime.combine(start_date, time.min, tzinfo=tz)
        .astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )

    notes = list_notes(created_after=since_iso, page_size=args.page_size, max_pages=args.max_pages)
    standups = select_standups(notes, args.title_regex, tz)
    coverage = build_coverage(start_date, end_date, standups)

    payload = {
        "run": {
            "mode": "granola-standup-coverage",
            "timezone": args.timezone,
            "days": args.days,
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "titleRegex": args.title_regex,
            "granolaNotesFetched": len(notes),
        },
        "counts": {
            "standupNotes": len(standups),
            "expectedWeekdays": len(coverage["expectedWeekdays"]),
            "coveredWeekdays": len(coverage["coveredWeekdays"]),
            "missingWeekdays": len(coverage["missingWeekdays"]),
        },
        "coverage": coverage,
        "standups": standups,
    }

    (out_dir / "coverage.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (out_dir / "summary.md").write_text(render_summary(payload), encoding="utf-8")

    print(f"Fetched {len(notes)} accessible Granola notes.")
    print(f"Found {len(standups)} Daily-Standup notes.")
    print(f"Expected weekdays: {len(coverage['expectedWeekdays'])}")
    print(f"Covered weekdays: {len(coverage['coveredWeekdays'])}")
    print(f"Missing weekdays: {len(coverage['missingWeekdays'])}")
    print(f"Summary: {out_dir / 'summary.md'}")
    return 0


def parse_args():
    parser = argparse.ArgumentParser(description="Check Granola Daily-Standup weekday coverage.")
    parser.add_argument("--days", type=int, default=int(os.environ.get("STANDUP_COVERAGE_DAYS", "60")))
    parser.add_argument("--timezone", default=os.environ.get("STANDUP_COVERAGE_TIMEZONE", "Asia/Kolkata"))
    parser.add_argument("--page-size", type=int, default=int(os.environ.get("GRANOLA_PAGE_SIZE", "30")))
    parser.add_argument("--max-pages", type=int, default=int(os.environ.get("GRANOLA_MAX_PAGES", "10")))
    parser.add_argument(
        "--title-regex",
        default=os.environ.get("STANDUP_TITLE_REGEX", r"^Daily[- ]Stand[- ]?up$|^Daily-Standup$"),
    )
    parser.add_argument("--out-dir", default=os.environ.get("STANDUP_COVERAGE_OUT_DIR", DEFAULT_OUT_DIR))
    return parser.parse_args()


def prepare_out_dir(out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    for child in out_dir.iterdir():
        if child.is_file():
            child.unlink()
        elif child.is_dir():
            shutil.rmtree(child)


def select_standups(notes, title_regex, tz):
    pattern = re.compile(title_regex, re.IGNORECASE)
    selected = []
    for note in notes:
        title = (note.get("title") or "").strip()
        if not pattern.search(title):
            continue
        created_at = note.get("created_at") or note.get("createdAt")
        if not created_at:
            continue
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(tz)
        item = safe_note_metadata(note)
        item["local_date"] = created.date().isoformat()
        item["local_weekday"] = created.strftime("%A")
        item["local_created_at"] = created.isoformat()
        selected.append(item)
    selected.sort(key=lambda item: item["local_created_at"])
    return selected


def build_coverage(start_date, end_date, standups):
    by_date = {}
    for standup in standups:
        by_date.setdefault(standup["local_date"], []).append(standup)

    expected = []
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:
            expected.append(current.isoformat())
        current += timedelta(days=1)

    covered = [day for day in expected if day in by_date]
    missing = [day for day in expected if day not in by_date]
    return {
        "expectedWeekdays": expected,
        "coveredWeekdays": covered,
        "missingWeekdays": missing,
        "standupsByDate": by_date,
    }


def render_summary(payload):
    run = payload["run"]
    counts = payload["counts"]
    coverage = payload["coverage"]
    missing_lines = "\n".join(
        f"- {day} ({datetime.fromisoformat(day).strftime('%A')})" for day in coverage["missingWeekdays"]
    )
    covered_lines = "\n".join(
        f"- {day} ({datetime.fromisoformat(day).strftime('%A')})"
        for day in coverage["coveredWeekdays"]
    )
    if not missing_lines:
        missing_lines = "- None"
    if not covered_lines:
        covered_lines = "- None"
    return f"""# Daily-Standup Coverage

Range: `{run["startDate"]}` to `{run["endDate"]}`  
Timezone: `{run["timezone"]}`  
Title regex: `{run["titleRegex"]}`

## Counts

- Accessible Granola notes fetched: `{run["granolaNotesFetched"]}`
- Daily-Standup notes found: `{counts["standupNotes"]}`
- Expected weekdays: `{counts["expectedWeekdays"]}`
- Covered weekdays: `{counts["coveredWeekdays"]}`
- Missing weekdays: `{counts["missingWeekdays"]}`

## Missing Weekdays

{missing_lines}

## Covered Weekdays

{covered_lines}
"""


if __name__ == "__main__":
    sys.exit(main())
