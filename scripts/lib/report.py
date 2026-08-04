import json
from collections import Counter, defaultdict

from lib.linear import owner_of, status_of


def write_reports(out_dir, issues, findings, analysis, mode):
    out_dir.mkdir(parents=True, exist_ok=True)
    for old_file in out_dir.iterdir():
        if old_file.is_file():
            old_file.unlink()

    team_summary = render_team_summary(issues, findings, analysis, mode)
    artifacts = {
        "summary.md": team_summary,
        "owners.md": render_owner_details(issues, findings, analysis, mode),
        "issues.md": render_issue_improvements(findings, analysis, mode),
        "report.md": render_full_report(team_summary, issues, findings, analysis, mode),
        "slack.json": json.dumps(render_slack_blocks(team_summary), indent=2),
        "data.json": json.dumps(
            {
                "mode": mode,
                "issueCount": len(issues),
                "analysisSource": analysis.get("source"),
                "findings": findings,
                "analysis": analysis,
            },
            indent=2,
        ),
        "linear.json": json.dumps(issues, indent=2),
    }
    for name, content in artifacts.items():
        (out_dir / name).write_text(content.rstrip() + "\n", encoding="utf-8")
    return team_summary


def render_team_summary(issues, findings, analysis, mode):
    statuses = Counter(status_of(issue) for issue in issues)
    owner_issue_counts = issue_counts_by_owner(findings)
    owner_suggestion_counts = Counter(item.get("owner", "Unassigned") for item in findings)
    owners = sorted(owner_suggestion_counts, key=lambda owner: (-owner_issue_counts.get(owner, 0), owner.lower()))[:8]
    owner_lines = "\n".join(
        f"- {owner}: {owner_issue_counts.get(owner, 0)} issue{'s' if owner_issue_counts.get(owner, 0) != 1 else ''}, {owner_suggestion_counts[owner]} suggestion{'s' if owner_suggestion_counts[owner] != 1 else ''}"
        for owner in owners
    ) or "- No suggestions this run"
    theme_lines = "\n".join(f"- {theme}" for theme in analysis.get("teamThemes", [])[:4])

    source_note = "AI-assisted review" if analysis.get("source") == "azure-openai" else "Local checks only"
    return f"""Weekly Linear issue management check - {mode}

Reviewed {len(issues)} active Linear issues across Backlog, Todo, In Progress, and In Review.

Review mode: {source_note}

Status mix:
- Backlog: {statuses.get("Backlog", 0)}
- Todo: {statuses.get("Todo", 0)}
- In Progress: {statuses.get("In Progress", 0)}
- In Review: {statuses.get("In Review", 0)}

Main themes:
{theme_lines or "- No major themes this run."}

Suggestions by owner:
{owner_lines}

This check is read-only. No Linear changes were made.

Reply with:
- show <name>
- improve <issue id>
- examples"""


def render_owner_details(issues, findings, analysis, mode):
    notes_by_owner = {note.get("owner"): note for note in analysis.get("ownerNotes", [])}
    issues_by_owner = defaultdict(list)
    findings_by_owner = defaultdict(list)
    owner_level_findings = defaultdict(list)
    for issue in issues:
        issues_by_owner[owner_of(issue)].append(issue)
    for item in findings:
        owner = item.get("owner", "Unassigned")
        if is_issue_finding(item):
            findings_by_owner[owner].append(item)
        else:
            owner_level_findings[owner].append(item)

    owners = sorted(
        issues_by_owner,
        key=lambda owner: (-(len(findings_by_owner.get(owner, [])) + len(owner_level_findings.get(owner, []))), owner.lower()),
    )
    lines = [
        "# Owner-Specific Linear Review",
        "",
        f"Mode: `{mode}`",
        f"Analysis source: `{analysis.get('source')}`",
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
        if owner_level_findings.get(owner):
            lines.append("Owner-level suggestions:")
            for item in owner_level_findings[owner]:
                lines.append(f"- {item.get('noticed')} Next edit: {item.get('nextEdit')}")
            lines.append("")
        owner_findings = findings_by_owner.get(owner, [])
        if owner_findings:
            lines.append("Flagged issues:")
            for item in owner_findings:
                lines.append(f"- {item.get('issueId')}: {item.get('title')} - {item.get('noticed')}")
        else:
            lines.append("No flagged issues from this run.")
        lines.append("")
    return "\n".join(lines)


def render_issue_improvements(findings, analysis, mode):
    notes_by_issue = {note.get("issueId"): note for note in analysis.get("issueNotes", [])}
    grouped = defaultdict(list)
    for item in findings:
        if not is_issue_finding(item):
            continue
        grouped[item.get("issueId")].append(item)

    lines = [
        "# Issue Improvement Notes",
        "",
        f"Mode: `{mode}`",
        f"Analysis source: `{analysis.get('source')}`",
        "",
    ]
    for issue_id in sorted(grouped):
        first = grouped[issue_id][0]
        note = notes_by_issue.get(issue_id, {})
        lines.extend([f"## {issue_id}: {first.get('title')}", ""])
        lines.append(f"- Owner: {first.get('owner')}")
        lines.append(f"- Status: `{first.get('status')}`")
        lines.append(f"- Link: {first.get('url') or 'No URL available'}")
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


def render_full_report(team_summary, issues, findings, analysis, mode):
    return "\n\n".join(
        [
            "# Weekly Linear Issue Management Report",
            team_summary,
            render_owner_details(issues, findings, analysis, mode),
            render_issue_improvements(findings, analysis, mode),
        ]
    )


def render_slack_blocks(team_summary):
    return [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": team_summary},
        }
    ]


def issue_counts_by_owner(findings):
    owner_to_issues = defaultdict(set)
    for item in findings:
        if is_issue_finding(item):
            owner_to_issues[item.get("owner", "Unassigned")].add(item.get("issueId"))
    return {owner: len(issue_ids) for owner, issue_ids in owner_to_issues.items()}


def is_issue_finding(item):
    issue_id = item.get("issueId")
    return bool(issue_id and issue_id != "owner-summary")
