---
name: qa-sync
description: Sync approved QA artifacts (structure, test cases, automated twins, Maestro flows, results) to Execute.io safely - approved names only, full payloads, no secrets, verified afterwards.
argument-hint: "<what to sync, e.g. \"test cases for <feature-slug>\" | \"flows for TC-005,029\" | \"results of round 2\">"
---

# QA Sync to Execute.io

Argument: `$ARGUMENTS` — what to sync.

## Steps

1. Identify the artifacts and the target project (from the workspace `CLAUDE.md`).
2. If anything new would be created (suite, folder, milestone, plan, run), list the exact
   names and wait for the QA member's explicit approval.
3. Launch the `qa-framework:qa-sync-manager` subagent with the approved names and artifacts.
4. Present its verification (IDs, mismatches, skipped items). Never report a sync as done
   without that verification.
