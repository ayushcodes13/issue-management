from collections import Counter

from lib.linear import labels_of, owner_of, priority_of, status_of


TYPE_LABELS = {"Bug", "Feature", "Improvement", "Chore", "Spike"}
READY_STATUSES = {"Todo", "In Progress", "In Review"}


def run_checks(issues):
    findings = []
    for issue in issues:
        check_issue(issue, findings)

    in_progress_by_owner = Counter(
        owner_of(issue)
        for issue in issues
        if status_of(issue) == "In Progress" and owner_of(issue) != "Unassigned"
    )
    for owner, count in in_progress_by_owner.items():
        if count > 3:
            findings.append(
                finding(
                    issue_id="owner-summary",
                    title="Too many In Progress issues",
                    url="",
                    owner=owner,
                    status="In Progress",
                    severity="needs_fix",
                    category="too_many_in_progress",
                    noticed=f"{owner} has {count} issues In Progress.",
                    why="The SOP caps In Progress work at three per person.",
                    next_edit="Ask which items should remain active and move the rest back to Todo.",
                    confidence="high",
                )
            )
    return findings


def check_issue(issue, findings):
    issue_labels = labels_of(issue)
    type_labels = [label for label in issue_labels if label in TYPE_LABELS]
    status = status_of(issue)

    if len(type_labels) == 0:
        add(
            findings,
            issue,
            "needs_fix",
            "missing_type_label",
            "This issue does not show one SOP type label.",
            "Every issue should have exactly one type label.",
            "Add one of Bug, Feature, Improvement, Chore, or Spike.",
        )
    elif len(type_labels) > 1:
        add(
            findings,
            issue,
            "needs_fix",
            "multiple_type_labels",
            "This issue has more than one SOP type label.",
            "Multiple type labels make reporting harder to scan.",
            "Keep the best matching type label and remove the others.",
        )

    if status in READY_STATUSES and owner_of(issue) == "Unassigned":
        add(
            findings,
            issue,
            "needs_fix",
            "missing_owner",
            f"This issue is in {status} without an assignee.",
            "Ready or active work needs a visible owner.",
            "Assign an owner, or move it back until ownership is clear.",
        )

    if status == "Todo" and priority_of(issue) == "No priority":
        add(
            findings,
            issue,
            "needs_fix",
            "missing_priority_for_todo",
            "This Todo issue does not show a priority.",
            "Todo work should be prioritized before someone starts it.",
            "If priority is known, add it. Otherwise consider Backlog.",
        )

    if status in READY_STATUSES and not has_text(issue, ["definition of done", "dod:", "goal:", "outcome"]):
        add(
            findings,
            issue,
            "should_improve",
            "missing_defined_outcome",
            f"This {status} issue could make the defined outcome clearer.",
            "Someone else should be able to tell what will be true when complete.",
            "Add a one-sentence Definition of done focused on the outcome.",
            "medium",
        )

    if status in READY_STATUSES and not has_text(issue, ["acceptance criteria", "how to verify", "verify by", "criteria:"]):
        add(
            findings,
            issue,
            "should_improve",
            "missing_acceptance_criteria",
            f"This {status} issue could use clearer acceptance criteria.",
            "Acceptance criteria make the issue verifiable.",
            "Add 2-4 observable checks.",
            "medium",
        )

    if "Spike" in type_labels:
        if not has_text(issue, ["question to answer", "question:", "research the best way", "study how"]):
            add(
                findings,
                issue,
                "should_improve",
                "spike_missing_question",
                "This Spike could use a more explicit question.",
                "A Spike should answer a bounded question.",
                "Add a `Question to answer` section.",
                "medium",
            )
        if not has_text(issue, ["timebox"]):
            add(
                findings,
                issue,
                "needs_fix",
                "spike_missing_timebox",
                "This Spike does not show a timebox.",
                "Spike work should have a hard limit.",
                "Add `Timebox: <n> hours`.",
            )
        if not has_text(issue, ["output"]):
            add(
                findings,
                issue,
                "needs_fix",
                "spike_missing_output",
                "This Spike does not show an output.",
                "A Spike is done when the output is recorded.",
                "Add an `Output` section.",
            )

    title = issue.get("title", "").lower().strip()
    if title.startswith(("check ", "look into", "investigate", "research ", "work on", "plan out")):
        add(
            findings,
            issue,
            "gentle_suggestion",
            "activity_style_title",
            "The title reads like an activity rather than an outcome.",
            "Outcome-style titles are easier to scan and verify.",
            "Consider rewriting the title as the result that should exist when complete.",
            "medium",
        )


def add(findings, issue, severity, category, noticed, why, next_edit, confidence="high"):
    findings.append(
        finding(
            issue_id=issue.get("identifier"),
            title=issue.get("title"),
            url=issue.get("url"),
            owner=owner_of(issue),
            status=status_of(issue),
            severity=severity,
            category=category,
            noticed=noticed,
            why=why,
            next_edit=next_edit,
            confidence=confidence,
        )
    )


def finding(issue_id, title, url, owner, status, severity, category, noticed, why, next_edit, confidence):
    return {
        "issueId": issue_id,
        "title": title,
        "url": url,
        "owner": owner,
        "status": status,
        "severity": severity,
        "category": category,
        "noticed": noticed,
        "why": why,
        "nextEdit": next_edit,
        "confidence": confidence,
    }


def has_text(issue, needles):
    description = (issue.get("description") or "").lower()
    return any(needle.lower() in description for needle in needles)
