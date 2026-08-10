"""Azure OpenAI proposal generation for API-based work-memory runs."""

import json
import urllib.error
from pathlib import Path

from lib.ai import azure_config, extract_response_text, request_azure_response
from lib.linear import labels_of, owner_of, priority_of, status_of


DEFAULT_SOP_DOC_PATH = "docs/how-we-use-linear.md"


def generate_work_memory_proposals(notes, issues, since_iso, meeting_limit):
    config = azure_config()
    if not config["api_key"]:
        return fallback_result("AZURE_OPENAI_API_KEY is not set", since_iso, meeting_limit)

    issue_context = issue_payloads(issues)
    sop_text = load_sop_text()
    prompt = build_prompt(notes, issue_context, sop_text, since_iso, meeting_limit)
    try:
        body = request_azure_response(config, prompt)
    except (TimeoutError, urllib.error.URLError, ConnectionError) as exc:
        return fallback_result(f"Azure OpenAI network error: {exc}", since_iso, meeting_limit)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return fallback_result(f"Azure OpenAI API failed with HTTP {exc.code}: {detail[:500]}", since_iso, meeting_limit)

    try:
        response = json.loads(body)
        output_text = extract_response_text(response)
        parsed = json.loads(output_text)
    except (json.JSONDecodeError, RuntimeError) as exc:
        return fallback_result(f"Could not parse Azure OpenAI response: {exc}", since_iso, meeting_limit)

    parsed.setdefault("runSummary", {})
    parsed.setdefault("proposals", [])
    parsed.setdefault("limitations", [])
    parsed["tokenUsage"] = build_token_usage(notes, issue_context, sop_text, prompt, output_text, response)
    parsed["source"] = "azure-openai"
    return parsed


def issue_payloads(issues):
    payloads = []
    for issue in issues:
        description = (issue.get("description") or "").strip()
        if len(description) > 1200:
            description = description[:1200] + "\n...[truncated]"
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
    path = Path(DEFAULT_SOP_DOC_PATH)
    if not path.exists():
        raise RuntimeError(f"SOP doc not found: {path}")
    return path.read_text(encoding="utf-8")


def build_prompt(notes, issues, sop_text, since_iso, meeting_limit):
    return f"""You are Bynd's scheduled Work Memory proposal generator.

This is the production API path. Do not assume Codex, MCP, browser OAuth, Slack, or human-local context exists.

Inputs:
- Granola notes fetched through the Granola API since {since_iso}
- Active Linear issues fetched through the Linear GraphQL API
- Bynd's Linear SOP below

Your task:
Extract the concrete work mentioned in the meeting, assign it to the right
person, compare it with Linear, and create useful draft proposals.

The output will be turned into a Slack DM, so use simple human wording and avoid internal labels in any user-facing text.
DMs should be short enough for busy people to read. Each proposal becomes one
line in Slack: short todo + short Linear follow-up. Avoid long explanations,
repeated wording, or questions like "Should I add...".

Coverage rule:
- Prioritize recall over brevity. Missing a concrete task is worse than sending
  one extra review item.
- Do not collapse unrelated workstreams just because the same person owns them.
- If one person has four distinct tasks, create four proposals for that person.
- Create a separate proposal for a person only when they are the likely owner:
  they said they are doing it, someone assigned it to them, they are blocked on
  it, or the work clearly sits in their current ownership.
- A person being mentioned as context, as the source of examples, as a reviewer,
  or inside another person's task is not enough to make them the owner.
- If a task says another person should do it, assign it to that other person
  even if the topic concerns someone else's work.
- If a person says they need input, examples, data, files, access, or a review
  from someone else, assign the "send/provide/share/review" follow-up to the
  person expected to provide it. Only assign the downstream work to the requester
  if the downstream work is also clearly active and worth tracking.
- When you split that dependency, do not duplicate the provider's task in the
  requester's wording. For example, if Devayush must send full markdown to
  Piyush, Devayush's proposal can say "share the full markdown"; Piyush's
  separate proposal should say "build the regression set from the latest
  validation results". Do not tell Piyush to "use full markdown" in
  mentionedTodo, evidenceSummary, suggestedSlackMessage, or draftText; if the
  dependency must be mentioned, phrase it as "after receiving full markdown from
  Devayush".
- If ownership is unclear, set owner to "Unassigned" and category to
  "needs_human_review" instead of guessing.
- Keep related sub-tasks together only when they are clearly part of the same
  outcome.

Safety:
- Do not say anything was changed.
- Do not recommend backfilling already finished work.
- Do not create noise from vague standup chatter.
- Treat the output as proposals requiring human approval.
- Use paraphrased evidence only. Do not include transcript-style detail.

Useful proposal categories:
- add_context_to_existing_issue
- create_new_linear_issue
- already_in_linear
- not_linear_worthy
- needs_human_review

Prefer:
- explicit Linear issue IDs mentioned in notes
- exact title/project/owner matches
- transcript speaker cues when transcript_text is present
- concrete decisions, blockers, scope changes, owner changes, deadlines, benchmark results, client-facing problems, or important follow-ups
- separate proposals for separate workstreams, such as delivery cleanup,
  regression/eval set work, architecture comparison, taxonomy review, or
  report-structure work

Suppress:
- casual status updates with no decision
- "we should think about"
- brainstorming
- unclear/garbled notes
- work that is already done and should not be backfilled
- completed status updates that have no next action, such as "no new follow-up"

Do not suppress:
- work that sounds urgent or was requested "today"
- work that compares quality/cost/token impact
- work that builds or reviews eval/regression examples
- work that needs full source/markdown context
- work that updates how output labels or taxonomy are shown to users

Return only valid JSON in this exact shape:
{{
  "runSummary": {{
    "meetingsConsidered": 0,
    "linearIssuesReviewed": 0,
    "proposalCount": 0,
    "mainThemes": ["theme"]
  }},
  "proposals": [
    {{
      "id": "stable-id",
      "category": "add_context_to_existing_issue|create_new_linear_issue|already_in_linear|not_linear_worthy|needs_human_review",
      "confidence": "high|medium|low",
      "owner": "person or Unassigned",
      "sourceMeetingIds": [],
      "sourceMeetingTitles": [],
      "mentionedTodo": "plain-language task or update from the standup that mentioned this person",
      "workingOn": "plain-language summary of what this person appears to be working on, or empty string if unclear",
      "targetLinearIssue": {{
        "identifier": "",
        "title": "",
        "url": ""
      }},
      "evidenceSummary": "short paraphrase only",
      "rationale": "why this category was chosen",
      "suggestedSlackMessage": "short declarative message for the owner, not a question",
      "proposedLinearChange": {{
        "action": "none|add_comment|create_issue|update_issue",
        "draftText": ""
      }},
      "requiresApproval": true,
      "status": "draft"
    }}
  ],
  "limitations": []
}}

Granola note payloads, capped to {meeting_limit} detail records:
{json.dumps(notes, indent=2)}

Active Linear issues:
{json.dumps(issues, indent=2)}

Linear SOP:
{sop_text}
"""


def fallback_result(reason, since_iso, meeting_limit):
    return {
        "source": "no-ai-review",
        "fallbackReason": reason,
        "runSummary": {
            "meetingsConsidered": 0,
            "linearIssuesReviewed": 0,
            "proposalCount": 0,
            "mainThemes": ["No work-memory proposals were generated because the AI review was unavailable."],
        },
        "proposals": [],
        "limitations": [reason, f"Requested since={since_iso}, meeting_limit={meeting_limit}"],
    }


def build_token_usage(notes, issues, sop_text, prompt, output_text, response):
    granola_json = json.dumps(notes, indent=2)
    linear_json = json.dumps(issues, indent=2)
    prompt_overhead_chars = max(0, len(prompt) - len(granola_json) - len(linear_json) - len(sop_text))
    usage = response.get("usage") or {}
    return {
        "estimateMethod": "chars_div_4_approximation_for_breakdown; provider_usage_when_available_for_actual_totals",
        "estimatedBreakdown": {
            "granola": token_size(granola_json),
            "linear": token_size(linear_json),
            "sop": token_size(sop_text),
            "promptInstructionsAndTemplate": token_size_by_chars(prompt_overhead_chars),
            "fullPrompt": token_size(prompt),
            "output": token_size(output_text),
        },
        "providerUsage": usage,
    }


def token_size(text):
    return {
        "chars": len(text or ""),
        "approxTokens": approx_tokens(text or ""),
    }


def token_size_by_chars(chars):
    return {
        "chars": chars,
        "approxTokens": approx_tokens_from_chars(chars),
    }


def approx_tokens(text):
    return approx_tokens_from_chars(len(text or ""))


def approx_tokens_from_chars(chars):
    if chars <= 0:
        return 0
    return max(1, round(chars / 4))
