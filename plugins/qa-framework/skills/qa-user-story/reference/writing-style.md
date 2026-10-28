# User story writing style (Portonics "User Story & Estimation Template")

Learned from the BA reference sheet "MyTM Mobile Application Story - Release - 3.27"
(Google Sheet 1hnP8zTdWHL-0bbCb-13UkxkKfxX7Lwq_7nQoI3bxXco, tabs such as "Star Gamification - Weekly Draw",
"Movie Series (Big9 + Mahar)", "New Thingyan theme for Golden Farm Game") and approved by the QA member on
2026-10-28 for the Toh Toh United Leaderboard story. `example-story.json` is the worked example: copy its tone.

## Sheet layout (fixed by the template)

- One sheet only: the story tab. No Instructions, Settings, Task Estimation or other tabs.
- Header block rows 1–9: Document Title / Version / Template Last Modified, Project Title, Client Name, Created By,
  Date Created, Business Lead, Tech Lead, NOTES (Figma link or a special note), EPIC name, Epic ID. Plain values,
  never formulas.
- Row 11 = column headers: # SL | Screen/MockUp (B:C merged) | Feature / Functionality | As a/an | Expectation |
  Condition of Satisfaction | Acceptance Criteria | Note/ Dependency | QA Comments | QA Requirements.
- Story rows start at row 12, one row per feature.

## Rows

- **One row per feature or screen**, numbered 1.0, 2.0, 3.0 … A sub-part of a feature that is a separate screen
  goes in its own row numbered x.1 right after its parent (e.g. 3.1 Previous Winners after 3.0 Leaderboard Page).
- Order: user journey first (eligibility/rules → entry/journey → main page → sub pages → T&C → error/stop cases),
  then BackOffice rows, then Report rows.
- Usually 5–10 rows for a feature. Keep each cell short enough that the row stays under Excel's 409-pt height limit;
  if a row gets too long, split the feature.

## Columns

| Column | How to write it | Example |
|---|---|---|
| # SL | 1.0, 2.0 … (x.1 for a sub-row) | `3.1` |
| Screen/MockUp | Leave empty, or an image (FRS mockup, Figma export, or one the QA member gives). Never invent an image. | — |
| Feature / Functionality | Short title, Title Case. BackOffice rows start with "BackOffice - ", report rows with "Report - ". | `BackOffice - Manual Repush of Match Result` |
| As a/an | The app's user type from the FRS, e.g. "ATOM Store App Prepaid User", "MyTM App Prepaid User", "BackOffice User", "CMS User". | `ATOM Store App Prepaid User` |
| Expectation | One sentence, first person, starts with "I will be able to …" (or "I want to …", "I will be informed …"). | `I will be able to see the winners of the recent 3 seasons.` |
| Condition of Satisfaction | What the system does, from the FRS. Plain short sentences, third person ("User will …", "There will be …", "BackOffice user will be able to …"). One idea per paragraph, blank line between paragraphs. Numbered lists `1.` `2.` for items, values or columns. | see below |
| Acceptance Criteria | What the user can see or do once it is built. Short "User will see …", "By clicking X, user will be redirected to Y." sentences. Include the negative/edge outcome the FRS gives ("If there is no link, nothing will happen."). | see below |
| Note/ Dependency | Open questions and dependencies. Each question on a line starting with "- ", the answer on the next line starting with ">> " (">> TBC" until the BA answers). A "Required info:" numbered list is also fine. Put "Not in FRS vX.Y …" and "Screen flow and Figma UI will be shared …" notes here. | `- Will repush be done for one MSISDN or in bulk?`<br>`>> TBC` |
| QA Comments / QA Requirements | Leave empty (QA fills them later). | — |

## Language

- Simple, plain business English, like the BA writes it. Short sentences. No marketing words, no "shall/must"
  legalese, no bold, no emoji, no markdown symbols other than "- " and "1." lists and ">>" answers.
- Use the FRS's own terms and quoted labels: button and page names in single quotes ('Continue Challenge').
- Name BackOffice as "BackOffice" (one word), app pages as "… page", pop-ups as "popup".
- Numbers and values exactly as in the FRS (Win = 3, Draw = 1, Loss = 0; Day -1).
- Examples are welcome when the FRS gives one: "Example:" on its own line, then the example.
- Do not copy whole FRS paragraphs; restate them shortly. Do not repeat the same rule in several rows; refer to it
  ("Players will be sorted by the ranking logic in row 1.0.").

## Scope rules

- The FRS is the only source. Every CoS/AC line must trace to an FRS statement.
- Anything the FRS does not say (meeting notes, an older story, a mockup detail) goes in only when the QA member
  asks, and its Note starts with "Not in FRS vX.Y. … to be confirmed with BA."
- Where an FRS section is empty (reports columns, analytics events), write the row with what is known and list the
  gaps in Note/Dependency as "Required info:" with ">> TBC". An empty section with no row of its own (e.g.
  Analytics & Deep-Link) goes in the Note of the closest row (usually the Report row).
- The example story's row 3.1 (Previous Winners) is not in its FRS: the QA member asked to keep it, so its Note says
  "Not in FRS v1.1 … to be confirmed with BA". Do not add such rows unless asked.
- If a mockup differs from the FRS text, the FRS wins; say so in the Note.

## Example row (from example-story.json, row 7.0)

- Feature: `BackOffice - Manual Repush of Match Result`
- As a/an: `BackOffice User`
- Expectation: `I will be able to manually repush a player's match result to fix the Leaderboard ranking.`
- CoS:
  ```
  Manual repush function will be available in BackOffice for the match result XP (Win, Draw, Loss) and goal score count, along with the timestamp.

  After repushing, it will reflect in the Leaderboard ranking.
  ```
- AC: `After a repush, the player's Score/XP, total goals and rank will be updated in the app Leaderboard.`
- Note:
  ```
  - Will repush be done for one MSISDN or in bulk (file upload)?
  >> TBC

  - Will repush add to the existing record or replace it? Is there any audit log?
  >> TBC
  ```
