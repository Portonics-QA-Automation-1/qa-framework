---
name: qa-impact-analysis
description: Assess what existing tests/features are affected by a code or requirement change, to scope regression testing. Use before deciding what to re-test after a change.
argument-hint: "<description of the change, a diff, or a PR>"
---

# QA Impact Analysis

Argument: `$ARGUMENTS` — describe what changed, or point at a diff/PR/changed files.

## Steps

1. Launch the `qa-framework:qa-impact-analyst` subagent with the change description/diff and any known
   existing test-case suites for the affected area.
2. Present its direct/indirect/adjacent impact findings and suggested regression scope to the
   QA member as-is — do not narrow or editorialize the findings yourself.
3. Ask the QA member to confirm the actual regression scope; this agent's output is input to
   that decision, not the decision itself.
