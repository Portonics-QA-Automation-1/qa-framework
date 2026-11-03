# <Project name> – lifecycle and gates

Defaults from qa-framework 2.x. The QA lead may tighten any row (never loosen the hard rules).
`verify: required` = the next stage does not start until the QA member has verified the results by hand
and the verification is recorded (agent protocol, section 6).

| # | Stage | Agent / skill | QA gate to leave the stage | verify |
|---|---|---|---|---|
| 0 | Intake | qa-master | scope and feature name confirmed | – |
| 1 | Requirement analysis | qa-requirement-analysis | analysis approved, questions sent to BA | – |
| 2 | Test plan | qa-test-plan | plan and Execute.io names approved | – |
| 3 | Test design | qa-test-design | cases reviewed and approved | required |
| 4 | Readiness | qa-env-readiness | gaps accepted | – |
| 5 | Sync to Execute.io | qa-sync | each write approved | – |
| 6 | Build intake | qa-browserstack-round (phase 1) / qa-execute | build upload approved | – |
| 7 | Execution round | qa-browserstack-round / qa-execute | results delivered | **required** |
| 8 | Defects | qa-triage, qa-file-bug | each ticket approved (only verified-valid failures) | – |
| 9 | Retest / next round | qa-retest, qa-browserstack-round | results delivered | **required** |
| 10 | Automation | qa-automate-flow | entry: feature **Stable** (protocol 8b) + QA yes, or a QA member's direct instruction; exit: selection and flows reviewed | required |
| 11 | Regression per deployment | qa-regression | failures reviewed | required |
| 12 | Release report | qa-report-signoff | go/no-go by people | – |
| 13 | Post-release | qa-post-release | findings reviewed | – |

Always needs a yes at the moment it happens: Execute.io / tracker writes, build downloads and uploads,
anything in production, publishing or sharing. Never done by an agent: credentials on a third-party site,
completing a payment, go/no-go.
