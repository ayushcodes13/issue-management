# Central Work Orchestrator

## Working Prompt

We want to build a centralized work-memory service for Bynd.

The service should fetch context from Granola, Linear, GitHub, Slack, and future tools, bring that context into one orchestrator, reason over it, and send useful Slack messages to the right people. It should help keep Linear up to date with what was actually discussed and delivered.

The problem is that important work context is scattered:

- Granola has meeting notes, transcripts, decisions, action items, blockers, and handoffs.
- Linear has planned work, owners, priorities, projects, comments, and status.
- GitHub has implementation and delivery signals through PRs, reviews, commits, and merges.
- Slack is where people should receive short approval messages and nudges.

The service should run on a schedule at first. Every week it should:

1. Fetch recent company meeting notes from Granola.
2. Fetch relevant Linear issues and projects.
3. Fetch GitHub PRs and delivery signals from selected repositories.
4. Use an AI reasoning layer to identify what matters.
5. Decide whether each finding is already reflected in Linear, should update an existing issue, should become a new issue, should be linked to a GitHub PR, or should be ignored.
6. Send concise Slack messages to the relevant person for approval.
7. Update Linear only after approval.
8. Store an audit trail so the same suggestion is not repeated.

The end state is a second brain across Granola, Linear, GitHub, and Slack:

- Granola is the source of meeting truth.
- Linear is the source of planned work.
- GitHub is the source of delivery truth.
- Slack is the approval and notification surface.
- The orchestrator is the memory and reasoning layer.

The system should be modular because more integrations will be added over time.

The central product object is a proposal:

```text
Proposal = an evidence-backed suggested mutation or no-op decision.
```

The service should not be framed as "AI creates tasks from meetings." It should
be framed as:

```text
A weekly safety net that catches meeting decisions missing from Linear.
```

## Research Findings

### Granola

Granola API is the correct production ingestion path for a scheduled service.

Important points from the Granola docs:

- API keys are for scripts, automations, and custom integrations.
- API keys are available on Business and Enterprise plans.
- Workspace API keys are created by workspace admins.
- Workspace API keys belong to the workspace, not an individual person.
- Workspace API keys can read public notes and spaces where Granola API access is enabled.
- Workspace API keys cannot read arbitrary private notes unless those notes are exposed through allowed scopes or API-enabled spaces.
- Granola webhooks are available on Business and Enterprise plans and can notify a service when notes change.
- Granola MCP is browser OAuth based and connects as an individual user.

Implication:

For a company-wide scheduled service, use Granola Business or Enterprise with a workspace API key and API-enabled spaces. Do not design the main production system around every employee giving a personal key.

### Linear

Linear has two useful surfaces:

- GraphQL API and webhooks for stable backend automation.
- Linear MCP for AI-agent workflows in clients like Claude, Cursor, and Codex.

Implication:

Use Linear API for the central backend service. Use Linear MCP for prototyping, debugging, or supervised agent workflows.

### GitHub

GitHub has REST API, GraphQL API, and webhooks.

Useful v1 signals:

- Open PRs.
- PR author.
- Review status.
- Merge state.
- Branch name.
- Linked Linear issue IDs in title, body, branch, or commit messages.
- Recent merged PRs.
- Failing checks, if needed later.

Implication:

Start with GitHub REST or GraphQL polling for selected repos. Add GitHub webhooks later when the system needs near-real-time delivery signals.

### Slack

Slack is the approval surface, not the source of truth.

Useful v1 capabilities:

- Send short DMs or channel messages.
- Use buttons for approve, ignore, edit later.
- Use signed request verification for interactive actions.
- Keep public messages aggregated and non-blaming.

Implication:

Slack should receive proposed actions. Linear should only be updated after explicit approval in v1.

### MCP vs API

MCP is good for the agent experience:

- Claude/Codex can query Granola.
- Claude/Codex can query Linear.
- A human can supervise reasoning and actions.

API is better for production automation:

- Works on a schedule.
- Uses service credentials.
- Easier to monitor and retry.
- Better for central storage and audit trails.
- Less dependent on one user's browser OAuth session.

Recommendation:

- Prototype with MCP if useful.
- Build production around APIs and webhooks.

### Low-Cost MCP-First Option

If Granola Business or Enterprise is too expensive for now, an MCP-first v1 is possible.

This should be treated as a low-cost prototype, not the final backend shape.

How it would work:

```text
Each teammate uses Granola Basic or their existing Granola account
  -> each teammate connects Granola MCP in Claude
  -> a shared Claude workflow/prompt reviews that person's last 7 days of notes
  -> Claude compares those notes with Linear through Linear MCP
  -> Claude drafts Slack/Linear suggestions
  -> the person or Devayush approves before anything is written
```

Important constraints:

- Granola MCP is per-user browser OAuth.
- It is not a workspace service account.
- A central scheduled job cannot magically access every teammate's personal MCP connection.
- On Basic, Granola MCP access is limited compared with paid plans, including recent-note limits and paid-only tools such as some folder/transcript access.
- If multiple people record the same meeting, the workflow needs dedupe.
- If someone does not connect or run the workflow, their notes are invisible.
- It is harder to store central audit history unless we add a shared database or repository output.

There are two workable MCP-first variants:

1. Personal MCP runs:

```text
Each person runs the Claude/Granola/Linear workflow for their own notes.
Claude sends suggested Slack/Linear updates.
This is cheapest but least centralized.
```

2. Shared Basic workspace experiment:

```text
Everyone records or shares business notes into one shared Granola workspace/folder.
One service account or shared Claude session connects to that workspace through MCP.
The weekly workflow reviews the shared workspace notes.
```

The shared workspace experiment only works if Granola Basic allows the required shared workspace/folder behavior and if the notes needed by the workflow are visible to the connected MCP user. It still remains user-OAuth based, so it is weaker than a workspace API key.

Recommended low-cost v1:

```text
Use MCP for a manual weekly pilot.
Keep a shared output folder in GitHub for reports.
Use Linear MCP for read/write after approval.
Use Slack manually or through the existing Slack app for previews.
Do not promise full company coverage until the Granola access model is proven.
```

This repo now implements the daily standup API path as:

```bash
./run_daily_standup_memory.sh
```

The command uses Granola API, Linear GraphQL API, and Azure OpenAI. It processes
exactly one note: today's `Daily-Standup` in `Asia/Kolkata`, waits for the note
and transcript to stabilize, then writes read-only draft proposal artifacts
under:

```text
results/daily-standup-memory/
```

The daily run deliberately does not send Slack messages and does not mutate
Linear. It only creates draft proposals for human review.

Decision rule:

```text
If the goal is "cheap proof of concept", use MCP.
If the goal is "reliable company-wide scheduled service", use Granola API/workspace key.
```

## Recommended Architecture

```text
Granola API / webhooks
  -> ingestion adapter

Linear API / webhooks
  -> work adapter

GitHub API / webhooks
  -> delivery adapter

Slack API / interactivity
  -> approval adapter

All adapters
  -> central orchestrator
  -> AI reasoning layer
  -> database
  -> Slack approvals
  -> approved Linear updates
```

The core pipeline:

1. Ingest raw evidence from Granola, Linear, and GitHub.
2. Normalize into canonical meetings, work items, PRs, people, and facts.
3. Resolve identities across Slack, Linear, GitHub, and Granola.
4. Match meeting facts to Linear and GitHub context.
5. Generate proposals.
6. Send Slack approval cards.
7. Mutate Linear only after approval.
8. Store audit and idempotency records permanently.

The orchestrator owns relationships between systems, not the source data itself.
Granola remains meeting truth, Linear remains planned-work truth, GitHub remains
delivery truth, and Slack remains the approval surface.

Suggested pipeline stages:

```text
Scheduler or webhook receiver
  -> connector fetch
  -> normalization
  -> correlation
  -> reasoning/classification
  -> dedup/audit lookup
  -> proposal store
  -> Slack notifier
  -> approval handler
  -> action executor
  -> audit log
```

Weekly is a schedule, not the architecture. Model each execution as:

```text
Run(since, until, scope)
```

At launch, a weekly cron creates a broad run. Later, Granola, Linear, and GitHub
webhooks can create scoped runs for one note, one issue, or one PR without
rewriting the rest of the pipeline.

## Connector Interface

Connectors should be plugins with a small shared interface. The orchestrator
should not hardcode Granola or Linear behavior outside connector registration.

```python
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class Connector(ABC):
    name: str

    @abstractmethod
    async def fetch_since(self, since: datetime) -> list[dict[str, Any]]:
        """Return raw records created or updated since the given timestamp."""

    @abstractmethod
    def normalize(self, raw: dict[str, Any]) -> "WorkSignal | EntitySnapshot":
        """Convert raw payload into the canonical model."""

    async def write(self, action: "ProposedAction") -> "ActionResult":
        raise NotImplementedError(f"{self.name} connector is read-only")
```

Concrete connectors:

- `GranolaConnector`: read-only meeting notes, summaries, transcripts, attendees, timestamps, links.
- `LinearConnector`: read and write issues, projects, comments, assignees, labels, priorities, statuses.
- `GitHubConnector`: read PRs, commits, reviews, merge state, branch names, Linear references.
- `SlackConnector`: resolve identities, send approval messages, receive button/modal responses.

Future connectors should implement the same interface and emit the same canonical
types.

## Deployment Recommendation

Use Azure for the real service.

V1 can be:

```text
Azure Container App Job
  scheduled weekly
  reads from APIs
  writes reports and Slack suggestions
```

When Slack approval buttons are added:

```text
Azure Container App or Azure Function HTTP endpoint
  receives Slack interactivity
  verifies Slack signature
  applies approved Linear updates
```

GitHub Actions is acceptable for a quick proof of concept, but it is less ideal once Slack interactivity and persistent state become important.

## Recommended Stack

Use Python for the first implementation.

```text
Language: Python 3.12+
Web/API framework: FastAPI
Scheduler: Azure Container App Job, Kubernetes CronJob, or APScheduler for local MVP
Queue later: Celery/Arq + Redis, or cloud queue if already available
Database: Postgres + pgvector
ORM: SQLAlchemy 2.x or SQLModel
Slack: Slack Bolt for Python
Linear: GraphQL API/SDK
GitHub: GitHub App + Octokit-compatible API calls or PyGithub/httpx
Granola: REST API first, MCP only for prototype
LLM: Claude or Azure OpenAI with structured JSON output
Observability: structured logs with run_id/proposal_id, Sentry/OpenTelemetry later
Secrets: cloud secret manager, never committed env files
```

## Data Model

Use Postgres for production. SQLite is acceptable for a local demo.

Core tables:

```text
integration_runs
- id
- started_at
- finished_at
- status
- source_window_start
- source_window_end

meetings
- id
- granola_note_id
- title
- date
- owner
- attendees
- granola_url
- transcript_hash
- raw_payload_uri

linear_issues_snapshot
- id
- linear_issue_id
- identifier
- title
- state
- assignee
- labels
- project
- url
- fetched_at

github_prs_snapshot
- id
- repo
- pr_number
- title
- author
- state
- review_state
- merge_state
- url
- fetched_at

findings
- id
- run_id
- source_type
- source_id
- owner
- category
- confidence
- evidence
- suggested_action
- status

proposals
- id
- proposal_type
- target_linear_issue_id
- slack_approver_user_id
- confidence
- rationale
- evidence_quotes
- proposed_linear_payload
- idempotency_key
- status
- created_at
- decided_at

linear_links
- id
- proposal_id
- linear_issue_id
- relationship

github_links
- id
- proposal_id
- repo
- pr_number
- relationship

approvals
- id
- proposal_id
- slack_user_id
- slack_channel_id
- slack_message_ts
- status
- approved_text
- decided_at

audit_events
- id
- actor
- action
- target_type
- target_id
- payload
- created_at
```

Canonical model:

```text
EntitySnapshot
- source: granola | linear | github | slack
- external_id
- entity_type: linear_issue | github_pr | meeting | slack_message
- title
- body
- status
- assignee
- labels
- priority
- url
- updated_at
- raw_payload_uri

WorkSignal
- id: deterministic hash of source + source_ref + normalized text
- source
- source_ref
- signal_type: action_item | decision | blocker | ownership_change | delivery_event | benchmark_result | scope_change
- text
- people
- project_hint
- occurred_at
- extracted_at
- embedding
```

Proposal fields should include:

```text
proposal_type: add_comment | create_issue | update_issue | noop | ignore
target Linear issue, if any
source Granola note ids
related GitHub PRs
evidence quotes
confidence
rationale
proposed Linear payload
Slack approver
status
idempotency key
audit trail
```

## Finding Categories

The AI reasoning layer should classify each item as:

```text
already_in_linear
add_context_to_existing_issue
create_new_linear_issue
link_github_pr_to_linear
linear_ticket_stale
owner_or_scope_changed
not_linear_worthy
needs_human_review
```

Lower-level classifier categories:

```text
missing_from_linear
needs_context_added
issue_outdated
already_correct
ignore_too_small
```

Correlation should combine:

- explicit Linear issue IDs in meetings or PRs
- branch/PR/title/body references to Linear IDs
- attendee/assignee/PR-author overlap
- project/team scope
- recent activity
- semantic similarity through embeddings

Use embeddings for candidate generation, not as final truth. The final proposal
still needs an evidence quote, target issue, confidence, and rationale.

Vague items should be suppressed aggressively.

Ignore:

- "Let's sync later."
- "Maybe we should."
- "We should think about."
- "Follow up sometime."
- generic brainstorming
- repeated status with no delta

Keep:

- owner changed
- blocker discovered or resolved
- implementation decision
- deadline changed
- PR merged but Linear is stale
- scope changed
- benchmark/result affects work
- concrete new work missing from Linear

## Slack Message Shape

Per-person DM:

```text
Hey <name>, I reviewed this week's Granola notes, Linear tickets, and GitHub PRs.

I found <n> possible updates for you.

1. <meeting or PR title>
Likely Linear issue: <issue id or "none found">
Suggestion: <one-line update>

Reply:
- yes 1
- ignore 1
- edit 1: <your wording>
```

Public/channel summary:

```text
Weekly work-memory check

Reviewed <n> Granola notes, <n> Linear issues, and <n> GitHub PRs.
Found <n> possible Linear updates.
Sent short approval messages to the relevant owners.

Nothing was changed in Linear without approval.
```

Approval card actions:

- Approve
- Edit
- Wrong ticket
- Already handled
- Ignore
- Snooze

Rejection reasons:

- Already captured
- Not real work
- Wrong issue
- Too vague
- Wrong owner
- Low priority

Approval behavior:

- `Approve`: execute the exact proposed action.
- `Edit`: open a modal pre-filled with the proposed comment or payload.
- `Wrong ticket`: let the approver choose a different Linear issue.
- `Already handled`: log rejection and suppress future duplicates.
- `Ignore`: log rejection and suppress future duplicates.
- `Snooze`: keep pending but do not resend until the snooze expires.

If one person has too many proposals, batch them into one digest instead of
sending many separate DMs.

## Linear Write Policy

V1 should allow only approval-based writes:

- Add a comment to an existing Linear issue.
- Add a Granola note link to a Linear comment.
- Add a GitHub PR link to a Linear comment.

V1 should not automatically:

- Create new Linear issues.
- Change issue status.
- Change assignee.
- Change priority.
- Change project.
- Close issues.

Those can be suggested, but not applied automatically.

Best initial allowed mutation:

```text
Add comment only.
```

Example comment:

```text
Meeting context from Granola - Aug 5

Decision:
Retry dedupe should happen at the proposal level, not just the job level.

Relevant context:
- Alice will add a dedupe key using source note + target issue + mutation type.
- Bob flagged that failed Slack approvals should not retry mutations automatically.

Source:
Granola note: Agent Runtime Weekly Sync
Related GitHub PR: #456

Added by Bynd Work Memory after approval from @alice.
```

Rules:

- No proposal without evidence.
- No Linear write without approval.
- No create issue without owner and deliverable.
- No field update without explicit evidence.
- No duplicate proposal if the audit log says rejected, applied, or ignored.
- No Slack spam.
- No full meeting dumps into Linear.

Action executor invariant:

```text
The executor must only consume approved or edited proposals from the proposal
store. It must never consume raw classifier output directly.
```

Allowed v1 executor action:

```text
AddComment(issue_id, text, links=[granola_url, github_url])
```

## Rollout Plan

### Phase 0: Confirm Access

- Confirm Bynd has or will get Granola Business or Enterprise.
- Confirm whether a workspace API key can be created.
- Confirm which Granola spaces have API access enabled.
- Confirm selected GitHub repos.
- Confirm Linear API key permissions.
- Confirm Slack app scopes.

### Phase 1: Read-Only Weekly Report

- Fetch Granola notes from a fixed date range.
- Fetch active Linear issues.
- Fetch GitHub PRs from selected repos.
- Produce a Markdown and JSON report.
- Do not send Slack.
- Do not write Linear.

MVP constraints:

- One pilot team/project.
- Max 10 suggestions per week.
- Max 3 suggestions per person per week.
- Existing issue comment proposals only.
- Require a source quote for every proposal.

### Phase 1.5: Quality Calibration

- Build a small evaluation set from 30-50 real meeting-derived signals.
- Track whether each generated proposal was useful, wrong-ticket, duplicate,
  too vague, or already handled.
- Tune confidence thresholds before enabling writes.

### Phase 2: Slack Preview

- Send one preview message to Devayush/Mrinal.
- Include public summary and per-person draft messages.
- No Linear writes.

### Phase 3: Slack DMs

- Send per-person suggestions.
- Track sent suggestions.
- No Linear writes yet.

### Phase 4: Approval-Based Linear Writes

- Add Slack approval handling.
- On approval, write Linear comments only.
- Store audit event.

### Phase 5: Webhooks And More Integrations

- Add Granola webhooks for note changes.
- Add Linear webhooks for issue changes.
- Add GitHub webhooks for PR events.
- Add more integrations through adapter interfaces.

Later expansion:

- Create issue proposals.
- Slack edit modal.
- Field update proposals for assignee, status, priority, and due date.
- Stronger evidence gates for any field mutation.
- Daily or event-driven runs after the weekly batch is trusted.

## Four-Week Build Plan

Week 1:

- Granola connector.
- Linear connector.
- Slack app.
- Postgres schema.
- Weekly job.
- Raw evidence store.

Week 2:

- Meeting fact extraction.
- Linear issue matching.
- Proposal generation.
- Idempotency keys.
- Slack approval cards.

Week 3:

- Linear comment executor.
- Audit log.
- Approval state machine.
- Dry-run mode.
- Pilot team config.

Week 4:

- GitHub App.
- PR-to-Linear linkage.
- Stale/delivery mismatch proposals.
- Evaluation set from 30-50 real meetings.

## Success Metrics

- More than 60% proposal approval rate after calibration.
- Less than 10% wrong-ticket rate.
- Less than 5% duplicate suggestions.
- Less than 3 suggestions per person per week.
- Clear rejection reason distribution.
- Zero unapproved Linear writes.

## Open Decisions

1. Is Bynd moving to Granola Business or Enterprise?
2. Will there be a workspace API key?
3. Which spaces/folders should be API-readable?
4. Should 1:1 business meetings be included by default?
5. Should v1 create new Linear issues, or only comment on existing issues?
6. Which GitHub repositories are in scope?
7. Should Slack approval use buttons or text replies first?
8. Should v1 run on GitHub Actions or Azure Container App Job?
9. Should the system be called Bynd Work Memory?
10. What is the precedence for Slack recipient: Linear assignee, meeting owner,
    action owner, or GitHub PR author?
11. Which meeting types are excluded as sensitive?
12. What happens when valid proposals are ignored for multiple runs?

## First Linear Ticket Draft

Title:
Design v1 centralized work-memory service for Granola, Linear, GitHub, and Slack

Type label:
Spike

Product labels:
Internal Tooling, Linear

Status:
Backlog

Owner:
Devayush Rout

Description:

```markdown
Question to answer:
What is the best v1 architecture for a proposal-driven central service that ingests Granola notes, Linear issues, and GitHub PRs, then sends Slack approval messages for evidence-backed Linear comment proposals?

Timebox:
1 day

Output:
A short architecture proposal covering Granola access model, data store, proposal model, orchestration flow, Slack approval UX, Linear write policy, GitHub PR signals, deployment option, and phased rollout.

Acceptance criteria:
- Confirm Granola Business/Enterprise API requirement.
- Decide whether v1 uses workspace API key, shared Team space, or per-user keys.
- Define v1 ingestion flow for Granola, Linear, and GitHub.
- Define central data model for meetings, proposals, approvals, and links.
- Define Slack approval flow before Linear writes.
- Define why v1 is comment-only for Linear writes.
- Define GitHub PR signals included in v1.
- Recommend deployment target: Azure Container App Job vs GitHub Actions.
- Produce phased rollout plan from read-only report to approval-based Linear updates.
```
