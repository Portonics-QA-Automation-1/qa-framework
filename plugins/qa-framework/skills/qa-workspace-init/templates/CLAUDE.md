# <Project name> – QA workspace

This workspace is for **<Project name> only** (<platforms; app ids>). Work for any other project
belongs in that project's own workspace, never here.

## How work is done here (qa-framework 2.x)

- AI agents execute; QA members validate. All agents follow the plugin's agent protocol
  (`reference/agent-protocol.md` in the qa-framework plugin): preflight questions before a test session,
  ask before marking Blocked or Failed, a hard QA verification gate after every round, approval before
  each stage's agent starts, a proposed next step after every task.
- Lifecycle and gates: `conventions/gates.md`. Test-case rules: `conventions/qa-guidelines.md`.
  Environments and accounts (variable names only): `conventions/environments.md`. Integrations:
  `conventions/integrations.md`.

## Project logic and status

- `BRAIN.md` holds the project logic (loaded below); `CONTEXT.md` the live status; `CONTEXT-archive.md`
  finished history. Read `CONTEXT.md` first at the start of a session.
- Every agent updates `CONTEXT.md` and the feature's `features/<feature>/status.md` when it finishes.
- Lasting facts go to `BRAIN.md`. This brain is for this project only and is never committed or pushed.

@BRAIN.md

## Rules that always apply

- No secrets in any file, flow, comment or chat (phone numbers, OTPs, passwords, keys, tokens).
- Execute.io structure (suites, folders, milestones, plans, runs) is created only with names the QA member
  gives. Production writes are confirmed each time.
- Agents never type credentials on a third-party site, never complete a payment, never decide go/no-go.
