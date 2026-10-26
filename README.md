# QA Framework — Claude Code plugin

The team's QA agent framework, packaged as a Claude Code plugin marketplace so every QA can
install it once per machine and get updates with one command.

It contains one plugin, **`qa-framework`**: 15 agents and 15 skills that cover the whole QA
lifecycle.

| Stage | Skill (run as `/qa-framework:<skill>`) | Agent (`qa-framework:<agent>`) |
|---|---|---|
| Requirement analysis | `qa-requirement-analysis` | `qa-requirement-analyst` |
| Test plan | `qa-test-plan` | `qa-test-planner` |
| Environment readiness | `qa-env-readiness` | `qa-env-readiness` |
| Test design | `qa-test-design` | `qa-test-designer` |
| Sync to Execute.io | `qa-sync` | `qa-sync-manager` |
| Manual execution | `qa-execute` | `qa-manual-executor` |
| Failure triage | `qa-triage` | `qa-triage` |
| Karmo bug filing | `qa-file-bug` | `qa-defect-filer` |
| Maestro automation | `qa-automate-flow` | `qa-automation-engineer` |
| Regression run | `qa-regression` | `qa-regression-runner` |
| Fix verification | `qa-retest` | `qa-retest` |
| Impact analysis | `qa-impact-analysis` | `qa-impact-analyst` |
| Release-readiness report | `qa-report-signoff` | `qa-report-signoff` |
| Post-release check | `qa-post-release` | `qa-post-release` |
| Real-user exploration | `qa-real-user-test` | `qa-real-user` |

The agents are **project-neutral**. They hold no product names, test accounts, phone numbers or
keys. Everything project-specific comes from the project's QA workspace and from Execute.io.

## Install (once per machine)

You need Claude Code. Inside a Claude Code session, add the marketplace, then install the plugin:

```text
/plugin marketplace add <path-or-git-url-of-this-repo>
/plugin install qa-framework@qa-team
```

- **Local folder** (for example, a shared drive or a copied folder):
  `/plugin marketplace add /path/to/qa-framework`
- **GitHub** (the team's copy, private; ask the QA manager for read access first):
  `/plugin marketplace add https://github.com/AkramOffice/qa-framework.git`
  (or `AkramOffice/qa-framework`). Claude Code clones it with your own GitHub login, so run
  `gh auth login` or set up Git credentials for github.com first.

Then run `/reload-plugins`, or restart Claude Code. `/plugin` → **Installed** shows the plugin.

You can do the same from a terminal:

```bash
claude plugin marketplace add https://github.com/AkramOffice/qa-framework.git
```

```bash
claude plugin install qa-framework@qa-team
```

## Update

When the QA manager publishes a new version, refresh the marketplace, then update the plugin:

```text
/plugin marketplace update qa-team
```

Then open `/plugin` → **Installed** → `qa-framework` → **Update**. You can also run these from a
terminal:

```bash
claude plugin marketplace update qa-team
```

```bash
claude plugin update qa-framework@qa-team
```

After that, run `/reload-plugins`. The manager bumps `version` in
`plugins/qa-framework/.claude-plugin/plugin.json` and in `.claude-plugin/marketplace.json` for
every release.

## How it pairs with Execute.io

The plugin is the **how**: the agents, the skills and the gates. The Execute.io QA workspace
is the **what**: one project, its rules and its data. You need both.

1. In Execute.io, open **API Keys** → **Set up QA workspace** for your project. Download the
   zip and unpack it where you work. It contains:
   - `CLAUDE.md`: project facts and the workflow.
   - `conventions/qa-guidelines.md`: a snapshot of the team rulebook.
   - `conventions/environments.md`: environments, builds, test-account variable **names** and
     the project conventions.
   - `TestCase/` and `maestro/`: the test-case and Maestro framework folders.
   - The `execute-io-sync` MCP server, set up with **your personal key**, and
     `setup_workspace.py`.
2. Run `setup_workspace.py` as the workspace README says. Then open Claude Code **in that
   folder**.
3. Use the skills, for example `/qa-framework:qa-requirement-analysis <feature>`.

At the start of their work, the agents:

- call `get_qa_guidelines` to get the live team rulebook and this project's conventions. If
  the live version is newer than the snapshot in `conventions/`, the live version wins.
- call `get_project_context` to get suites, app ids, builds and test-account variable names.
- call `get_test_accounts(environment)` to get test-account values. These values are never
  read from files. Secrets stay masked unless a value must be typed on a device right then.
- fall back to `conventions/qa-guidelines.md` and `conventions/environments.md` when the MCP
  server is not connected.

Account types, sections, environments, Back Office/VPN routes, the defect tracker and naming
defaults are all defined in the project conventions, which a project editor maintains in
Execute.io. Change them there, not in this plugin.

## Karmo bug filing (per-project rules)

`/qa-framework:qa-file-bug` (agent `qa-defect-filer`) files a bug in Karmo in four steps: the
agent drafts it and fills the fields from the project's rules, the skill asks the QA member for
Assignee, Sprint and (if the rules say so) Components with a pick-list, shows the final ticket
and waits for a yes, and only then the agent creates it. You need the claude.ai **Karmo**
connector with a read/write key.

The plugin holds no Karmo project key, client name or people. Each project describes them in a
section headed **`## Karmo bug filing`**, in the Execute.io project conventions or in the
workspace's `conventions/environments.md`. Without that section the skill stops and asks for it.

The section has these parts (the example is a real project's section, with its key and names
replaced by placeholders):

```markdown
## Karmo bug filing

Project **<KEY>**, work type **Bug**. Read the field options with `get_project_meta` before filing
(they can change). Reporter is always the QA member (`whoami`).

**Ask the QA member every time** (show the options from Karmo):
- **Components**: e.g. Backend, Android, iOS, Backoffice, Frontend, Database, Infrastructure.
  Suggest one from the issue, but the QA member confirms it.
- **Assignee**: always ask with a pick-list. Offer up to 4 developers who recently worked on
  related <KEY> tickets for the same component, plus "Other". Resolve with `search_users`.
- **Sprint**: ask in the same prompt, listing the active sprints and "Backlog".

**Agent proposes, QA member can change in the same reply:**
- **Parent**: the story/epic the bug belongs to (search <KEY> tickets). If none fits, leave it empty.

**Agent decides from the title and depth of the issue** (shown in the draft):
| Field | Rule |
|---|---|
| Bug Type | Functional, Visual, Content, Performance, Crash. |
| Bug Severity | Critical: core journey blocked for all users, crash, data loss or security. Major: a feature fails with no workaround. Minor: fails partly or has a workaround. Low: cosmetic. |
| Priority | Critical → High (or Urgent if production is down), Major → High, Minor → Medium, Low → Low. |
| Bug Cause | Escaped Defect, User Story Mismatch, Corner Case, Improvement/CR, Known Issue. |
| Environment (Deployment) | Staging / Pre-Production / Production. |
| Client Project | <Client project name>. |
| Raised By | Internal. |
| QA Assignee | The QA member. |
| API | Backend bugs: endpoint, method, request and response, secrets masked. |

**Title format:** `[BE]`, `[Android]`, `[iOS]` or `[BO]` + what fails + when.

**Description:** Summary, Environment (env, build, platform, account type), Preconditions,
Steps (numbered), Expected, Actual, API details (backend), Evidence, Execute.io case/run if any.
Mask account identifiers, OTPs, tokens and personal emails.

Always show the full draft and wait for an explicit "yes" before creating the ticket. Save the
draft to `TestCase/evidence/<feature>/defects/<short-title>.md` first.
```

- **Ask** fields are always put to the QA member; the agent never guesses them.
- **Propose** fields are pre-filled and the QA member can change them in the same reply.
- **Decide** fields are set by the agent with a one-line reason each. The field names must match
  the custom fields of your Karmo project; the agent takes option values only from Karmo.

## Rules that never change

- **No secrets in this repo or in any workspace file.** No API keys, OTPs, passwords, phone
  numbers or other account identifiers. Your Execute.io key lives only in your own workspace's
  MCP configuration, and you must never commit it or share it.
- Agents never create Execute.io structure, file defects or sync anything without the QA
  member's explicit approval of the exact names and content.

## Repository layout

```text
qa-framework/
├── .claude-plugin/marketplace.json      # marketplace "qa-team"
├── README.md
├── CHANGELOG.md
└── plugins/qa-framework/
    ├── .claude-plugin/plugin.json       # plugin "qa-framework"
    ├── agents/*.md                      # 15 agents
    └── skills/<skill>/SKILL.md          # 15 skills
```

To check the plugin after a change:

```bash
claude plugin validate .
```

## Note for the QA manager

If your own machine still has the original copies in `~/.claude/agents` and `~/.claude/skills`,
you see both: the plain names (`/qa-test-design`) and the plugin names
(`/qa-framework:qa-test-design`). After you install the plugin, keep only one set, so you
don't edit the copy that nobody else gets.
