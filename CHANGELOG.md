# Changelog

## 2.1.6 — 2026-11-04

- **BrowserStack upload key from the chat** (needs Workspace Connector 0.9.1): before the first App Live upload,
  `mcp__qa_connector__browserstack_key` asks the QA member once with two input cards (username, then the access key)
  when the computer has no `browserstack.env`, and saves them only on that computer. The agent never asks for the
  key in a message or reads the file. Removes the key file from the desk-only setup (the user, 2026-11-04).
  Updated: qa-browserstack-round, qa-build-intake, agent-protocol §4a.

## 2.1.5 — 2026-11-04

- **Everything from Google Chat, browser opened automatically** (protocol section 4a; needs Workspace Connector
  0.9.0): the connector opens Chrome in the member's remembered profile, links Claude Code to Chrome, checks the
  connection and reopens / restarts Chrome by itself before the agent starts; the prompt names the browser to
  select. Only what it cannot fix is a chat card: a pick-list (profile, browser; asked once) or Retry / Cancel saying
  "from the chat" or "one-time setup at the computer" (install and sign in the Claude extension; save the
  BrowserStack password in that profile — both listed by `setup`). Mid-task: `open_chrome`, then
  `open_chrome restart`, then `browser_problem`. Never AskUserQuestion; a browser problem never ends the task (task
  53 stopped with "no connected browser").
- **BrowserStack sign-in from the chat** (the QA lead's safety line): the member saves the BrowserStack password
  once in Chrome's password manager in their BrowserStack profile; the agent only clicks Sign in on a form Chrome
  filled. It never sees, types, copies or stores the password. No saved login, a non-code 2FA, a CAPTCHA or no
  App Live seat → a card; a verification code → `request_input`. Claude Desktop is unchanged (the QA member signs
  in). Updated: qa-browserstack-round, qa-browserstack-executor, qa-build-intake, agent-protocol (sections 4, 4a, 11).

## 2.1.4 — 2026-11-04

- qa-build-intake: cheaper builds from the build group: reuse a file already in Downloads first; the direct lookup
  only if it works (no admin step mentioned); otherwise the browser read as text (get_page_text / find / refs),
  screenshots only when needed at scale 0.4; the download is checked on disk, not in the browser.

## 2.1.3 — 2026-11-04

- qa-build-intake: Drive links and folders in the build group, including Drive's "can't scan for viruses" page for
  large builds (Download anyway, only for the approved file); no access → the QA member asks the sender.

## 2.1.2 — 2026-11-04

- qa-build-intake: reuse a build already in Downloads (same name and size); say clearly that a TestFlight-only
  iOS build cannot go to App Live and ask for the .ipa.

## 2.1.1 — 2026-11-04

- App Live login from the chat, every environment: `request_input` takes `env_key` (MSISDN_PREPAID,
  MSISDN_POSTPAID, MSISDN, OTP, PIN). Staging: Execute.io answers from the project's stored test accounts.
  Preprod and production: the QA member replies to the input card in the chat (number, then the OTP from their
  phone; an expired OTP is asked again up to 3 times). OTPs that confirm payments or transfers stay human.
  The same for rounds on the emulator/simulator or the member's own device when run from the chat
  (qa-manual-executor). Needs Workspace Connector 0.7.0.
- qa-build-intake: builds from the dev team's Google Chat build group or shared Drive folder by group name and
  build name + version (`find_builds` / `download_build`, connector 0.7.0), saved in the member's Downloads folder.
- qa-browserstack-round: a "login check only" mode (upload, open, log in, report; no cases).

## 2.1.0 — 2026-11-04 (App Live rounds from the chat)

Decided by the QA lead on 2026-11-04. Needs Workspace Connector 0.6.0+ for the chat parts.

- **App Live login from the chat** (`qa-browserstack-round`, `qa-browserstack-executor`, protocol section 4): a
  round knows it runs from the chat when `mcp__qa_connector__request_input` is in the session's tool list. Then,
  on staging and preprod only, the agent asks the QA member for each MSISDN / OTP / PIN with `request_input` (one
  value per call, secret) and types it only into the app's login field on the App Live device. The value is
  never written into a file, result, evidence, summary, log or chat message, never repeated back, never typed
  anywhere else. Production OTPs and passwords stay with the QA member. In Claude Desktop (no `request_input`)
  the QA member still logs in (`NEEDS_HUMAN`). `NEEDS_HUMAN` stays for final payment confirms, production logins
  and values the QA member rejects or does not answer.
- **Builds** (`qa-build-intake`, `qa-browserstack-round`, `qa-feature-pipeline`): the agent may download the
  APK/IPA (team chat, Drive link, Firebase App Distribution) and upload it to App Live after the QA member's
  approval; from the chat that approval is an Approve card. A browser download is moved into the builds folder.
- **Browser** (`qa-browserstack-round`, `qa-browserstack-executor`, `qa-build-intake`, `qa-manual-executor`,
  protocol): agents use whichever browser tools the session has: the built-in browser (`mcp__Claude_Browser__*`)
  in Claude Desktop, Claude in Chrome (`mcp__claude-in-chrome__*`) in the chat. Parallel Android + iOS = one tab
  each. The `qa-workspace-init` CLAUDE.md template states the login exception.
- Fix: the `qa-browserstack-round` skill's `argument-hint` is quoted; before, its frontmatter failed to parse
  and the skill loaded without its description.

## 2.0.0 — 2026-11-03 (phases 1 and 2)

- Every agent has an "Agent protocol (qa-framework 2.x)" section: a QA member's direct instruction comes first
  (overrides workflow rules, never the hard rules); never stop without a way forward (`NEEDS_INPUT` with options and
  another agent that could continue); a yes at the moment of any external write; the result contract (status line,
  outputs, what to verify, next step); CONTEXT.md and the feature's status.md updated at the end (read-only agents
  return a `CONTEXT entry:` block for the caller).
- Every skill points to the protocol.
- New agent `qa-result-reviewer`: second-pass review of a round before the QA member sees it (coverage,
  cross-platform and cross-account consistency, status discipline incl. Blocked-without-QA-confirmation, regression
  signals, secrets, traceability); proposes corrections, never changes results.
- New agent `qa-build-intake`: finds and identifies builds (version, environment, debug/release, signing), checks
  they fit the release and the target, uploads/installs only after a yes.
- `qa-feature-pipeline` follows the 2.x lifecycle: build intake (5b), preflight + BrowserStack or local round (6),
  result review + hard QA verification gate (6b), only verified-valid failures to triage/filing (7), automation only
  for a Stable feature or on a QA instruction (8), sanity tag at promotion (9), retest = reported issues + related
  area (10); supports the `features/<feature>/` layout.

## Unreleased (2.0.0, phase 1) — 2026-11-03

Design: `docs/framework-v2-design.md` (approved by the QA lead 2026-11-03).

- **Agent protocol** `reference/agent-protocol.md`: task and result contract (`DONE`, `NEEDS_APPROVAL`,
  `NEEDS_INPUT`, `BLOCKED`, `PARTIAL`, always with options and a recommendation), preflight questions before
  any manual test (build, environment, target BrowserStack / device / emulator, single or parallel, cases,
  result destination, accounts and data), login per target, ask before marking Blocked or Failed, a hard QA
  verification gate after every round, approval before a stage's agent starts, next step proposed after every
  task, CONTEXT.md updated by every task.
- New skill `qa-workspace-init`: creates or upgrades a project workspace (layout, CLAUDE.md, conventions
  templates for environments, integrations and gates, feature status page) and its brain.
- Skill `workspace-brain` now ships in the plugin (project-neutral wording).
- New skill `qa-browserstack-round` and agent `qa-browserstack-executor`: agentic manual round on BrowserStack
  App Live, Android and iOS in parallel, results to Execute.io or the workspace, stops at the verification gate.
  Scripts `bs_upload.py`, `results_sheet.py` (five statuses incl. Needs Review), `setup_venv.sh`.
- Rules merged from older local copies, in neutral wording: pop-up guard rule (`qa-automation-engineer`,
  `qa-automate-flow`); tracker field fallbacks, priority scale and "no invented test case" (`qa-defect-filer`);
  optional database-level sync verification (`qa-sync-manager`); a preprod/prod OTP is entered by the QA member
  unless the project's conventions explicitly allow an agent lookup (`qa-manual-executor`, `qa-post-release`,
  `qa-regression-runner`).
- Retest (`qa-retest` agent and skill): a recheck of a fixed build always covers the reported issues **plus
  the related area** (neighbours, impact of the fix, the feature's core passed cases); new failures are reported
  separately as possible regressions from the fix; ends at the verification gate.
- Automation (`qa-automation-engineer`, `qa-automate-flow`): starts only after the QA member says yes to
  automating a verified feature; the agent decides the selection and suites (new suite tag **sanity** next to
  smoke / regression / one-time), shows it, and the QA member may change it; each case needs a QA-confirmed
  validation point and every flow ends with a labelled assertion; flows run green, then the agent asks to sync
  them to Execute.io.
- **Feature stable gate** (protocol 8b): agents offer automation only when a feature is stable (verified failures
  fixed and retested, no open requirement question changing behaviour, design final, last round passed and
  verified, known issues deferred by QA); a QA member's direct instruction to automate is always followed, with
  the open items stated once. Flows never match a bug. `gates.md` and `feature-status.md` templates record it.
- Protocol: any write to an external system needs the QA member's yes through the Master Agent at that moment
  (sections 7, 8a, 8b).

## 1.4.0 — 2026-11-02

- New skill `/qa-framework:qa-feature-pipeline`: runs one feature through the whole STLC with the
  agents above (requirement analysis → post-release), stops at every QA approval gate, and keeps
  `pipeline/<feature>/status.md` ("Waiting on QA" list) and `metrics.csv` (AI and QA minutes per
  stage). Modes: `start`, `status`, `build <apk|latest>` (smoke, new-feature cases, retest of
  fixed bugs, regression) and `report` (management report). It ships templates for the three
  files. The VPN check runs only when the project conventions name one.
- Automation selection gets the row status **Waiting on fix**: a case failed by a bug gets its
  flow only after `/qa-framework:qa-retest` passes on a fixed build and the QA member approves
  the verification (`qa-automation-engineer`, `qa-automate-flow`, `qa-retest`).

## 1.3.0 — 2026-10-28

- Test-case priority uses Execute.io's own names: Critical, High, Medium, Low. They replace
  P0, P1, P2, P3 one-to-one, so QA members and Execute.io users see the same words.
  `qa-test-designer` writes the new names. `qa-sync-manager` sends `critical`/`high`/
  `medium`/`low` and maps any older P0–P3 file the same way, never storing `P0`–`P3`.
  `qa-automation-engineer`, `qa-test-planner`, `qa-report-signoff` and `qa-post-release`
  use the new names. Defect severity (S1/S2, "P0 defects") and story priority are unchanged.
- New skill `/qa-framework:qa-user-story` and agent `qa-user-story-writer`: write a feature's
  user story from its FRS as a single-sheet xlsx in the "User Story & Estimation Template", in
  the BA's writing style, with mockup images in the Screen/MockUp column. The FRS is the only
  source; non-FRS rows only on request, marked "Not in FRS". The skill ships the blank template,
  the writing-style guide, an approved example story and Python scripts (FRS reader, sheet
  builder). They run in `~/.cache/qa-framework/user-story-venv`, created on first use (needs
  `python3`).

## 1.2.0 — 2026-10-28

- Test cases follow the story: `qa-test-designer` reads each story's Expectation, Conditions
  of Satisfaction (CoS) and Acceptance Criteria (AC) first, then orders cases story row by row
  and CoS by CoS (happy path first, then that CoS's negative/boundary/edge cases, Android and
  iOS twins together), each linked to the AC that gives its expected result. Each CoS gets a
  heading quoting the bullet and naming its AC; a CoS with nothing testable keeps its heading
  with `No cases — Specification gap RA-n`. The traceability table is in story order, and a
  workbook export opens with a `Story map` sheet; the import sheet keeps its 12 columns.
- `/qa-framework:qa-test-design` checks that order against the story before reporting.
- `qa-requirement-analyst` assigns `USn-CSm` / `USn-ACm` ids in story order when a story has
  none, and lists its inventory in story order.

## 1.1.0 — 2026-10-26

- New skill `/qa-framework:qa-file-bug` and agent `qa-defect-filer`: file a bug in Karmo. The
  agent drafts the ticket from the project's "Karmo bug filing" rules, the skill asks for
  Assignee, Sprint and Components with a pick-list, shows the final ticket, and files only after
  an explicit yes. See "Karmo bug filing" in the README for the section each project needs.
- `qa-triage` skill: hands Karmo filing over to `/qa-framework:qa-file-bug`; other trackers keep
  the previous flow.

## 1.0.0 — 2026-10-20

- First release: 14 agents and 14 skills, from requirement analysis to post-release.
