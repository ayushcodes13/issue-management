**This is a two-week experiment, starting Monday 3 August.**

**We will review it on Friday 7 August and Friday 14 August.**

This is deliberately simple. It will not cover every situation, and some rules will prove to be wrong. If a rule makes you slower or does not make sense, note it and raise it at standup or at the Friday review.

Please read this document carefully. It's important for us to be on the same page about how we use this new tool.

---

## What we are using in this experiment

**We are only using Linear Projects and Issues, plus labels.** Labels are for the issue type (bug, feature, improvement, etc.) and the product surface (chat, metrics etc.) 

For the first 2 weeks, we are not using "Milestones" (Linear's primitive for stages inside a project) or "Initiatives" (groups of projects) or any other Linear concept for tracking work. We are using the six issue statuses Linear already gives us and not adding any of our own. We will revisit this as we learn more.

---

## What goes in Linear

We are using [Linear's own rule](https://linear.app/method/write-issues-not-user-stories):

> "An issue should describe a task with a clear, defined outcome. This could be a piece of code, design, document, or action to be taken. **If it's not a task, then it doesn't belong in the issue tracker.**"
> 

And, for work that is not clear yet, Linear's exception to that rule:

> "You can create placeholder issues in these instances to break down later (e.g. Explore design) or frame it as a deliverable (e.g. Write project spec)."
> 

A **defined outcome** is a short, observable statement of what will be true when the work is finished. It describes the result from the work, not the activity:

- Activity: "Look into why report generation got slower."
- Defined outcome: "Identify what caused report generation to slow down and recommend a fix."
- Activity: "Improve Chat retrieval."
- Defined outcome: "Recommend the next retrieval improvement to ship, including the expected impact and the decision it requires."

For delivery work, the outcome is usually a working change: code, configuration, a document, or an operational action. For research work, it is usually an answer or a decision, or sometimes a doc or a new, scoped out Issue itself.

**Important Note**

We will use the following rule: A defined outcome is required to move an issue to `Todo`. It is **not** required to capture an issue in `Backlog`. An Issue in `Backlog` needs only a title clear enough for someone else to understand. This is explained in more detail in **Issue statuses** and **Backlog-to-Todo** sections.

### When work should become an issue

Create an issue when there is a meaningful piece of work that we need to remember, coordinate, prioritise, or verify. This includes work that:

- extends beyond a small, self-contained task, and continues from several hours to days*;
- needs a decision, handoff, review, or visibility to others;
- is a client request, a production issue, a request from Nikhil; or
- is a timeboxed research task with a clear question and an agreed decision to unblock (see **Research and Spikes** below)

**Important Note: Linear is not meant to be a log of your day.** Not all work you do should become a Linear Issue or exist in Linear. Meetings, questions you answered in Slack, something you researched because you were hazy on the concept, a teammate you helped for 30 min - these are generally not tracked Issues (there will be exceptions to this, ask in Standup when unsure). Nobody is being measured on the number of issues they have completed. Create issues thoughtfully. Use your judgement.

Also - Do not backfill work that is already finished. ****Keep Linear forward looking.

**Note that time is a useful signal, but not the rule: a 30 min urgent production fix for a client deserves a ticket; two hours spent with Claude understanding code or some concept as part of an existing Issue does not need a separate one.*

### Examples

A few examples on what should be an Issue and what shouldn't. Not exhaustive. Just for reference.

| Situation | What belongs in Linear? | Why |
| --- | --- | --- |
| A client is waiting for an answer or change | An issue | The request needs ownership and visibility |
| A deployed service is broken | A `Bug` issue, even for a quick fix | We need a record of the defect and its verification |
| A small question answered and finished in 20 minutes | Nothing | It is complete, self-contained activity |
| Understanding code to make a change already tracked in an Issue | Nothing separate | It is part of the existing issue |
| Two hours onboarding a new engineer | An issue | This would be planned work with dedicated time. It is not ad hoc. |
| "Go think about how we should do X" | A `Spike` Issue once Nikhil has asked to spend time on it | See section on Spikes |
| An unapproved product or technical idea you have | Nothing yet | Discuss in Standup/with Nikhil whether to investigate it before tracking it |
| Fixing a quick small bug you discovered while already working on something else | Nothing | You can log that you fixed this bug in your github PR/commit history. Doesn’t need it's own Linear Issue. |
| Discovering a large and important bug while you were already working on something else | An Issue | You should log this as an issue but probably not move to To Do/In Progress unless you would lose momentum by not working on the fix immediately with the context in your head. |

If you are genuinely unsure whether a real piece of work should be an Issue, just make it and then bring it up at standup or the Friday review. We can always prune Linear later.

---

## Projects

A project is a linear primitive meant for a body of work that **can be finished** and has a clear end state.

**In most situations, Nikhil will create projects or explicitly ask you to create them.** If you think something should be a project, raise it in Standup or Friday review first rather than creating it yourself.

If you are asked to create one, it needs four things: an **outcome** (what is true when the project is finished), a **lead**, a **target date**, and its **issues** linked to it.

### Project vs label

A **project** has an end. A **label** is a durable product surface or category.

| This is a project | This is a label |
| --- | --- |
| HDFC VPC deployment | Chat |
| Validation phase 1 and 2 | Reports |
| Chat front end phase 1 | Intelligence |
| News one-pager V1 | Metrics |
|  | Validation |
|  | Vault |

The test is: **can you complete the sentence "This is done when ___"?** If yes, it may be a project. If no, it is probably a label, an idea that needs a Spike or work that has not been scoped yet and should be in Backlog (see **Issue statuses**).

---

## Research and Spikes

A Spike is an issue type label we have created (see full list of Issue Types below) for a bounded question whose output is a decision or recommendation (and sometimes a document or a new scoped issue), not shipped code.

Every Spike must include:

- **Question to answer**: the specific uncertainty.
- **Timebox**: a hard limit on effort, in hours
- **Output**: the recommendation or decision to record.

When the timebox expires, stop investigating and record the best recommendation supported by what you learned, or clearly add a comment extending the timebox if you need more time, ideally with approval from Nikhil.

A Spike is complete when that output is recorded, not merely because time has elapsed. If the result calls for delivery work, create or update the resulting issue/project and prioritise it separately.

### Research inside an issue or a separate Spike?

If a delivery issue is mostly clear and needs a small amount of investigation, keep that investigation inside the issue and update the definition of done before starting implementation. You can use sub issues for Spikes inside larger Issues.

Create a separate Spike when the investigation is substantial enough to deserve its own timebox, has a separate decision to make, or could lead us to decide not to do the delivery work at all. Prefer the first option when possible; Spikes should be deliberate exceptions, not a way to label vague work.

---

## Definition of done and acceptance criteria

These fields turn a captured issue into work that someone can start.

**Definition of done** is the defined outcome written out on the issue: one sentence describing what is true when the work is finished. State the end result, not a list of activities. Someone who was not involved should understand what changed.

**Acceptance criteria** are the specific, observable checks that demonstrate the definition of done. Another person should be able to use them (assume they have the necessary access to all systems) to verify the result.

```
Title: Fix document upload retry loop on large batches

Definition of done:
A 60-document upload completes with every document linked to its job, and no job
enters a retry loop.

Acceptance criteria:
- Upload the 60-document test set on staging; all 60 complete.
- Check the jobs table: 60 rows, each linked to a document.
- Check the worker log: no retry entries for the run.
```

### If you do not yet know what done means

As mentioned before, you can always capture the issue in Backlog. **You cannot move it to Todo or start committed work until the outcome is clear enough to define and verify.**

Write your best draft, then raise the uncertainty at standup or ask Nikhil.

If someone creates an issue in Todo for you that is too vague to start and doesn't have clear acceptance criteria and definition of done, bring this up in standup.

---

## Issue statuses

We are using the six statuses below. They already exist in Linear and we are adding none. (Linear also ships a Duplicate status, which we are not using for now.)

```
Backlog  ->  Todo  ->  In Progress  ->  In Review  ->  Done

Canceled is an exit from any status.
```

| Status | Use it when |
| --- | --- |
| **`Backlog`** | The work is captured. It may still be unscoped, unassigned, or unprioritised. |
| **`Todo`** | The work is ready to start **this week**: it meets all of the Backlog-to-Todo checks below. |
| **`In Progress`** | The owner is actively working on it. Maximum three per person. |
| **`In Review`** | The work is awaiting review, testing, feedback, or another explicit response before it can be completed. The original owner remains accountable for closing the loop. |
| **`Done`** | The outcome is complete and the acceptance criteria have been checked. |
| **`Canceled`** | We decided not to do it. Leave a one-line comment explaining why. |

*Note: We do not have a formal process for reviewing work yet. This will be defined.*

*Note: these statuses may change as we define our review and deployment processes, and we may need more granular statuses for "Done". We will figure this out in the future. For now, use these 6.*

### The Backlog-to-Todo flow

An issue moves from Backlog to Todo only when it has all of the following:

1. **An owner**
2. **A priority**: set or clearly communicated by Nikhil.
3. **A defined outcome / definition of done**: what is true when the work is complete.
4. **Acceptance criteria**: the checks that prove the outcome.
5. **Enough scope to begin**: including the project, if one applies.
6. **Clear alignment with Nikhil to begin the work this week**

If any of these are missing, leave it in Backlog.

**Who moves it.** You do, for your own work, once all 6 are true. If the only thing missing is the priority, ask Nikhil rather than guessing. **"This week"** means the current working week; we are not using Linear Cycles, so nothing does this automatically.

### Priority

**Nikhil sets or clearly communicates priority. Do not invent your own priority.**

Priority is required for `Todo`, not for `Backlog`. If Nikhil has already set it in a meeting, standup, or Slack, put that priority on the issue yourself. If the work is ready to move to `Todo` and you do not know its priority, ask him explicitly. Do not guess.

### Limits and completion

**`In Progress` : maximum three at a time.** If something new arrives and you already have three issues in progress, do not silently start a fourth. Ask Nikhil what should come off your plate, and move that item back to Todo if appropriate.

**Moving to `Done`.** You can move your own issues to Done without permission once the outcome and acceptance criteria are met. Update the issue with any useful evidence (test result, link, decision, or brief note). Work moved to Done is reviewed on Friday. Bring the evidence you used to verify it.

---

## Issue types

Put one type on every issue. In Linear the type is a **label**; there is no separate type field. The type does not change how the issue moves through statuses, it just tells everyone what kind of work it is.

The quick test between the three that get confused: **Feature** means it did not exist, **Improvement** means it existed and now works better, **Chore** means user-visible behaviour probably doesn’t change.

| Type | Use it when | Example |
| --- | --- | --- |
| **`Bug`** | Something is broken or does not behave as intended | Citations render in the wrong position in exported DOCX files |
| **`Feature`** | A capability that did not exist before | Users can ask for certain types of charts to be included in their DRHP reports |
| **`Chore`** | Planned upkeep that does not change user-visible behaviour | Bump the SDK version and update the Dockerfile |
| **`Spike`** | A bounded question to answer; output is a decision/recommendation/doc, not shipped code | Benchmark Glean data connectors and recommend go/no-go |
| **`Improvement`** | Something that already exists works better, faster, or at larger scale | Enabling 50 documents to be processed at once in the Chat app |

Improvement issues need a measurable current state and target state. "Make it handle concurrency" is not finite enough to start.

```
Title: Process 50 documents at once in Chat, up from 30

Definition of done:
A single upload of 50 documents in Chat processes completely, and all 50 are
queryable afterwards.

Acceptance criteria:
- Current measured limit: 30 documents (measured, not assumed).
- Upload 50 documents in one go on staging. All 50 finish processing.
- Verify (from logs, blob or otherwise that all 50 were processed successfully)
```

---

## Creating an issue

Linear has native fields, plus a free-text description. **Two of the things we require are not fields.** They go in the description.

| What we need | Where it lives in Linear |
| --- | --- |
| Title | Title |
| Type (`Bug, Feature, Chore, Spike, Improvement`) | A **label**. There is no type field |
| Product surface (Chat, Reports, Metrics, and so on) | Also a **label** |
| Owner | Assignee |
| Priority | Priority |
| Project | Project, if one applies |
| Status | Status |
| **Definition of done** | In the **description**, under a "Definition of done" heading |
| **Acceptance criteria** | In the **description**, under an "Acceptance criteria" heading |

**At creation, the minimum is a title and a type label.** Everything else can come later. Put it in Backlog and carry on.

**Before it moves to Todo**, it needs all 6 Backlog-to-Todo checks.

**Owner.** Assign yourself if you are doing it.

**Project.** Add one only if the work clearly belongs to a project that already exists. If you are unsure, leave it blank and raise it at standup. Do not create the project yourself.

**Status.** Backlog, unless it already meets all 6 checks.

### An example

```
Title:      Show the section heading on metric search results
Labels:     Feature, Metrics
Project:    (none)
Status:     Todo
Priority:   Medium
Assignee:   Pratham

Description:

Definition of done:
A metric search result shows the section heading it came from, above the
matched text.

Acceptance criteria:
- Search "revenue" in the D&B report. Every result shows its section heading.
- A result taken from a table shows the table caption instead.
- A result with no heading above it shows the document name, not a blank.
```