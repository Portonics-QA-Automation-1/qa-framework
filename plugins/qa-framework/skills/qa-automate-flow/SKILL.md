---
name: qa-automate-flow
description: Write Maestro flows for approved test cases in the workspace's maestro/ framework, optionally run them on an emulator/device, and report what is validated. Usage - /qa-automate-flow <feature slug | test case id(s) | short description>
---

1. **Resolve the test cases.** Find the feature's test-case file (`TestCase/<feature>-test-cases.md`
   or `specs/<feature>/qa/test-cases.md`). If the argument names TC ids, automate only those.
   If no test-case file exists, ask the QA member to paste the steps and expected results.
   **Selection first.** Automation is a subset, not every case. Check that the feature's manual
   round is finished (results recorded); if not, stop and say flows come after the manual run.
   Then look for `maestro/automation-selection/<feature-slug>-automation-selection.xlsx`. If it
   is missing, have the `qa-framework:qa-automation-engineer` build it using its "Which cases to automate"
   rules (core positive per story + one negative per limit/validation, ~25–40% of the unique scenarios;
   no duplicate account-type/platform variants, visual, BackOffice, timing cases; disputed
   failures and blocked cases "On hold"). Show it and wait for the QA member's yes. Automate
   only rows in the `Selected` sheet with Status "To write" (or the TC ids named, if they are
   in that sheet).
2. **Check the framework.** The workspace must have `maestro/` (with `README.md`, `scripts/run.sh`,
   `common/login/`). If it doesn't, stop and ask the QA member to copy the framework in.
3. **Check the device.** Run `adb devices`. If a device/emulator is connected, ask the QA member
   whether to run the flows on it after writing them (and which environment: staging, preprod or
   prod). If none is connected, the flows stay "not run yet".
4. **Delegate** to the `qa-framework:qa-automation-engineer` subagent: "Automate <cases> for <feature> following
   your instructions. Run them on <device> against <env>: <yes/no>."
5. **Check the result.** Every automated case has exactly one flow file with the header, a suite
   tag and `ensure_logged_in.yaml` as its first step; `maestro check-syntax` is OK for each; no
   test-case, spec or plan file changed; no Execute.io tool was called.
6. **Report** to the QA member: files, per-case suite tag and status, deviations and UNVERIFIED
   selectors, manual-only cases, missing env variables/fixtures. Then ask:
   "Review these against the real app. Which flows do you approve for syncing to Execute.io?"

Never sync or mark a flow approved without the QA member's explicit yes. Syncing is a separate
step (ask the main session to sync named, approved files to the chosen Execute.io environment).
