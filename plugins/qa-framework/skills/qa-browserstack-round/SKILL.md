---
name: qa-browserstack-round
description: Agentic manual test round on a new Android and/or iOS build - AI agents execute the feature's existing test cases (no scripted automation) on BrowserStack App Live real devices (single or parallel), or hand the round to qa-execute for the emulator / a local device, record every case as Passed / Failed / Blocked / Needs Review with evidence, write results to the named Execute.io run or the workspace, and stop at the QA verification gate. Also used for the retest round on a better build. Use when asked "push the latest build to BrowserStack and test <feature>", "run <feature> on App Live", "retest <feature> on the new build", or "BrowserStack round for <feature>".
argument-hint: "<feature> [run name] [build] [target: browserstack | emulator | device] [single | parallel] [env] [cases: all | failed | ids]"
---

# Agentic manual test round (BrowserStack App Live)

Argument: `$ARGUMENTS`. Follow `${CLAUDE_PLUGIN_ROOT}/reference/agent-protocol.md` (task and result contract,
preflight, ask-before-Blocked, verification gate). Project specifics come from the workspace: `BRAIN.md`,
`conventions/environments.md`, `conventions/integrations.md`, `conventions/gates.md`.

Scripts: `${CLAUDE_PLUGIN_ROOT}/skills/qa-browserstack-round/scripts/`. `bs_upload.py` runs with
`python3 -I`; for `results_sheet.py` get the interpreter with `PY=$(sh <scripts>/setup_venv.sh)` and run
`$PY -I <scripts>/results_sheet.py …`. The BrowserStack username and access key are read from
`~/.config/browserstack.env` (or `$BROWSERSTACK_ENV`); never print or read them into the conversation. From the
chat, call `mcp__qa_connector__browserstack_key` before the first `bs_upload.py` call: when the file is missing it
asks the QA member once with two input cards (username, then the access key) and saves them only on that computer
(Workspace Connector 0.9.1). `{"ready": false}` → stop the upload and report it. In Claude Desktop the QA member
fills in the file.

## Where the round runs: Claude Desktop or the chat

Check the session's tool list once, at the start:
- **From the chat** (Google Chat or the Execute.io web chat, through the Workspace Connector): the tool
  `mcp__qa_connector__request_input` is in the tool list. The browser is Claude in Chrome
  (`mcp__claude-in-chrome__*`; if deferred, load them in one ToolSearch call). Approvals arrive as
  Approve/Reject cards. The QA member works only in Google Chat: the connector has already opened Chrome and
  checked the connection; select the browser the prompt names (protocol section 4a; otherwise `choose_browser` →
  `select_browser`; lost → `open_chrome`, `open_chrome` restart, then a `browser_problem` card). A browser problem
  is a card with Retry, never the end of the round.
- **Claude Desktop** (the QA member at the computer): no `request_input` tool. The browser is the built-in
  browser (`mcp__Claude_Browser__*`).

Use whichever browser tools the session has; the steps below are the same for both. Name the browser family
and the tab id in every executor's task contract.

## Login check only

When the QA member asks only to try the login ("push the builds and log in", "login test"), run Phases 1 and 2
for the requested platforms (in parallel when both), stop on each device after the login, and report per
platform: build uploaded (app id), device, app opened, logged in as <account type> or the step that failed, with
one screenshot of the logged-in Home (never of a screen showing the number or OTP). No test cases, no results
sheet, no Execute.io writes.

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
7. **Accounts and data available**: which account types will be logged in this session, and whether
   Back Office data, a second number or a linked account will be needed. From the chat, say how logins work: from
   the values saved in Execute.io for that environment (staging, preprod or prod), else by an input card the member
   answers (number, then the OTP from their phone).

Then state the plan (devices, builds, case counts per platform, result destination) and wait for a yes.

## Phase 1 - Build intake

When the QA member names the dev team's build group and the build ("from Atom Store Build share group, AtomStore
90.17.1 (64)"), qa-build-intake finds and downloads it with `find_builds` / `download_build` (chat) into the
member's Downloads folder, and the round uses that file.

1. If the build is not in the builds folder yet, `qa-build-intake` gets it from the team chat, a Drive link or
   Firebase App Distribution after the QA member's yes (`NEEDS_APPROVAL`; from the chat, an Approve card).
2. Identify each build: APK from the file name; IPA from `Payload/*.app/Info.plist` (bundle id, version,
   build) and its provisioning type. A TestFlight-only IPA cannot be installed on App Live: say so and continue
   with the other platform. If Android release builds hide secure screens (black login), ask for a debug build
   (see the workspace BRAIN.md).
3. From the chat, `mcp__qa_connector__browserstack_key` first (see Scripts above). Then `bs_upload.py check` must
   print HTTP 200; otherwise report the exact problem.
4. After the QA member's yes (from the chat, an Approve card), upload: `bs_upload.py upload <file> --custom-id <feature>-<platform>-<version>-<build>`.
   Record the `app_url`.

## Phase 2 - Devices and login

- Use the browser signed in to a BrowserStack user with an App Live seat (`conventions/integrations.md`): the
  built-in browser in Claude Desktop, the QA member's Chrome (Claude in Chrome, the profile chosen in protocol
  section 4a) from the chat. Open https://app-live.browserstack.com/dashboard:
  - Signed in → continue.
  - Signed out, **from the chat**: protocol section 4a. Click **Sign in** only on a form Chrome filled from the
    profile's saved password (it shows as dots); never type, read, copy or store a password. Not filled, a
    non-code 2FA, a CAPTCHA or no App Live seat → the matching `browser_problem` card, then Retry. A verification
    code → `request_input` (secret), typed only into that field.
  - Signed out, **Claude Desktop**: ask the QA member to sign in.
- **Parallel needs one Claude session per platform.** Claude in Chrome binds one session to one tab group in one
  window, so two platforms driven from one session take turns, never run at the same time (tested 2026-11-04).
  Never drive two platforms in tabs of one session.
  - **From the chat** (`mcp__qa_connector__start_platform_workers` is in the tool list): this session is the
    coordinator. Do Phase 0, Phase 1 (build check and upload) and pick the devices here, then call
    `start_platform_workers` with one entry per platform: `{"platform": "Android", "contract": <the executor's
    full task contract, Phase 3, including "start the device, bring the app to its login screen and log in"
    and the login method>}`. Each worker is a separate Claude process running `qa-browserstack-executor`; it
    selects the same Chrome, opens its own window and drives only that; the workers that start together place
    their windows side by side once, before any device starts (`arrange_round_windows`, connector 0.17.0), so the
    member sees every platform at once. Then call `wait_platform_workers` (again
    while `still_running` is not empty). The live status in the chat shows one line per platform, and each
    worker's cards carry its platform ("Android – …"). Stop in the chat ends every worker. The computer runs at
    most its `parallel-platforms` setting at once (default 2); more platforms wait for a free slot. Don't drive a
    device yourself in this mode. The tool answers with an error (an older connector, or no browser checked) →
    run the platforms one after the other in this session and say so.
  - **Claude Desktop:** start one extra Claude session per extra platform with the executor's task contract (the
    session-starting tool, e.g. `start_session`; each opens its own Chrome window with `tabs_context_mcp`
    `createIfEmpty: true`) and drive the first platform yourself. No way to start a session → one platform after
    the other, and say so.
- Single platform, or one after the other: drive it in this session as before.
- Start each device, bring the app to its login screen (language, pop-ups).
- **Login, by where the round runs and the environment:**
  - Staging QA auto-login in the build (documented in the workspace): the agent uses it, anywhere.
  - **From the chat, any environment:** the agent logs in itself. It gets each value with
    `mcp__qa_connector__request_input`, one value per call, `secret: true`, e.g. label "MSISDN for prepaid
    account on Android", then "OTP sent to the prepaid number" (and "PIN …" if the app asks), each with
    `env_key` set to the project's Execute.io variable (`MSISDN_PREPAID` / `MSISDN_POSTPAID` / `MSISDN`, `OTP`,
    `PIN`). Execute.io answers from the value saved for the round's environment
    (staging, preprod or prod); when it is not saved there, or the brief says `Login values: from the
    member` (pass that line on to every executor), the QA member replies to the card in the chat (number first, then the OTP that arrives on their phone; an expired OTP is
    asked again, at most 3 times). It types the value only into the login field of the app under test on that
    App Live device.
  - **Claude Desktop** (no request_input): the QA member logs in on each device (`NEEDS_HUMAN`).
  - **Production from Claude Desktop:** the QA member logs in. An OTP that confirms a payment or transfer is
    never typed by an agent, anywhere.
- **Values from request_input:** never written into any file, result sheet, evidence, summary, log or chat
  message; never repeated back; never typed anywhere else (not BrowserStack's sign-in, not another site). Results
  say "logged in as <account type>". A `rejected` or `timeout` answer: do not ask again in a loop; treat that
  login as `NEEDS_HUMAN`.
- **Each platform starts the moment it is logged in**: hand that device to its executor at once; never wait for
  the other platform.

## Phase 3 - Execution

- One `qa-browserstack-executor` per platform (parallel: one Claude session per platform, Phase 2) with a task
  contract: platform, case sheet and TC IDs
  in order (grouped by account type), Execute.io IDs, round folder, build, environment, device, app, browser
  family and tab id, login method (QA member / auto-login / request_input) and logged-in account type,
  evidence yes/no, accounts and data the QA member said are available.
- Executors return `NEEDS_INPUT` instead of marking a case Blocked when an account, Back Office data or other
  data is missing (protocol section 5). Ask the QA member, with the executor's options, and resume it with the
  answer. Record Blocked only after the QA member confirms the data is not available, quoting that.
- From the chat, executors get a login, account switch or login OTP value themselves with request_input.
  `NEEDS_HUMAN` steps (a final payment confirm, a payment/transfer OTP, a value the QA member
  rejected or did not answer, and any login in Claude Desktop): ask for just that step on that device; the other
  platform keeps running.

## Phase 4 - Results

- Round folder: the feature's `rounds/<round>/` (or `TestCase/evidence/<feature>/<round>/` in older layouts).
- After each executor reply, check the platform's results file covers every case (latest line per TC wins).
- **Execute.io** (if chosen): send results with `sync_results` (status passed / failed / blocked; Needs Review →
  `retest`; `version` = build per platform; comment starts `AI-executed (awaiting QA verification)` with device,
  environment, account type, expected vs actual, repro for Failed, reason for Blocked). Every result must come
  back with a `result_id`; report any that did not. Production writes need the QA member's yes for this run.
- `results_sheet.py merge` writes `results.xlsx` + `SUMMARY.md`, once every platform has ended (parallel from the
  chat: after `wait_platform_workers` returns `finished`; each worker's `RESULT_FILE` is its per-platform file).
  A worker that failed or was stopped: its cases without a result are "Not run" with the worker's reason.

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
- No secrets anywhere. A login value is typed only from request_input, in the chat, into the app's login field
  on the App Live device. Never type an OTP that confirms a payment or transfer; never see or type a password
  (from the chat, only click Sign in on a BrowserStack form Chrome filled, protocol section 4a); never sign in
  to any other site; never complete a payment; never change BrowserStack account settings or sign anyone out
  without the QA member asking.
- Never create Execute.io structure or sync test cases from this skill; never file bugs.
