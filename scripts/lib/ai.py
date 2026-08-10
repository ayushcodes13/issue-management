"""Azure OpenAI SOP review for all active Linear issues.

This module does not run deterministic hygiene checks. It sends the local SOP
Markdown plus all fetched active issues to Azure OpenAI and asks for cautious,
gentle suggestions. The model may return zero or more issue notes, but the
report must not treat omitted issues as "clean".
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
DEFAULT_AZURE_TIMEOUT_SECONDS = 600
DEFAULT_SOP_DOC_PATH = "docs/how-we-use-linear.md"

NETWORK_ERRORS = (TimeoutError, urllib.error.URLError, ConnectionError)


def review_issues_with_ai(issues):
    config = azure_config()
    if not config["api_key"]:
        return no_review("AZURE_OPENAI_API_KEY is not set")

    prompt = build_prompt(issue_payloads(issues), load_sop_text())
    try:
        body = request_azure_response(config, prompt)
    except NETWORK_ERRORS as exc:
        return no_review(f"Azure OpenAI network error: {exc}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return no_review(f"Azure OpenAI API failed with HTTP {exc.code}: {detail[:500]}")

    try:
        parsed = json.loads(extract_response_text(json.loads(body)))
    except (json.JSONDecodeError, RuntimeError) as exc:
        return no_review(f"Could not parse Azure OpenAI response: {exc}")

    parsed.setdefault("teamThemes", [])
    parsed.setdefault("ownerNotes", [])
    parsed.setdefault("issueNotes", [])
    parsed.setdefault("positiveExample", {})
    parsed["source"] = "azure-openai"
    return parsed


def findings_from_analysis(issues, analysis):
    issues_by_id = {issue.get("identifier"): issue for issue in issues}
    findings = []
    for note in analysis.get("issueNotes", []):
        issue_id = note.get("issueId")
        issue = issues_by_id.get(issue_id)
        if not issue:
            continue
        findings.append(
            {
                "issueId": issue_id,
                "title": issue.get("title"),
                "url": issue.get("url"),
                "owner": owner_of(issue),
                "status": status_of(issue),
                "severity": note.get("severity") or "gentle_suggestion",
                "tier": note.get("tier") or infer_tier(note),
                "category": note.get("category") or "ai_sop_suggestion",
                "noticed": note.get("currentRead") or "This issue may benefit from a small SOP cleanup.",
                "why": note.get("whatToImprove") or "The SOP review found a possible improvement.",
                "nextEdit": note.get("suggestedNextEdit") or "Make the smallest useful edit.",
                "confidence": note.get("confidence") or "medium",
                "sopSection": note.get("sopSection") or "docs/how-we-use-linear.md",
            }
        )
    return findings


def infer_tier(note):
    severity = note.get("severity")
    category = (note.get("category") or "").lower()
    if severity == "needs_fix":
        return "should_have"
    if any(key in category for key in ("description", "acceptance", "definition", "done", "scope", "in_progress_limit")):
        return "should_have"
    if any(key in category for key in ("label", "priority")):
        return "nice_to_have"
    return "nice_to_have" if severity == "gentle_suggestion" else "should_have"


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
    with urllib.request.urlopen(request, timeout=config["timeout_seconds"]) as response:
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
        "timeout_seconds": int(os.environ.get("AZURE_OPENAI_TIMEOUT_SECONDS", str(DEFAULT_AZURE_TIMEOUT_SECONDS))),
    }


def azure_responses_url(endpoint, api_version):
    return f"{endpoint.rstrip('/')}/openai/responses?api-version={quote(api_version)}"


def issue_payloads(issues):
    payloads = []
    for issue in issues:
        description = (issue.get("description") or "").strip()
        if len(description) > 1500:
            description = description[:1500] + "\n...[truncated]"
        payloads.append(
            {
                "identifier": issue.get("identifier"),
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
            }
        )
    return payloads


def load_sop_text():
    path = Path(os.environ.get("SOP_DOC_PATH", DEFAULT_SOP_DOC_PATH))
    if not path.exists():
        raise RuntimeError(f"SOP doc not found: {path}")
    return path.read_text(encoding="utf-8")


def build_prompt(issues, sop_text):
    return f"""You are running a lightweight weekly Linear issue-management review for Bynd.

The only source of truth is the local SOP document below. Do not introduce checks, advice, or rules that are not stated in this document.

Review all active issues provided. Return only useful suggestions; do not claim omitted issues are clean or compliant. Be cautious: if a problem is uncertain, phrase it as "worth checking" and use low or medium confidence.

Important tone rules:
- Do not shame people.
- Do not use words like violation, non-compliant, wrong, invalid, bad issue, failed, worst, or offender.
- Prefer concrete one-line edits.
- Keep recommendations small enough to act on quickly.
- Silence is better than noise. Only return an issue note when the nudge is genuinely useful.

Priority tiers:
- should_have: Todo or In Progress items missing description, Definition of done, or Acceptance criteria; issues that should move back to Backlog until scoped; or more than 3 In Progress items for one owner.
- nice_to_have: missing labels or missing priority.
- future_only: cross-referencing GitHub activity against tickets is a future idea; do not create findings for it yet.

Message tone guidance:
- If an owner only has nice_to_have findings, make the owner note praise-first and light.
- If an owner has should_have findings, make the issue note direct but gentle.
- If an owner has no genuinely useful issue-level nudge and their Linear issues look healthy enough, include a positive owner note with messageKind "positive_no_action". It should sound human, e.g. "good work this week, nothing to do in Linear from this review."
- Do not force positive notes for everyone. Only include them when there is a real basis in the issues reviewed.

Return only valid JSON in this exact shape:
{{
  "teamThemes": ["theme 1", "theme 2", "theme 3"],
  "positiveExample": {{
    "issueId": "BYN-123",
    "title": "issue title",
    "url": "issue URL",
    "why": "one sentence explaining what is worth copying"
  }},
  "ownerNotes": [
    {{
      "owner": "Name",
      "messageKind": "positive_no_action|light_suggestion|context_only",
      "summary": "one sentence",
      "suggestedFocus": ["action 1", "action 2"]
    }}
  ],
  "issueNotes": [
    {{
      "issueId": "BYN-123",
      "severity": "needs_fix|should_improve|gentle_suggestion",
      "tier": "should_have|nice_to_have",
      "category": "short_snake_case_category",
      "confidence": "high|medium|low",
      "sopSection": "short name of the relevant SOP section",
      "currentRead": "one sentence",
      "whatToImprove": "one sentence",
      "suggestedNextEdit": "one concrete edit",
      "suggestedTitle": "optional better title or empty string",
      "suggestedDefinitionOfDone": "optional sentence or empty string",
      "suggestedAcceptanceCriteria": ["optional criterion"]
    }}
  ]
}}

Active Linear issues:
{json.dumps(issues, indent=2)}

Local SOP document:
{sop_text}
"""


def no_review(reason):
    return {
        "source": "no-ai-review",
        "fallbackReason": reason,
        "teamThemes": [
            "No SOP review was generated because Azure OpenAI was unavailable. This run should not be treated as a hygiene result."
        ],
        "positiveExample": {},
        "ownerNotes": [],
        "issueNotes": [],
    }


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
