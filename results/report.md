# Weekly Linear Issue Management Report

Weekly Linear issue management check - manual-preview

Reviewed 49 active Linear issues across Backlog, Todo, In Progress, and In Review.

Review mode: AI SOP review

This is an AI-assisted helper, not a compliance report. Issues without suggestions should not be treated as automatically clean.

Status mix:
- Backlog: 24
- Todo: 18
- In Progress: 7
- In Review: 0

Main themes:
- Several Todo and In Progress items have useful context but need an explicit Definition of done and Acceptance criteria before they are easy to verify.
- A few Todo items look like captured ideas rather than ready-this-week work, so they may be better parked in Backlog until scoped.
- The clearest issues pair a one-sentence outcome with observable checks that another teammate could use to close the loop.

Suggested follow-ups:
- 14 issues have AI suggestions.
- 5 people have short DM drafts in `results/dms/`.

Positive example to copy:
- BYN-66: Update industry report pipeline to new blob output structure - https://linear.app/byndai/issue/BYN-66/update-industry-report-pipeline-to-new-blob-output-structure
  Why: It has a clear Definition of done, concrete acceptance criteria, and a simple verification step worth copying.

A few people may get short DMs with specific suggestions. Feel free to ignore anything the review got wrong.

This review is read-only. No Linear changes were made.

## DM Drafts

- Aditya Singh: 2 items
- Mrinal Kanwar: 1 item
- Nikhil: 2 items
- Sanidhya: 3 items
- Shashank Rajak: 3 items

Suppressed repeat DM items: 0

# Owner-Specific Linear Review

Mode: `manual-preview`
Analysis source: `azure-openai`

This is AI-assisted. Missing suggestions do not mean the issue is clean.

## Shashank Rajak

Several Company Reports items are captured, but the Todo/In Progress ones need scoping before they are easy to start or close.

Suggested focus:
- Move empty Todo items back to Backlog until they have a description, Definition of done, and acceptance criteria.
- Add type/product labels and priority to the In Progress items when they remain committed work.

Issues with AI suggestions:
- BYN-61: Integrate PPT Agent into the main company reports application - This Todo item has an empty description, no priority, and no labels.
- BYN-60: Add examples for standard templates across different persona for the layout designer agent - This Todo item has an empty description, no priority, and no labels.
- BYN-59: Plan out UI/UX for the PPT export workflow - This Todo item has an empty description, no priority, and no labels.
- BYN-56: PPT Exports - This In Progress item describes the feature but has no explicit Definition of done or Acceptance criteria.
- BYN-55: Data connectors broker architecture - PoC - This In Progress issue has strong verification detail but no type or product labels and no priority.

## Sanidhya

The Chat and Intelligence items are pointed at useful work; a few Todo items need crisp completion checks.

Suggested focus:
- Add Definition of done and Acceptance criteria headings to the Todo items that are ready this week.
- For Improvement items, add the current state and target state where practical.

Issues with AI suggestions:
- BYN-68: Get Bynd added to the Azure alert group - The issue has a useful verify note, but the Definition of done and Acceptance criteria are not written as explicit sections.
- BYN-54: Change citation loading approach in chat view pane - This Todo Improvement has a proposed approach but no explicit outcome or acceptance checks.
- BYN-35: Add support for Bi-Weekly newsletter runs - This Todo item states the backend task but does not yet include finish criteria.
- BYN-19: Plan new architecture for agent flow - This Todo Improvement describes the problem but does not yet define the planning deliverable or verification checks.

## Nikhil

The HDFC Expansion Todo items have useful context; a quick finish-and-verify pass would make them easier to act on this week.

Suggested focus:
- Add one Definition of done line to BYN-79 and BYN-78.
- Add 2-3 acceptance checks for what counts as complete.

Issues with AI suggestions:
- BYN-79: Connect with Sanjay - This Todo item has context but no explicit Definition of done or Acceptance criteria.
- BYN-78: Draft press release - This Todo item describes activities but does not yet say what finished looks like.

## Aditya Singh

The bi-weekly newsletter frontend item is clear at a high level; adding verification checks would make it ready to close later.

Suggested focus:
- Add a one-sentence Definition of done to BYN-36.
- Add 2 acceptance checks for saving and displaying the bi-weekly cadence.

Issues with AI suggestions:
- BYN-36: Add support for Bi-Weekly newsletter on Frontend - This Todo item has a short description but no Definition of done or Acceptance criteria.

## Mrinal Kanwar

The validation roll-up is helpful context, and it is worth checking that the parent issue has its own close-out criteria.

Suggested focus:
- Add a parent-level Definition of done to BYN-72.
- Add acceptance criteria that reference the linked sub-issues.

Issues with AI suggestions:
- BYN-72: Validation speed and coverage improvements, - Worth checking: the parent issue points to sub-issues for details, but the parent does not have its own close-out criteria.

## Unassigned

One Todo item is empty and unowned, so it is worth parking until someone scopes it.

Suggested focus:
- Move BYN-11 back to Backlog until it has an owner and outcome.
- Fix the title typo when it is next edited.

Issues with AI suggestions:
- BYN-11: Update DB to support project-in-poject architecture - This Todo item is unassigned and has an empty description, no priority, and no labels.

## Devayush Rout

No AI suggestions from this run.

## kabir bahl

No AI suggestions from this run.

## Piyush Khurana

No AI suggestions from this run.


# Issue Improvement Notes

Mode: `manual-preview`
Analysis source: `azure-openai`

This is AI-assisted. Treat suggestions as review prompts, not final judgement.

## BYN-11: Update DB to support project-in-poject architecture

- Owner: Unassigned
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-11/update-db-to-support-project-in-poject-architecture
- SOP section: Backlog-to-Todo
- Current read: This Todo item is unassigned and has an empty description, no priority, and no labels.
- What to improve: Park it in Backlog until it has an owner, outcome, and acceptance criteria.
- Suggested next edit: Move to Backlog and fix the title typo when it is next scoped.
- Suggested title: Update DB to support project-in-project architecture
- Suggested Definition of done: The Vault database supports project-in-project relationships as required by the scoped architecture.
- Suggested Acceptance criteria:
  - The required parent-child project relationship is documented.
  - Database changes are implemented or planned in a linked issue.
  - A verification query or test confirms the relationship works.

## BYN-19: Plan new architecture for agent flow

- Owner: Sanidhya
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-19/plan-new-architecture-for-agent-flow
- SOP section: Definition of done
- Current read: This Todo Improvement describes the problem but does not yet define the planning deliverable or verification checks.
- What to improve: Make the architecture plan itself the observable output.
- Suggested next edit: Add a Definition of done that names the document or recommendation to be produced.
- Suggested Definition of done: A proposed Chat agent architecture for 50+ documents is documented with expected latency impact and the next decision needed.
- Suggested Acceptance criteria:
  - Current 20-30 document behavior is captured as the baseline.
  - The proposed fan-out and reduction approach is documented.
  - The plan is shared with the intended decision-makers.

## BYN-35: Add support for Bi-Weekly newsletter runs

- Owner: Sanidhya
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-35/add-support-for-bi-weekly-newsletter-runs
- SOP section: Backlog-to-Todo
- Current read: This Todo item states the backend task but does not yet include finish criteria.
- What to improve: Add checks that prove bi-weekly runs work and PropEquity is shifted.
- Suggested next edit: Add Definition of done and Acceptance criteria headings to the description.
- Suggested Definition of done: Backend newsletter scheduling supports bi-weekly runs, and PropEquity newsletters use that cadence.
- Suggested Acceptance criteria:
  - A bi-weekly newsletter run can be scheduled and created by the backend.
  - PropEquity's newsletter configuration is set to bi-weekly.
  - The next scheduled run date reflects the bi-weekly cadence.

## BYN-36: Add support for Bi-Weekly newsletter on Frontend

- Owner: Aditya Singh
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-36/add-support-for-bi-weekly-newsletter-on-frontend
- SOP section: Backlog-to-Todo
- Current read: This Todo item has a short description but no Definition of done or Acceptance criteria.
- What to improve: Add the exact frontend outcome and checks for bi-weekly cadence setup.
- Suggested next edit: Add a one-sentence Definition of done and two frontend verification checks.
- Suggested Definition of done: Intelligence frontend users can configure a bi-weekly newsletter cadence.
- Suggested Acceptance criteria:
  - A user can select bi-weekly cadence in the newsletter setup flow.
  - The selected cadence is saved and shown correctly when the setup is reopened.

## BYN-54: Change citation loading approach in chat view pane

- Owner: Sanidhya
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-54/change-citation-loading-approach-in-chat-view-pane
- SOP section: Backlog-to-Todo
- Current read: This Todo Improvement has a proposed approach but no explicit outcome or acceptance checks.
- What to improve: Add a measurable target for the citation loading change and checks for pagination behavior.
- Suggested next edit: Add Definition of done and Acceptance criteria headings before implementation continues.
- Suggested Definition of done: Citation clicks load only the cited page plus the agreed buffer, and additional pages load as the user scrolls.
- Suggested Acceptance criteria:
  - Clicking a citation loads the cited page with the three-page buffer above and below.
  - Scrolling through the PDF loads the next page range without reloading the whole PDF.
  - Current full-PDF load behavior and the target behavior are recorded on the issue.

## BYN-55: Data connectors broker architecture - PoC

- Owner: Shashank Rajak
- Status: `In Progress`
- Link: https://linear.app/byndai/issue/BYN-55/data-connectors-broker-architecture-poc
- SOP section: Creating an issue
- Current read: This In Progress issue has strong verification detail but no type or product labels and no priority.
- What to improve: Add the missing labels and priority so it is easier to scan and prioritise.
- Suggested next edit: Add one type label, one product surface label if applicable, and the priority Nikhil has communicated.

## BYN-56: PPT Exports

- Owner: Shashank Rajak
- Status: `In Progress`
- Link: https://linear.app/byndai/issue/BYN-56/ppt-exports
- SOP section: Backlog-to-Todo
- Current read: This In Progress item describes the feature but has no explicit Definition of done or Acceptance criteria.
- What to improve: Add the export outcome and checks that prove the PPT export works.
- Suggested next edit: Add Definition of done and Acceptance criteria headings to the description.
- Suggested Definition of done: Users can export a generated company report as a PPT using their branding and templates.
- Suggested Acceptance criteria:
  - A generated report can be exported in PPT format.
  - Branding and template inputs are reflected in the exported PPT.
  - The exported file opens successfully and contains the expected report content.

## BYN-59: Plan out UI/UX for the PPT export workflow

- Owner: Shashank Rajak
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-59/plan-out-uiux-for-the-ppt-export-workflow
- SOP section: Backlog-to-Todo
- Current read: This Todo item has an empty description, no priority, and no labels.
- What to improve: Define the UI/UX planning output before treating it as ready-this-week work.
- Suggested next edit: Move to Backlog until scoped, or add the plan deliverable under Definition of done.
- Suggested Definition of done: A UI/UX plan for the PPT export workflow is documented and ready for implementation scoping.
- Suggested Acceptance criteria:
  - Main user steps for PPT export are documented.
  - Open design or product decisions are listed.
  - Follow-up implementation issues are created or linked if needed.

## BYN-60: Add examples for standard templates across different persona for the layout designer agent

- Owner: Shashank Rajak
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-60/add-examples-for-standard-templates-across-different-persona-for-the
- SOP section: Backlog-to-Todo
- Current read: This Todo item has an empty description, no priority, and no labels.
- What to improve: Add the expected examples and verification checks before keeping it in Todo.
- Suggested next edit: Move to Backlog until scoped, or add the standard Definition of done and Acceptance criteria sections.
- Suggested title: Add standard template examples across personas for the layout designer agent
- Suggested Definition of done: The layout designer agent has standard template examples for the agreed personas.
- Suggested Acceptance criteria:
  - The agreed persona list is captured on the issue.
  - Each persona has at least one standard template example.
  - The examples are available where the layout designer agent can use them.

## BYN-61: Integrate PPT Agent into the main company reports application

- Owner: Shashank Rajak
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-61/integrate-ppt-agent-into-the-main-company-reports-application
- SOP section: Backlog-to-Todo
- Current read: This Todo item has an empty description, no priority, and no labels.
- What to improve: Either scope it with a defined outcome and checks, or move it back to Backlog until ready.
- Suggested next edit: Move to Backlog unless it is ready this week, then add description, Definition of done, Acceptance criteria, labels, and priority.
- Suggested Definition of done: The PPT Agent is integrated into the main company reports application and can generate a PPT export from an existing report.
- Suggested Acceptance criteria:
  - A generated company report can be exported through the integrated PPT Agent.
  - The export path works from the main application flow.
  - Any known limitations are captured on the issue.

## BYN-68: Get Bynd added to the Azure alert group

- Owner: Sanidhya
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-68/get-bynd-added-to-the-azure-alert-group
- SOP section: Definition of done
- Current read: The issue has a useful verify note, but the Definition of done and Acceptance criteria are not written as explicit sections.
- What to improve: Turn the existing verification idea into the standard finish-and-check format.
- Suggested next edit: Add a Definition of done heading above the alert outcome and move the manual trigger step under Acceptance criteria.
- Suggested Definition of done: Bynd receives Azure alert emails from HDFC's tenant-level alert group.
- Suggested Acceptance criteria:
  - Manually trigger an Azure alert through az cli.
  - Confirm the alert email lands in the Bynd email address.
  - Record any tenant-level config owner needed for future changes.

## BYN-72: Validation speed and coverage improvements,

- Owner: Mrinal Kanwar
- Status: `In Progress`
- Link: https://linear.app/byndai/issue/BYN-72/validation-speed-and-coverage-improvements
- SOP section: Definition of done
- Current read: Worth checking: the parent issue points to sub-issues for details, but the parent does not have its own close-out criteria.
- What to improve: Add a short roll-up Definition of done and acceptance checks so the parent can be closed cleanly.
- Suggested next edit: Add one roll-up Definition of done line plus acceptance criteria that reference the relevant sub-issues.
- Suggested Definition of done: Validation speed and coverage improvements are complete when the linked parallelism, text-fact, and blob-PDF work are finished and verified together.
- Suggested Acceptance criteria:
  - Linked sub-issues for parallelism, text-fact handling, and blob PDF reads are complete.
  - Combined verification result is recorded on the parent issue.
  - Any remaining follow-up work is linked or created separately.

## BYN-78: Draft press release

- Owner: Nikhil
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-78/draft-press-release
- SOP section: Backlog-to-Todo
- Current read: This Todo item describes activities but does not yet say what finished looks like.
- What to improve: Define the draft and outreach output that makes the work complete.
- Suggested next edit: Add a Definition of done line and a short Acceptance criteria list.
- Suggested Definition of done: A draft joint Bynd/HDFC Capital press release and a publisher outreach list are ready for review.
- Suggested Acceptance criteria:
  - Press release draft is shared with the agreed reviewers.
  - Target media agencies or publishers are listed with contact status.
  - Any open approvals or edits are captured on the issue.

## BYN-79: Connect with Sanjay

- Owner: Nikhil
- Status: `Todo`
- Link: https://linear.app/byndai/issue/BYN-79/connect-with-sanjay
- SOP section: Backlog-to-Todo
- Current read: This Todo item has context but no explicit Definition of done or Acceptance criteria.
- What to improve: Add the outcome and the checks that show the Sanjay follow-up is complete.
- Suggested next edit: Add headings for Definition of done and Acceptance criteria under the existing description.
- Suggested Definition of done: A phase-two scope discussion with Sanjay is completed or scheduled, and the next action for the HDFC investment team is recorded.
- Suggested Acceptance criteria:
  - Sanjay is contacted with the phase-two scope ask.
  - Call date or decision not to schedule a call is recorded on the issue.
  - Next owner and next step are captured after the conversation.
