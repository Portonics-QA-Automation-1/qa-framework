---
name: qa-env-readiness
description: Check test environment and test-data readiness (accounts per type, builds, devices, Back Office/VPN, integrations) for a feature before test design or a test round, and list the gaps that would block cases. Use when asked "are we ready to test X" or before starting execution.
argument-hint: "<feature slug> [environment: staging|preprod|prod]"
---

# QA Environment Readiness

Argument: `$ARGUMENTS` — the feature (slug or test-case file) and optionally the environment
(default: staging).

## Steps

1. Launch the `qa-framework:qa-env-readiness` subagent: "Check readiness for `<feature>` on `<env>`
   following your instructions."
2. Check its report: every area has a status with evidence; no secret value appears.
3. Present the verdict, the gaps (with owners) and the cases that would be Blocked. Ask the
   QA member whether to fix gaps first or start and mark those cases Blocked.

## Rules

- Read-only. Never log in, connect VPN or authenticate a connector on the QA member's behalf.
