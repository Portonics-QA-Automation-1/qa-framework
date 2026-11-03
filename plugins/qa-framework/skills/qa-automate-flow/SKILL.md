---
name: qa-automate-flow
description: Write Maestro flows for approved test cases in the workspace's maestro/ framework, optionally run them on an emulator/device, and report what is validated. Usage - /qa-automate-flow <feature slug | test case id(s) | short description>
---

1. **Resolve the test cases.** Find the feature's test-case file (`TestCase/<feature>-test-cases.md`
   or `specs/<feature>/qa/test-cases.md`). If the argument names TC ids, automate only those.
   If no test-case file exists, ask the QA member to paste the steps and expected results.
   **When to start.** If the QA member asked for the flows (this command), start: a QA member's
   instruction is always followed. If the feature is not "stable" (agent protocol section 8b: all
   verified failures fixed and retested, no open requirement question changing behaviour, design
   final, last round passed and verified, known issues deferred), say once what is still open and
   that these flows may need rework after the fixes, then continue. When the agent itself proposes
   automation, it does so only for a stable feature: "<feature> is stable. Shall I write the Maestro
   flows?"
   **Selection first.** Automation is a subset, not every case.
   Then look for `maestro/automation-selection/<feature-slug>-automation-selection.xlsx`. If it
   is missing, have the `qa-framework:qa-automation-engineer` build it using its "Which cases to automate"
   rules (core positive per story + one negative per limit/validation, ~25–40% of the unique scenarios;
   no duplicate account-type/platform variants, visual, BackOffice, timing cases; disputed
   failures and blocked cases "On hold"; cases failed by a bug "Waiting on fix" until the retest
   passes). The agent decides the selection and each case's suite tag (smoke / sanity /
   regression / one-time) and shows it with reasons; the QA member may change it, and their change
   wins. Automate only rows in the `Selected` sheet with Status "To write" (or the TC ids named, if
   they are in that sheet).
   **Validation point per case.** Before flows are final, send the QA member one table (TC | expected
   result | validation point | selector evidence) and get each row confirmed or corrected. No flow for
   a case without a confirmed validation point; every flow ends with at least one labelled assertion.
2. **Check the framework.** The workspace must have `maestro/` (with `README.md`, `scripts/run.sh`,
   `common/login/`). If it doesn't, stop and ask the QA member to copy the framework in.
3. **Check the device.** Run `adb devices`. If a device/emulator is connected, ask the QA member
   whether to run the flows on it after writing them (and which environment: staging, preprod or
   prod). If none is connected, the flows stay "not run yet".
4. **Delegate** to the `qa-framework:qa-automation-engineer` subagent: "Automate <cases> for <feature> following
   your instructions. Run them on <device> against <env>: <yes/no>."
   **Pop-ups:** where the workspace has a shared pop-up guard (see its `maestro/README.md` /
   project conventions), the flow clears pop-ups only through it (with its anchor) after
   launch/login and after every step that returns to Home; it has no `point:` taps except where
   the conventions allow them (e.g. drag-to-reorder), no banner/image taps and no generic
   OK/Yes/Allow taps. A pop-up found during the run is added to the guard, not to the feature flow.
5. **Check the result.** Every automated case has exactly one flow file with the header, a suite
   tag and `ensure_logged_in.yaml` as its first step; `maestro check-syntax` is OK for each; no
   test-case, spec or plan file changed; no Execute.io tool was called.
6. **Report** to the QA member: files, per-case suite tag and status, deviations and UNVERIFIED
   selectors, manual-only cases, missing env variables/fixtures. Then ask:
   "Review these against the real app. Which flows do you approve for syncing to Execute.io?"

7. **Run, then ask to sync.** Run the written flows on the device/emulator the QA member named.
   When they pass, return `NEEDS_APPROVAL` (through the Master Agent when there is one): "sync these
   N validated flows to Execute.io <environment> <suite> for future automation runs".

Never sync or mark a flow approved without the QA member's explicit yes. Syncing is a separate
step (`/qa-sync` syncs the named, approved files to the chosen Execute.io environment).
