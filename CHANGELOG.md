# Changelog

## 1.3.0 — 2026-10-28

- Test-case priority uses Execute.io's own names: Critical, High, Medium, Low. They replace
  P0, P1, P2, P3 one-to-one, so QA members and Execute.io users see the same words.
  `qa-test-designer` writes the new names. `qa-sync-manager` sends `critical`/`high`/
  `medium`/`low` and maps any older P0–P3 file the same way, never storing `P0`–`P3`.
  `qa-automation-engineer`, `qa-test-planner`, `qa-report-signoff` and `qa-post-release`
  use the new names. Defect severity (S1/S2, "P0 defects") and story priority are unchanged.
- New skill `/qa-framework:qa-user-story` and agent `qa-user-story-writer`: write a feature's
  user story from its FRS as a single-sheet xlsx in the "User Story & Estimation Template", in
  the BA's writing style, with mockup images in the Screen/MockUp column. The FRS is the only
  source; non-FRS rows only on request, marked "Not in FRS". The skill ships the blank template,
  the writing-style guide, an approved example story and Python scripts (FRS reader, sheet
  builder). They run in `~/.cache/qa-framework/user-story-venv`, created on first use (needs
  `python3`).

## 1.2.0 — 2026-10-28

- Test cases follow the story: `qa-test-designer` reads each story's Expectation, Conditions
  of Satisfaction (CoS) and Acceptance Criteria (AC) first, then orders cases story row by row
  and CoS by CoS (happy path first, then that CoS's negative/boundary/edge cases, Android and
  iOS twins together), each linked to the AC that gives its expected result. Each CoS gets a
  heading quoting the bullet and naming its AC; a CoS with nothing testable keeps its heading
  with `No cases — Specification gap RA-n`. The traceability table is in story order, and a
  workbook export opens with a `Story map` sheet; the import sheet keeps its 12 columns.
- `/qa-framework:qa-test-design` checks that order against the story before reporting.
- `qa-requirement-analyst` assigns `USn-CSm` / `USn-ACm` ids in story order when a story has
  none, and lists its inventory in story order.

## 1.1.0 — 2026-10-26

- New skill `/qa-framework:qa-file-bug` and agent `qa-defect-filer`: file a bug in Karmo. The
  agent drafts the ticket from the project's "Karmo bug filing" rules, the skill asks for
  Assignee, Sprint and Components with a pick-list, shows the final ticket, and files only after
  an explicit yes. See "Karmo bug filing" in the README for the section each project needs.
- `qa-triage` skill: hands Karmo filing over to `/qa-framework:qa-file-bug`; other trackers keep
  the previous flow.

## 1.0.0 — 2026-10-20

- First release: 14 agents and 14 skills, from requirement analysis to post-release.
