# BRAIN – <workspace / project name>

Last trained: YYYY-MM-DD

This file holds the **lasting project logic**. Where the work stopped is in `CONTEXT.md`; the rules are in
`CLAUDE.md`. Detailed rulebooks live in `<conventions/ or docs/>`; this file points to them. No secrets.

## 1. Purpose and scope
- What the product or workspace is for, and for whom.
- Out of scope, including workspaces that must never be mixed with this one.

## 2. System map
| Part | What it is | Where (path / URL / repo) |
|---|---|---|

## 3. Environments and IDs
- Environments (for example local → preprod → prod), URLs, project/suite IDs per environment, the deploy
  order and the backup rule.
- ID maps: how an item in one environment maps to another.
- Variable *names* only for credentials.

## 4. Domain model and business rules
- Entities, their relationships and states.
- Each rule with where it is enforced (`file:function`) or where it was observed.

## 5. Key flows
- Step by step for the most important journeys, with the files, screens or tools involved.

## 6. Workflow and conventions
- How work is done here (stages, approval gates, naming, file layout, test approach).
- How to add a new feature or item the same way existing ones are done.

## 7. Behaviour learned (app / system)
- What really happens, especially where it differs from the spec. Group it by feature.

## 8. Gotchas
- Looks wrong but is known or intended; traps and workarounds.

## 9. Open questions
| Topic | Question | Blocks |
|---|---|---|

## 10. Decisions (newest first; why in brackets)
| Date | Decision |
|---|---|

## 11. Keeping this file right
- Train it with `/workspace-brain learn` at the end of each working day, and after a feature, sync, deploy
  or bug round.
- Update it in the same step as any change to logic, a rule, an environment, an ID map or a decision.
- Edit in place; remove facts that are no longer true; keep it within about 300 lines.
- Status goes to CONTEXT.md, never here.
