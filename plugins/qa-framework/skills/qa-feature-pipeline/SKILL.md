---
name: qa-feature-pipeline
description: Run one feature through the whole STLC with the QA agents - requirement analysis, plan, readiness, test design, sync, manual round on each build, triage and bug filing, retest of fixed bugs, automation and promotion to regression, regression per build, sign-off and post-release - stopping only at the QA member's approval gates, keeping a live status file and timing metrics per feature. Use when asked to "run the pipeline for <feature>", "take <feature> from requirement to release", "what is waiting on me for <feature>", "a new build is out for <feature>", or "make the management report for <feature>".
argument-hint: "<feature slug> [start | status | build <apk|latest> | report]"
---

# QA Feature Pipeline (one QA member + AI agents)

Argument: `$ARGUMENTS`: the feature slug (as in `TestCase/<feature>-…`), then a mode:

| Mode | What it does |
|---|---|
| `start` (default) | Work out the current stage from the files, then run stages until the next gate |
| `status` | Print the status file's "Waiting on QA" list and stage table. Changes nothing |
| `build <apk\|latest>` | The build event: smoke, new-feature cases, retest of fixed bugs, regression |
| `report` | Write the management report from the metrics file |

The QA member is the only approver. The agents do the work, and the QA member reviews it at the gates.
**Never cross a gate without an explicit yes in chat.** One yes covers only the gate it was asked for.
Every rule of the workspace still applies: its `CLAUDE.md`, the project rulebook and conventions
(from `get_qa_guidelines` when the `execute-io-sync` MCP server is connected, otherwise
`conventions/qa-guidelines.md` and `conventions/environments.md`): no secrets in files, approved
Execute.io names only, bug filing only after a yes, pop-ups only through the workspace's guard,
automation only after the manual round.

## Files kept per feature

`pipeline/<feature>/` in the workspace:

- `status.md`: the live status (template: `templates/status.md` next to this skill). Rewrite it at the
  start and end of every stage and at every gate. Top section "Waiting on QA" lists open gates, newest
  first, each with the file to review and the exact question.
- `metrics.csv`: one row per stage run or gate (template: `templates/metrics.csv`). Columns:
  `stage,event,started,ended,actor,minutes,count,unit,source,notes`.
  - `actor` is `ai` for agent work, `qa` for the QA member's review time at a gate, `wait` for time
    a gate stayed open before the answer.
  - `source` is `measured` (timestamps taken by this skill) or `derived` (from file times or
    history, e.g. a replay). Never present derived numbers as measured.
  - At each gate, ask the QA member how many minutes the review took and log that as `qa`. If they
    don't say, log the gate with an empty `minutes` and the note "not reported".
- `report.md`: the management report (`report` mode).

Also update `CONTEXT.md` when a stage finishes (workspace rule).

## Stages

Work out the current stage from what exists. A stage counts as done only when its output exists
**and** its gate has a recorded yes in `status.md`. If a stage's output exists without a recorded
yes (work done before the pipeline), show it to the QA member as a gate and ask once.

| # | Stage | Run | Output | Gate (QA member approves) |
|---|---|---|---|---|
| 1 | Requirement analysis | `/qa-framework:qa-requirement-analysis` | `TestCase/<feature>-requirement-analysis.md` | The RA questions to send to BA/dev, and whether test design may start with open questions |
| 2 | Test plan | `/qa-framework:qa-test-plan` | `TestCase/<feature>-test-plan.md` | Scope, matrix and the Execute.io names (milestone, plan, run) |
| 3 | Readiness | `/qa-framework:qa-env-readiness` | readiness section in `status.md` | Only if Not ready: who fixes each gap. Ready → no gate |
| 4 | Test design | `/qa-framework:qa-test-design` | `TestCase/<feature>-test-cases.md` + `.xlsx` | The cases (spot check: story order, both account types, negatives per limit) |
| 5 | Sync cases | `/qa-framework:qa-sync` | Execute.io suite + cases, tc_ids written back | The sync itself (suite/folder names, local or production) |
| 6 | Manual round | `/qa-framework:qa-execute` per build | `TestCase/evidence/<feature>/<round>/SUMMARY.md` | Before start: the run name. Results are recorded live (the run was approved at gate 2) |
| 7 | Triage + bugs | `/qa-framework:qa-triage`, then `/qa-framework:qa-file-bug` (Karmo) | drafts under `TestCase/evidence/<feature>/<round>/bugs/` | Each draft: real bug or not. Then Components/Assignee/Sprint, then the final yes to file |
| 8 | Automation | `qa-framework:qa-automation-engineer` (selection, then flows) | `maestro/automation-selection/<feature>-automation-selection.xlsx`, `maestro/features/<feature>/` | The selection sheet; then each validated flow |
| 9 | Promote to regression | this skill (below) | tags in the flows, automation suite in Execute.io | The list of flows and tags, and the sync |
| 10 | Retest | `/qa-framework:qa-retest` per fixed bug | Execute.io results + verification comment drafts | Each comment before it is posted; the QA member closes the ticket |
| 11 | Regression per build | `/qa-framework:qa-regression` | `maestro/reports/<stamp>/` + run report | Syncing the results; any failure triaged as an app bug goes to stage 7 |
| 12 | Sign-off | `/qa-framework:qa-report-signoff` | release-readiness report | The QA member and the business make the go/no-go call. Never state it |
| 13 | Post-release | `/qa-framework:qa-post-release` | post-release report | Escaped defects → new test-case candidates (back to stage 4) |

Stages 6, 7, 10 and 11 repeat for every build until sign-off. Stage 8 runs **in parallel** with the
manual rounds once the first manual round has a summary (automation is a selected subset written
after the manual round; see `maestro/automation-selection`).

### How to run a stage

1. Log `started` in `metrics.csv` (actor `ai`) and set the stage to "Running" in `status.md`.
2. Run its skill or agent. Pass the feature slug and the approved names from `status.md`. Run
   independent stages as parallel subagents when both are unblocked (e.g. stage 8 flows while a
   manual round of the next build runs on a second emulator); one Maestro agent per emulator.
3. When it returns, log `ended`, the minutes and the count (cases written, cases executed, bugs
   drafted, flows validated…).
4. Check the output exists and is complete before calling it done (cases have 12 columns, every
   executed case has a status and evidence, every validated flow passed on the emulator).
5. Write the gate into "Waiting on QA" with the file to open and the question. Then ask it in chat,
   batching the gates that are open at the same time into one message so the QA member answers once.
6. Stop. Continue only after the answer. Log the gate's `qa` and `wait` rows.

## Build event (`build <apk|latest>`)

A new build is the main trigger once test design is done. In order:

0. **Network check**: if the project conventions name a VPN or network check for this environment
   (a check URL and the answer that means "reachable"), run it with
   `curl -s -o /dev/null -w "%{http_code}" --max-time 15 <check url>`. No answer means the VPN is
   off: stop, write the gate "Connect the VPN", and run nothing (a run without it only fails at
   the first network call). Never connect the VPN or enter its credentials.
1. **Build**: delegate to `qa-framework:qa-regression-runner` to fetch it (Firebase App Distribution through the
   QA member's logged-in CLI, or the named APK). A download needs the QA member's OK (file, version,
   size). Record the build in `status.md`.
2. **Smoke** (`/qa-framework:qa-regression … smoke`). If smoke fails: triage, write the gate, stop the event.
3. **New-feature cases**: run `/qa-framework:qa-execute` for the cases with no result yet, or Failed/Blocked in
   the last round, on this build. The run name follows `<Feature> - <Platform> - Round N - <build>`;
   a new run needs the QA member's yes for its name (one question).
4. **Retest**: read the feature's Karmo bugs (read-only); for each one in a fixed / ready-for-QA
   status, run `/qa-framework:qa-retest`. Draft the verification comments; never post or transition.
   Passed retests of "Waiting on fix" automation rows go into the same gate as "move to To
   write"; after the yes, their flows are written like any approved row.
5. **Regression**: `/qa-framework:qa-regression … regression` on the remaining emulators (up to 3, sharded),
   in parallel with step 3 when there is a free emulator.
6. **Triage** every failure from 3–5 (`/qa-framework:qa-triage`) and put the drafts into one gate.
7. Write one "Build <n>" summary in `status.md`: smoke, new cases (pass/fail/blocked), retests,
   regression totals, drafts waiting. Log each step in `metrics.csv`.

### Watching for builds (optional, persistent)

A scheduled task can start the build event without anyone typing. Creating it is a standing
configuration, so propose it and create it only after the QA member's yes. Suggested task: weekdays,
every 30 minutes on an always-on machine, prompt
`/qa-framework:qa-feature-pipeline <feature> build latest`, and the event exits at once when the latest Firebase
release is the build already recorded in `status.md`. It still stops at every gate (download OK,
run name, triage, filing, sync), so nothing is sent without the QA member.

## Promotion to regression (stage 9)

For each flow the QA member approved as validated:

1. Tags: keep `android` and the case id; add `regression`. Add `smoke` to at most one or two flows per
   feature: the shortest core positive path (for example "settings opens the customization page").
   Flows for one-off data setups get `one-time` instead and stay out of regression.
2. Run the feature once more by tag to prove the flows are picked up:
   use the workspace's Maestro run script (see its `maestro/README.md`) with the environment, the
   `regression` suite, the feature and the device. Pass every option and no stdin, so the script
   never waits at an interactive prompt.
3. Propose the Execute.io sync (automation suite, folder, flow bundle) through `/qa-framework:qa-sync`; sync after
   the yes. List the flows that were not promoted and why.

## `report` mode

Write `pipeline/<feature>/report.md` from `metrics.csv` and the stage outputs (template:
`templates/report.md`):

- Per stage: AI minutes, QA review minutes, output count.
- Totals: AI hours, QA hours, cases designed / executed, bugs drafted / filed / verified, flows
  validated / in regression, regression run time per build.
- "What the QA member decided" (every gate and its answer) and "What stayed manual" (iOS rounds,
  Back Office-only cases, exploratory checks, go/no-go).
- Mark every `derived` number as derived. Never compare with a two-QA estimate unless the QA member
  gives that estimate; then name it as their estimate.

Offer to publish the report as a page for management; publish only on a yes.

## Never

- Cross a gate, file a bug, post a Karmo comment, create Execute.io structure or sync without a yes.
- State a go/no-go decision.
- Write phone numbers, OTPs, keys or passwords into `status.md`, `metrics.csv` or the report.
- Write new Maestro flows outside stage 8, or before the first manual round of the feature.
