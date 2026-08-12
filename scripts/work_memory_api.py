#!/usr/bin/env python3
"""Manual API-based Work Memory runner.

This does not use Codex CLI or MCP. It uses Granola API, Linear GraphQL API,
and Azure OpenAI to write draft proposal artifacts under results/work-memory.
"""

import argparse
import json
import os
import re
import shutil
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from lib.granola import get_note, list_notes, note_payload_for_ai, safe_note_metadata
from lib.linear import fetch_active_issues, owner_of, status_of
from lib.work_memory_ai import generate_work_memory_proposals


DEFAULT_OUT_DIR = "results/work-memory"


def main():
    args = parse_args()
    out_dir = Path(args.out_dir)
    prepare_out_dir(out_dir)

    since = datetime.now(timezone.utc) - timedelta(days=args.days)
    since_iso = since.replace(microsecond=0).isoformat().replace("+00:00", "Z")

    print(f"Fetching Granola notes since {since_iso}...")
    note_index = fetch_granola_note_index(args, since_iso)
    print(f"Fetched {len(note_index)} Granola note metadata rows.")

    filtered_notes, filter_report = filter_note_index(note_index, args)
    print(f"Selected {len(filtered_notes)} Granola note metadata rows after relevance filters.")

    detailed_notes = []
    for item in filtered_notes[: args.meeting_limit]:
        note_id = item.get("id")
        if not note_id:
            continue
        detailed_notes.append(get_note(note_id, include_transcript=args.include_transcript))
    print(f"Fetched {len(detailed_notes)} Granola note detail rows.")

    print("Fetching active Linear issues...")
    issues = fetch_active_issues()
    print(f"Fetched {len(issues)} active Linear issues.")

    note_payloads = [note_payload_for_ai(note, include_transcript=args.include_transcript) for note in detailed_notes]
    print("Generating work-memory proposals with Azure OpenAI...")
    analysis = generate_work_memory_proposals(note_payloads, issues, since_iso, args.meeting_limit)
    proposals = normalize_proposals(analysis.get("proposals") or [])
    analysis["proposals"] = proposals

    write_outputs(out_dir, since_iso, note_index, filtered_notes, detailed_notes, issues, analysis, args, filter_report)

    print(f"Wrote Work Memory API results to {out_dir}")
    print(f"Draft proposals: {len(proposals)}")
    return 0


def parse_args():
    parser = argparse.ArgumentParser(description="Run API-based Granola-to-Linear work-memory proposal generation.")
    parser.add_argument("--days", type=int, default=int(os.environ.get("WORK_MEMORY_DAYS", "7")))
    parser.add_argument("--meeting-limit", type=int, default=int(os.environ.get("WORK_MEMORY_MEETING_LIMIT", "20")))
    parser.add_argument("--page-size", type=int, default=int(os.environ.get("GRANOLA_PAGE_SIZE", "30")))
    parser.add_argument("--max-pages", type=int, default=int(os.environ.get("GRANOLA_MAX_PAGES", "10")))
    parser.add_argument("--folder-id", default=os.environ.get("GRANOLA_FOLDER_ID", ""))
    parser.add_argument("--folder-ids", default=os.environ.get("GRANOLA_FOLDER_IDS", ""))
    parser.add_argument("--title-include-regex", default=os.environ.get("GRANOLA_TITLE_INCLUDE_REGEX", ""))
    parser.add_argument("--title-exclude-regex", default=os.environ.get("GRANOLA_TITLE_EXCLUDE_REGEX", ""))
    parser.add_argument("--attendee-email-domain", default=os.environ.get("GRANOLA_ATTENDEE_EMAIL_DOMAIN", ""))
    parser.add_argument("--owner-email", default=os.environ.get("GRANOLA_OWNER_EMAIL", ""))
    parser.add_argument("--out-dir", default=os.environ.get("WORK_MEMORY_OUT_DIR", DEFAULT_OUT_DIR))
    parser.add_argument(
        "--include-transcript",
        action="store_true",
        default=os.environ.get("WORK_MEMORY_INCLUDE_TRANSCRIPT", "").lower() in {"1", "true", "yes"},
        help="Fetch and include capped transcript text in the AI review payload.",
    )
    return parser.parse_args()


def prepare_out_dir(out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    for child in out_dir.iterdir():
        if child.is_file():
            child.unlink()
        elif child.is_dir():
            shutil.rmtree(child)


def fetch_granola_note_index(args, since_iso):
    folder_ids = split_csv(args.folder_ids)
    if args.folder_id:
        folder_ids.append(args.folder_id)
    folder_ids = list(dict.fromkeys(folder_ids))

    if not folder_ids:
        return list_notes(
            created_after=since_iso,
            page_size=args.page_size,
            max_pages=args.max_pages,
        )

    by_id = {}
    for folder_id in folder_ids:
        for note in list_notes(
            created_after=since_iso,
            page_size=args.page_size,
            max_pages=args.max_pages,
            folder_id=folder_id,
        ):
            note_id = note.get("id") or json.dumps(note, sort_keys=True)
            by_id[note_id] = note
    return list(by_id.values())


def normalize_proposals(proposals):
    normalized = []
    for index, proposal in enumerate(proposals, start=1):
        item = dict(proposal)
        item.setdefault("id", f"work-memory-{index:03d}")
        item.setdefault("category", "needs_human_review")
        item.setdefault("confidence", "medium")
        item.setdefault("owner", "Unassigned")
        item.setdefault("sourceMeetingIds", [])
        item.setdefault("sourceMeetingTitles", [])
        item.setdefault("mentionedTodo", "")
        item.setdefault("workingOn", "")
        item.setdefault("targetLinearIssue", {"identifier": "", "title": "", "url": ""})
        item.setdefault("evidenceSummary", "")
        item.setdefault("rationale", "")
        item.setdefault("suggestedSlackMessage", "")
        item.setdefault("proposedLinearChange", {"action": "none", "draftText": ""})
        item["requiresApproval"] = True
        item["status"] = "draft"
        normalized.append(item)
    return normalized


def filter_note_index(note_index, args):
    include_re = compile_optional_regex(args.title_include_regex)
    exclude_re = compile_optional_regex(args.title_exclude_regex)
    attendee_domain = (args.attendee_email_domain or "").strip().lower().lstrip("@")
    owner_email = (args.owner_email or "").strip().lower()

    selected = []
    excluded = Counter()

    for note in note_index:
        title = note.get("title") or ""
        if include_re and not include_re.search(title):
            excluded["title_include_regex"] += 1
            continue
        if exclude_re and exclude_re.search(title):
            excluded["title_exclude_regex"] += 1
            continue
        if attendee_domain and not note_has_attendee_domain(note, attendee_domain):
            excluded["attendee_email_domain"] += 1
            continue
        if owner_email and not note_owner_matches(note, owner_email):
            excluded["owner_email"] += 1
            continue
        selected.append(note)

    return selected, {
        "inputNotes": len(note_index),
        "selectedNotes": len(selected),
        "excludedCounts": dict(excluded),
        "activeFilters": {
            "folderId": args.folder_id,
            "folderIds": split_csv(args.folder_ids),
            "titleIncludeRegex": args.title_include_regex,
            "titleExcludeRegex": args.title_exclude_regex,
            "attendeeEmailDomain": args.attendee_email_domain,
            "ownerEmail": args.owner_email,
        },
    }


def compile_optional_regex(pattern):
    if not pattern:
        return None
    return re.compile(pattern, re.IGNORECASE)


def note_has_attendee_domain(note, domain):
    for attendee in note.get("attendees") or []:
        email = (attendee.get("email") or "").lower()
        if email.endswith(f"@{domain}") or email.endswith(domain):
            return True
    calendar = note.get("calendar_event") or {}
    for invitee in calendar.get("invitees") or []:
        email = (invitee.get("email") or invitee.get("email_address") or "").lower()
        if email.endswith(f"@{domain}") or email.endswith(domain):
            return True
    return False


def note_owner_matches(note, email):
    owner = note.get("owner") or {}
    return (owner.get("email") or "").lower() == email


def split_csv(value):
    return [item.strip() for item in (value or "").split(",") if item.strip()]


def write_outputs(out_dir, since_iso, note_index, filtered_notes, detailed_notes, issues, analysis, args, filter_report):
    proposals = analysis.get("proposals") or []
    raw_index = build_raw_index(since_iso, note_index, detailed_notes, issues, proposals, args)
    proposals_payload = {
        "run": {
            "mode": "api-read-only",
            "since": since_iso,
            "days": args.days,
            "meetingLimit": args.meeting_limit,
            "includeTranscript": args.include_transcript,
            "source": analysis.get("source"),
        },
        "counts": {
            "granolaNotesListed": len(note_index),
            "granolaNotesSelected": len(filtered_notes),
            "granolaNotesInspected": len(detailed_notes),
            "linearIssuesReviewed": len(issues),
            "proposals": len(proposals),
        },
        "tokenUsage": analysis.get("tokenUsage") or {},
        "proposals": proposals,
        "filterReport": filter_report,
        "limitations": analysis.get("limitations") or [],
    }

    (out_dir / "summary.md").write_text(render_summary(proposals_payload, analysis), encoding="utf-8")
    (out_dir / "report.md").write_text(render_report(proposals_payload, raw_index, analysis), encoding="utf-8")
    (out_dir / "proposals.json").write_text(json.dumps(proposals_payload, indent=2) + "\n", encoding="utf-8")
    (out_dir / "raw-index.json").write_text(json.dumps(raw_index, indent=2) + "\n", encoding="utf-8")


def build_raw_index(since_iso, note_index, detailed_notes, issues, proposals, args):
    referenced_ids = {
        (proposal.get("targetLinearIssue") or {}).get("identifier")
        for proposal in proposals
        if (proposal.get("targetLinearIssue") or {}).get("identifier")
    }
    referenced_issues = [safe_issue_metadata(issue) for issue in issues if issue.get("identifier") in referenced_ids]
    additional = []
    for issue in issues:
        if issue.get("identifier") in referenced_ids:
            continue
        additional.append(safe_issue_metadata(issue))
        if len(additional) >= 20:
            break
    return {
        "run": {
            "mode": "api-read-only",
            "since": since_iso,
            "days": args.days,
            "meetingLimit": args.meeting_limit,
            "folderId": args.folder_id,
            "includeTranscript": args.include_transcript,
        },
        "granola": {
            "notesListed": len(note_index),
            "notesInspectedCount": len(detailed_notes),
            "filterReport": build_raw_filter_report(args),
            "notesInspected": [safe_note_metadata(note) for note in detailed_notes],
            "listedNoteSample": [safe_note_metadata(note) for note in note_index[:20]],
        },
        "linear": {
            "activeIssueCountsByStatus": dict(Counter(status_of(issue) for issue in issues)),
            "issuesReferencedByProposals": referenced_issues,
            "additionalActiveIssues": additional,
        },
    }


def safe_issue_metadata(issue):
    return {
        "identifier": issue.get("identifier") or "",
        "title": issue.get("title") or "",
        "status": status_of(issue),
        "owner": owner_of(issue),
        "url": issue.get("url") or "",
        "project": (issue.get("project") or {}).get("name") or "",
    }


def render_summary(payload, analysis):
    counts = payload["counts"]
    lines = [
        "# Work Memory API Draft",
        "",
        "Read-only scheduled-path run completed with Granola API, Linear API, and Azure OpenAI.",
        "",
        f"- Granola notes listed: {counts['granolaNotesListed']}",
        f"- Granola notes selected after filters: {counts['granolaNotesSelected']}",
        f"- Granola notes inspected: {counts['granolaNotesInspected']}",
        f"- Active Linear issues reviewed: {counts['linearIssuesReviewed']}",
        f"- Draft proposals: {counts['proposals']}",
        "",
    ]
    themes = (analysis.get("runSummary") or {}).get("mainThemes") or []
    if themes:
        lines.append("Main themes:")
        lines.extend(f"- {theme}" for theme in themes[:5])
        lines.append("")
    if payload["proposals"]:
        lines.append("Top proposal reviews:")
        for proposal in payload["proposals"][:7]:
            target = proposal.get("targetLinearIssue") or {}
            issue_id = target.get("identifier") or "no target"
            lines.append(f"- `{proposal.get('category')}` / {issue_id}: {proposal.get('evidenceSummary')}")
        lines.append("")
    token_usage = payload.get("tokenUsage") or {}
    estimated = token_usage.get("estimatedBreakdown") or {}
    provider = token_usage.get("providerUsage") or {}
    if estimated:
        lines.append("Token estimate:")
        for key in ("granola", "linear", "sop", "promptInstructionsAndTemplate", "fullPrompt", "output"):
            item = estimated.get(key) or {}
            lines.append(f"- {key}: ~{item.get('approxTokens', 0)} tokens ({item.get('chars', 0)} chars)")
        if provider:
            lines.append(f"- provider usage: {json.dumps(provider, sort_keys=True)}")
        lines.append("")
    lines.append("No Slack messages were sent and no Linear changes were made.")
    return "\n".join(lines).rstrip() + "\n"


def render_report(payload, raw_index, analysis):
    lines = [
        "# Work Memory API Report",
        "",
        f"Mode: `{payload['run']['mode']}`",
        f"Since: `{payload['run']['since']}`",
        f"Analysis source: `{payload['run'].get('source')}`",
        "",
        "This is the schedulable production path. It does not depend on Codex CLI or MCP OAuth.",
        "",
        "## Counts",
        "",
        f"- Granola notes listed: {payload['counts']['granolaNotesListed']}",
        f"- Granola notes selected after filters: {payload['counts']['granolaNotesSelected']}",
        f"- Granola notes inspected: {payload['counts']['granolaNotesInspected']}",
        f"- Active Linear issues reviewed: {payload['counts']['linearIssuesReviewed']}",
        f"- Draft proposals: {payload['counts']['proposals']}",
        "",
        "## Linear Status Mix",
        "",
    ]
    status_counts = raw_index["linear"]["activeIssueCountsByStatus"]
    lines.extend(f"- {status}: {count}" for status, count in sorted(status_counts.items()))
    lines.extend(["", "## Proposal Categories", ""])
    categories = Counter(proposal.get("category") for proposal in payload["proposals"])
    if categories:
        lines.extend(f"- {category}: {count}" for category, count in sorted(categories.items()))
    else:
        lines.append("- No proposals generated.")
    limitations = payload.get("limitations") or []
    filter_report = payload.get("filterReport") or {}
    lines.extend(["", "## Relevance Filters", ""])
    lines.append("Only selected notes are fetched in detail and sent to Azure OpenAI.")
    lines.append("")
    lines.append(f"- Input notes: {filter_report.get('inputNotes', 0)}")
    lines.append(f"- Selected notes: {filter_report.get('selectedNotes', 0)}")
    active = filter_report.get("activeFilters") or {}
    active_lines = [f"{key}={value}" for key, value in active.items() if value]
    if active_lines:
        lines.append(f"- Active filters: {', '.join(active_lines)}")
    else:
        lines.append("- Active filters: none")
    excluded = filter_report.get("excludedCounts") or {}
    if excluded:
        lines.append(f"- Excluded counts: {json.dumps(excluded, sort_keys=True)}")
    if limitations:
        lines.extend(["", "## Limitations", ""])
        lines.extend(f"- {item}" for item in limitations)
    token_usage = payload.get("tokenUsage") or {}
    estimated = token_usage.get("estimatedBreakdown") or {}
    provider = token_usage.get("providerUsage") or {}
    if estimated:
        lines.extend(["", "## Token Usage", ""])
        lines.append(token_usage.get("estimateMethod") or "Approximate token estimate.")
        lines.append("")
        for key in ("granola", "linear", "sop", "promptInstructionsAndTemplate", "fullPrompt", "output"):
            item = estimated.get(key) or {}
            lines.append(f"- {key}: ~{item.get('approxTokens', 0)} tokens ({item.get('chars', 0)} chars)")
        if provider:
            lines.append(f"- Provider usage: `{json.dumps(provider, sort_keys=True)}`")
    lines.extend(["", "No Slack messages were sent and no Linear changes were made."])
    return "\n".join(lines).rstrip() + "\n"


def build_raw_filter_report(args):
    return {
        "folderId": args.folder_id,
        "folderIds": split_csv(args.folder_ids),
        "titleIncludeRegex": args.title_include_regex,
        "titleExcludeRegex": args.title_exclude_regex,
        "attendeeEmailDomain": args.attendee_email_domain,
        "ownerEmail": args.owner_email,
    }


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
