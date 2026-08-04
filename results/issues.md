# Issue Improvement Notes

Mode: `manual-preview`
Analysis source: `azure-openai`

This is AI-assisted. Treat suggestions as review prompts, not final judgement.

## BYN-11: Update DB to support project-in-poject architecture

- Owner: Unassigned
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-11/update-db-to-support-project-in-poject-architecture
- SOP section: Backlog-to-Todo
- Current read: This Todo is unassigned and has no priority, type label, description, Definition of done, or acceptance criteria.
- What to improve: Move it to Backlog unless it is ready to start this week with all required fields.
- Suggested next edit: Move to Backlog, or add owner, priority, type label, Definition of done, and Acceptance criteria.
- Suggested title: Update DB to support project-in-project architecture

## BYN-19: Plan new architecture for agent flow

- Owner: Sanidhya
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-19/plan-new-architecture-for-agent-flow
- SOP section: Issue types
- Current read: This Improvement mentions the current scale and desired larger scale, but lacks a defined deliverable and acceptance checks.
- What to improve: Frame the planning work as a concrete architecture recommendation or document.
- Suggested next edit: Add a Definition of done that makes the output a reviewed architecture plan.
- Suggested title: Recommend Chat agent architecture for 50+ documents
- Suggested Definition of done: A proposed Chat agent architecture for 50+ documents is documented with expected latency impact and next implementation steps.
- Suggested Acceptance criteria:
  - The plan covers agent fan-out and response-latency reduction.
  - The plan states the current 20-30 document limit and the 50+ document target.
  - Next implementation issues are created or linked.

## BYN-3: Import your data

- Owner: Unassigned
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-3/import-your-data
- SOP section: What goes in Linear
- Current read: This reads like Linear starter guidance rather than a current Bynd task.
- What to improve: Worth checking whether this should remain in active work tracking.
- Suggested next edit: If this is not a current Bynd task, move it to Canceled with a one-line reason.

## BYN-35: Add support for Bi-Weekly newsletter runs

- Owner: Sanidhya
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-35/add-support-for-bi-weekly-newsletter-runs
- SOP section: Backlog-to-Todo
- Current read: This urgent Todo has owner, priority, and type label, but no Definition of done or acceptance criteria.
- What to improve: Define what backend support for bi-weekly runs includes and how PropEquity migration will be checked.
- Suggested next edit: Add a Definition of done sentence covering backend cadence support and PropEquity switch-over.
- Suggested Definition of done: The backend supports bi-weekly newsletter runs, and PropEquity newsletters are configured to use the bi-weekly cadence.
- Suggested Acceptance criteria:
  - A bi-weekly newsletter cadence can be configured on the backend.
  - PropEquity is set to the bi-weekly cadence.
  - A test run confirms the configured cadence is used.

## BYN-36: Add support for Bi-Weekly newsletter on Frontend

- Owner: Aditya Singh
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-36/add-support-for-bi-weekly-newsletter-on-frontend
- SOP section: Backlog-to-Todo
- Current read: This Todo has owner, priority, and type label, but the description does not define completion or checks.
- What to improve: State the frontend behavior that proves bi-weekly cadence support exists.
- Suggested next edit: Add a Definition of done and two acceptance criteria for the cadence setup UI.
- Suggested Definition of done: Users can set up a bi-weekly newsletter cadence from the Intelligence frontend.
- Suggested Acceptance criteria:
  - Bi-weekly appears as a cadence option in the newsletter setup flow.
  - Saving the setup sends the bi-weekly cadence value to the backend.

## BYN-43: Native-text vs OCR/scanned classification for Download Financials

- Owner: Unassigned
- Status: `In Progress`
- Link: https://linear.app/byndai/issue/BYN-43/native-text-vs-ocrscanned-classification-for-download-financials
- SOP section: Issue statuses
- Current read: This issue is In Progress but unassigned.
- What to improve: Assign the active owner so the status reflects someone currently working on it.
- Suggested next edit: Set the assignee to the person actively working on native-text versus OCR classification.

## BYN-44: Deterministic figure verification and highlighting in Download Financials

- Owner: Unassigned
- Status: `In Progress`
- Link: https://linear.app/byndai/issue/BYN-44/deterministic-figure-verification-and-highlighting-in-download
- SOP section: Issue statuses
- Current read: This issue is In Progress but unassigned.
- What to improve: Assign the active owner so the person accountable for closing the loop is clear.
- Suggested next edit: Set the assignee to the person actively working on deterministic figure verification.

## BYN-51: eme Sources

- Owner: Unassigned
- Status: `Backlog`
- Link: https://linear.app/byndai/issue/BYN-51/eme-sources
- SOP section: Creating an issue
- Current read: This backlog title is too terse for someone else to understand, and it has no type label.
- What to improve: Rewrite the title as the remembered task and add a type label.
- Suggested next edit: Replace the title with a clear task phrase and add the matching type label.

## BYN-54: Change citation loading approach in chat view pane

- Owner: Sanidhya
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-54/change-citation-loading-approach-in-chat-view-pane
- SOP section: Issue types
- Current read: This Improvement describes the current pain and approach, but not a measurable target state or acceptance checks.
- What to improve: Add the current state and target state in terms someone can verify after the citation loading change.
- Suggested next edit: Add an Acceptance criteria section with the page-window behavior and expected loading behavior.
- Suggested title: Load only the cited PDF page window in chat citations
- Suggested Definition of done: Clicking a citation loads only the cited page plus the defined surrounding page buffer, with additional pages loaded as the user scrolls.
- Suggested Acceptance criteria:
  - Clicking a citation loads the cited page plus three pages before and after when available.
  - Scrolling loads additional pages through pagination.
  - The full PDF is not loaded on the initial citation click.

## BYN-55: Data connectors broker architecture - PoC

- Owner: Shashank Rajak
- Status: `In Progress`
- Link: https://linear.app/byndai/issue/BYN-55/data-connectors-broker-architecture-poc
- SOP section: Issue types
- Current read: This In Progress issue has strong verification detail, but no type label and no priority.
- What to improve: Add the issue type and priority so the active work matches the SOP fields.
- Suggested next edit: Add the most fitting type label, likely Spike if the output is an architecture recommendation rather than shipped code.

## BYN-56: PPT Exports

- Owner: Shashank Rajak
- Status: `In Progress`
- Link: https://linear.app/byndai/issue/BYN-56/ppt-exports
- SOP section: Backlog-to-Todo
- Current read: This In Progress issue has an owner and broad outcome, but no priority, type label, or acceptance criteria.
- What to improve: Add the fields that would have made it ready before active work started.
- Suggested next edit: Add a type label and Acceptance criteria for a successful PPT export.
- Suggested Definition of done: Users can export a generated company report as a PPT using their branding and templates.
- Suggested Acceptance criteria:
  - A generated report can be exported in PPT format.
  - The export applies the selected branding or template.
  - The exported PPT opens successfully for review.

## BYN-58: Integrate Validation Service

- Owner: Shashank Rajak
- Status: `Backlog`
- Link: https://linear.app/byndai/issue/BYN-58/integrate-validation-service
- SOP section: Issue types
- Current read: This backlog issue has a Reports label but no type label.
- What to improve: Add the type label so the work category is clear at a glance.
- Suggested next edit: Add a type label, likely Spike if the immediate output is an integration plan.
- Suggested title: Plan validation service integration for company reports

## BYN-59: Plan out UI/UX for the PPT export workflow

- Owner: Shashank Rajak
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-59/plan-out-uiux-for-the-ppt-export-workflow
- SOP section: Backlog-to-Todo
- Current read: This Todo has no priority, type label, description, Definition of done, or acceptance criteria.
- What to improve: Make the planning output observable, such as a UI/UX spec or decision note.
- Suggested next edit: Add a Definition of done that names the UI/UX artifact to be produced.
- Suggested title: Write UI/UX plan for the PPT export workflow
- Suggested Definition of done: A UI/UX plan for the PPT export workflow is documented and ready for implementation discussion.
- Suggested Acceptance criteria:
  - The planned user flow is documented.
  - The export entry point and output behavior are covered.
  - Open implementation questions are listed.

## BYN-60: Add examples for standard templates across different persona for the layout designer agent

- Owner: Shashank Rajak
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-60/add-examples-for-standard-templates-across-different-persona-for-the
- SOP section: Backlog-to-Todo
- Current read: This Todo has no priority, type label, description, Definition of done, or acceptance criteria.
- What to improve: Turn the template examples work into a verifiable deliverable before keeping it in Todo.
- Suggested next edit: Add a type label and a Definition of done that states where the examples will live.
- Suggested title: Add standard layout-template examples by persona
- Suggested Definition of done: The layout designer agent has standard template examples for the agreed personas.
- Suggested Acceptance criteria:
  - The agreed personas are listed in the issue.
  - Each persona has at least one standard template example.
  - The examples are available where the layout designer agent uses or references them.

## BYN-61: Integrate PPT Agent into the main company reports application

- Owner: Shashank Rajak
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-61/integrate-ppt-agent-into-the-main-company-reports-application
- SOP section: Backlog-to-Todo
- Current read: This Todo has no priority, type label, description, Definition of done, or acceptance criteria.
- What to improve: Either make it ready for this week or keep it as captured work in Backlog.
- Suggested next edit: Move it to Backlog unless priority and the ready-to-start fields are added now.
- Suggested Definition of done: The PPT Agent is integrated into the main company reports application and can be used from the intended workflow.
- Suggested Acceptance criteria:
  - The main company reports application can call the PPT Agent.
  - A generated company report can be exported through the integrated flow.
  - The integration path is documented or linked in the issue.

## BYN-68: Get Bynd added to the Azure alert group

- Owner: Sanidhya
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-68/get-bynd-added-to-the-azure-alert-group
- SOP section: Definition of done
- Current read: The issue has useful verification detail, but the done state is not separated under the required heading.
- What to improve: Turn the current text into a Definition of done plus Acceptance criteria so another person can verify it quickly.
- Suggested next edit: Add a Definition of done heading before the verification text.
- Suggested Definition of done: Bynd receives Azure tenant alerts at the configured Bynd email address.
- Suggested Acceptance criteria:
  - Yogesh confirms the tenant-level alert group configuration.
  - A manual az cli alert test is triggered.
  - The Bynd email address receives the alert.

## BYN-72: Validation speed and coverage improvements,

- Owner: Mrinal Kanwar
- Status: `In Progress`
- Link: https://linear.app/byndai/issue/BYN-72/validation-speed-and-coverage-improvements
- SOP section: Definition of done
- Current read: This In Progress parent issue says details are in sub-issues, but the parent does not state its own done state.
- What to improve: Add a short parent-level outcome so the bundle can be closed without rereading every sub-issue.
- Suggested next edit: Add one Definition of done sentence that summarizes the combined speed and coverage outcome.
- Suggested Definition of done: Validation speed and coverage improvements from the linked sub-issues are implemented and verified together.
- Suggested Acceptance criteria:
  - Linked sub-issues for parallelism, text checks, and blob PDF reads are completed or explicitly deferred.
  - The combined verification evidence is linked from this parent issue.

## BYN-76: Metric retrieval accuracy

- Owner: kabir bahl
- Status: `Backlog`
- Link: https://linear.app/byndai/issue/BYN-76/metric-retrieval-accuracy
- SOP section: Issue types
- Current read: This backlog benchmark issue has product-surface labels, but no type label.
- What to improve: Add the issue type so it is clear whether this is a Spike, Chore, or other work type.
- Suggested next edit: If this is research, add the Spike label plus a Question, Timebox, and Output.
- Suggested title: Benchmark financial metric retrieval accuracy across models

## BYN-78: Draft press release

- Owner: Nikhil
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-78/draft-press-release
- SOP section: Backlog-to-Todo
- Current read: This is in Todo with priority and owner, but it does not yet state the finished outcome or acceptance checks.
- What to improve: Clarify whether done means a draft only, publisher outreach only, or both.
- Suggested next edit: Add a Definition of done sentence that names the completed press-release artifact and outreach status.
- Suggested title: Draft and route HDFC deployment press release
- Suggested Definition of done: A joint Bynd and HDFC Capital press release draft is ready for review, and the target media outreach list is captured.
- Suggested Acceptance criteria:
  - Press release draft link is added to the issue.
  - HDFC/Bynd reviewers are identified.
  - Target media agencies or publishers are listed with owner for outreach.

## BYN-79: Connect with Sanjay

- Owner: Nikhil
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-79/connect-with-sanjay
- SOP section: Backlog-to-Todo
- Current read: This is in Todo with owner and priority, but it lacks a type label, Definition of done, and acceptance criteria.
- What to improve: Make the outreach outcome and verification explicit before treating it as ready-to-start work.
- Suggested next edit: Add a Definition of done heading with: Sanjay has confirmed the phase two discussion path, or a call is scheduled with the investment team scope captured.
- Suggested title: Align with Sanjay on HDFC phase two scope
- Suggested Definition of done: Sanjay has confirmed the next step for HDFC phase two scope, and the Mumbai investment team follow-up is either scheduled or documented.
- Suggested Acceptance criteria:
  - Sanjay confirms whether a call is needed.
  - If a call is needed, calendar invite and agenda are shared.
  - If no call is needed, the agreed next step is recorded in the issue.
