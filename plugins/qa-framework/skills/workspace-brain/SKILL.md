---
name: workspace-brain
description: Set up, train and check a workspace's project memory - BRAIN.md (lasting project logic), CONTEXT.md (live status), CONTEXT-archive.md (finished history) and a SessionStart check. Use when a workspace or repo has no BRAIN.md yet ("set up the brain here"), at the end of a working day or after a feature/deploy ("train the brain", "update the brain"), or when asked whether the brain is up to date.
argument-hint: setup | learn | check
---

# Workspace brain

Every project workspace (for example one per client app, plus a product repo such as Execute.io) keeps the same
three files, so a new session knows the project logic and where the work stopped, and that knowledge grows
day by day instead of being lost.

| File | Holds | Changes |
|---|---|---|
| `CLAUDE.md` (or `AGENTS.md`) | Rules for working in this workspace, plus the hand-off section from `templates/claude-md-section.md` | Rarely |
| `BRAIN.md` | **Lasting project logic, the core**: purpose, system map, domain rules, key flows, environments and IDs, conventions, open questions, recent decisions, and a one-line index of `brain/` | Whenever logic is learned or changes; trained at least daily |
| `brain/*.md` | **The detail**, word for word: app behaviour, gotchas, older decisions, playbooks of known journeys. Fetched with `recall_brain` (chat) or Read, never loaded into every session | With BRAIN.md |
| `CONTEXT.md` | **Live status**: in progress, waiting on the user, next steps, last 7 days | After every finished piece of work. Under about 150 lines |
| `CONTEXT-archive.md` | Finished history, word for word, newest on top | When CONTEXT.md is pruned |

**Why a core:** BRAIN.md is loaded into every session of the workspace - every Claude Desktop chat and every Google
Chat message and task through the Execute.io connector - so every line in it is paid again and again from the
team's shared plan. `scripts/brain_split.py` keeps it a core the same way in every project: when BRAIN.md passes
~8k tokens, or once `brain/` has detail files, it moves behaviour and gotcha items and decisions older than 3 days (the newest
5 always stay) word for word into `brain/`, leaving a one-line index; it checks no line is lost and keeps the old
file in `~/.claude/backups/brain/`. It is reorganisation, not a logic change: run it without asking. The Execute.io
connector runs it after every finished task too.

Rules for every mode:
- **One fact, one place.** Status never goes in BRAIN.md, and lasting logic never stays only in CONTEXT.md.
- **No secrets** in any of these files: no phone numbers, OTPs, passwords, API keys or tokens, and no URLs or
  connection strings that contain them. Use variable names instead.
- Every BRAIN.md statement is backed by code, docs or observed behaviour. Mark a guess "(inferred)".
- Never delete knowledge silently. Correct a wrong fact in place and note the change in the decisions log if
  it changes a rule. Archived history stays word for word.
- Respect the workspace's own boundaries in its CLAUDE.md, for example "work for project B never goes into project A's
  workspace".
- **The brain is LOCAL ONLY: it is never committed or pushed** to git, GitHub or Bitbucket (team rule). Don't ask about committing it. In a git repo:
  - `BRAIN.md`, `CONTEXT.md`, `CONTEXT-archive.md`, `CLAUDE.local.md`, `.claude/settings.local.json`,
    `.claude/hooks/session-state.sh` and `.claude/brain.conf` go into `.git/info/exclude`. That file is local
    and never shared. Skip anything `.gitignore` already covers.
  - **Never edit a tracked file for the brain.** That includes `CLAUDE.md`, `AGENTS.md` and a tracked
    `.claude/settings.json`.
    - The hand-off section and `@BRAIN.md` go in `CLAUDE.local.md`, which Claude Code loads automatically.
    - The hook goes in `.claude/settings.local.json`.
  - If the repo already tracks a `CONTEXT.md`, leave it alone and keep the live status in `CONTEXT.local.md`
    (excluded). Tell the user that the tracked one is no longer the brain.
  - Finish with `git status --short`. It must show no brain file.
- **Each brain has its own scope; never mix brains.**
  - A **product development** repo (for example Execute.io/TestForge) keeps the product's code, architecture,
    data model, environments, deploy, backups and dev decisions.
  - A **project workspace** (one per client project) keeps the project work: features, test cases,
    the app's behaviour, the QA agents and skills used there, and the project's IDs and conventions.
    - When a project uses a product such as Execute.io, its brain keeps only *how the project uses it*:
      project IDs, suites, MCP server names, run rules.
    - For the product's internals (code, servers, deploy), it points to that product's brain.
  - Status follows the same split: product development work goes into the product repo's CONTEXT, and project
    work goes into the workspace's CONTEXT.

Mode: `$ARGUMENTS` (default `check`).

## setup – a workspace without BRAIN.md

1. **Read before writing:**
   - CLAUDE.md/AGENTS.md, README, the docs and any existing CONTEXT/notes files;
   - the folder layout, manifests, config (variable *names* only) and the main code entry points;
   - for a code repo, also the models, routes, auth, migrations, tests, CI and deploy scripts;
   - `git log` (last ~50 commits) and `git status`.
2. **Write `BRAIN.md`** from `templates/BRAIN.md`.
   - Fill every section that applies, and delete the ones that don't.
   - Aim for 150–300 lines. Point to detailed docs instead of copying them.
   Then run `python3 <this skill>/scripts/brain_split.py <workspace> --init` (Windows: `py -3`): it creates
   `brain/playbooks.md` and, for a long BRAIN.md, moves the detail into `brain/`.
3. **Write `CONTEXT.md`** from `templates/CONTEXT.md` with the current state.
   - If a long CONTEXT/status file already exists, keep its current part.
   - Move its finished history word for word to `CONTEXT-archive.md` (`templates/CONTEXT-archive.md`).
   - Check that no line was lost (compare the old file with the new files line by line).
4. **Install the check:**
   - Copy `scripts/session-state.sh` to `.claude/hooks/session-state.sh` and make it executable.
   - Create `.claude/brain.conf` (see the comments in the script) listing the related repos and the logic
     paths.
   - Add the SessionStart hook, merging with what is already there:
     `"$CLAUDE_PROJECT_DIR"/.claude/hooks/session-state.sh 2>/dev/null || true`.
     - In a git repo, put it in `.claude/settings.local.json`.
     - In a workspace that is not a git repo, put it in `.claude/settings.json`.
   - Run the script once and show its output.
5. **Add the hand-off section** from `templates/claude-md-section.md`, with `@BRAIN.md`, so BRAIN.md loads
   automatically:
   - In a git repo, put it in `CLAUDE.local.md` (excluded). Never touch the tracked CLAUDE.md or AGENTS.md.
   - In a local, non-git workspace, put it in CLAUDE.md. If CLAUDE.md already repeats project background, move
     that background into BRAIN.md instead of keeping it twice.
6. **Show the user:**
   - the files and their line counts;
   - BRAIN.md's table of contents and Open questions;
   - the hook output;
   - in a git repo, `git status --short`, which must list no brain files.

   Never commit any of it.

## learn – daily training (end of day, after a feature, sync, deploy or bug round)

1. **Collect what happened since BRAIN.md's `Last trained:` date:**
   - the CONTEXT.md entries;
   - `git log` and the changed files in the workspace and the repos in `.claude/brain.conf`;
   - new or changed files in the logic paths;
   - corrections the user gave in this session;
   - from the Execute.io chat (the `qa_connector` tools are there): brain cards never answered, from the open
     approvals `project_tasks` lists. Name them in the report; never write an item nobody approved.
2. **For each item, decide where it belongs:**
   - **New lasting knowledge** goes into the right place: a rule, a system/ID mapping, a convention or a decision
     into its BRAIN.md section (a decision also gets a decisions-log row `date | decision (why)`); app or system
     behaviour, a gotcha or a playbook (a known journey: steps and a checkpoint per stage) into its `brain/` file,
     with a one-line entry in BRAIN.md's index for it.
   - **An answered open question:** remove its row and write the answer into its section.
   - **A fact that is no longer true:** fix it in place. If a rule changed, add a decisions-log row.
   - **Status:** stays in CONTEXT.md.
   - **Finished work no next step needs:** move it word for word to the top of CONTEXT-archive.md, under
     `## Archived YYYY-MM-DD`.
3. **Keep the files lean:**
   - Run `python3 <this skill>/scripts/brain_split.py <workspace>` (Windows: `py -3`): it keeps BRAIN.md a core and
     moves new detail into `brain/`. Report its line in the training summary;
   - CONTEXT.md under about 150 lines.
4. **Close the training:**
   - Set `Last trained: YYYY-MM-DD` at the top of BRAIN.md.
   - Touch BRAIN.md, then CONTEXT.md, so the hook starts clean.
   - Report in 3–6 lines what the brain learned, corrected and retired.
5. **Escalate instead of guessing.** If a change contradicts BRAIN.md and nothing shows it was intended,
   don't overwrite. Ask the user and list it under Open questions.

## check – is the brain healthy?

Run `.claude/hooks/session-state.sh`, then report:
- the BRAIN.md and CONTEXT.md line counts and the `Last trained:` date;
- what `scripts/brain_split.py <workspace> --check` says (the core's size, and what would move to `brain/`);
- files changed since the last training;
- sections that are empty or out of date;
- facts that duplicate CONTEXT.md or CLAUDE.md;
- any secret-looking strings (long digit runs, `key=`, `token`, `password`).

Suggest `learn` when the last training is older than the newest CONTEXT.md entry.
