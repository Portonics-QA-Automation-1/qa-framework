#!/usr/bin/env python3
"""Case list and results sheet for a BrowserStack App Live round.

Run with the python that scripts/setup_venv.sh prints (needs openpyxl).

  list   --cases <case.xlsx> --section Android|iOS
         Prints the section's cases as JSON (TC ID, account type, preconditions, data, steps, expected).
  add    --round <dir> --platform android|ios --tc <TC ID> --status Passed|Failed|Blocked|Needs Review|Not run
         --actual <text> --reason <text> --device <model / OS> [--evidence <text>]
         Appends one result to <dir>/results-<platform>.jsonl (one file per platform, so the
         two executors never write the same file). A later line for the same TC ID wins.
  merge  --cases <case.xlsx> --round <dir> --build <label>
         Writes <dir>/results.xlsx (the case sheet plus result columns and a Summary sheet)
         and <dir>/SUMMARY.md. The original case sheet is never changed.
"""
import argparse
import datetime
import json
import shutil
import sys
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

CASE_SHEET = "Test Cases"
RESULT_COLS = ["Status", "Actual Result", "Reason", "Device / OS", "Tested at", "Evidence"]
STATUSES = ["Passed", "Failed", "Blocked", "Needs Review", "Not run"]
NEEDS_REASON = ("Failed", "Blocked", "Needs Review")
FILLS = {
    "Passed": PatternFill("solid", fgColor="C6EFCE"),
    "Failed": PatternFill("solid", fgColor="FFC7CE"),
    "Blocked": PatternFill("solid", fgColor="FFEB9C"),
    "Needs Review": PatternFill("solid", fgColor="BDD7EE"),
    "Not run": PatternFill("solid", fgColor="D9D9D9"),
}


def case_rows(path):
    ws = openpyxl.load_workbook(path)[CASE_SHEET]
    header = [c.value for c in ws[1]]
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0]:
            yield dict(zip(header, row))


def load_results(round_dir):
    results = {}
    for f in sorted(Path(round_dir).glob("results-*.jsonl")):
        for line in f.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                results[r["tc_id"]] = r
    return results


def cmd_list(a):
    keep = ["TC ID", "Section", "User / Account Type", "Test Description", "Priority",
            "Preconditions", "Test Data", "Test Steps", "Expected Result"]
    cases = [{k: c.get(k) for k in keep} for c in case_rows(a.cases)
             if (c.get("Section") or "").lower() == a.section.lower()]
    json.dump(cases, sys.stdout, ensure_ascii=False, indent=1)
    print()


def cmd_add(a):
    if a.status not in STATUSES:
        sys.exit(f"status must be one of {STATUSES}")
    if a.status in NEEDS_REASON and not a.reason:
        sys.exit("a Failed, Blocked or Needs Review result needs --reason")
    rec = {
        "tc_id": a.tc, "platform": a.platform, "status": a.status, "actual": a.actual or "",
        "reason": a.reason or "", "device": a.device, "evidence": a.evidence or "",
        "tested_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    Path(a.round).mkdir(parents=True, exist_ok=True)
    with open(Path(a.round) / f"results-{a.platform}.jsonl", "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"{a.tc}: {a.status}")


def cmd_merge(a):
    round_dir = Path(a.round)
    out = round_dir / "results.xlsx"
    shutil.copyfile(a.cases, out)
    wb = openpyxl.load_workbook(out)
    ws = wb[CASE_SHEET]
    results = load_results(round_dir)

    first = ws.max_column + 1
    for i, name in enumerate(RESULT_COLS):
        cell = ws.cell(row=1, column=first + i, value=name)
        cell.font = Font(bold=True)
    keys = ["status", "actual", "reason", "device", "tested_at", "evidence"]
    counts = {}
    failures = []
    for row in range(2, ws.max_row + 1):
        tc = ws.cell(row=row, column=1).value
        if not tc:
            continue
        section = ws.cell(row=row, column=2).value or ""
        r = results.get(tc, {"status": "Not run"})
        for i, k in enumerate(keys):
            cell = ws.cell(row=row, column=first + i, value=r.get(k, ""))
            cell.alignment = Alignment(wrap_text=True, vertical="top")
        ws.cell(row=row, column=first).fill = FILLS[r["status"]]
        counts.setdefault(section, dict.fromkeys(STATUSES, 0))[r["status"]] += 1
        if r["status"] in NEEDS_REASON:
            desc = ws.cell(row=row, column=4).value or ""
            failures.append((tc, section, r["status"], desc, r.get("reason", ""), r.get("device", "")))
    for i, width in enumerate([12, 50, 50, 22, 16, 30]):
        ws.column_dimensions[openpyxl.utils.get_column_letter(first + i)].width = width

    if "Summary" in wb.sheetnames:
        del wb["Summary"]
    sm = wb.create_sheet("Summary", 0)
    sm.append([f"BrowserStack App Live round - build {a.build}"])
    sm["A1"].font = Font(bold=True, size=13)
    sm.append([])
    sm.append(["Platform"] + STATUSES + ["Total"])
    for c in sm[3]:
        c.font = Font(bold=True)
    for section, c in sorted(counts.items()):
        sm.append([section] + [c[s] for s in STATUSES] + [sum(c.values())])
    sm.append([])
    sm.append(["Failed / Blocked / Needs Review - to check"])
    sm.cell(row=sm.max_row, column=1).font = Font(bold=True)
    sm.append(["TC ID", "Platform", "Status", "Case", "Reason", "Device / OS"])
    for c in sm[sm.max_row]:
        c.font = Font(bold=True)
    for f in failures:
        sm.append(list(f))
        sm.cell(row=sm.max_row, column=3).fill = FILLS[f[2]]
    for col, width in zip("ABCDEF", [18, 10, 10, 50, 60, 22]):
        sm.column_dimensions[col].width = width
    wb.save(out)

    lines = [f"# BrowserStack App Live round - build {a.build}", "",
             f"Results sheet: `{out.name}` (case sheet + Status / Actual Result / Reason columns).", "",
             "| Platform | " + " | ".join(STATUSES) + " | Total |",
             "|---|" + "---|" * (len(STATUSES) + 1)]
    for section, c in sorted(counts.items()):
        lines.append(f"| {section} | " + " | ".join(str(c[s]) for s in STATUSES) + f" | {sum(c.values())} |")
    lines += ["", "## Failed / Blocked / Needs Review - to check", "",
              "| TC ID | Platform | Status | Case | Reason | Device / OS |", "|---|---|---|---|---|---|"]
    for f in failures:
        lines.append("| " + " | ".join(str(x).replace("|", "/").replace("\n", " ") for x in f) + " |")
    (round_dir / "SUMMARY.md").write_text("\n".join(lines) + "\n")
    print(f"wrote {out} and {round_dir / 'SUMMARY.md'}")
    for section, c in sorted(counts.items()):
        print(section, c)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list")
    s.add_argument("--cases", required=True)
    s.add_argument("--section", required=True)
    s = sub.add_parser("add")
    for k in ("--round", "--platform", "--tc", "--status", "--device"):
        s.add_argument(k, required=True)
    for k in ("--actual", "--reason", "--evidence"):
        s.add_argument(k)
    s = sub.add_parser("merge")
    for k in ("--cases", "--round", "--build"):
        s.add_argument(k, required=True)
    a = p.parse_args()
    {"list": cmd_list, "add": cmd_add, "merge": cmd_merge}[a.cmd](a)


if __name__ == "__main__":
    main()
