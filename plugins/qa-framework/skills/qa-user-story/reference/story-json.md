# Story JSON format (input to scripts/build_user_story.py)

```json
{
  "sheet_name": "Toh Toh United Leaderboard",
  "source": "Toh Toh United LeaderBoard.docx (FRS v1.1, 10 Sept 2026)",
  "header": {
    "project": "ATOM Store App",
    "client": "ATOM Myanmar",
    "created_by": "name@portonics.com",
    "date_created": "2026-10-27",
    "business_lead": "…",
    "tech_lead": "…",
    "notes": "Figma link or a special note",
    "epic": "Toh Toh United Leaderboard",
    "epic_id": ""
  },
  "rows": [
    {
      "sl": "1.0",
      "feature": "…",
      "as_a": "…",
      "expectation": "I will be able to …",
      "cos": "…",
      "ac": "…",
      "note": "- question?\n>> TBC",
      "image": "images/flow.png",
      "qa_comments": "",
      "qa_requirements": ""
    }
  ]
}
```

- Text uses `\n` for line breaks and `\n\n` between paragraphs.
- `image` is optional; a path relative to the JSON file (or absolute). It is scaled to the Screen/MockUp column.
- Any `header` key left out is left blank in the sheet. Document Title ("User Story & Estimation Template"), Version
  (5) and Template Last Modified (07-Jun-20) describe the template itself and stay fixed. `notes` is shown as a blue
  link only when it starts with `http`.
- `image` is shrunk to fit the column width and at most ~390 pt high, so an image never breaks the row-height limit. `sheet_name` is cut to 31 characters (Excel limit).
- The build prints a WARNING when a row would pass Excel's 409-pt row height; shorten or split that row.
