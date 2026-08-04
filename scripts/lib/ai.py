"""Azure OpenAI analysis for flagged Linear issues only.

This module sends only issues already flagged by local checks. It does not send
the full Linear issue list, and it makes one batched request for the run.
"""

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import quote

from lib.linear import labels_of, owner_of, priority_of, status_of


DEFAULT_AZURE_ENDPOINT = "https://alerts-sweden-central.openai.azure.com/"
DEFAULT_AZURE_API_VERSION = "2025-03-01-preview"
DEFAULT_AZURE_DEPLOYMENT = "gpt-5.5"
DEFAULT_SOP_DOC_PATH = "docs/how-we-use-linear.md"


def analyze_flagged_issues(issues, findings):
    flagged = flagged_issue_payloads(issues, findings)
    config = azure_config()
    if not config["api_key"]:
        return fallback_analysis(flagged, findings, "AZURE_OPENAI_API_KEY is not set")
    if not flagged:
        return {
            "source": "azure-openai",
            "teamThemes": ["No flagged issues from the local SOP checks."],
            "ownerNotes": [],
            "issueNotes": [],
        }

    prompt = build_prompt(flagged, load_sop_text())
    try:
        body = request_azure_response(config, prompt)
    except NETWORK_ERRORS as exc:
        return fallback_analysis(flagged, findings, f"Azure OpenAI network error: {exc}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return fallback_analysis(flagged, findings, f"Azure OpenAI API failed with HTTP {exc.code}: {detail[:500]}")

    try:
        parsed = json.loads(extract_response_text(json.loads(body)))
    except (json.JSONDecodeError, RuntimeError) as exc:
        return fallback_analysis(flagged, findings, f"Could not parse Azure OpenAI response: {exc}")

    parsed["source"] = "azure-openai"
    return parsed


NETWORK_ERRORS = (TimeoutError, urllib.error.URLError, ConnectionError)


def request_azure_response(config, prompt):
    payload = {
        "model": config["deployment"],
        "input": prompt,
    }
    request = urllib.request.Request(
        azure_responses_url(config["endpoint"], config["api_version"]),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "api-key": config["api_key"],
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read().decode("utf-8")


def azure_config():
    return {
        "api_key": os.environ.get("AZURE_OPENAI_API_KEY", ""),
        "endpoint": (
            os.environ.get("AZURE_OPENAI_4_1_MODELS_ENDPOINT")
            or os.environ.get("AZURE_OPENAI_API_ENDPOINT")
            or DEFAULT_AZURE_ENDPOINT
        ),
        "api_version": (
            os.environ.get("AZURE_OPENAI_4_1_MODELS_VERSION")
            or os.environ.get("AZURE_OPENAI_API_VERSION")
            or DEFAULT_AZURE_API_VERSION
        ),
        "deployment": (
            os.environ.get("AZURE_OPENAI_4_1_MODELS_DEPLOYMENT")
            or os.environ.get("AZURE_OPENAI_API_MODEL")
            or DEFAULT_AZURE_DEPLOYMENT
        ),
    }


def azure_responses_url(endpoint, api_version):
    return f"{endpoint.rstrip('/')}/openai/responses?api-version={quote(api_version)}"


def flagged_issue_payloads(issues, findings):
    findings_by_issue = {}
    for item in findings:
        issue_id = item.get("issueId")
        if issue_id and issue_id != "owner-summary":
            findings_by_issue.setdefault(issue_id, []).append(item)

    payloads = []
    for issue in issues:
        issue_id = issue.get("identifier")
        if issue_id not in findings_by_issue:
            continue
        description = (issue.get("description") or "").strip()
        if len(description) > 1000:
            description = description[:1000] + "\n...[truncated]"
        payloads.append(
            {
                "identifier": issue_id,
                "title": issue.get("title"),
                "status": status_of(issue),
                "priority": priority_of(issue),
                "owner": owner_of(issue),
                "creator": (issue.get("creator") or {}).get("name"),
                "team": (issue.get("team") or {}).get("name"),
                "project": (issue.get("project") or {}).get("name"),
                "labels": labels_of(issue),
                "updatedAt": issue.get("updatedAt"),
                "url": issue.get("url"),
                "description": description,
                "findings": findings_by_issue[issue_id],
            }
        )
    return payloads


def load_sop_text():
    path = Path(os.environ.get("SOP_DOC_PATH", DEFAULT_SOP_DOC_PATH))
    if not path.exists():
        raise RuntimeError(f"SOP doc not found: {path}")
    return path.read_text(encoding="utf-8")


def build_prompt(flagged, sop_text):
    return f"""You are running a lightweight weekly Linear issue-management review for Bynd.

You will receive only the issues flagged by local deterministic SOP checks, not all issues.

The only source of truth is the local SOP document below. Do not introduce checks, advice, or rules that are not stated in this document.

Write concise, gentle, owner-specific recommendations. Do not shame people. Do not use words like violation, non-compliant, wrong, invalid, bad issue, failed, worst, or offender.

Return only valid JSON in this exact shape:
{{
  "teamThemes": ["theme 1", "theme 2", "theme 3"],
  "ownerNotes": [
    {{
      "owner": "Name",
      "summary": "one sentence",
      "suggestedFocus": ["action 1", "action 2"]
    }}
  ],
  "issueNotes": [
    {{
      "issueId": "BYN-123",
      "currentRead": "one sentence",
      "whatToImprove": "one sentence",
      "suggestedNextEdit": "one concrete edit",
      "suggestedTitle": "optional better title or empty string",
      "suggestedDefinitionOfDone": "optional sentence or empty string",
      "suggestedAcceptanceCriteria": ["optional criterion"]
    }}
  ]
}}

Issues:
{json.dumps(flagged, indent=2)}

Local SOP document:
{sop_text}
"""


def fallback_analysis(flagged, findings, reason):
    themes = []
    category_counts = {}
    for item in findings:
        category = item.get("category")
        category_counts[category] = category_counts.get(category, 0) + 1
    if category_counts.get("missing_owner"):
        themes.append("Some active work needs clearer ownership.")
    if category_counts.get("missing_priority"):
        themes.append("Some Todo or active items may not be ready because priority is missing.")
    if category_counts.get("missing_acceptance_criteria"):
        themes.append("Some ready or active issues could use clearer acceptance criteria.")
    if category_counts.get("missing_type_label"):
        themes.append("Some issues need exactly one SOP type label.")

    owner_counts = {}
    for issue in flagged:
        owner_counts[issue["owner"]] = owner_counts.get(issue["owner"], 0) + 1

    return {
        "source": "fallback",
        "fallbackReason": reason,
        "teamThemes": themes or ["No major themes found."],
        "ownerNotes": [
            {
                "owner": owner,
                "summary": f"{count} flagged issue{'s' if count != 1 else ''} to review.",
                "suggestedFocus": ["Review the issue notes and make the smallest useful cleanup edit."],
            }
            for owner, count in sorted(owner_counts.items(), key=lambda item: (-item[1], item[0].lower()))
        ],
        "issueNotes": [
            {
                "issueId": issue["identifier"],
                "currentRead": first_finding(issue).get("noticed", "This issue was flagged by the local SOP checks."),
                "whatToImprove": first_finding(issue).get("why", "Make the issue easier to understand and verify."),
                "suggestedNextEdit": first_finding(issue).get("nextEdit", "Add the missing issue detail."),
                "suggestedTitle": "",
                "suggestedDefinitionOfDone": "",
                "suggestedAcceptanceCriteria": [],
            }
            for issue in flagged
        ],
    }


def first_finding(issue):
    return (issue.get("findings") or [{}])[0]


def extract_response_text(response):
    if response.get("output_text"):
        return extract_json_object(response["output_text"])
    chunks = []
    for item in response.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                chunks.append(content["text"])
    if not chunks:
        raise RuntimeError("response did not include output text")
    return extract_json_object("\n".join(chunks))


def extract_json_object(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise RuntimeError("no JSON object found")
    return text[start : end + 1]
