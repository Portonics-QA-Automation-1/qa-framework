---
name: qa-user-story
description: Write a feature's user story from its FRS (Feature Requirement Document) in the Portonics "User Story & Estimation Template" - one story sheet only, in the BA's writing style (short rows, "I will be able to…", plain CoS/AC, notes as "question / >> answer"), with mockup images in the Screen/MockUp column. Use when asked to "write / rewrite the user story from the FRS".
argument-hint: "<FRS path or Google Drive link> [feature name]"
---

# QA User Story from FRS

Argument: `$ARGUMENTS` — the FRS (a local .docx/.pdf path or a Google Drive link) and optionally the feature name.

## Steps

1. **Resolve inputs.** Find the FRS file. If it is a Google Drive link, read it with the Google Drive connector
   (`read_file_content`, or `download_file_content` for a .docx) and save a copy under
   `TestCase/<feature-slug>/`. Ask the QA member for anything you cannot find: the header values (Project, Client,
   Created By, Business Lead, Tech Lead, Figma link) and any mockup images they want used. If an older story for
   the feature exists, use it only for the header values and images, never as a requirement source.
2. **Run the writer.** Launch the `qa-framework:qa-user-story-writer` subagent with the workspace root, the FRS
   path, the feature slug, the header values, the image paths and any QA instructions (e.g. "keep the Previous
   Winners row although it is not in the FRS").
3. **Check the result.** The agent returns the xlsx path, the row list, the FRS gaps it put in Note/Dependency and
   any non-FRS rows. Look at its Quick Look render (macOS). Show the QA member the row table and the gaps.
4. **Hand over.** Nothing is uploaded to Google Drive or shared with the BA without the QA member's yes. If the
   workspace keeps a `CONTEXT.md`, add the file path and what waits on the QA member.

## Files in this skill

- `template/user-story-template.xlsx` — blank single-sheet template (header block + column headers).
- `scripts/setup_venv.sh` — creates `~/.cache/qa-framework/user-story-venv` once (openpyxl, pillow, python-docx)
  and prints its python path. Run every script with that python and `-I`.
- `scripts/build_user_story.py` — story JSON → formatted xlsx (fonts, borders, widths, row heights, images, freeze
  panes, landscape print).
- `scripts/read_frs.py` — prints a .docx FRS in order (headings, paragraphs, tables) and saves its embedded images.
- `reference/writing-style.md` — the writing rules. `reference/example-story.json` (+ `example-images/`) — an
  approved story (Toh Toh United Leaderboard) as a worked example. `reference/story-json.md` — the JSON format.
