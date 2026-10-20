---
name: qa-test-plan
description: Write a feature test plan (scope, test matrix, entry/exit criteria, risks, effort, proposed Execute.io names) after requirement analysis and before test design.
argument-hint: "<feature slug>"
---

# QA Test Plan

Argument: `$ARGUMENTS` — the feature slug.

## Steps

1. Check `TestCase/<feature>-requirement-analysis.md` exists; if not, recommend
   `/qa-framework:qa-requirement-analysis` first and stop.
2. Launch the `qa-framework:qa-test-planner` subagent: "Write the test plan for `<feature>` following your
   instructions."
3. Check: every requirement ID is in scope or out of scope; the matrix has no blank cells;
   proposed Execute.io names follow `conventions/environments.md`.
4. Present the plan summary and ask the QA member to approve it and the proposed names.
   Nothing is created in Execute.io at this step.
