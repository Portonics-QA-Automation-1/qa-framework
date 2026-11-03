# <Project name> – integrations

| System | Used for | Configuration (names / ids only) |
|---|---|---|
| Execute.io (local) | test cases, runs, results | MCP server `<execute-io-sync>`; project `<name>` id `<…>` |
| Execute.io (production) | the team's shared runs | MCP server `<execute-io-sync-prod>`; project id `<…>`; every write confirmed |
| Defect tracker (<Karmo>) | bugs | project key `<…>`; filing rules: `conventions/environments.md` or `conventions/defect-filing.md` |
| Design (<Figma>) | designs | file `<…>` |
| Builds | where new builds arrive | `<team chat space / Drive folder / Firebase App Distribution>`; saved to `builds/` |
| BrowserStack App Live | real-device rounds | user `<…>`; API key file outside the workspace `<~/.config/browserstack.env>` |
| Maestro | automation | flows in `maestro/`; Execute.io Maestro agent |
| Analytics (<CleverTap / GA>) | event checks | access: `<who / how>` |
