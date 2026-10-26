---
name: qa-triage
description: Triage a test failure - classify it as a real bug, flaky/environmental issue, or test-design problem, and draft a defect report if it's real. Use when a test fails and you need to assess what happened before filing anything.
argument-hint: "<logs, screenshots, or a description of the failure>"
---

# QA Triage

Argument: `$ARGUMENTS` — the failure evidence (logs, stack trace, description) or a pointer
to it (e.g. a job id, a screenshot path).

## Steps

1. Launch the `qa-framework:qa-triage` subagent with the failure evidence.
2. Present its classification and reasoning as-is.
3. If classified as a Real bug, present the drafted defect report and ask whether to file it
   (in whatever tracker this project uses) or revise it first — never file it automatically.
4. **Filing in Karmo:** when the project files bugs in Karmo and the QA member wants this one
   filed, hand over to `/qa-framework:qa-file-bug` with the draft. It follows the project's
   "Karmo bug filing" rules, asks the Assignee/Sprint (and Components) pick-list and files only
   after a yes.
   **Filing in another tracker (only after an explicit yes for this specific draft):**
   using the claude.ai connector for the tracker the project conventions name (e.g. Jira)
   and the project key from the conventions (`get_qa_guidelines` → `project_conventions`, or
   `conventions/environments.md`):
   - Read the project's bug work type, priority values and labels first (read-only), and map
     the workspace severity (S1 Blocker … S4 Minor) to tracker priority; show the mapping once
     and ask the QA member to record it in the project conventions (Execute.io → API Keys →
     QA workspace) after approval.
   - Create the ticket with the approved title and description (steps, expected, actual,
     environment, build, Execute.io case/run IDs). No account identifiers, OTPs or personal
     data.
   - Attach the evidence screenshots, link the bug to its story ticket, add labels
     (feature, platform, account type).
   - Report the new ticket key and URL.
   If the connector is missing or needs authentication, save the draft to
   `TestCase/evidence/<feature>/defects/<short-title>.md` and say so.
