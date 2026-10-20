# QA Framework — Claude Code plugin

The team's QA agent framework, packaged as a Claude Code plugin marketplace so every QA can
install it once per machine and get updates with one command.

It contains one plugin, **`qa-framework`**: 14 agents and 14 skills that cover the whole QA
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
- **Git** (once this repo is pushed to the team's Git host):
  `/plugin marketplace add https://<git-host>/<group>/qa-framework.git`, or `owner/repo` for GitHub.

Then run `/reload-plugins`, or restart Claude Code. `/plugin` → **Installed** shows the plugin.

You can do the same from a terminal:

```bash
claude plugin marketplace add /path/to/qa-framework
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
└── plugins/qa-framework/
    ├── .claude-plugin/plugin.json       # plugin "qa-framework"
    ├── agents/*.md                      # 14 agents
    └── skills/<skill>/SKILL.md          # 14 skills
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
