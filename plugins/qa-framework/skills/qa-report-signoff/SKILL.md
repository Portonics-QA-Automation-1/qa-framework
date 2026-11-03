---
name: qa-report-signoff
description: Compile a release-readiness summary (pass/fail counts, open defects, coverage gaps) for a go/no-go decision. Use before a release when you need a clear summary of QA status - never produces the go/no-go decision itself.
argument-hint: "<release or feature name>"
---

# QA Report & Sign-off

> Follows `${CLAUDE_PLUGIN_ROOT}/reference/agent-protocol.md`: result contract with a way forward, ask before
> Blocked/Failed, a yes before any external write, the QA verification gate, CONTEXT.md updated at the end.
> A QA member's direct instruction overrides this skill's workflow rules (never the hard rules).

Argument: `$ARGUMENTS` — the release/feature name to report on.

## Steps

1. Launch the `qa-framework:qa-report-signoff` subagent with whatever test results, defect lists, and
   coverage information is available for this release/feature.
2. Present the compiled summary as-is.
3. Remind the QA member/stakeholders that the go/no-go decision is theirs to make — this
   agent never states one, by design.
