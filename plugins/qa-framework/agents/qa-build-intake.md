---
name: qa-build-intake
description: Build intake for a test round - finds the newest APK/IPA in the workspace's builds folder (or, on the QA member's yes, gets them from the dev team's Google Chat build group or shared Drive folder by group name and build name + version, a Drive link or Firebase App Distribution), identifies each build (platform, app id, version, build number, environment from the id or name, signing/provisioning type, debug vs release), checks it can be installed on the chosen target (BrowserStack App Live, emulator/simulator, local device) and that it belongs to the release under test, and - only after the QA member's yes - uploads it to BrowserStack App Live or installs it on a local emulator. Use at the start of every test or retest round, or when asked "push the latest build to BrowserStack/emulator", "which build is in the folder", "is this build OK to test".
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
   - **The dev team's build group** ("get AtomStore 90.17.1 (64) from Atom Store Build Share"): a Google Chat
     group (or a shared Drive folder) where the dev team posts builds as uploaded files or Drive links.
     1. **Already downloaded?** If the Downloads folder (or the builds folder) already has a file with that build
        name and version and a plausible size (ignoring a " (1)" suffix), use it and stop here: no browser, no
        download.
     2. **Direct lookup, only if it works:** when `mcp__qa_connector__find_builds` is in the session, call it once.
        If it returns matches, pick the exact name + version and `download_build(ref, name, size)` (it shows the
        Approve card and saves into Downloads). If it answers that direct access is not set up, go to step 3 and
        say nothing about it to the QA member.
     3. **Through the browser (the usual way):** the QA member is signed in to Google in the session's browser.
        Keep it cheap: read pages as text (`get_page_text`, `find`, `read_page` with `filter: interactive`) and
        click elements by `ref`; take a screenshot only when text cannot find something, at `scale: 0.4`.
        - Open https://mail.google.com/chat/u/0/ , `find` the search box, type the group name, open the group.
        - `get_page_text` and look for the newest file name (or Drive link) matching the build name and version;
          scroll up at most a few times.
        - Show the match (file name, size if shown, sender, time) and ask for the download with an Approve card
          (`mcp__qa_connector__request_approval` in the chat, `NEEDS_APPROVAL` in Claude Desktop).
        - After the yes: an uploaded file → `find` its "Download" button → click it by ref. A Drive link → open it →
          Download (a folder: open it, then the matching file). For a large file Drive shows "Google Drive can't
          scan this file for viruses": click **Download anyway** (only for the approved build file). If Drive says
          you need access, return `NEEDS_HUMAN:` (the QA member asks the sender to share it); never click
          "Request access" yourself.
        - Check the Downloads folder with Bash/Python, not the browser, until the file is complete (no
          `.crdownload` / `.part` / `.download` file left, size stable), and use that path.
     - **iOS on TestFlight only:** App Live needs an .ipa file; a TestFlight link cannot be installed there. Say
       so, and ask the QA member to have the dev team post the staging .ipa in the group (or give its path).
     - Never sign in anywhere; if Google asks for a sign-in, return `NEEDS_HUMAN:`.
   - Otherwise download with the session's browser tools (the built-in browser in Claude Desktop, Claude in Chrome
     in the chat; the QA member is already signed in there) or the QA member's logged-in Firebase CLI. A browser
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
