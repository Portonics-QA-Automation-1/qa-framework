---
name: qa-regression
description: Run the automated Maestro regression for a new build - smoke first, then regression sharded across emulators, with failures triaged and a timed report. Use when a new build arrives (Firebase App Distribution) or for the nightly run.
argument-hint: "[build/apk or \"latest\"] [env: staging|preprod|prod] [suite: smoke|regression]"
---

# QA Regression Run

Argument: `$ARGUMENTS` — the build (or "latest" from Firebase App Distribution), environment
(default staging) and suite (default: smoke then regression).

## Steps

1. Launch the `qa-framework:qa-regression-runner` subagent with the arguments.
2. Approve any build download it asks for (file, version, size).
3. Present the report: totals, duration, each failure with its classification and evidence.
4. Ask which follow-ups to do: sync results to a named Execute.io run (`/qa-framework:qa-sync`), draft
   defects (`/qa-framework:qa-triage`), or fix flows (`/qa-framework:qa-automate-flow`).
