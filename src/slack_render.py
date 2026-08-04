from audit import summarize


def render_weekly_text(issues, findings, mode="dev-smoke"):
    summary = summarize(issues, findings)
    status_counts = summary["statusCounts"]
    owner_counts = summary["ownerCounts"]
    category_counts = summary["categoryCounts"]

    title = "Weekly Linear issue management check"
    if mode != "public-beta":
        title = f"{title} - {mode}"

    sorted_owners = sorted(owner_counts.items(), key=lambda item: (-item[1], item[0].lower()))[:8]
    if sorted_owners:
        owners = "\n".join(
            f"- {owner}: {count} suggestion{'s' if count != 1 else ''}"
            for owner, count in sorted_owners
        )
    else:
        owners = "- No suggestions this run"

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


def button(text, action_id):
    return {
        "type": "button",
        "text": {"type": "plain_text", "text": text},
        "action_id": action_id,
        "value": action_id,
    }


def pretty_category(category):
    return category.replace("_", " ")
