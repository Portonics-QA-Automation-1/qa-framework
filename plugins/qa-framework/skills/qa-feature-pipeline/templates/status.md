# <Feature> — QA pipeline status

- Project: <project> · Platforms: <Android, iOS> · Account types: <Prepaid, Postpaid>
- QA member: <name> · Last update: <YYYY-MM-DD HH:MM>
- Current stage: <n. name> · Latest build: <version (code)> · Execute.io: <suite / plan / run names>

## Waiting on QA

<!-- Newest first. Every open gate: what to open, the exact question. Remove a gate once answered. -->
- [ ] **Gate <n> — <stage>** (opened <date time>): open `<file>`. <Question?>

## Stages

| # | Stage | State | Output | Gate answer (date) |
|---|---|---|---|---|
| 1 | Requirement analysis | Not started | | |
| 2 | Test plan | Not started | | |
| 3 | Readiness | Not started | | |
| 4 | Test design | Not started | | |
| 5 | Sync cases | Not started | | |
| 6 | Manual round | Not started | | |
| 7 | Triage + bugs | Not started | | |
| 8 | Automation | Not started | | |
| 9 | Promote to regression | Not started | | |
| 10 | Retest | Not started | | |
| 11 | Regression per build | Not started | | |
| 12 | Sign-off | Not started | | |
| 13 | Post-release | Not started | | |

States: Not started · Running · Waiting on QA · Done · Blocked (<who must act>) · Skipped (<why>)

## Builds

| Build | Date | Smoke | New-feature cases (P/F/B) | Retests | Regression (P/F) | Drafts waiting |
|---|---|---|---|---|---|---|

## Bugs

| Karmo key / draft | Title | Severity | State | Last retest |
|---|---|---|---|---|

## Decisions log

<!-- Every gate answer, verbatim in short: date, gate, answer. -->
