---
name: qa-retest
description: Verify a fixed defect - re-test the linked cases and their neighbours on the new build, record results in Execute.io, and draft the verification comment for the defect.
argument-hint: "<defect key or description> <build> <run name>"
---

# QA Retest / Fix Verification

> Follows `${CLAUDE_PLUGIN_ROOT}/reference/agent-protocol.md`: result contract with a way forward, ask before
> Blocked/Failed, a yes before any external write, the QA verification gate, CONTEXT.md updated at the end.
> A QA member's direct instruction overrides this skill's workflow rules (never the hard rules).

Argument: `$ARGUMENTS` — the defect, the build containing the fix, and the Execute.io run.

## Steps

1. Ask for anything missing in one question: the fixed build (newest in the builds folder), run
   name, environment, target (BrowserStack / own device / emulator), single or parallel.
2. Launch the `qa-framework:qa-retest` subagent. Its scope is always the reported issues **plus the
   related area** (neighbours, impact of the fix, the feature's core passed cases), so a fix that
   breaks something else is caught. Show the scope with reasons and wait for a yes before execution.
3. Present the outcome per case and the drafted defect comment, with **new issues since the previous
   build listed separately** (possible regressions from the fix). Stop at the QA verification gate.
   Post to the defect tracker (or change the ticket status) only after the QA member approves the
   exact text; new issues are filed through `/qa-file-bug` after verification.
4. If retested cases were "Waiting on fix" in the automation selection sheet and now pass, show
   the proposed move to "To write". After the QA member's yes, update the sheet and ask whether
   to write those flows now (`/qa-automate-flow`).
