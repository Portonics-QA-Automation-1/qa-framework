---
name: qa-file-bug
description: File a bug in Karmo on the QA member's behalf - draft it with every field filled from the workspace rules, ask only for Components / Assignee / Sprint with a pick-list, show the final ticket, and create it after an explicit yes. Use when the QA member says "post / file / raise this issue in Karmo".
argument-hint: "<what happened - steps, expected, actual, environment/build/platform, API request/response, evidence paths>"
---

# File a bug in Karmo

Argument: `$ARGUMENTS` is the issue in the QA member's words (plus any evidence paths, payloads or
Execute.io case/run).

The project key and field rules come from the workspace's **"Karmo bug filing"** section
(Execute.io project conventions, or `conventions/environments.md`). If there is none, say so and
point the QA member to the format in the qa-framework README; don't file.

## Steps

1. **Gather facts.** If the argument lacks something the ticket needs, ask in one short message:
   the environment (staging/preprod/prod), the app version and platform, and for an API issue the
   endpoint and response. Don't block on optional facts; note them as missing.
   Never echo a full account identifier, OTP or token back. Mask it.
2. **Draft.** Launch the `qa-framework:qa-defect-filer` subagent in **DRAFT** mode with the issue.
   It reads Karmo (read-only), checks duplicates, fills the fields from the "Karmo bug filing"
   rules, saves the draft under `TestCase/evidence/<feature>/defects/` and returns pick-list
   options.
3. **Duplicates.** If it reports a likely duplicate, show it and ask whether to file anyway or
   comment on the existing ticket instead.
4. **Ask with a pick-list.** Use AskUserQuestion, never just prose. Ask in one prompt:
   - **Assignee:** up to 4 suggested developers, each with the reason; the QA member can type
     another name via "Other".
   - **Sprint:** the active sprints, plus Backlog.
   - **Components:** only if the rules mark it "ask" and the QA member didn't already say it; the
     suggested component goes first.
   - **Parent:** only if the subagent found candidates.
5. **Show the final ticket.** Give the title, every field with its value, and the description, with
   secrets masked. Then ask "File this in Karmo?" and wait for an explicit yes. Apply corrections
   and show it again if they change anything.
6. **File.** Launch `qa-framework:qa-defect-filer` in **FILE** mode with:
   - the draft path;
   - the answers;
   - the line "Approved by the QA member: yes".
7. **Report.** Give the ticket key and link, and anything that couldn't be set or attached. If the
   connection is read-only, say exactly that: a read/write Karmo key, then reconnect, then a new
   session. If the workspace keeps a `CONTEXT.md`, add one line to it (key, title, assignee).

Never file without the yes from step 5. Never change, transition or close existing tickets.
