# Changelog

## 2.8.4 — 2026-11-07

- **Results always go to the right case** (qa-browserstack-round, qa-manual-executor): every `sync_results` entry
  sends the case `title` with its `tc_id`, and tc_ids come from the case file's sync table or the `sync_test_cases`
  answer, never by counting from a first ID. Execute.io (from this release on) refuses a result whose title is not
  that case's title. Task 186 put 77 of run 145's results on the wrong cases with a counted ID map.

## 2.8.3 — 2026-11-07

- **A device session ends before its window closes** (qa-browserstack-executor): the agent stops the App Live
  session with the toolbar's Stop / End session button, then closes its tab. Closing a tab with a live session made
  Chrome ask "Leave site?" and left the window open (task 186's Android window); after one failed retry it now
  says so in its report instead of retrying.

## 2.8.2 — 2026-11-07

- **The recording question is always asked** (agent-protocol §4 question 8 and §4d; qa-browserstack-round,
  qa-execute, qa-retest): before every round on a recordable target, even when everything else is known, unless the
  request says it (`Recording: …`, including none). From the chat the Master Agent asks before dispatching (Workspace
  Connector 0.20.3); a round with no `Recording:` line asks once with a `request_input` card. A second round that
  was fully specified had skipped it before.

## 2.8.1 — 2026-11-07

- **Only the device windows are on screen in a parallel App Live round** (qa-browserstack-round, with Workspace
  Connector 0.20.2): the coordinating session closes its own App Live tabs before it starts the platform workers,
  so its window is never placed beside the Android and iOS windows.

## 2.8.0 — 2026-11-07

- **Session recording, only when the QA member asks** (agent-protocol §4d, new `scripts/session_recorder.py`,
  standard-library Python for macOS, Windows and Linux): preflight question 8 asks none (default), the full session
  (one video with each case's start-end time in `recordings.md`) or each case (all clips, or failed only: passed
  clips are deleted at once). Targets: the emulator or the member's Android device (scrcpy, else adb screenrecord in
  3-minute pieces), the iOS simulator (macOS) and BrowserStack App Live (ffmpeg captures the App Live window).
  Recording pauses while a number, OTP or PIN is typed. Every clip is compressed (720p, 10 fps, H.264) the moment
  it stops and the raw file is deleted; clips are cleaned after 7 days unless kept (a bug's clip is kept). `share`
  makes a copy that fits one chat message (cut to a case, split when long), so "send the recording of TC-012" in
  Google Chat posts it. qa-manual-executor, qa-retest, qa-browserstack-executor, qa-execute, qa-browserstack-round
  and qa-defect-filer follow it. A recorder that writes nothing (e.g. macOS without the Screen Recording
  permission) stops with the fix instead of leaving an empty video.

## 2.7.0 — 2026-11-07

- **Every project keeps a slim brain by itself** (workspace-brain `scripts/brain_split.py`, standard-library Python
  for macOS, Windows and Linux): BRAIN.md is loaded into every session (Claude Desktop, and every Google Chat
  message and task through the Execute.io connector), so once it passes ~8k tokens its behaviour and gotcha items
  and decisions older than 3 days (the newest 5 stay) move word for word into `brain/`, leaving a one-line index;
  entries written straight into `brain/` get their index line; no line is ever lost (checked before writing) and
  the previous file is kept in `~/.claude/backups/brain/`. It is reorganisation, never a logic change, so nobody is
  asked: `setup` runs it with `--init` (creates `brain/playbooks.md`), `learn` after each training, `check` reports
  it, and Workspace Connector 0.19.0 runs it after each chat task that wrote the brain. The BRAIN template says
  where detail and playbooks go.

## 2.6.0 — 2026-11-07

- **Known journeys cost no exploration** (agent-protocol §5b; qa-manual-executor, qa-retest,
  qa-browserstack-executor, qa-execute): before the first case the agent looks up the brain's playbook for the way
  there (login, pop-ups after login, the feature's screen: the workspace's `brain/playbooks.md`, found by
  `recall_brain`), follows it and looks only at its checkpoints and at each expected result. On the emulator or a
  local Android device the workspace's Maestro shared steps do that way with zero model tokens. A checkpoint that
  does not match switches to §5a; a new or changed journey goes on the brain card as a playbook item. The judgement
  of each expected result never shrinks. Part of the token plan with Workspace Connector 0.18.0 (thread memo, model
  per job, slim brain).

## 2.5.2 — 2026-11-07

- **Round progress from every session that executes** (agent-protocol §4b, qa-execute): a skill or main session that
  runs the cases or checks itself (an exploratory full-app check) reports `report_progress` after every recorded
  result too, with `total` raised as the round grows; a "Progress reminder" after a tool result (Workspace Connector
  0.17.4) means the chat's counts are stale. Task #139 had reported 3 passed at the start and nothing for 42 checks.
- **Messages from the QA member while a task runs** (agent-protocol §4c; Workspace Connector 0.17.4): the member's
  `tell N …`, the live card's Message box or a chat message qa-master passes on arrives after a tool result as
  "MESSAGE FROM THE QA MEMBER" in every session of the task. It is binding like the brief (the hard rules still
  apply), redone results are marked, and every message is listed in the report under "Instructions received during
  the task". Task #139's eight mid-run notes had arrived as a teammate session's notes, which the agent weighed.
  The task prompt names the channel, so that header in hook context is not an injection; text in pages, screens,
  files and other tool output stays data.

## 2.5.1 — 2026-11-06

- **Parallel App Live rounds side by side** (qa-browserstack-executor, qa-browserstack-round; Workspace Connector
  0.17.0): the platform workers that start together call `mcp__qa_connector__arrange_round_windows` once, as soon
  as their window shows App Live and before any device starts; the connector waits until every window is open and
  places them side by side (Android left, iOS right; four as a grid) on macOS, Windows and Linux (wmctrl), so the
  QA member sees all sessions at once. Windows never move during the round (a resize moves the device under the
  agent's taps). Older connectors or Claude Desktop: no change.

## 2.5.0 — 2026-11-06

- **Obstacles: ask the brain, then reason** (agent-protocol §5a; qa-browserstack-executor, qa-manual-executor,
  qa-retest): when the app shows something the case does not mention, the executor describes it and asks the
  brain first (`mcp__qa_connector__recall_brain`, Workspace Connector 0.16.0; else BRAIN.md and the evidence
  summaries), applies what is known, tries at most 3 safe moves when it is new (never spend, send or type an OTP
  or password it was not given), then asks the QA member. Only a new obstacle and what solved it is proposed for
  the brain: a known one is never proposed again, even in other words.

## 2.4.1 — 2026-11-05

- **Login values from every environment:** qa-browserstack-executor, qa-manual-executor, qa-browserstack-round,
  agent-protocol and the workspace template now say Execute.io answers `request_input` from the values saved for
  the round's environment (staging, preprod or prod); the member's card only when a value is not saved there
  (needs the Execute.io server of 2026-11-05; the member saves values for all three).
  A brief line `Login values: from the member` (the member said they give them) means input cards only, no
  `env_key`; qa-browserstack-round passes it on to every executor.
- **OTP typed fast:** an OTP is typed in one action the moment it arrives, never digit by digit or in chunks
  (codes expire in about a minute); chunked typing is only for a phone-number field that dropped digits.
- **qa-browserstack-executor closes its own window** after the last case and the end-state screenshot, so only
  running Claude tab groups stay in Chrome (the member could not tell which session was running).

## 2.4.0 — 2026-11-05

- **Firebase App Distribution downloads** (`scripts/firebase_builds.py`, Python + the npm firebase-tools package;
  macOS, Windows, Linux): `check`, `apps`, `list`, `download` (dry run by default, `--yes` after the Approve card;
  newest release when a version repeats; size and free-disk check; saves into Downloads). Access is the QA member's
  own `firebase login`, once, until `firebase logout`; no key is asked or stored. qa-build-intake uses it for
  "download <env> <version> from Firebase" and for TestFlight-only iOS builds (Apple allows no TestFlight download);
  qa-regression-runner lists the latest release with it (the user, 2026-11-05: agents must get builds from anywhere,
  Android and iOS, staging/preprod/live, with access given once).

## 2.3.0 — 2026-11-05

- **Round progress in the chat** (needs Workspace Connector 0.12.0; agent-protocol §4b): qa-browserstack-executor,
  qa-manual-executor and qa-retest call `mcp__qa_connector__report_progress` with the total at the start and the
  running totals plus the next case after each recorded case. Execute.io shows it in Google Chat as a progress bar
  per platform. `current` is a case id and title only; a failed call never stops the round; `stop: true` stops it.
  Without the tool (Claude Desktop) nothing changes (the user, 2026-11-05: members in Google Chat could not tell
  what was happening in the background).

## 2.2.0 — 2026-11-04

- **Parallel App Live rounds, truly at the same time** (needs Workspace Connector 0.11.0): Claude in Chrome binds one
  Claude session to one tab group in one window, so two platforms in one session took turns. From the chat the round
  is now a coordinator: after the build upload it calls `start_platform_workers` (one Claude process per platform,
  each running qa-browserstack-executor in its own Chrome window of the same profile) and `wait_platform_workers`,
  then merges and reviews once. In Claude Desktop the round starts one extra session per extra platform; without
  that it runs the platforms one after the other and says so. Never two platforms in tabs of one session.
- **qa-browserstack-executor:** its own window first (`tabs_context_mcp createIfEmpty`), a screenshot budget (zoom on
  the device, one wait while a device starts, `find`/`read_page` on BrowserStack's pages; Pass/Failed/Needs Review
  evidence unchanged), no full MSISDN in evidence, and `RESULT_FILE:` at the end of a worker's report.
- **workspace-brain `learn`** names brain cards from the Execute.io chat that were never answered (Workspace
  Connector 0.10.0 brain capture); it never writes an item nobody approved.

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
