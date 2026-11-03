---
name: qa-browserstack-round
description: Agentic manual test round on a new Android and/or iOS build - AI agents execute the feature's existing test cases (no scripted automation) on BrowserStack App Live real devices (single or parallel), or hand the round to qa-execute for the emulator / a local device, record every case as Passed / Failed / Blocked / Needs Review with evidence, write results to the named Execute.io run or the workspace, and stop at the QA verification gate. Also used for the retest round on a better build. Use when asked "push the latest build to BrowserStack and test <feature>", "run <feature> on App Live", "retest <feature> on the new build", or "BrowserStack round for <feature>".
argument-hint: <feature> [run name] [build] [target: browserstack | emulator | device] [single | parallel] [env] [cases: all | failed | ids]
---

# Agentic manual test round (BrowserStack App Live)

Argument: `$ARGUMENTS`. Follow `${CLAUDE_PLUGIN_ROOT}/reference/agent-protocol.md` (task and result contract,
preflight, ask-before-Blocked, verification gate). Project specifics come from the workspace: `BRAIN.md`,
`conventions/environments.md`, `conventions/integrations.md`, `conventions/gates.md`.

Scripts: `${CLAUDE_PLUGIN_ROOT}/skills/qa-browserstack-round/scripts/`. `bs_upload.py` runs with
`python3 -I`; for `results_sheet.py` get the interpreter with `PY=$(sh <scripts>/setup_venv.sh)` and run
`$PY -I <scripts>/results_sheet.py …`. The BrowserStack username and access key are read from
`~/.config/browserstack.env` (or `$BROWSERSTACK_ENV`), filled in by the QA member; never print them.

## Phase 0 - Preflight (protocol section 4)

Ask in one message only what the request and the workspace do not already answer:
1. **Build**: list the newest APK/IPA in the workspace's builds folder (`builds/`, or the folder the
   conventions name) with version and build number; confirm which to use.
2. **Environment**: staging, preprod or production.
3. **Target**: BrowserStack App Live, the emulator/simulator, or the QA member's own device.
   Emulator/simulator or own device → hand the round to `qa-execute` (local devices; on staging the agent
   logs in itself through the project's login automation) with the same answers, and stop here.
4. **Single or parallel** (BrowserStack): Android and iOS at the same time, or one after the other.
5. **Cases**: all of the feature, the last round's Failed + Needs Review first, or named cases.
6. **Results**: the named Execute.io run (name from the QA member; agents never create runs), or the
   workspace only.
7. **Accounts and data available**: which account types the QA member will log in this session, and whether
   Back Office data, a second number or a linked account will be needed.

Then state the plan (devices, builds, case counts per platform, result destination) and wait for a yes.

## Phase 1 - Build intake

1. Identify each build: APK from the file name; IPA from `Payload/*.app/Info.plist` (bundle id, version,
   build) and its provisioning type. A TestFlight-only IPA cannot be installed on App Live: say so and continue
   with the other platform. If Android release builds hide secure screens (black login), ask for a debug build
   (see the workspace BRAIN.md).
2. `bs_upload.py check` must print HTTP 200; otherwise report the exact problem.
3. After the QA member's yes, upload: `bs_upload.py upload <file> --custom-id <feature>-<platform>-<version>-<build>`.
   Record the `app_url`.

## Phase 2 - Devices and login

- Use the browser signed in to a BrowserStack user with an App Live seat (`conventions/integrations.md`).
  Before starting a device in a second tab, make sure the page fills the pane (a tab drawn smaller than the
  pane sends taps to the wrong place): reset the tab's size first.
- Start each device, bring the app to its login screen (language, pop-ups).
- **The QA member logs in on each device.** Agents never type a phone number, OTP, PIN or password on
  BrowserStack, whatever the source. Exception only when the build has a staging QA auto-login (documented in
  the workspace): then the agent uses it.
- **Each platform starts the moment it is logged in**: hand that device to its executor at once; never wait for
  the other platform.

## Phase 3 - Execution

- One `qa-browserstack-executor` per platform (parallel) with a task contract: platform, case sheet and TC IDs
  in order (grouped by account type), Execute.io IDs, round folder, build, environment, device, app, browser tab
  id, login method and logged-in account type, evidence yes/no, accounts and data the QA member said are
  available.
- Executors return `NEEDS_INPUT` instead of marking a case Blocked when an account, Back Office data or other
  data is missing (protocol section 5). Ask the QA member, with the executor's options, and resume it with the
  answer. Record Blocked only after the QA member confirms the data is not available, quoting that.
- `NEEDS_HUMAN` steps (login, account switch, OTP, final payment confirm): ask for just that step on that
  device; the other platform keeps running.

## Phase 4 - Results

- Round folder: the feature's `rounds/<round>/` (or `TestCase/evidence/<feature>/<round>/` in older layouts).
- After each executor reply, check the platform's results file covers every case (latest line per TC wins).
- **Execute.io** (if chosen): send results with `sync_results` (status passed / failed / blocked; Needs Review →
  `retest`; `version` = build per platform; comment starts `AI-executed (awaiting QA verification)` with device,
  environment, account type, expected vs actual, repro for Failed, reason for Blocked). Every result must come
  back with a `result_id`; report any that did not. Production writes need the QA member's yes for this run.
- `results_sheet.py merge` writes `results.xlsx` + `SUMMARY.md`.

## Phase 5 - Review and verification gate

1. Second pass before reporting: the same case on Android and iOS judged the same way (align or explain);
   every Failed has step, expected, actual, repro; every Blocked has a QA-confirmed reason; no secrets.
2. Report per platform and per account type: totals for Passed / Failed / Blocked / Needs Review / Not run,
   the Failed and Needs Review list, possible defects, limitations.
3. **Stop at the verification gate (protocol section 6):** the round is "awaiting QA verification". Bug filing,
   retest or automation do not start until the QA member has verified and the decisions are recorded in the
   feature's `status.md`. Propose the next step (verify, then `qa-file-bug` for valid failures).
4. Update `CONTEXT.md` and the feature's `status.md`; close the App Live sessions.

## Rules

- Original case files are never changed; improvement ideas go to `case-improvements-<platform>.md`.
- No secrets anywhere; never type credentials on BrowserStack; never complete a payment; never change
  BrowserStack account settings or sign anyone out without the QA member asking.
- Never create Execute.io structure or sync test cases from this skill; never file bugs.
