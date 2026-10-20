---
name: qa-test-design
description: Generate a traceable QA test-case suite for a feature from its approved spec/requirement. Use when QA asks to design or generate test cases, normally after requirement analysis is clean.
argument-hint: "<feature name or slug>"
---

# QA Test Design

Argument: `$ARGUMENTS` — the feature name/slug, or a pasted requirement.

## Steps

1. **Resolve the feature** the same way as `/qa-framework:qa-requirement-analysis`.
2. **Check requirement analysis first**, if a report exists for this feature. If there are
   Open Blocker findings, tell the user test design will be incomplete for those areas and
   ask whether to proceed anyway or wait for them to be resolved.
3. **Run the designer.** Launch the `qa-framework:qa-test-designer` subagent with: "Run test design for
   `<slug or requirement>` following your instructions."
4. **Check the result.** Verify, for every row (not a sample):
   - the table has the 12 required columns (no `Spec Reference` column);
   - `Section` is exactly one of the values the rulebook/project conventions allow (default
     `Android`, `iOS`, `BackOffice`, `Back End API Testing`), and app checks that apply to
     both platforms have an Android row and an iOS row;
   - `User / Account Type` is exactly one of the project's account types (from
     `get_qa_guidelines` → `project_conventions` or `conventions/environments.md`; no
     combined values; one row per type);
   - `Test Steps`, `Test Data` and `Expected Result` have the same numbered lines (1..N,
     matching numbers), and `Preconditions` holds no test data.
   Also verify: every requirement id is in the Requirements traceability table with TC IDs
   or in Specification gaps; every TC ID is unique; the coverage summary has no blank
   cells; no file outside the test-case output changed.
5. **Report to the user**: total case count, coverage summary verdict, the gaps list, and the
   file path. Next step: once this looks right, hand it to `/qa-framework:qa-automate-flow` per case.

## Rules

- Do not edit the spec/requirement, plan, or contracts.
- Do not commit changes.
- If a suite already exists and is marked approved, don't regenerate it silently — confirm
  the change first.
