"""Minimal read-only Linear GraphQL client.

This module only fetches Linear issues. It does not create issues, update
issues, assign owners, change statuses, or post comments.
"""

import json
import os
import urllib.error
import urllib.request


LINEAR_ENDPOINT = "https://api.linear.app/graphql"
ACTIVE_STATUSES = {"Backlog", "Todo", "In Progress", "In Review"}


def linear_graphql(query, variables=None):
    api_key = os.environ.get("LINEAR_API_KEY")
    if not api_key:
        raise RuntimeError("LINEAR_API_KEY is required")

    request = urllib.request.Request(
        LINEAR_ENDPOINT,
        data=json.dumps({"query": query, "variables": variables or {}}).encode("utf-8"),
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
