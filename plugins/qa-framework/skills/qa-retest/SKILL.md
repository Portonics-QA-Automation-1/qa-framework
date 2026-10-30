---
name: qa-retest
description: Verify a fixed defect - re-test the linked cases and their neighbours on the new build, record results in Execute.io, and draft the verification comment for the defect.
argument-hint: "<defect key or description> <build> <run name>"
---

# QA Retest / Fix Verification

Argument: `$ARGUMENTS` — the defect, the build containing the fix, and the Execute.io run.

## Steps

1. Ask for anything missing (run name, build, device) in one question.
2. Launch the `qa-framework:qa-retest` subagent; show the retest scope it proposes before execution.
3. Present the outcome per case and the drafted defect comment. Post it to the defect
   tracker (or change the ticket status) only after the QA member approves the exact text.
4. If retested cases were "Waiting on fix" in the automation selection sheet and now pass, show
   the proposed move to "To write". After the QA member's yes, update the sheet and ask whether
   to write those flows now (`/qa-automate-flow`).
