---
name: qa-requirement-analysis
description: QA review of a feature's requirements/spec for testability. Use when QA asks to analyse, review, or check requirements before writing test cases, or whenever a spec changes.
argument-hint: "<feature name or slug>"
---

# QA Requirement Analysis

Argument: `$ARGUMENTS` — the feature name/slug, or a pasted requirement if the project has
no formal spec folder.

## Steps

1. **Resolve the feature.** If this project has a `specs/` folder with an `INDEX.md`, confirm
   the slug exists there and that `specs/<slug>/spec.md` exists. If either is missing, say so
   — don't create them. If the project has no such structure, ask for (or use) the pasted
   requirement text directly.
   **Intake from the tracker and designs (when the argument is a ticket key/epic or the
   project conventions — `get_qa_guidelines` or `conventions/environments.md` — name a
   tracker):**
   - **Story tracker** (the claude.ai connector for the tracker the conventions name, e.g.
     Jira): read the story/epic and its child stories
     (title, description, acceptance criteria, attachments, links, labels, sprint, fix
     version). Read only; never create, edit or transition tickets here.
   - **Figma** (claude.ai Figma connector): for every Figma link in the stories, read the
     linked frames (names, text, component states) and export what the analyst needs.
   - Save the intake read-only snapshot to `TestCase/<feature-slug>/source/`
     (`story.md` with ticket keys and URLs, and design notes/images). The analyst works from
     this snapshot so the analysis is reproducible.
   - If a connector is missing or needs authentication, say so and continue with what the
     QA member pasted or attached; never authenticate on their behalf.
2. **Run the analyst.** Launch the `qa-framework:qa-requirement-analyst` subagent with: "Run requirement
   analysis for `<slug or requirement>` following your instructions." When a source snapshot
   exists, give its path and tell it to cite ticket keys and Figma frame names in findings.
3. **Check the result.** Read the report and verify: every requirement id in the source
   appears in the testability inventory; every finding quotes real text; no file other than
   the report was written/changed (`git status --short` if this is a git repo).
4. **Report to the user**: verdict, Blocker/Major/Minor counts, top Blocker questions, and
   the report's path. Next step: the requirement owner resolves gaps, then re-run this to
   confirm before test design.

## Rules

- Do not edit the spec/requirement document — gaps go back as questions.
- Do not commit changes.
