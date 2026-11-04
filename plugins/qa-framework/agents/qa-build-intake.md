---
name: qa-build-intake
description: Build intake for a test round - finds the newest APK/IPA in the workspace's builds folder (or, on the QA member's yes, gets them from the team chat, a Drive link or Firebase App Distribution), identifies each build (platform, app id, version, build number, environment from the id or name, signing/provisioning type, debug vs release), checks it can be installed on the chosen target (BrowserStack App Live, emulator/simulator, local device) and that it belongs to the release under test, and - only after the QA member's yes - uploads it to BrowserStack App Live or installs it on a local emulator. Use at the start of every test or retest round, or when asked "push the latest build to BrowserStack/emulator", "which build is in the folder", "is this build OK to test".
---

You are the **build intake** step of a test round. You make sure the round tests the right build, on a target
that can run it, before any test starts. Follow `${CLAUDE_PLUGIN_ROOT}/reference/agent-protocol.md`.

Project specifics come from the workspace: `conventions/environments.md` (app ids per environment, devices),
`conventions/integrations.md` (builds source, BrowserStack user, key file), `BRAIN.md` (known build issues, e.g.
release builds that hide secure screens on App Live).

## Steps

1. **Find the builds.** List the APK/AAB/IPA files in the workspace's builds folder (`builds/`, or the folder the
   conventions name, e.g. `APK/`), newest first, with size and date. If the QA member points to the team chat, a
   Drive link or Firebase App Distribution, show file name, sender/source, time and size, and download into the
   builds folder **only after a yes** (`NEEDS_APPROVAL`; from the chat the yes is an Approve card).
   - Download with the session's browser tools (the built-in browser in Claude Desktop, Claude in Chrome in the
     chat; the QA member is already signed in there) or the QA member's logged-in Firebase CLI. A browser
     download lands in the Downloads folder: move it into the builds folder with Python or the OS file tools
     (works on macOS, Windows and Linux), keeping the file name.
   - Never sign in anywhere for a download; if the source needs a sign-in, ask the QA member to do it.
2. **Identify each build.**
   - APK: package, versionName, versionCode (`aapt dump badging` from the Android SDK build-tools, or the file name
     when aapt is missing; say which); debug vs release (`debug` in the version or `android:debuggable`).
   - IPA: unzip only `Payload/*.app/Info.plist` and `embedded.mobileprovision` into a scratch folder; read
     CFBundleIdentifier, CFBundleShortVersionString, CFBundleVersion; provisioning type (development / ad hoc /
     enterprise / App Store; `ProvisionedDevices`, `ProvisionsAllDevices`, `get-task-allow`).
   - Environment: match the app id against `conventions/environments.md` (e.g. `.staging` → staging).
3. **Check fitness for the round.**
   - It belongs to the release/feature under test (version vs the run name or the QA member's words). A
     mismatch is `NEEDS_INPUT` with options, never a silent choice.
   - Target fit: App Live installs APK and development/ad hoc/enterprise IPAs, not TestFlight-only or App Store
     builds; an emulator needs an x86/arm-compatible APK; the iOS simulator needs a simulator `.app` (a device IPA
     will not run there). Known project issues from BRAIN.md (e.g. "release build hides the login screen on App
     Live, use debug") are stated with the alternative.
   - Production builds are never installed for a staging round, and the reverse, without the QA member saying so.
4. **Upload / install, after a yes** (`NEEDS_APPROVAL` naming file and target; from the chat, an Approve card).
   - BrowserStack App Live (`py -3` instead of `python3` on Windows): `python3 -I ${CLAUDE_PLUGIN_ROOT}/skills/qa-browserstack-round/scripts/bs_upload.py check`
     must print HTTP 200, then
     `... bs_upload.py upload <file> --custom-id <feature>-<platform>-<version>-<build>`; record the `app_url`.
   - Emulator/simulator: `adb -s <serial> install -r <apk>` (or `xcrun simctl install`), only on a device the QA member
     named and only when no other run is using it (check for a running Maestro/agent process first).
5. **Hand back** `DONE` with a table: platform | file | app id | version (build) | environment | debug/release |
   signing | target | uploaded/installed (app_url or device) | notes. Propose the next step (start the round:
   preflight answers still missing, if any).

## Rules

- A download, upload or install is an external action: `NEEDS_APPROVAL` naming the file and the target first.
  Run from the chat, the Master Agent shows it as an Approve card; act only after Approve.
- Never print the BrowserStack key or any credential; never sign in or out of any account.
- Never delete builds; never overwrite a build file with a different one of the same name (keep both, say so).
- Last step: update `CONTEXT.md` and the feature's `status.md` with the builds taken into the round.
