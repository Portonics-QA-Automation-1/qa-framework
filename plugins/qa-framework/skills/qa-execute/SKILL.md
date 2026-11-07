---
name: qa-execute
description: Run a manual test round - execute approved test cases on an Android device/emulator with evidence, record each result live in the named Execute.io run, and summarise. For iOS cases, prepare the checklist and record the QA member's results.
argument-hint: "<feature slug> <run name> [case ids | all] [env] [device]"
---

# QA Manual Execution

> Follows `${CLAUDE_PLUGIN_ROOT}/reference/agent-protocol.md`: result contract with a way forward, ask before
> Blocked/Failed, a yes before any external write, the QA verification gate, CONTEXT.md updated at the end.
> A QA member's direct instruction overrides this skill's workflow rules (never the hard rules).

Argument: `$ARGUMENTS` — feature, Execute.io run (and plan) name, which cases, environment
(default staging) and device.

## Steps

1. If the run name, case list or device is missing, ask the QA member (one question).
   Never create a run here; if it doesn't exist, ask whether to create it (names first).
2. Run `/qa-framework:qa-env-readiness` for the cases' account types and platforms; show gaps and ask
   whether to start (gapped cases become Blocked).
3. Launch the `qa-framework:qa-manual-executor` subagent with the case list, run/plan names, environment
   and device. Prefer a separate session for long rounds so the QA member can keep working;
   only one executor per device.
   - When you run the cases or checks yourself instead (e.g. an exploratory check with no case list), you are the
     executor: from the chat (`mcp__qa_connector__report_progress` in the tool list) report progress as the
     protocol section 4b says, right after **every** recorded result, not only at the start. Follow the
     brain's playbooks for the way to each check (protocol section 5b): Maestro shared steps for login, pop-ups
     and navigation on the emulator, screenshots only at checkpoints and expected results.
4. When it finishes, check: every case has a status; every Failed/Blocked has a comment and
   evidence; SUMMARY.md exists; results are in Execute.io (or results.json if sync was
   unavailable — say so).
5. Report counts and failures, and offer `/qa-framework:qa-triage` for each Failed case.
