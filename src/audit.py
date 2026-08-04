import json
import os
import urllib.error
import urllib.request
from collections import Counter


LINEAR_ENDPOINT = "https://api.linear.app/graphql"

TYPE_LABELS = {"Bug", "Feature", "Improvement", "Chore", "Spike"}
ACTIVE_STATUSES = {"Backlog", "Todo", "In Progress", "In Review"}
READY_STATUSES = {"Todo", "In Progress", "In Review"}


def linear_graphql(query, variables=None):
    api_key = os.environ.get("LINEAR_API_KEY")
    if not api_key:
        raise RuntimeError("LINEAR_API_KEY is required")

    payload = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    request = urllib.request.Request(
        LINEAR_ENDPOINT,
        data=payload,
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Linear API failed with HTTP {exc.code}: {detail}") from exc

    data = json.loads(raw)
    if data.get("errors"):
        raise RuntimeError(f"Linear API failed: {json.dumps(data['errors'])}")
    return data["data"]


def fetch_active_issues():
    query = """
    query Issues($after: String) {
      issues(first: 100, after: $after, filter: { archivedAt: { null: true } }) {
        pageInfo { hasNextPage endCursor }
        nodes {
          identifier
          title
          description
          url
          updatedAt
          priority
          priorityLabel
          state { name type }
          assignee { name email }
          creator { name email }
          team { name key }
          project { name }
          labels { nodes { name } }
        }
      }
    }
    """

    issues = []
    after = None
    while True:
        data = linear_graphql(query, {"after": after})
        page = data["issues"]
        for issue in page["nodes"]:
            if status_of(issue) in ACTIVE_STATUSES:
                issues.append(issue)
        if not page["pageInfo"]["hasNextPage"]:
            return issues
        after = page["pageInfo"]["endCursor"]


def audit_issues(issues):
    findings = []
    for issue in issues:
        audit_issue(issue, findings)

    in_progress_by_owner = Counter(
        owner_of(issue)
        for issue in issues
        if status_of(issue) == "In Progress" and owner_of(issue) != "Unassigned"
    )
    for owner, count in in_progress_by_owner.items():
        if count > 3:
            findings.append(
                {
                    "issueId": "owner-summary",
                    "title": "Too many In Progress issues",
                    "url": "",
                    "owner": owner,
                    "status": "In Progress",
                    "severity": "needs_fix",
                    "category": "too_many_in_progress",
                    "noticed": f"{owner} has {count} issues In Progress.",
                    "why": "The SOP caps In Progress work at three per person.",
                    "nextEdit": "Ask Nikhil which items should remain active and move the rest back to Todo.",
                    "confidence": "high",
                }
            )

    return findings


def audit_issue(issue, findings):
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
            "The SOP says Nikhil sets priority before Todo.",
            "If Nikhil has set priority, add it. Otherwise consider Backlog.",
        )

    if status in READY_STATUSES and not has_text(issue, ["definition of done", "goal:", "outcome"]):
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

    if status in READY_STATUSES and not has_text(issue, ["acceptance criteria", "how to verify", "verify by", "drills:"]):
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
                "The SOP requires a hard limit for Spike work.",
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
    activity_starts = ("check ", "look into", "investigate", "research ", "work on", "plan out")
    if title.startswith(activity_starts):
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

    if "Improvement" in type_labels and not has_text(issue, ["current", "today", "baseline", "target", "after the change", "before"]):
        add(
            findings,
            issue,
            "gentle_suggestion",
            "improvement_missing_current_target",
            "This Improvement could make the before/after clearer.",
            "Improvement issues are easier to prioritize when current and target states are visible.",
            "Add a short current-state and target-state note.",
            "low",
        )


def add(findings, issue, severity, category, noticed, why, next_edit, confidence="high"):
    findings.append(
        {
            "issueId": issue.get("identifier"),
            "title": issue.get("title"),
            "url": issue.get("url"),
            "owner": owner_of(issue),
            "status": status_of(issue),
            "severity": severity,
            "category": category,
            "noticed": noticed,
            "why": why,
            "nextEdit": next_edit,
            "confidence": confidence,
        }
    )


def labels_of(issue):
    return [label["name"] for label in issue.get("labels", {}).get("nodes", [])]


def owner_of(issue):
    assignee = issue.get("assignee")
    return assignee.get("name") if assignee else "Unassigned"


def status_of(issue):
    state = issue.get("state")
    return state.get("name") if state else "Unknown"


def priority_of(issue):
    return issue.get("priorityLabel") or "No priority"


def has_text(issue, needles):
    description = (issue.get("description") or "").lower()
    return any(needle.lower() in description for needle in needles)


def summarize(issues, findings):
    return {
        "statusCounts": dict(Counter(status_of(issue) for issue in issues)),
        "ownerCounts": dict(Counter(finding["owner"] for finding in findings)),
        "categoryCounts": dict(Counter(finding["category"] for finding in findings)),
    }
