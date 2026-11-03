---
name: qa-workspace-init
description: Create (or upgrade) a QA project workspace for one project - the folder layout, CLAUDE.md, the project brain (BRAIN.md, CONTEXT.md, CONTEXT-archive.md via workspace-brain), conventions stubs (qa-guidelines, environments, integrations, gates) and a builds folder - so every qa-* agent works from that project's own rules and knowledge. Use when a QA member starts on a new project ("set up a workspace for <project>"), joins an existing project on a new machine, or when an older workspace should get the framework 2.x layout ("upgrade this workspace").
argument-hint: <project name> [folder] | upgrade
---

# QA workspace init

Argument: `$ARGUMENTS`. One workspace per project; never mix two projects in one folder. All agents follow
`${CLAUDE_PLUGIN_ROOT}/reference/agent-protocol.md`; this skill gives them a workspace to read from.

## 1. Ask first (one message, only what is missing)

- Project name (e.g. "ATOM Store App") and short code (e.g. `ATOM`), used in task ids.
- Folder (default `~/Desktop/<ProjectName>Workspace`). If it exists, switch to **upgrade** (section 4).
- Platforms and app ids (Android package / iOS bundle per environment), environments in use
  (staging / preprod / prod).
- Execute.io: server (local / production), project name and id; MCP server name configured for this folder.
- Defect tracker (e.g. Karmo) project key; design tool (e.g. Figma) file name.
- Account types the project uses (names only, e.g. prepaid, postpaid, guest) and the env-variable names that
  hold them. Never the values.
- Where builds arrive (team chat, Drive, Firebase App Distribution) and the BrowserStack user, if any.

Show the plan (folders and files to create) and wait for a yes.

## 2. Create the layout

```
<folder>/
  CLAUDE.md                 from templates/CLAUDE.md
  conventions/
    qa-guidelines.md        team rulebook snapshot: from Execute.io get_qa_guidelines if connected, else the
                            plugin default (templates/qa-guidelines.md); the live Execute.io text wins when newer
    environments.md         templates/environments.md, filled with the answers above
    integrations.md         templates/integrations.md, filled
    gates.md                templates/gates.md (defaults; the QA lead may tighten)
  features/                 one folder per feature (templates/feature-status.md is copied in per feature)
  builds/                   APK/IPA received; add to .gitignore if the folder is a repo
  maestro/                  only when the project automates (env NAME files; values never written)
```

Fill every `<…>` you know; leave the others as `TODO (ask QA)` lines, never invented values.

## 3. Create the brain

Run the plugin's `workspace-brain` skill in `setup` mode for this folder. It writes `BRAIN.md`, `CONTEXT.md`,
`CONTEXT-archive.md`, the SessionStart hook and the hand-off section. Then add to `BRAIN.md`:
- section "Purpose and scope": project name, platforms, what is out of scope;
- section "System map": app ids, environments, Execute.io project, tracker, builds source (from the answers);
- a pointer to `conventions/` for the details.

Rules (also written into the new CLAUDE.md):
- This workspace holds this project only. A product the project uses (e.g. Execute.io) keeps its own
  development brain in its own repo; this brain records only how the project uses it.
- The brain is local only; never committed or pushed. No secrets in any brain or conventions file.

## 4. Upgrade an existing workspace

1. Read its CLAUDE.md, BRAIN.md, CONTEXT.md and `conventions/`.
2. Add only what is missing (`conventions/integrations.md`, `conventions/gates.md`, `features/`, `builds/`,
   the CLAUDE.md section "Framework 2.x"); never overwrite or move existing files. Existing folders such as
   `TestCase/`, `pipeline/` or `APK/` keep working: agents read both layouts.
3. Run `workspace-brain check` and show its result.

## 5. Finish

Show the created files with line counts, the open `TODO (ask QA)` items, and the hook output. Update the new
`CONTEXT.md` with "Workspace created/upgraded on <date>; open TODOs: …". Propose the next step (usually
"start a feature: requirement analysis of <feature>").
