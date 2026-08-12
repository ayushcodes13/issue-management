#!/usr/bin/env python3
"""Daily Standup to Linear draft proposal runner.

Read-only:
- fetches today's single Daily-Standup note from Granola
- waits for it to exist and stabilize before reading transcript content
- fetches active Linear issues
- writes draft proposals locally
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time as time_module
from collections import Counter
from datetime import datetime, time, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from lib.granola import get_note, list_notes, note_payload_for_ai, safe_note_metadata
from lib.linear import fetch_active_issues, status_of
from lib.work_memory_ai import generate_work_memory_proposals
from work_memory_api import normalize_proposals, render_report, render_summary, safe_issue_metadata


DEFAULT_OUT_DIR = "results/daily-standup-memory"
DEFAULT_TITLE_REGEX = r"^Daily[- ]Stand[- ]?up$|^Daily-Standup$"
DEFAULT_MAX_TRANSCRIPT_CHARS = 60000
DEFAULT_MIN_TRANSCRIPT_CHARS = 1000
DEFAULT_POLL_SECONDS = 60
DEFAULT_STABLE_SECONDS = 900


def main():
    args = parse_args()
    out_dir = Path(args.out_dir)
    prepare_out_dir(out_dir)

    tz = ZoneInfo(args.timezone)
    target_date = parse_target_date(args.date, tz)
    start_utc = (
        datetime.combine(target_date, time.min, tzinfo=tz)
        .astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )

    print(f"Looking for exactly one Daily-Standup on {target_date.isoformat()} ({args.timezone})...")
    selected = wait_for_standup(args, start_utc, target_date, tz)
    print(f"Selected standup: {selected.get('title')} ({selected.get('created_at')})")

    detailed_note = wait_for_stable_detail(selected["id"], args)
    print("Fetched stable standup detail with transcript.")

    print("Fetching active Linear issues...")
    issues = fetch_active_issues()
    print(f"Fetched {len(issues)} active Linear issues.")

    note_payloads = [
        note_payload_for_ai(
            detailed_note,
            include_transcript=True,
            max_transcript_chars=args.max_transcript_chars,
        )
    ]
    print("Generating standup-to-Linear draft proposals with Azure OpenAI...")
    analysis = generate_work_memory_proposals(note_payloads, issues, start_utc, 1)
    proposals = normalize_proposals(analysis.get("proposals") or [])
    analysis["proposals"] = proposals

    write_outputs(out_dir, args, start_utc, target_date, selected, detailed_note, issues, analysis)

    print(f"Wrote Daily Standup results to {out_dir}")
    print(f"Draft proposals: {len(proposals)}")
    return 0


def parse_args():
    parser = argparse.ArgumentParser(description="Process exactly one Granola Daily-Standup note for a target date.")
    parser.add_argument("--date", default=os.environ.get("DAILY_STANDUP_DATE", "today"))
    parser.add_argument("--timezone", default=os.environ.get("DAILY_STANDUP_TIMEZONE", "Asia/Kolkata"))
    parser.add_argument("--title-regex", default=os.environ.get("DAILY_STANDUP_TITLE_REGEX", DEFAULT_TITLE_REGEX))
    parser.add_argument("--page-size", type=int, default=int(os.environ.get("GRANOLA_PAGE_SIZE", "30")))
    parser.add_argument("--max-pages", type=int, default=int(os.environ.get("GRANOLA_MAX_PAGES", "10")))
    parser.add_argument(
        "--poll-seconds",
        type=int,
        default=int(os.environ.get("DAILY_STANDUP_POLL_SECONDS", str(DEFAULT_POLL_SECONDS))),
    )
    parser.add_argument(
        "--max-wait-seconds",
        type=int,
        default=int(os.environ.get("DAILY_STANDUP_MAX_WAIT_SECONDS", "14400")),
        help="How long to wait for today's standup to appear.",
    )
    parser.add_argument(
        "--stable-seconds",
        type=int,
        default=int(os.environ.get("DAILY_STANDUP_STABLE_SECONDS", str(DEFAULT_STABLE_SECONDS))),
        help="How long the note signature must remain unchanged before processing.",
    )
    parser.add_argument("--out-dir", default=os.environ.get("DAILY_STANDUP_OUT_DIR", DEFAULT_OUT_DIR))
    parser.add_argument(
        "--max-transcript-chars",
        type=int,
        default=int(os.environ.get("DAILY_STANDUP_MAX_TRANSCRIPT_CHARS", str(DEFAULT_MAX_TRANSCRIPT_CHARS))),
        help="Maximum transcript characters to send to the AI review.",
    )
    parser.add_argument(
        "--min-transcript-chars",
        type=int,
        default=int(os.environ.get("DAILY_STANDUP_MIN_TRANSCRIPT_CHARS", str(DEFAULT_MIN_TRANSCRIPT_CHARS))),
        help="Minimum transcript text required before the standup can be treated as ready.",
    )
    return parser.parse_args()


def parse_target_date(value, tz):
    if value == "today":
        return datetime.now(tz).date()
    return datetime.fromisoformat(value).date()


def prepare_out_dir(out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    for child in out_dir.iterdir():
        if child.is_file():
            child.unlink()
        elif child.is_dir():
            shutil.rmtree(child)


def wait_for_standup(args, start_utc, target_date, tz):
    deadline = time_module.monotonic() + args.max_wait_seconds
    last_candidates = []
    while True:
        notes = list_notes(created_after=start_utc, page_size=args.page_size, max_pages=args.max_pages)
        candidates = filter_standups(notes, target_date, tz, args.title_regex)
        if candidates:
            if len(candidates) > 1:
                print(f"WARNING: found {len(candidates)} standups for {target_date}; using the latest note.", file=sys.stderr)
            return candidates[-1]
        last_candidates = candidates
        if time_module.monotonic() >= deadline:
            raise RuntimeError(
                f"No Daily-Standup note found for {target_date.isoformat()} after waiting "
                f"{args.max_wait_seconds} seconds. Last candidate count: {len(last_candidates)}"
            )
        print(f"No Daily-Standup found yet for {target_date}; sleeping {args.poll_seconds}s...")
        time_module.sleep(args.poll_seconds)


def filter_standups(notes, target_date, tz, title_regex):
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
        if created.date() != target_date:
            continue
        item = dict(note)
        item["_local_created_at"] = created.isoformat()
        selected.append(item)
    selected.sort(key=lambda note: note["_local_created_at"])
    return selected


def wait_for_stable_detail(note_id, args):
    detail = get_note(note_id, include_transcript=True)
    if args.stable_seconds <= 0 and transcript_ready(detail, args):
        return detail

    stable_since = time_module.monotonic()
    previous_signature = note_signature(detail)
    deadline = time_module.monotonic() + args.max_wait_seconds

    while True:
        sleep_for = min(args.poll_seconds, max(args.stable_seconds, 1))
        time_module.sleep(sleep_for)
        current = get_note(note_id, include_transcript=True)
        current_signature = note_signature(current)
        if current_signature != previous_signature:
            previous_signature = current_signature
            stable_since = time_module.monotonic()
            print("Standup note changed; restarting stability timer.")
        elif time_module.monotonic() - stable_since >= args.stable_seconds and transcript_ready(current, args):
            return current
        elif time_module.monotonic() - stable_since >= args.stable_seconds:
            print(
                "Standup note is stable but transcript is still below the minimum "
                f"({transcript_char_count(current)}/{args.min_transcript_chars} chars); continuing to wait."
            )

        if time_module.monotonic() >= deadline:
            if not transcript_ready(current, args):
                raise RuntimeError(
                    "Daily-Standup transcript did not reach the minimum size before timeout "
                    f"({transcript_char_count(current)}/{args.min_transcript_chars} chars)."
                )
            print("WARNING: stability wait timed out; using latest fetched note detail.", file=sys.stderr)
            return current


def transcript_ready(note, args):
    return transcript_char_count(note) >= args.min_transcript_chars


def transcript_char_count(note):
    transcript = note.get("transcript") or []
    if not isinstance(transcript, list):
        return 0
    total = 0
    for entry in transcript:
        if not isinstance(entry, dict):
            continue
        total += len(entry.get("text") or entry.get("content") or entry.get("utterance") or "")
    return total


def note_signature(note):
    transcript = note.get("transcript") or []
    return {
        "transcript_entries": len(transcript) if isinstance(transcript, list) else 0,
        "transcript_chars": transcript_char_count(note),
        "transcript_digest": transcript_digest(transcript),
        "last_transcript_text": last_transcript_text(transcript),
    }


def transcript_digest(transcript):
    if not isinstance(transcript, list):
        return ""
    digest = hashlib.sha256()
    for entry in transcript:
        if not isinstance(entry, dict):
            continue
        speaker = speaker_for_digest(entry.get("speaker"))
        text = entry.get("text") or entry.get("content") or entry.get("utterance") or ""
        start = entry.get("start_time") or entry.get("startTime") or ""
        digest.update(f"{speaker}\t{start}\t{text}\n".encode("utf-8", errors="replace"))
    return digest.hexdigest()


def speaker_for_digest(speaker):
    if isinstance(speaker, str):
        return speaker
    if isinstance(speaker, dict):
        return speaker.get("name") or speaker.get("email") or speaker.get("attribution") or speaker.get("source") or ""
    return ""


def last_transcript_text(transcript):
    if not isinstance(transcript, list) or not transcript:
        return ""
    last = transcript[-1]
    if not isinstance(last, dict):
        return ""
    return (last.get("text") or last.get("content") or "")[-200:]


def write_outputs(out_dir, args, since_iso, target_date, selected, detailed_note, issues, analysis):
    proposals = analysis.get("proposals") or []
    payload = {
        "run": {
            "mode": "daily-standup-read-only",
            "targetDate": target_date.isoformat(),
            "since": since_iso,
            "meetingLimit": 1,
            "includeTranscript": True,
            "source": analysis.get("source"),
        },
        "counts": {
            "granolaNotesListed": 1,
            "granolaNotesSelected": 1,
            "granolaNotesInspected": 1,
            "linearIssuesReviewed": len(issues),
            "proposals": len(proposals),
        },
        "tokenUsage": analysis.get("tokenUsage") or {},
        "proposals": proposals,
        "filterReport": {
            "inputNotes": "today-only lookup",
            "selectedNotes": 1,
            "excludedCounts": {},
            "activeFilters": {
                "targetDate": target_date.isoformat(),
                "titleRegex": args.title_regex,
            },
        },
        "limitations": analysis.get("limitations") or [],
    }
    raw_index = build_daily_raw_index(since_iso, target_date, selected, detailed_note, issues, proposals, args)
    dm_drafts = build_dm_drafts(proposals, target_date)

    (out_dir / "summary.md").write_text(render_summary(payload, analysis), encoding="utf-8")
    (out_dir / "report.md").write_text(render_report(payload, raw_index, analysis), encoding="utf-8")
    (out_dir / "proposals.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (out_dir / "raw-index.json").write_text(json.dumps(raw_index, indent=2) + "\n", encoding="utf-8")
    (out_dir / "dm-drafts.json").write_text(json.dumps(dm_drafts, indent=2) + "\n", encoding="utf-8")
    write_dm_markdown(out_dir / "dms", dm_drafts)


def build_daily_raw_index(since_iso, target_date, selected, detailed_note, issues, proposals, args):
    referenced_ids = {
        (proposal.get("targetLinearIssue") or {}).get("identifier")
        for proposal in proposals
        if (proposal.get("targetLinearIssue") or {}).get("identifier")
    }
    referenced_issues = [safe_issue_metadata(issue) for issue in issues if issue.get("identifier") in referenced_ids]
    return {
        "run": {
            "mode": "daily-standup-read-only",
            "since": since_iso,
            "targetDate": target_date.isoformat(),
            "meetingLimit": 1,
            "includeTranscript": True,
            "stableSeconds": args.stable_seconds,
            "minTranscriptChars": args.min_transcript_chars,
            "maxTranscriptChars": args.max_transcript_chars,
        },
        "granola": {
            "selectedStandup": safe_note_metadata(selected),
            "notesInspected": [safe_note_metadata(detailed_note)],
            "transcriptEntries": len(detailed_note.get("transcript") or []),
        },
        "linear": {
            "activeIssueCountsByStatus": dict(Counter(status_of(issue) for issue in issues)),
            "issuesReferencedByProposals": referenced_issues,
        },
    }


def build_dm_drafts(proposals, target_date):
    by_owner = {}
    for proposal in proposals:
        if not should_include_in_dm(proposal):
            continue
        owner = proposal.get("owner") or "Unassigned"
        if owner == "Unassigned":
            continue
        by_owner.setdefault(owner, []).append(proposal)

    drafts = []
    for owner, items in sorted(by_owner.items()):
        text = render_dm_text(owner, items, target_date)
        drafts.append(
            {
                "recipient": owner,
                "kind": "daily_standup_memory",
                "targetDate": target_date.isoformat(),
                "itemCount": len(items),
                "items": [dm_item(item) for item in items],
                "text": text,
            }
        )
    return drafts


def should_include_in_dm(proposal):
    todo = (mentioned_todo(proposal) or "").strip().lower()
    if not todo:
        return False
    no_action_prefixes = (
        "no new follow-up",
        "no follow-up",
        "no linear follow-up",
    )
    return not todo.startswith(no_action_prefixes)


def dm_item(proposal):
    target = proposal.get("targetLinearIssue") or {}
    change = proposal.get("proposedLinearChange") or {}
    return {
        "proposalId": proposal.get("id") or "",
        "category": proposal.get("category") or "",
        "confidence": proposal.get("confidence") or "",
        "mentionedTodo": proposal.get("mentionedTodo") or "",
        "workingOn": proposal.get("workingOn") or "",
        "targetIssueId": target.get("identifier") or "",
        "targetIssueTitle": target.get("title") or "",
        "targetIssueUrl": target.get("url") or "",
        "proposedAction": change.get("action") or "none",
        "evidenceSummary": proposal.get("evidenceSummary") or "",
        "suggestedSlackMessage": proposal.get("suggestedSlackMessage") or "",
        "draftText": change.get("draftText") or "",
    }


def render_dm_text(owner, proposals, target_date):
    lines = [
        f"Hi {owner},",
        "",
        "Here are suggested todos from today's standup:",
        "",
    ]
    lines.extend(bullets(todo_with_linear_follow_up(proposal) for proposal in proposals))
    lines.append("")

    lines.extend(
        [
            "Please take 5 minutes to keep Linear clean and up to date today.",
            "",
            "This is generated by AI. Sorry if something was missed or not relevant.",
            "",
            "Thank you for reading.",
            "",
            f"Date: {target_date.isoformat()}",
        ]
    )
    return "\n".join(lines).rstrip()


def bullets(items):
    values = [item for item in items if item]
    if not values:
        return ["- Nothing specific."]
    return [f"- {item}" for item in values]


def mentioned_todo(proposal):
    return proposal.get("mentionedTodo") or proposal.get("evidenceSummary") or ""


def working_on(proposal):
    return proposal.get("workingOn") or ""


def todo_with_linear_follow_up(proposal):
    todo = sentence(mentioned_todo(proposal))
    follow_up = short_linear_follow_up(proposal)
    if not todo:
        return ""
    return f"{todo} Linear: {follow_up}"


def short_linear_follow_up(proposal):
    category = proposal.get("category") or ""
    target = proposal.get("targetLinearIssue") or {}
    issue = target_issue_id(target)

    if category == "add_context_to_existing_issue" and issue:
        return f"tracked in {issue}; add context if useful."
    if category == "create_new_linear_issue":
        return "possible new issue."
    if category == "already_in_linear" and issue:
        return f"already tracked in {issue}."
    if category == "not_linear_worthy":
        return "no update needed."
    if category == "needs_human_review":
        return "needs quick human review."
    if issue:
        return f"review {issue}."
    return "review if this should be tracked."


def sentence(value):
    text = (value or "").strip()
    if not text:
        return ""
    text = text[0].upper() + text[1:]
    if text[-1] in ".!?":
        return text
    return f"{text}."


def target_issue_id(target):
    return target.get("identifier") or ""


def target_issue_label(target):
    issue_id = target.get("identifier")
    title = target.get("title")
    url = target.get("url")
    if issue_id and title and url:
        return f"{issue_id} - {title} ({url})"
    if issue_id and title:
        return f"{issue_id} - {title}"
    if issue_id and url:
        return f"{issue_id} ({url})"
    return issue_id or title or ""


def write_dm_markdown(out_dir, drafts):
    out_dir.mkdir(parents=True, exist_ok=True)
    for child in out_dir.iterdir():
        if child.is_file():
            child.unlink()
    for draft in drafts:
        slug = slugify(draft["recipient"])
        (out_dir / f"{slug}.md").write_text(draft["text"] + "\n", encoding="utf-8")


def slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "unknown"


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
