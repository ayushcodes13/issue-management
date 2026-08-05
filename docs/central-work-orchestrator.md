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

linear_links
- id
- finding_id
- linear_issue_id
- relationship

github_links
- id
- finding_id
- repo
- pr_number
- relationship

approvals
- id
- finding_id
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

## Linear Write Policy

V1 should allow only approval-based writes:

- Add a comment to an existing Linear issue.
- Create a new Linear issue in Backlog.
- Add a Granola note link to a Linear comment.
- Add a GitHub PR link to a Linear comment.

V1 should not automatically:

- Change issue status.
- Change assignee.
- Change priority.
- Change project.
- Close issues.

Those can be suggested, but not applied automatically.

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
- On approval, write Linear comment or create Backlog issue.
- Store audit event.

### Phase 5: Webhooks And More Integrations

- Add Granola webhooks for note changes.
- Add Linear webhooks for issue changes.
- Add GitHub webhooks for PR events.
- Add more integrations through adapter interfaces.

## Open Decisions

1. Is Bynd moving to Granola Business or Enterprise?
2. Will there be a workspace API key?
3. Which spaces/folders should be API-readable?
4. Should 1:1 business meetings be included by default?
5. Should v1 create new Linear issues, or only comment on existing issues?
6. Which GitHub repositories are in scope?
7. Should Slack approval use buttons or text replies first?
8. Should v1 run on GitHub Actions or Azure Container App Job?

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
What is the best v1 architecture for a central service that ingests Granola notes, Linear issues, and GitHub PRs, then sends Slack approval messages for suggested Linear updates?

Timebox:
1 day

Output:
A short architecture proposal covering Granola access model, data store, orchestration flow, Slack approval UX, Linear write policy, GitHub PR signals, deployment option, and phased rollout.

Acceptance criteria:
- Confirm Granola Business/Enterprise API requirement.
- Decide whether v1 uses workspace API key, shared Team space, or per-user keys.
- Define v1 ingestion flow for Granola, Linear, and GitHub.
- Define central data model for meetings, findings, approvals, and links.
- Define Slack approval flow before Linear writes.
- Define which Linear updates are allowed in v1.
- Define GitHub PR signals included in v1.
- Recommend deployment target: Azure Container App Job vs GitHub Actions.
- Produce phased rollout plan from read-only report to approval-based Linear updates.
```
