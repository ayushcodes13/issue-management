from audit import summarize


SEVERITY_ORDER = {"needs_fix": 0, "should_improve": 1, "gentle_suggestion": 2}

CATEGORY_LABELS = {
    "missing_type_label": "missing SOP type label",
    "multiple_type_labels": "multiple SOP type labels",
    "missing_owner": "missing owner",
    "missing_priority_for_todo": "Todo missing priority",
    "missing_defined_outcome": "unclear Definition of done",
    "missing_acceptance_criteria": "unclear Acceptance criteria",
    "spike_missing_question": "Spike missing question",
    "spike_missing_timebox": "Spike missing timebox",
    "spike_missing_output": "Spike missing output",
    "activity_style_title": "activity-style title",
    "improvement_missing_current_target": "Improvement missing current/target state",
    "too_many_in_progress": "too many In Progress issues",
}


def render_weekly_text(issues, findings, mode="dev-smoke"):
    summary = summarize(issues, findings)
    status_counts = summary["statusCounts"]
    owner_counts = summary["ownerCounts"]
    category_counts = summary["categoryCounts"]

    title = "Weekly Linear issue management check"
    if mode != "public-beta":
        title = f"{title} - {mode}"

    owner_issue_counts = issue_counts_by_owner(findings)
    sorted_owners = sorted(
        owner_counts.items(),
        key=lambda item: (-owner_issue_counts.get(item[0], 0), -item[1], item[0].lower()),
    )[:8]
    if sorted_owners:
        owners = "\n".join(
            f"- {owner}: {owner_issue_counts.get(owner, 0)} issue{'s' if owner_issue_counts.get(owner, 0) != 1 else ''}, {count} suggestion{'s' if count != 1 else ''}"
            for owner, count in sorted_owners
        )
    else:
        owners = "- No suggestions this run"

    top_actions = render_top_actions(category_counts)

    return f"""{title}

Reviewed {len(issues)} active Linear issues across Backlog, Todo, In Progress, and In Review.

Status mix:
- Backlog: {status_counts.get("Backlog", 0)}
- Todo: {status_counts.get("Todo", 0)}
- In Progress: {status_counts.get("In Progress", 0)}
- In Review: {status_counts.get("In Review", 0)}

Highlights:
- {category_counts.get("missing_type_label", 0)} active issues may need one SOP type label: Bug, Feature, Improvement, Chore, or Spike.
- {category_counts.get("missing_priority_for_todo", 0)} Todo issues are missing priority.
- {category_counts.get("missing_owner", 0)} Todo/In Progress issues appear unassigned.
- {category_counts.get("missing_acceptance_criteria", 0)} Todo/In Progress issues could use clearer acceptance criteria.

Suggested triage order:
{top_actions}

Suggestions by owner:
{owners}

This is a {mode} check only. No Linear changes were made.

Try:
- show me
- show <name>
- improve BYN-67
- examples"""


def render_weekly_blocks(issues, findings, mode="dev-smoke"):
    text = render_weekly_text(issues, findings, mode)
    title = "Weekly Linear issue management check"
    if mode != "public-beta":
        title = f"{title} - {mode}"

    body = text.split("\n\n", 1)[1]
    return [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*{title}*"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": body},
        },
        {
            "type": "actions",
            "elements": [
                button("Show my suggestions", "show_me"),
                button("Team themes", "team_themes"),
                button("Examples", "examples"),
            ],
        },
    ]


def render_owner_detail(findings, owner_name):
    normalized = owner_name.lower()
    matches = [
        finding
        for finding in findings
        if normalized in finding.get("owner", "").lower()
    ]
    if not matches:
        return f'I could not find suggestions for "{owner_name}" in the latest audit.'

    rows = []
    for finding in matches[:8]:
        link = f"\n{finding['url']}" if finding.get("url") else ""
        rows.append(
            f"*{finding['issueId']}: {finding['title']}*\n"
            f"Suggestion: {finding['noticed']}\n"
            f"Suggested next edit: {finding['nextEdit']}{link}"
        )
    return "\n\n".join(rows)


def render_owner_details_markdown(issues, findings, mode="manual-preview"):
    owner_counts = issue_counts_by_owner(findings)
    owners = sorted(owner_counts, key=lambda owner: (-owner_counts[owner], owner.lower()))
    lines = [
        "# Owner-Specific Linear SOP Suggestions",
        "",
        f"Mode: `{mode}`",
        "",
        "This report is meant to help people make the next edit quickly. It is not a ranking, and no Linear changes were made.",
        "",
        "## Owner Summary",
        "",
        "| Owner | Issues with suggestions | Total suggestions | Needs fix | Should improve | Gentle suggestions |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]

    for owner in owners:
        owner_findings = [finding for finding in findings if finding.get("owner") == owner]
        severity_counts = count_by(owner_findings, lambda finding: finding.get("severity", "unknown"))
        lines.append(
            f"| {owner} | {owner_counts[owner]} | {len(owner_findings)} | "
            f"{severity_counts.get('needs_fix', 0)} | "
            f"{severity_counts.get('should_improve', 0)} | "
            f"{severity_counts.get('gentle_suggestion', 0)} |"
        )

    lines.extend(["", "## Details By Owner", ""])
    for owner in owners:
        owner_findings = sorted_findings([finding for finding in findings if finding.get("owner") == owner])
        lines.extend([f"### {owner}", ""])
        if owner == "Unassigned":
            lines.extend([
                "Focus: these are best handled as ownership triage. Assign an owner if the work is planned, or keep it in Backlog until ownership is clear.",
                "",
            ])
        else:
            lines.extend([
                "Focus: make the issue easier for someone else to pick up, review, or verify.",
                "",
            ])

        for issue_id, issue_findings in group_findings_by_issue(owner_findings).items():
            first = issue_findings[0]
            lines.extend([
                f"#### {issue_id}: {first.get('title')}",
                "",
                f"- Status: `{first.get('status')}`",
                f"- Link: {first.get('url') or 'No URL available'}",
            ])
            for finding in issue_findings:
                lines.extend([
                    f"- Noticed: {finding.get('noticed')}",
                    f"- Why it matters: {finding.get('why')}",
                    f"- Suggested next edit: {finding.get('nextEdit')}",
                ])
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_issue_improvements_markdown(findings, mode="manual-preview"):
    lines = [
        "# Issue-Level Improvement Suggestions",
        "",
        f"Mode: `{mode}`",
        "",
        "Use this when someone asks: what exactly should I edit on this issue?",
        "",
    ]

    for issue_id, issue_findings in group_findings_by_issue(sorted_findings(findings)).items():
        first = issue_findings[0]
        lines.extend([
            f"## {issue_id}: {first.get('title')}",
            "",
            f"- Owner: {first.get('owner')}",
            f"- Status: `{first.get('status')}`",
            f"- Link: {first.get('url') or 'No URL available'}",
            "",
        ])
        for finding in issue_findings:
            lines.extend([
                f"### {friendly_category(finding.get('category'))}",
                "",
                f"- Severity: `{finding.get('severity')}`",
                f"- Noticed: {finding.get('noticed')}",
                f"- Why it matters: {finding.get('why')}",
                f"- Suggested next edit: {finding.get('nextEdit')}",
                "",
            ])

    return "\n".join(lines).rstrip() + "\n"


def render_full_report_markdown(issues, findings, mode="manual-preview"):
    return "\n".join(
        [
            "# Weekly Linear Issue Management Report",
            "",
            render_weekly_text(issues, findings, mode),
            "",
            "---",
            "",
            render_owner_details_markdown(issues, findings, mode),
            "",
            "---",
            "",
            render_examples().replace("*", ""),
            "",
        ]
    ).rstrip() + "\n"


def render_issue_improvement(findings, issue_id):
    normalized = issue_id.upper()
    matches = [
        finding
        for finding in findings
        if finding.get("issueId", "").upper() == normalized
    ]
    if not matches:
        return (
            f"I did not find an audit suggestion for {normalized}. "
            "It may already be in decent SOP shape, or it was outside the latest audit scope."
        )

    finding = matches[0]
    return f"""*{finding['issueId']}: {finding['title']}*

This may be easier to pick up if {finding['why'].lower()}

Suggested next edit:
{finding['nextEdit']}

Tone note:
This is a suggestion, not a correction. The goal is to make the next edit obvious."""


def render_examples():
    return """*Good issue shape*

Title:
Make validation output include source-level failure reasons

Definition of done:
Validation responses include source-level failure reasons for every failed fact.

Acceptance criteria:
- Run the validator on one supported and one failed report.
- Confirm every failed fact includes a source-level reason.
- Confirm existing quality gates still pass.

Quick rule: write the result, not the activity."""


def render_team_themes(findings):
    counts = {}
    for finding in findings:
        category = finding["category"]
        counts[category] = counts.get(category, 0) + 1

    rows = "\n".join(
        f"- {pretty_category(category)}: {count}"
        for category, count in sorted(counts.items(), key=lambda item: -item[1])[:8]
    )
    return f"*Team themes from latest audit*\n\n{rows or 'No themes this run.'}"


def render_top_actions(category_counts):
    actions = []
    if category_counts.get("missing_owner", 0):
        actions.append("- First, assign owners for ready/active unassigned work.")
    if category_counts.get("missing_priority_for_todo", 0):
        actions.append("- Then, confirm priority for Todo items before people start them.")
    if category_counts.get("missing_acceptance_criteria", 0):
        actions.append("- Then, add 2-4 verifiable acceptance criteria to planned work.")
    if category_counts.get("missing_type_label", 0):
        actions.append("- Finally, add exactly one type label so reporting stays clean.")
    return "\n".join(actions[:4]) if actions else "- No obvious triage needed from this run."


def button(text, action_id):
    return {
        "type": "button",
        "text": {"type": "plain_text", "text": text},
        "action_id": action_id,
        "value": action_id,
    }


def pretty_category(category):
    return category.replace("_", " ")


def friendly_category(category):
    return CATEGORY_LABELS.get(category, pretty_category(category or "unknown"))


def issue_counts_by_owner(findings):
    owners = {}
    for finding in findings:
        owner = finding.get("owner", "Unassigned")
        issue_id = finding.get("issueId")
        if not issue_id or issue_id == "owner-summary":
            continue
        owners.setdefault(owner, set()).add(issue_id)
    return {owner: len(issue_ids) for owner, issue_ids in owners.items()}


def sorted_findings(findings):
    return sorted(
        findings,
        key=lambda finding: (
            SEVERITY_ORDER.get(finding.get("severity"), 9),
            finding.get("owner", ""),
            finding.get("issueId", ""),
            finding.get("category", ""),
        ),
    )


def group_findings_by_issue(findings):
    grouped = {}
    for finding in findings:
        issue_id = finding.get("issueId") or "unknown"
        grouped.setdefault(issue_id, []).append(finding)
    return grouped


def count_by(items, fn):
    counts = {}
    for item in items:
        key = fn(item)
        counts[key] = counts.get(key, 0) + 1
    return counts
