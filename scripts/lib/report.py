import json
import re
import shutil
from collections import Counter, defaultdict

from lib.linear import owner_of, status_of
from lib.state import already_sent


MAX_DM_ITEMS = 3


def write_reports(out_dir, issues, findings, analysis, mode, history=None):
    history = history or {}
    out_dir.mkdir(parents=True, exist_ok=True)
    for old_file in out_dir.iterdir():
        if old_file.is_file():
            old_file.unlink()
        elif old_file.is_dir():
            shutil.rmtree(old_file)

    dm_drafts, suppressed = build_dm_drafts_with_analysis(issues, findings, analysis, history)
    team_summary = render_team_summary(issues, findings, analysis, mode, dm_drafts)

    artifacts = {
        "summary.md": team_summary,
        "owners.md": render_owner_details(issues, findings, analysis, mode),
        "issues.md": render_issue_improvements(findings, analysis, mode),
        "report.md": render_full_report(team_summary, issues, findings, analysis, mode, dm_drafts, suppressed),
        "friction-notes.md": render_friction_notes(suppressed),
        "slack.json": json.dumps(render_slack_blocks(team_summary), indent=2),
        "dm-drafts.json": json.dumps(dm_drafts, indent=2),
        "data.json": json.dumps(
            {
                "mode": mode,
                "issueCount": len(issues),
                "analysisSource": analysis.get("source"),
                "findings": findings,
                "analysis": analysis,
                "dmDrafts": dm_drafts,
                "suppressedRepeats": suppressed,
            },
            indent=2,
        ),
        "linear.json": json.dumps(issues, indent=2),
    }
    for name, content in artifacts.items():
        (out_dir / name).write_text(content.rstrip() + "\n", encoding="utf-8")

    write_dm_files(out_dir / "dms", dm_drafts)
    return team_summary


def build_dm_drafts(issues, findings, history):
    return build_dm_drafts_with_analysis(issues, findings, {}, history)


def build_dm_drafts_with_analysis(issues, findings, analysis, history):
    issues_by_id = {issue.get("identifier"): issue for issue in issues}
    by_recipient = defaultdict(list)
    suppressed = []

    for finding in sorted(findings, key=finding_sort_key):
        issue_id = finding.get("issueId")
        issue = issues_by_id.get(issue_id)
        if not issue:
            continue
        recipient = recipient_for_issue(issue)
        if recipient == "Unassigned":
            continue
        category = finding.get("category") or "ai_sop_suggestion"
        item = dm_item(finding, recipient)
        if already_sent(history, issue_id, category, recipient):
            suppressed.append(item)
            continue
        by_recipient[recipient].append(item)

    drafts = []
    recipients_with_issue_items = set(by_recipient)
    for recipient in sorted(by_recipient):
        items = by_recipient[recipient][:MAX_DM_ITEMS]
        drafts.append(
            {
                "recipient": recipient,
                "kind": "issue_suggestions",
                "itemCount": len(items),
                "items": items,
                "text": render_dm_text(recipient, items),
            }
        )
    drafts.extend(owner_note_drafts(analysis, recipients_with_issue_items))
    return drafts, suppressed


def owner_note_drafts(analysis, excluded_recipients):
    drafts = []
    for note in analysis.get("ownerNotes", []):
        recipient = note.get("owner")
        if not recipient or recipient in excluded_recipients or recipient == "Unassigned":
            continue
        text = render_owner_note_dm_text(note)
        if not text:
            continue
        drafts.append(
            {
                "recipient": recipient,
                "kind": "owner_note",
                "itemCount": 0,
                "items": [],
                "text": text,
            }
        )
    return sorted(drafts, key=lambda draft: draft["recipient"].lower())


def recipient_for_issue(issue):
    assignee = issue.get("assignee")
    if assignee and assignee.get("name"):
        return assignee["name"]
    creator = issue.get("creator")
    if creator and creator.get("name"):
        return creator["name"]
    return "Unassigned"


def dm_item(finding, recipient):
    return {
        "recipient": recipient,
        "issueId": finding.get("issueId"),
        "title": finding.get("title"),
        "url": finding.get("url"),
        "category": finding.get("category"),
        "tier": finding.get("tier") or infer_tier(finding),
        "severity": finding.get("severity"),
        "confidence": finding.get("confidence"),
        "noticed": finding.get("noticed"),
        "nextEdit": finding.get("nextEdit"),
        "sopSection": finding.get("sopSection") or "docs/how-we-use-linear.md",
    }


def finding_sort_key(finding):
    tier_order = {"should_have": 0, "nice_to_have": 1}
    severity_order = {"needs_fix": 0, "should_improve": 1, "gentle_suggestion": 2}
    confidence_order = {"high": 0, "medium": 1, "low": 2}
    return (
        tier_order.get(finding.get("tier"), 2),
        severity_order.get(finding.get("severity"), 3),
        confidence_order.get(finding.get("confidence"), 3),
        finding.get("issueId") or "",
    )


def render_team_summary(issues, findings, analysis, mode, dm_drafts):
    statuses = Counter(status_of(issue) for issue in issues)
    theme_lines = "\n".join(f"- {theme}" for theme in analysis.get("teamThemes", [])[:4])
    positive = render_positive_example(analysis.get("positiveExample") or {})
    suggestion_issue_count = len({item.get("issueId") for item in findings if is_issue_finding(item)})
    dm_recipient_count = len(dm_drafts)

    source_note = "AI SOP review" if analysis.get("source") == "azure-openai" else "No AI review"
    return f"""Weekly Linear issue management check - {mode}

Reviewed {len(issues)} active Linear issues across Backlog, Todo, In Progress, and In Review.

Review mode: {source_note}

This is an AI-assisted helper, not a compliance report. Issues without suggestions should not be treated as automatically clean.

Status mix:
- Backlog: {statuses.get("Backlog", 0)}
- Todo: {statuses.get("Todo", 0)}
- In Progress: {statuses.get("In Progress", 0)}
- In Review: {statuses.get("In Review", 0)}

Main themes:
{theme_lines or "- No major themes this run."}

Suggested follow-ups:
- {suggestion_issue_count} issues have AI suggestions.
- {dm_recipient_count} people have short DM drafts in `results/dms/`.

Positive example to copy:
{positive}

A few people may get short DMs with specific suggestions. Feel free to ignore anything the review got wrong.

This review is read-only. No Linear changes were made."""


def render_positive_example(example):
    issue_id = example.get("issueId")
    title = example.get("title")
    url = example.get("url")
    why = example.get("why")
    if not issue_id:
        return "- No positive example selected this run."
    label = f"{issue_id}: {title}" if title else issue_id
    if url:
        label = f"{label} - {url}"
    if why:
        return f"- {label}\n  Why: {why}"
    return f"- {label}"


def render_owner_details(issues, findings, analysis, mode):
    notes_by_owner = {note.get("owner"): note for note in analysis.get("ownerNotes", [])}
    issues_by_owner = defaultdict(list)
    findings_by_owner = defaultdict(list)
    for issue in issues:
        issues_by_owner[owner_of(issue)].append(issue)
    for item in findings:
        if is_issue_finding(item):
            findings_by_owner[item.get("owner", "Unassigned")].append(item)

    owners = sorted(
        issues_by_owner,
        key=lambda owner: (-len(findings_by_owner.get(owner, [])), owner.lower()),
    )
    lines = [
        "# Owner-Specific Linear Review",
        "",
        f"Mode: `{mode}`",
        f"Analysis source: `{analysis.get('source')}`",
        "",
        "This is AI-assisted. Missing suggestions do not mean the issue is clean.",
        "",
    ]
    for owner in owners:
        note = notes_by_owner.get(owner, {})
        lines.extend([f"## {owner}", ""])
        if note.get("summary"):
            lines.append(note["summary"])
            lines.append("")
        focus = note.get("suggestedFocus") or []
        if focus:
            lines.append("Suggested focus:")
            lines.extend(f"- {item}" for item in focus)
            lines.append("")
        owner_findings = findings_by_owner.get(owner, [])
        if owner_findings:
            lines.append("Issues with AI suggestions:")
            for item in owner_findings:
                lines.append(f"- {item.get('issueId')}: {item.get('title')} - {item.get('noticed')}")
        else:
            lines.append("No AI suggestions from this run.")
        lines.append("")
    return "\n".join(lines)


def render_issue_improvements(findings, analysis, mode):
    notes_by_issue = {note.get("issueId"): note for note in analysis.get("issueNotes", [])}
    grouped = defaultdict(list)
    for item in findings:
        if is_issue_finding(item):
            grouped[item.get("issueId")].append(item)

    lines = [
        "# Issue Improvement Notes",
        "",
        f"Mode: `{mode}`",
        f"Analysis source: `{analysis.get('source')}`",
        "",
        "This is AI-assisted. Treat suggestions as review prompts, not final judgement.",
        "",
    ]
    for issue_id in sorted(grouped):
        first = grouped[issue_id][0]
        note = notes_by_issue.get(issue_id, {})
        lines.extend([f"## {issue_id}: {first.get('title')}", ""])
        lines.append(f"- Owner: {first.get('owner')}")
        lines.append(f"- Status: `{first.get('status')}`")
        lines.append(f"- Link: {first.get('url') or 'No URL available'}")
        lines.append(f"- SOP section: {first.get('sopSection') or note.get('sopSection') or 'docs/how-we-use-linear.md'}")
        if note:
            lines.append(f"- Current read: {note.get('currentRead')}")
            lines.append(f"- What to improve: {note.get('whatToImprove')}")
            lines.append(f"- Suggested next edit: {note.get('suggestedNextEdit')}")
            if note.get("suggestedTitle"):
                lines.append(f"- Suggested title: {note.get('suggestedTitle')}")
            if note.get("suggestedDefinitionOfDone"):
                lines.append(f"- Suggested Definition of done: {note.get('suggestedDefinitionOfDone')}")
            criteria = note.get("suggestedAcceptanceCriteria") or []
            if criteria:
                lines.append("- Suggested Acceptance criteria:")
                lines.extend(f"  - {item}" for item in criteria)
        else:
            for item in grouped[issue_id]:
                lines.append(f"- Suggested next edit: {item.get('nextEdit')}")
        lines.append("")
    return "\n".join(lines)


def render_full_report(team_summary, issues, findings, analysis, mode, dm_drafts, suppressed):
    dm_index = "\n".join(
        f"- {draft['recipient']}: {draft['itemCount']} item{'s' if draft['itemCount'] != 1 else ''}"
        for draft in dm_drafts
    ) or "- No DM drafts this run."
    suppressed_count = len(suppressed)
    return "\n\n".join(
        [
            "# Weekly Linear Issue Management Report",
            team_summary,
            "## DM Drafts",
            dm_index,
            f"Suppressed repeat DM items: {suppressed_count}",
            render_owner_details(issues, findings, analysis, mode),
            render_issue_improvements(findings, analysis, mode),
        ]
    )


def render_friction_notes(suppressed):
    lines = [
        "# Friction Notes",
        "",
        "Repeat DM items are suppressed here so the bot does not nudge the same person about the same issue/category twice.",
        "",
    ]
    if not suppressed:
        lines.append("No repeat DM items were suppressed this run.")
        return "\n".join(lines)

    lines.append("Suppressed repeats:")
    for item in suppressed:
        lines.append(
            f"- {item.get('issueId')} / {item.get('category')} for {item.get('recipient')}: {item.get('title')}"
        )
    lines.append("")
    lines.append("Bring repeated patterns to standup or the Friday review; treat them as feedback on the SOP, not the person.")
    return "\n".join(lines)


def render_dm_text(recipient, items):
    if items and all(item.get("tier") == "nice_to_have" for item in items):
        lines = [
            f"Hi {recipient}, your Linear issues mostly look okay from this week's SOP review.",
            "A couple of small nice-to-have cleanups could make them easier to scan:",
            "",
        ]
    else:
        lines = [
            f"Hi {recipient}, here are a few Linear SOP suggestions from this week's AI-assisted review.",
            "These are the items most worth tightening so the work is easier to start or verify.",
            "",
        ]
    for idx, item in enumerate(items, start=1):
        lines.append(f"{idx}. {item.get('issueId')}: {item.get('title')}")
        if item.get("url"):
            lines.append(f"   Link: {item.get('url')}")
        lines.append(f"   Noticed: {item.get('noticed')}")
        lines.append(f"   One-line fix: {item.get('nextEdit')}")
        lines.append(f"   SOP reference: {item.get('sopSection')}")
        lines.append("")
    lines.append("If a rule seems wrong or slows you down, raise it at standup or the Friday review.")
    return "\n".join(lines)


def render_owner_note_dm_text(note):
    recipient = note.get("owner")
    summary = clean_owner_summary(note.get("summary") or "")
    message_kind = note.get("messageKind") or infer_owner_note_kind(note)
    focus = [item for item in note.get("suggestedFocus", []) if item]
    if not recipient or not summary:
        return ""

    if message_kind == "positive_no_action" and not focus:
        lines = [
            f"Hi {recipient}, good work this week. There is nothing specific to clean up in Linear from this review.",
            "",
            f"The review noted: {summary.rstrip('.')}.",
        ]
    else:
        lines = [
            f"Hi {recipient}, no specific Linear SOP nudge for you this week.",
            "",
            f"The review noted: {summary.rstrip('.')}.",
        ]

    if focus:
        if len(focus) == 1:
            lines.append(f"The only light follow-up is to {focus[0][0].lower() + focus[0][1:] if focus[0] else focus[0]}.")
        else:
            lines.append("A couple of light follow-ups:")
            lines.extend(f"- {item}" for item in focus[:3])
    lines.extend(
        [
            "",
            "This is a draft/helper, not a judgement. If a rule seems wrong or slows you down, raise it at standup or the Friday review.",
        ]
    )
    return "\n".join(lines)


def clean_owner_summary(summary):
    cleaned = summary.strip()
    prefixes = (
        "good work this week;",
        "good work this week,",
        "nothing to do in linear from this review;",
        "nothing to do in linear from this review,",
    )
    lower = cleaned.lower()
    for prefix in prefixes:
        if lower.startswith(prefix):
            cleaned = cleaned[len(prefix) :].strip()
            break
    trailing_phrases = (
        "; nothing to do in linear from this review",
        ", nothing to do in linear from this review",
    )
    lower = cleaned.lower()
    for phrase in trailing_phrases:
        if phrase in lower:
            idx = lower.index(phrase)
            cleaned = cleaned[:idx].strip()
            break
    return cleaned


def infer_owner_note_kind(note):
    focus = [item for item in note.get("suggestedFocus", []) if item]
    if focus:
        return "light_suggestion"
    summary = (note.get("summary") or "").lower()
    positive_words = ("good", "well", "clear", "healthy", "scoped", "solid", "nothing")
    if any(word in summary for word in positive_words):
        return "positive_no_action"
    return "context_only"


def infer_tier(item):
    severity = item.get("severity")
    category = (item.get("category") or "").lower()
    if severity == "needs_fix":
        return "should_have"
    if any(key in category for key in ("description", "acceptance", "definition", "done", "scope", "in_progress_limit")):
        return "should_have"
    if any(key in category for key in ("label", "priority")):
        return "nice_to_have"
    return "nice_to_have" if severity == "gentle_suggestion" else "should_have"


def write_dm_files(dms_dir, dm_drafts):
    dms_dir.mkdir(parents=True, exist_ok=True)
    if not dm_drafts:
        (dms_dir / "no-dms.md").write_text("No DM drafts this run.\n", encoding="utf-8")
        return
    for draft in dm_drafts:
        filename = f"{slugify(draft['recipient'])}.md"
        (dms_dir / filename).write_text(draft["text"].rstrip() + "\n", encoding="utf-8")


def slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "unknown"


def render_slack_blocks(team_summary):
    return [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": team_summary},
        }
    ]


def is_issue_finding(item):
    issue_id = item.get("issueId")
    return bool(issue_id and issue_id != "owner-summary")
