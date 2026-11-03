# QA Framework v2: enterprise agentic SQA (design for approval)

Status: **draft for the QA lead's approval** (2026-11-03). Nothing below is built until it is approved.

Principle: **AI agents execute, QA members validate.** Every stage ends at a QA approval gate. No task
ever stops without an answer: an agent that cannot continue returns what is missing, why, and the
options to continue, with its recommendation.

---

## 1. What changes, in one table

| Today | v2 |
|---|---|
| Agents exist twice (plugin copies and older copies on one Mac); the BrowserStack agent exists only on one Mac | **One source of truth: the `qa-framework` plugin.** Every QA member installs it; no local copies |
| Some agents and skills carry ATOM-specific words and paths | **Agents are project-neutral.** Everything project-specific comes from the workspace (BRAIN, conventions) and Execute.io |
| Brain set up by hand per workspace | `/qa-workspace-init` creates a project workspace with its brain, conventions and folders in one step |
| CONTEXT.md updated when someone remembers | **Every agent finishes by writing its result to CONTEXT.md** through one shared step, so a new session never misses work |
| An agent that lacks information stops or guesses | **Hand-back protocol:** status + what is missing + options + recommendation; the Master Agent turns it into a choice card |
| Stages chained loosely | **Enterprise SQA lifecycle** with entry/exit criteria and a QA gate per stage |
| Results judged by one agent | **Second-pass reviewer** checks results for consistency before the QA member sees them |

---

## 2. Three layers

```
 QA member (validator)
    │ chat
    ▼
 Master Agent (qa-master)  ── routes, tracks, asks, never does the work itself
    │ task contract                    ▲ result contract (hand-back)
    ▼                                  │
 Specialist agents (qa-* in the plugin) ── do the work, report back
    │ read / write
    ▼
 Project workspace (one per project): BRAIN.md · CONTEXT.md · conventions/ · features/
 + integrations: Execute.io (TMS), Karmo (defects), BrowserStack App Live, Maestro, Firebase, Figma
```

- **Plugin** (`qa-framework`, GitHub): agents, skills, the Master Agent prompt, templates and the
  protocol. Versioned, with a changelog. Project-neutral.
- **Project workspace** (local, per project): the project's knowledge and work. ATOM Store and Robi
  each have their own; they never share files or facts.
- **Integrations** are configured per workspace in `conventions/integrations.md` (which Execute.io
  project, which Karmo key, which BrowserStack user, which devices). No secrets, only variable names.

### Brains: one per scope, never mixed

| Brain | Where | Holds | Never holds |
|---|---|---|---|
| **Execute.io development** | `~/PycharmProjects/TestForge` (`BRAIN.md`, `CONTEXT.local.md`, `CONTEXT-archive.md`) | Product code, architecture, servers, deploy, Master Agent internals, dev decisions | Project QA work |
| **ATOM Store project** | `~/Desktop/AtomStoreWorkSpace` (`BRAIN.md`, `CONTEXT.md`, `CONTEXT-archive.md`) | ATOM app logic and behaviour, features, cases, rounds, IDs, QA decisions, how ATOM uses Execute.io | Execute.io internals, Robi |
| **Robi Single App** (and any new project) | its own workspace, created by `/qa-workspace-init` | That project only | Anything from another project |

Each brain follows the rules of its own `CLAUDE.md`. A task that touches two scopes writes each fact
to its own brain (example: "Master Agent card bug" → TestForge brain; "ATOM round blocked by it" →
ATOM CONTEXT).

---

## 3. Project workspace layout (created by `/qa-workspace-init <project>`)

```
<Project>Workspace/
  CLAUDE.md                 rules for this workspace (small; points to BRAIN.md)
  BRAIN.md                  lasting project logic (system map, domain rules, environments, IDs, app behaviour, decisions)
  CONTEXT.md                live status (in progress, waiting on QA, next steps); written by every agent
  CONTEXT-archive.md        finished history
  conventions/
    qa-guidelines.md        test-case rulebook (snapshot; Execute.io rulebook wins if newer)
    environments.md         environments, account variable NAMES, devices, VPN, Back Office
    integrations.md         Execute.io project ids, Karmo key, BrowserStack user, Maestro, Firebase
    gates.md                this project's approval gates (defaults from the plugin; the project may add)
  features/<feature>/
    story/                  FRS, user story, mockups
    analysis.md             requirement analysis (RA-n)
    plan.md                 test plan
    cases.md + cases.xlsx   test cases (source of truth + client sheet), Execute.io ID map
    rounds/<round>/         results.xlsx, SUMMARY.md, evidence, case-improvement notes
    automation/             selection sheet, flow list
    status.md + metrics.csv stage, gates passed, what waits on QA, timings
  builds/                   APK/IPA received (git-ignored)
  maestro/                  flows, shared steps, env NAME files (values never committed)
```

The ATOM workspace today uses `TestCase/`, `pipeline/` and `APK/`. v2 reads both layouts, so nothing
has to move at once; new features use `features/<feature>/`.

---

## 4. Enterprise SQA lifecycle (per feature, per release)

Aligned with ISTQB's test process (planning, analysis, design, implementation, execution, completion)
and the team's tools.

| # | Stage | Agent(s) | Entry criteria | Output | Exit = QA gate |
|---|---|---|---|---|---|
| 0 | **Intake** | qa-master | QA request or new story/build | feature folder, status.md | QA confirms scope and feature name |
| 1 | **Requirement analysis** | qa-requirement-analyst | FRS / story available | analysis.md: testable items, RA questions, verdict | QA approves; RA questions sent to BA |
| 2 | **Test planning** | qa-test-planner | analysis approved | plan.md: scope, risks, matrix, entry/exit, effort, Execute.io names | QA approves plan and names |
| 3 | **Test design** | qa-test-designer | plan approved | cases.md/xlsx with traceability; risk-based priority | QA reviews cases |
| 4 | **Readiness** | qa-env-readiness | cases approved | ready / not-ready list (accounts, builds, devices, access) | QA accepts gaps |
| 5 | **TMS sync** | qa-sync-manager | readiness accepted | suite, cases, run in Execute.io | QA approves each write |
| 6 | **Build intake** | qa-build-intake (new) | build shared | build identified (version, env, signing), uploaded, smoke on one device | QA approves upload; smoke fail stops the round |
| 7 | **Execution round N** | qa-browserstack-executor ×2 (Android, iOS in parallel) or qa-manual-executor (local device) | build accepted, run named | results per case with evidence, in Execute.io | — (goes to review) |
| 8 | **Result review** | qa-result-reviewer (new) then QA | round finished | consistency-checked report: Failed / Needs Review / Blocked with reasons | **QA validates each failure** |
| 9 | **Defect management** | qa-triage, qa-defect-filer | QA marked failures valid | Karmo tickets linked to cases | QA approves each ticket |
| 10 | **Retest / round N+1** | qa-retest + executors | fixed build | failed + needs-review first, then the feature | QA validates |
| 11 | **Automation** | qa-automation-engineer | feature passed | smoke / sanity / regression selection + Maestro flows, validated | QA reviews selection and flows |
| 12 | **Regression per deployment** | qa-regression-runner (Execute.io Maestro agent) | flows promoted | run report, triaged failures | QA reviews failures |
| 13 | **Release readiness** | qa-report-signoff | exit criteria met or waived | readiness report (no go/no-go) | **Go/no-go stays human** |
| 14 | **Post-release** | qa-post-release | release live | crash/analytics check, escaped defects → new cases | QA reviews |

Cross-cutting, every stage: CONTEXT.md update, status.md + metrics.csv (time per stage, cases, defects),
traceability (story ↔ case ↔ run ↔ defect), brain learning (new app behaviour → BRAIN.md).

**Gates** (default; a project may add more in `conventions/gates.md`):
- Always QA approval: end of every stage; any write to Execute.io, Karmo, Figma or a shared doc;
  downloads and uploads of builds; anything in production; Maestro flow promotion; release report.
- Never needs approval: reading, analysing, drafting, running cases on a test device, writing local
  round files.
- Never done by an agent: typing credentials on a third-party site, completing a payment, go/no-go.

---

## 5. Master Agent ↔ specialist protocol

### 5.1 Task contract (Master → specialist)

```yaml
task_id: ATOM-PINU-R2-ANDROID          # project-feature-step
goal: Execute the Android cases of Pin/Unpin on build 90.17.1-debug (64)
project: ATOM Store                    # selects the workspace and brain
feature: pin-unpin
inputs: {cases: features/pin-unpin/cases.xlsx, run: "Pin Unpin ... v2", env: staging, device: Galaxy S24}
constraints: [no credentials on BrowserStack, no payment confirm, results only to the named run]
done_when: every Android case has a status with evidence; results file written
report_to: qa-master
```

### 5.2 Result contract (specialist → Master), the hand-back

Every specialist ends with exactly one of these:

| Status | Meaning | Must include |
|---|---|---|
| `DONE` | finished | summary, outputs (files, IDs), what the QA member should check |
| `NEEDS_APPROVAL` | ready, but the next step has a side effect | the exact action (e.g. "sync 38 results to run 140") |
| `NEEDS_INPUT` | cannot continue without information | what is missing, why, **2–3 options**, recommended option, what each option costs |
| `BLOCKED` | cannot continue for a reason no input fixes now | the blocker, who can remove it, **what can continue meanwhile**, and a suggested route |
| `PARTIAL` | some done, some blocked | done list + blocked list, each blocked item with options |

Rule: **no hand-back without a way forward.** "Test cases not available" is never the whole answer.

### 5.3 Example: "test feature X" but there are no test cases

```yaml
status: NEEDS_INPUT
missing: test cases for feature X (no cases.md, no Execute.io suite)
options:
  A: {route: qa-test-design, does: write cases from the story in features/X/story, cost: ~20 min + QA review,
      then: qa-sync -> execution}
  B: {route: qa-browserstack-executor (exploratory mode), does: charter-based exploratory session from the
      story's acceptance criteria, gives: session report + draft cases, cost: ~30 min, limit: not traceable to approved cases}
  C: {route: ask QA, does: QA points to cases stored elsewhere}
recommended: A if a story exists, else B
continue_meanwhile: build intake and upload can start now
```

The Master Agent shows this as one card ("No cases for X. A) write them first (recommended) B) explore now
C) cases are elsewhere"). One click continues. Routes with side effects still pass their own gates.

### 5.4 Master Agent behaviour

- Answers status questions itself from CONTEXT.md, status.md and the task list; dispatches real work.
- Keeps a **task ledger** (in Execute.io's task list and mirrored to CONTEXT.md): every task, its state,
  what it waits on.
- Splits independent work and runs it in parallel (Android and iOS executors start as soon as each device is
  ready; neither waits for the other).
- Never says "done" before the specialist's `DONE` arrives; never decides go/no-go; asks one question at a
  time, each with options.
- Re-routes on `NEEDS_INPUT`/`BLOCKED` using the options, after the QA member picks (or automatically when
  the chosen route has no side effect and the project's gates allow it).

### 5.5 Rules added by the QA lead (2026-11-03), detailed in `reference/agent-protocol.md`

- **Preflight before any manual test:** build, environment (staging / preprod / prod), where to test
  (BrowserStack App Live / own device / emulator), single or parallel (BrowserStack), which cases, where results
  go (Execute.io run or workspace), which accounts and data are available. Asked together, only what is missing.
- **Login per target:** BrowserStack → the QA member logs in; emulator/simulator → the agent logs in with the
  fixed staging OTP through the project's login automation; production → the QA member enters any OTP.
- **Ask before Blocked/Failed:** missing accounts or data (postpaid, Back Office, linked number) are asked for
  first, with options; Blocked only after the QA member confirms it is unavailable; Failed only for real app
  behaviour.
- **Hard verification gate:** after testing, results wait for the QA member's manual verification; the next
  stage (bug filing, retest, automation) does not start until it is recorded.
- **Next step proposed** after every task; the QA member can still assign any task to any agent.
- **Bugs filed by a separate agent** (`qa-defect-filer`) after verification and approval.
- **Recheck of a fixed build:** reported issues + related area (neighbours, impact of the fix, core passed cases);
  new failures reported separately as possible regressions from the fix.
- **Automation:** the agent asks "write the Maestro flows for <feature>?"; after the yes it decides smoke / sanity /
  regression, gets each case's validation point confirmed by the QA member, writes and runs the flows, and asks to
  sync them to Execute.io once they pass.
- **Any external write** (Execute.io, tracker, Figma, shared docs) is approved through the Master Agent at the moment
  it happens.

(The Master Agent's code, cards and relay live in Execute.io: that part is Execute.io development and is
planned and tracked in the TestForge brain, not here.)

---

## 6. Accuracy controls (no ambiguous or wrong results)

1. **Evidence rule:** Passed only when every expected result was seen; the actual result is written per step.
2. **Five statuses:** Passed, Failed, Blocked, Needs Review, Not run. Needs Review whenever the outcome
   depends on an open requirement question or the copy differs from the mockup.
3. **Re-check before Failed:** a failure is reproduced once (fresh state) before it is recorded Failed.
4. **Second-pass reviewer (`qa-result-reviewer`, new):** after a round, before the QA member sees it:
   - same case on Android and iOS judged the same way? (Round 2 marked the same Setting finding Failed on
     iOS and Needs Review on Android; the reviewer would have aligned them);
   - every Failed has step, expected, actual and repro; every Blocked has a cause and an owner;
   - no Passed without per-step actuals; no secrets in any comment.
5. **AI vs human results kept apart:** comments start "AI-executed (awaiting QA review)"; the QA member's
   validation is recorded separately.
6. **Traceability check** at each gate: every story criterion has a case, every case a result, every failure
   a decision.

---

## 7. Context that never gets lost

- Every agent's last step: append a dated entry to the workspace's CONTEXT.md (what was done, outputs,
  what waits on QA, next step) and update `features/<feature>/status.md`.
- The SessionStart hook shows the latest entries and anything changed since BRAIN.md was trained.
- `/workspace-brain learn` daily or after a round moves lasting facts to BRAIN.md and old entries to the
  archive.

---

## 8. New and changed pieces

| Piece | Type | Change |
|---|---|---|
| `qa-workspace-init` | skill (new) | create a project workspace: folders, CLAUDE.md, BRAIN/CONTEXT from templates, conventions stubs, hook |
| `qa-master` | agent (in Execute.io) | protocol 5.1–5.4, ledger, re-routing, parallel dispatch |
| `qa-build-intake` | agent (new) | find/download build, identify, upload to App Live, smoke check |
| `qa-browserstack-round` + `qa-browserstack-executor` | skill + agent | move into the plugin, project-neutral; add exploratory mode |
| `qa-result-reviewer` | agent (new) | second-pass consistency and evidence check |
| all `qa-*` agents | agents | end with the result contract and the CONTEXT update; read project facts from the workspace |
| `qa-feature-pipeline` | skill | follows section 4, writes status.md/metrics.csv |
| templates | plugin | BRAIN/CONTEXT/CLAUDE.md, conventions/*.md, gates.md, status.md |
| local copies in `~/.claude/agents`, `~/.claude/skills` | — | retired after the plugin release (backed up first) |

---

## 9. Known limits (stated, not hidden)

- **Login on BrowserStack:** agents do not type credentials on a third-party site. Fully agent-only rounds
  need a staging QA auto-login in the app; until then the QA member logs in once per device.
- **Android secure screens:** use debug staging builds on App Live (release builds stream the login black).
- **Execute.io:** results cannot carry attachments; a run's cases cannot be listed through the MCP tools
  (both are Execute.io development items).
- **Analytics checks** need CleverTap/GA access for the agent's environment.

---

## 10. Roll-out (each phase ends at a QA approval)

| Phase | Work | Where |
|---|---|---|
| 1 | Protocol + templates + `qa-workspace-init`; merge local agent changes into the plugin; move the BrowserStack round into it | qa-framework |
| 2 | Result contract + CONTEXT step in every agent; `qa-result-reviewer`; `qa-build-intake`; pipeline per section 4 | qa-framework |
| 3 | Master Agent: contracts, ledger, choice cards, parallel dispatch, re-routing | Execute.io (TestForge brain) |
| 4 | Pilot: one ATOM feature end to end; fix; release qa-framework 2.0.0; Robi workspace onboarded with `/qa-workspace-init` | ATOM, Robi |
