---
name: qa-post-release
description: After a production release - read-only production smoke, Crashlytics and analytics check for the new version, and escaped-defect feedback into test design.
argument-hint: "<released version>"
---

# QA Post-Release Check

> Follows `${CLAUDE_PLUGIN_ROOT}/reference/agent-protocol.md`: result contract with a way forward, ask before
> Blocked/Failed, a yes before any external write, the QA verification gate, CONTEXT.md updated at the end.
> A QA member's direct instruction overrides this skill's workflow rules (never the hard rules).

Argument: `$ARGUMENTS` — the released version.

## Steps

1. Confirm the QA member is available for the production smoke (entering the production
   account, and any OTP route the project conventions document, e.g. VPN + Back Office
   session). If not, skip the smoke and do the monitoring part only.
2. Launch the `qa-framework:qa-post-release` subagent.
3. Present the report and the recommended actions; the go/hotfix decision stays with the QA
   member and the business.
