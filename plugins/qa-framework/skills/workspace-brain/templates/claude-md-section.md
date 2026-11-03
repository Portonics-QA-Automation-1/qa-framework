## Project logic (BRAIN.md)

`BRAIN.md` holds the lasting project logic and is loaded below. Work from it, and keep it right.

@BRAIN.md

Working with BRAIN.md:
- Before a new task, find the BRAIN.md sections it touches and follow that logic.
- If the task conflicts with BRAIN.md (a rule, a decision, an environment or an ID map), stop and ask. Never
  change the logic quietly.
- BRAIN.md is the map, not a substitute for the files. Read the files the task touches before changing them.
- Reuse the existing helpers, agents, skills and conventions. Do not build a second way of doing the same
  thing.

## Session hand-off (three files)

| File | Holds | Update when |
|---|---|---|
| `CLAUDE.md` | Rules | A rule changes (rarely) |
| `BRAIN.md` | Lasting project logic | Logic, a rule or a decision changes: in the same step. Train it daily with `/workspace-brain learn` |
| `CONTEXT.md` | Live status | **As soon as a piece of work is finished**, not only at the end |

- At session start, CLAUDE.md and BRAIN.md are loaded.
  - Read CONTEXT.md ("In progress", "Waiting on the user", "Next steps").
  - Read the SessionStart hook output. When it warns, reconcile it before naming a next step.
- Keep CONTEXT.md under about 150 lines. Move finished history word for word to the top of
  `CONTEXT-archive.md`. Don't read the archive at session start; open it only when a task needs past details.
- One fact, one place. No secrets in any of these files.
