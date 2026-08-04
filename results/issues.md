# Issue Improvement Notes

Mode: `manual-preview`
Analysis source: `azure-openai`

This is AI-assisted. Treat suggestions as review prompts, not final judgement.

## BYN-11: Update DB to support project-in-poject architecture

- Owner: Unassigned
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-11/update-db-to-support-project-in-poject-architecture
- SOP section: Backlog-to-Todo
- Current read: This Todo item is empty, unassigned, has no priority, and does not show the outcome or checks.
- What to improve: Move it to Backlog until scoped, or add the required Todo details.
- Suggested next edit: Add owner, priority, Definition of done, Acceptance criteria, and labels before keeping it in Todo.
- Suggested title: Update DB to support project-in-project architecture

## BYN-19: Plan new architecture for agent flow

- Owner: Sanidhya
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-19/plan-new-architecture-for-agent-flow
- SOP section: Backlog-to-Todo
- Current read: This Todo item describes the architecture planning need, but not the expected planning output or acceptance checks.
- What to improve: Define the planning deliverable and how it will be reviewed.
- Suggested next edit: Add a Definition of done for the architecture plan and 2-3 checks for the document or recommendation.
- Suggested Definition of done: A proposed Chat agent architecture for 50+ documents is documented with the expected latency impact and next decision needed.
- Suggested Acceptance criteria:
  - The proposed fan-out and reduction approach is documented.
  - The plan states how it supports 50+ documents.
  - The expected latency impact and next decision are captured.

## BYN-35: Add support for Bi-Weekly newsletter runs

- Owner: Sanidhya
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-35/add-support-for-bi-weekly-newsletter-runs
- SOP section: Backlog-to-Todo
- Current read: This Todo item states the backend work, but the completion checks are not visible.
- What to improve: Add a Definition of done and Acceptance criteria for backend bi-weekly newsletter runs.
- Suggested next edit: Add checks for backend support and PropEquity cadence migration.
- Suggested Definition of done: Backend supports bi-weekly newsletter runs and PropEquity newsletters are shifted to the bi-weekly cadence.
- Suggested Acceptance criteria:
  - Bi-weekly newsletter runs can be scheduled on the backend.
  - PropEquity is configured to use the bi-weekly cadence.
  - A run or dry run confirms the cadence configuration.

## BYN-36: Add support for Bi-Weekly newsletter on Frontend

- Owner: Aditya Singh
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-36/add-support-for-bi-weekly-newsletter-on-frontend
- SOP section: Backlog-to-Todo
- Current read: This Todo item has a short description, but no Definition of done or Acceptance criteria.
- What to improve: Add the frontend outcome and checks for bi-weekly cadence setup.
- Suggested next edit: Add a Definition of done for configuring bi-weekly newsletters from the Intelligence frontend.
- Suggested Definition of done: Users can configure a bi-weekly newsletter cadence from the Intelligence frontend.
- Suggested Acceptance criteria:
  - Bi-weekly cadence is available in the frontend setup flow.
  - The selected cadence is saved.
  - The saved cadence is visible when the setup is reopened.

## BYN-43: Native-text vs OCR/scanned classification for Download Financials

- Owner: Unassigned
- Status: `In Progress`
- Link: https://linear.app/byndai/issue/BYN-43/native-text-vs-ocrscanned-classification-for-download-financials
- SOP section: Issue statuses
- Current read: This In Progress item has no owner assigned, so the active owner is not visible.
- What to improve: Make the owner explicit or move the item out of In Progress if no one is actively working on it.
- Suggested next edit: Assign the current owner; if there is no current owner, move it back to Todo or Backlog.

## BYN-44: Deterministic figure verification and highlighting in Download Financials

- Owner: Unassigned
- Status: `In Progress`
- Link: https://linear.app/byndai/issue/BYN-44/deterministic-figure-verification-and-highlighting-in-download
- SOP section: Issue statuses
- Current read: This In Progress item has no owner assigned, so the active owner is not visible.
- What to improve: Make the owner explicit or move the item out of In Progress if no one is actively working on it.
- Suggested next edit: Assign the current owner; if there is no current owner, move it back to Todo or Backlog.

## BYN-54: Change citation loading approach in chat view pane

- Owner: Sanidhya
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-54/change-citation-loading-approach-in-chat-view-pane
- SOP section: Definition of done
- Current read: This Todo item explains the proposed approach, but the finish line and checks are not explicit.
- What to improve: Add a Definition of done and Acceptance criteria for the citation loading change.
- Suggested next edit: Add checks for initial page-range loading and scroll-based pagination.
- Suggested Definition of done: Citation clicks initially load only the cited page range, with adjacent pages loaded as the user scrolls.
- Suggested Acceptance criteria:
  - Clicking a citation loads the cited page plus the intended buffer instead of the whole PDF.
  - Scrolling through the PDF loads additional pages as needed.
  - The cited page still renders correctly in the view pane.

## BYN-55: Data connectors broker architecture - PoC

- Owner: Shashank Rajak
- Status: `In Progress`
- Link: https://linear.app/byndai/issue/BYN-55/data-connectors-broker-architecture-poc
- SOP section: Priority
- Current read: This In Progress item is well scoped, but it has no priority and no labels.
- What to improve: Add priority and type/product labels so it is easier to filter and plan.
- Suggested next edit: Ask Nikhil for priority and add the most fitting type label plus a product-surface label if one applies.

## BYN-56: PPT Exports

- Owner: Shashank Rajak
- Status: `In Progress`
- Link: https://linear.app/byndai/issue/BYN-56/ppt-exports
- SOP section: Definition of done
- Current read: This In Progress item describes the feature, but does not show the completion checks.
- What to improve: Add a Definition of done and Acceptance criteria for the PPT export feature.
- Suggested next edit: Add checks for exporting a generated report as PPT with branding/templates applied.
- Suggested Definition of done: Users can export a generated company report as a PPT using their branding and templates.
- Suggested Acceptance criteria:
  - A generated report can be exported in PPT format.
  - A selected branding/template option is reflected in the PPT output.
  - The exported PPT opens successfully for review.

## BYN-59: Plan out UI/UX for the PPT export workflow

- Owner: Shashank Rajak
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-59/plan-out-uiux-for-the-ppt-export-workflow
- SOP section: Backlog-to-Todo
- Current read: This Todo item has an empty description, so the planning deliverable is not visible yet.
- What to improve: Define the UI/UX planning output and the checks that show it is ready.
- Suggested next edit: Add whether the output is a wireframe, doc, or decision note, plus who needs to review it.
- Suggested Definition of done: A UI/UX plan for the PPT export workflow is documented and ready for implementation discussion.
- Suggested Acceptance criteria:
  - The planned user flow is documented.
  - Open product or design decisions are listed.
  - The plan is shared with the relevant reviewer.

## BYN-60: Add examples for standard templates across different persona for the layout designer agent

- Owner: Shashank Rajak
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-60/add-examples-for-standard-templates-across-different-persona-for-the
- SOP section: Backlog-to-Todo
- Current read: This Todo item has an empty description, so it is not yet clear what examples are needed or how completion will be checked.
- What to improve: Add a scoped outcome and acceptance checks before keeping it in Todo.
- Suggested next edit: Add the target personas, where examples should live, and how someone will verify the examples are usable.

## BYN-61: Integrate PPT Agent into the main company reports application

- Owner: Shashank Rajak
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-61/integrate-ppt-agent-into-the-main-company-reports-application
- SOP section: Backlog-to-Todo
- Current read: This Todo item has an empty description, so the outcome and checks are not visible yet.
- What to improve: Add enough scope to begin, or move it back to Backlog until scoped.
- Suggested next edit: Add Definition of done and Acceptance criteria for what integration means in the main company reports app.
- Suggested Definition of done: The PPT agent is integrated into the main company reports application with a verified export path.
- Suggested Acceptance criteria:
  - A generated company report can invoke the PPT agent from the main app.
  - A PPT output is produced from the integrated flow.
  - The result is checked from the app path, not only the standalone agent.

## BYN-67: Research Azure Monitoring for code-level alerting/observability

- Owner: Sanidhya
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-67/research-azure-monitoring-for-code-level-alertingobservability
- SOP section: Priority
- Current read: This Spike has a timebox and output, but it is in Todo with no priority.
- What to improve: Add the priority if Nikhil has set it, or ask before keeping it as this-week Todo work.
- Suggested next edit: Ask Nikhil for priority and update the field.

## BYN-68: Get Bynd added to the Azure alert group

- Owner: Sanidhya
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-68/get-bynd-added-to-the-azure-alert-group
- SOP section: Definition of done
- Current read: This Todo item has a verification idea, but the Definition of done and Acceptance criteria are not explicitly written.
- What to improve: Turn the existing verification note into the standard issue structure.
- Suggested next edit: Add headings for Definition of done and Acceptance criteria using the alert email test already described.
- Suggested Definition of done: Bynd receives Azure tenant alerts at the Bynd email address added to HDFC's Azure tenant.
- Suggested Acceptance criteria:
  - Bynd email address is added to the Azure alert group.
  - A manual alert is triggered through az cli.
  - The alert email is received and noted on the issue.

## BYN-72: Validation speed and coverage improvements,

- Owner: Mrinal Kanwar
- Status: `In Progress`
- Link: https://linear.app/byndai/issue/BYN-72/validation-speed-and-coverage-improvements
- SOP section: Definition of done
- Current read: This In Progress parent points to sub-issues for details, but its own completion test is not visible.
- What to improve: Add a parent-level Definition of done and acceptance check for the bundle.
- Suggested next edit: Add one sentence describing what is true when all sub-issue work is complete.
- Suggested Definition of done: Parallelism, text-classification, and blob-PDF changes are completed through their sub-issues and verified together.
- Suggested Acceptance criteria:
  - The relevant sub-issues are linked and completed.
  - A combined validation run confirms the speed and coverage improvements.
  - Any remaining follow-up work is linked or created.

## BYN-78: Draft press release

- Owner: Nikhil
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-78/draft-press-release
- SOP section: Backlog-to-Todo
- Current read: This Todo item says what to do, but not what complete looks like.
- What to improve: Add a Definition of done and Acceptance criteria for the press release draft and outreach.
- Suggested next edit: Add a finish line for the draft plus a small checklist for media outreach.
- Suggested Definition of done: A joint Bynd and HDFC Capital press release draft and publisher outreach list are ready to share.
- Suggested Acceptance criteria:
  - Press release draft is written in a shareable doc.
  - Relevant media agencies or publishers are listed.
  - The next outreach owner or handoff is captured.

## BYN-79: Connect with Sanjay

- Owner: Nikhil
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-79/connect-with-sanjay
- SOP section: Backlog-to-Todo
- Current read: This Todo item has context, but the finish line and verification checks are not visible yet.
- What to improve: Add a Definition of done and Acceptance criteria so the conversation outcome is clear.
- Suggested next edit: Add a short Definition of done plus 2-3 checks for contacting Sanjay and capturing next steps.
- Suggested Definition of done: A phase-two scope conversation with Sanjay is completed or scheduled, and next steps for the Mumbai investment team are captured.
- Suggested Acceptance criteria:
  - Sanjay has been contacted with the phase-two scope prompt.
  - A call is scheduled or the outcome is documented.
  - Next steps for the investment team in Mumbai are added to the issue.
