#!/usr/bin/env python3
"""Keep a workspace's BRAIN.md a slim core, the same way in every project.

BRAIN.md is loaded into every Claude session of the workspace (Claude Desktop,
and every Google Chat message and task through the Execute.io connector), so
its size is paid again and again. This script keeps it a core: rules, IDs,
workflow, open questions and recent decisions, plus a one-line index of the
detail it moves word for word into `brain/`:

  - "behaviour" sections   -> brain/app-behaviour.md
  - "gotcha" sections      -> brain/gotchas.md
  - decisions older than KEEP_DAYS (at least KEEP_ROWS stay) -> brain/decisions.md
  - brain/playbooks.md is created for known journeys (agent-protocol §5b)

Agents fetch the detail with recall_brain (from the chat) or Read. Nothing is
reworded or dropped: every line of the old BRAIN.md is checked to exist in the
new core or a brain/ file before anything is written, and the old file is kept
in ~/.claude/backups/brain/<workspace>-BRAIN.md (latest only).

It acts when BRAIN.md is over the budget, or once the workspace has brain/
detail files (then it moves only the new full items, so the core stays slim).
Safe to run at any time; it changes nothing when there is nothing to move.

Usage: python3 brain_split.py <workspace> [--init] [--check] [--today YYYY-MM-DD]
(Windows: py -3 brain_split.py ...)
Standard library only (macOS, Windows, Linux).
"""
import argparse
import datetime as dt
import re
import shutil
import sys
from pathlib import Path

BUDGET_CHARS = 32000           # ~8k tokens: above it, a brain without brain/ is split
KEEP_DAYS = 3                  # decisions this recent stay in full in the core
KEEP_ROWS = 5                  # ...and at least this many
BRAIN_DIR = "brain"
FILES = {"behaviour": "app-behaviour.md", "gotchas": "gotchas.md", "decisions": "decisions.md"}
TITLES = {"behaviour": "App behaviour learned from testing", "gotchas": "Gotchas (looks wrong, but is known)",
          "decisions": "Older decisions (newest first; why in brackets)"}
POINTERS = {
    "behaviour": "Full text: `brain/app-behaviour.md` (fetch with `recall_brain`, or Read it, before testing an area "
                 "below). Areas:",
    "gotchas": "Full text: `brain/gotchas.md`. Fetch the item with `recall_brain` (or Read it) before the step it "
               "concerns. Items:",
    "decisions": "Older decisions (full rows with their reasons in `brain/decisions.md`; still in force unless a newer "
                 "row replaces them):",
}
PLAYBOOKS_TEMPLATE = """# Playbooks: known journeys (detail of BRAIN.md)

The way to a test case that the brain already knows, so agents follow it instead of exploring
(qa-framework agent-protocol §5b). One "## PB-<NAME>" section per journey: the app line it was verified on, its
steps, a checkpoint per stage, and the sources in brackets. Added from approved brain cards; no values (numbers,
OTPs, passwords) here, only variable names.
"""
HEADER = ("# {title} (detail of BRAIN.md)\n\nMoved word for word from BRAIN.md by the workspace-brain split "
          "(qa-framework); BRAIN.md keeps a one-line index. Same rules for keeping it right as BRAIN.md.\n\n")
ROW = re.compile(r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|")


def kind_of(heading):
    text = heading.lower()
    if "gotcha" in text:
        return "gotchas"
    if "behaviour" in text or "behavior" in text:
        return "behaviour"
    if "decision" in text:
        return "decisions"
    return None


def plain(text):
    return re.sub(r"\s+", " ", re.sub(r"[*`]", "", str(text or ""))).strip().lower()


def lead(text, limit=150):
    """The one-line index entry of an item: its bold title, else its opening clause."""
    text = text.strip()
    if text.startswith("- "):
        text = text[2:]
    match = re.match(r"^\*\*(.+?)\*\*", text)
    if match:
        return match.group(1).rstrip(" :.")
    clean = re.sub(r"\*\*|`", "", text)
    cut = len(clean)
    for found in re.finditer(r"(?<=[a-z0-9\)])[.;:] ", clean):
        if found.start() >= 40:
            cut = found.start()
            break
    clean = clean[:cut]
    return (clean if len(clean) <= limit else clean[:limit].rsplit(" ", 1)[0] + "…").rstrip(" :.")


def statement(row_text, limit=200):
    """A decision's index entry: its rule, without the reason in brackets."""
    text = re.sub(r"\*\*|`", "", row_text)
    text = re.sub(r"\s*\((the user|user|the QA member|QA member)[^)]*\)\s*$", "", text)
    cut = len(text)
    for found in re.finditer(r"(?<=[a-z0-9\)])[.;] ", text):
        if found.start() >= 40:
            cut = found.start()
            break
    text = text[:cut]
    return (text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + "…").rstrip(" :.")


def sections(lines):
    """[(heading line or None, body lines)] split at "## " headings."""
    out, heading, body = [], None, []
    for line in lines:
        if line.startswith("## "):
            out.append((heading, body))
            heading, body = line, []
        else:
            body.append(line)
    out.append((heading, body))
    return out


def blocks(body):
    """[(sub-header or None, item lines)] of a list section: a bullet with its
    continuation lines; "**Sub-header**" lines group the items after them.
    Other lines (intro, pointer) come back as (None, [line]) with item False."""
    out, group, item, in_header = [], None, None, False
    for line in body:
        if in_header and line.strip() and not line.startswith(("- ", "**")):
            # A sub-header that wraps onto the next line(s).
            group = f"{group}\n{line}"
            out[-1] = (group, out[-1][1] + [line], "header")
            continue
        in_header = False
        if re.match(r"^\*\*.+\*\*", line):
            if item:
                out.append((group, item, True))
                item = None
            group = line
            in_header = True
            out.append((group, [line], "header"))
        elif line.startswith("- "):
            if item:
                out.append((group, item, True))
            item = [line]
        elif item and line.startswith("  ") and line.strip():
            item.append(line)
        else:
            if item:
                out.append((group, item, True))
                item = None
            out.append((None, [line], False))
    if item:
        out.append((group, item, True))
    return out


def read(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError:
        return ""


def split_list(kind, heading, body, detail_text):
    """(new body, lines to add to the brain file) for a behaviour/gotchas section."""
    pointer = POINTERS[kind]
    known = plain(detail_text)
    keep, moved, index = [], [], []
    has_pointer = any(line.startswith("Full text: `brain/") for line in body)
    groups_moved = []
    parts = blocks(body)
    for group, lines, is_item in parts:
        if is_item == "header":
            continue
        if not is_item:
            line = lines[0]
            if line.startswith("Full text: `brain/"):
                continue
            keep.append(line)
            continue
        text = " ".join(l.strip() for l in lines)
        single = len(lines) == 1
        if has_pointer and single and len(plain(lines[0])) > 2 and plain(lines[0][2:]) in known:
            index.append(lines[0])  # already an index entry
            continue
        if group and kind == "behaviour":
            if group not in groups_moved:
                groups_moved.append(group)
                if group not in detail_text:
                    moved.append("")
                    moved.append(group)
                entry = f"- {lead(group)}"
                if plain(entry[2:]) not in [plain(i[2:]) for i in index]:
                    index.append(entry)
            moved.extend(lines)
        else:
            moved.extend(lines)
            index.append(f"- {lead(text)}")
    # A bold line with no item moved under it (a note such as "**Playbooks**",
    # or any header in a gotchas section) stays in the core.
    for group, lines, is_item in parts:
        if is_item == "header" and group not in groups_moved:
            keep.extend(lines + [""])
    intro = [line for line in keep if line.strip() or (keep and line == "")]
    while intro and not intro[-1].strip():
        intro.pop()
    new_body = [""] + intro + ([""] if intro else []) + [pointer, ""] + index + [""]
    return new_body, moved


def detail_leads(kind, detail_text):
    """The index entries a brain/ file calls for: one per feature header
    (behaviour) or per top-level item (gotchas)."""
    leads = []
    for group, lines, is_item in blocks(detail_text.split("\n")):
        if kind == "behaviour" and is_item == "header":
            leads.append(lead(group.split("\n")[0]))
        elif kind == "gotchas" and is_item is True:
            leads.append(lead(" ".join(l.strip() for l in lines)))
    return [entry for entry in leads if entry]


def add_missing_index(kind, body, detail_text):
    """(body, added) with an index line for every brain/ entry the core does
    not list yet (an approved item written straight into brain/)."""
    pointer = POINTERS[kind]
    if pointer not in body:
        return body, 0
    listed = [plain(line[2:])[:40] for line in body if line.startswith("- ")]
    missing = [f"- {entry}" for entry in detail_leads(kind, detail_text)
               if not any(plain(entry)[:40] == item or (item and plain(entry).startswith(item.rstrip("…")))
                          for item in listed)]
    if not missing:
        return body, 0
    start = body.index(pointer)
    end = start + 1
    while end < len(body) and (not body[end].strip() or body[end].startswith("- ")):
        end += 1
    while end > start + 1 and not body[end - 1].strip():
        end -= 1
    return body[:end] + missing + body[end:], len(missing)


def split_decisions(body, today):
    """(new body, rows to add to brain/decisions.md)."""
    rows = [line for line in body if ROW.match(line)]
    if not rows:
        return body, []
    dated = sorted(rows, key=lambda r: ROW.match(r).group(1), reverse=True)
    limit = (today - dt.timedelta(days=KEEP_DAYS)).isoformat()
    keep_rows = [r for r in dated if ROW.match(r).group(1) >= limit]
    if len(keep_rows) < KEEP_ROWS:
        keep_rows = dated[:KEEP_ROWS]
    move = [r for r in rows if r not in keep_rows]
    if not move:
        return body, []
    new_index = [f"- {ROW.match(r).group(1)}: {statement(r.split('|')[2].strip())}" for r in move]
    out, in_index, placed = [], False, False
    for line in body:
        if line in move:
            continue
        if line.startswith(POINTERS["decisions"]):
            out.append(line)
            in_index = True
            continue
        if in_index and not placed and line.startswith("- "):
            out.extend(new_index)
            placed = True
        out.append(line)
    if not placed:
        while out and not out[-1].strip():
            out.pop()
        if not any(line.startswith(POINTERS["decisions"]) for line in out):
            out += ["", POINTERS["decisions"], ""]
        elif out and out[-1] != "":
            pass
        out += new_index + [""]
    return out, move


def plan(workspace, today):
    """(new core text, {file: new text}, moved line count) or None when nothing moves."""
    root = Path(workspace)
    core_path = root / "BRAIN.md"
    original = read(core_path)
    if not original:
        return None
    folder = root / BRAIN_DIR
    # A small brain is cheap to load whole: the split starts at the budget,
    # and keeps going once detail files exist (playbooks.md alone does not count).
    split_already = any((folder / name).exists() for name in FILES.values())
    if not split_already and len(original) <= BUDGET_CHARS:
        return None
    files = {kind: read(folder / name) for kind, name in FILES.items()}
    new_lines, added, count, indexed_total = [], {kind: [] for kind in FILES}, 0, 0
    for heading, body in sections(original.split("\n")):
        kind = kind_of(heading) if heading else None
        if heading:
            new_lines.append(heading)
        if kind in ("behaviour", "gotchas"):
            body2, moved = split_list(kind, heading, body, files[kind])
            if any(l.strip() for l in moved):
                added[kind] += moved
                count += sum(1 for l in moved if l.strip())
                body = body2
            body, indexed = add_missing_index(kind, body, files[kind] + "\n" + "\n".join(added[kind]))
            indexed_total += indexed
        elif kind == "decisions":
            body2, moved = split_decisions(body, today)
            if moved:
                added[kind] += moved
                count += len(moved)
                body = body2
        new_lines.extend(body)
    if not count and not indexed_total:
        return None
    outputs = {}
    for kind, lines in added.items():
        if not any(l.strip() for l in lines):
            continue
        name = FILES[kind]
        current = files[kind] or HEADER.format(title=TITLES[kind]) + ("| Date | Decision |\n|---|---|\n"
                                                                       if kind == "decisions" else "")
        if kind == "decisions":
            head, sep, rest = current.partition("|---|---|\n")
            current = head + sep + "\n".join(lines) + "\n" + rest if sep else current + "\n".join(lines) + "\n"
        else:
            current = current.rstrip("\n") + "\n\n" + "\n".join(lines).strip("\n") + "\n"
        outputs[name] = current
    core = re.sub(r"\n{3,}", "\n\n", "\n".join(new_lines))
    # Nothing lost: every line of the old brain is in the new core or a brain/ file.
    everything = "\n".join([core] + [outputs.get(n, files[k]) for k, n in FILES.items()])
    lost = [l for l in original.split("\n") if l.strip() and l not in everything]
    if lost:
        raise RuntimeError(f"{len(lost)} line(s) would be lost, nothing written; first: {lost[0][:120]}")
    return core, outputs, count, indexed_total


def report(count, indexed, outputs, before, after, prefix):
    parts = []
    if count:
        parts.append(f"{prefix} {count} line(s) into {', '.join('brain/' + n for n in outputs)}")
    if indexed:
        parts.append(f"{'would add' if prefix == 'Would move' else 'added'} {indexed} index line(s) for entries "
                     "already in brain/")
    text = "; ".join(parts)
    return f"{text[0].upper()}{text[1:]}; core ~{before // 4} -> ~{after // 4} tokens."


def backup(core_path):
    target = Path.home() / ".claude" / "backups" / "brain"
    target.mkdir(parents=True, exist_ok=True)
    name = f"{core_path.parent.name}-BRAIN.md"
    shutil.copy2(core_path, target / name)
    return target / name


def init(workspace):
    """A new brain's brain/ folder with the playbooks file (setup)."""
    folder = Path(workspace) / BRAIN_DIR
    folder.mkdir(exist_ok=True)
    if not (folder / "playbooks.md").exists():
        (folder / "playbooks.md").write_text(PLAYBOOKS_TEMPLATE, encoding="utf-8")
    return f"{folder} ready (playbooks.md)."


def run(workspace, check=False, today=None):
    root = Path(workspace)
    today = today or dt.date.today()
    result = plan(root, today)
    if not result:
        size = len(read(root / "BRAIN.md"))
        return f"BRAIN.md core: ~{size // 4} tokens; nothing to move."
    core, outputs, count, indexed = result
    before = len(read(root / "BRAIN.md"))
    if check:
        return report(count, indexed, outputs, before, len(core), "Would move")
    saved = backup(root / "BRAIN.md")
    folder = root / BRAIN_DIR
    folder.mkdir(exist_ok=True)
    for name, text in outputs.items():
        (folder / name).write_text(text, encoding="utf-8")
    if not (folder / "playbooks.md").exists():
        (folder / "playbooks.md").write_text(PLAYBOOKS_TEMPLATE, encoding="utf-8")
    (root / "BRAIN.md").write_text(core, encoding="utf-8")
    return f"{report(count, indexed, outputs, before, len(core), 'Moved')} Previous BRAIN.md: {saved}"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("workspace")
    parser.add_argument("--check", action="store_true", help="say what would move, change nothing")
    parser.add_argument("--today", help="YYYY-MM-DD (for tests)")
    parser.add_argument("--init", action="store_true", help="create brain/ with playbooks.md (setup), then split")
    args = parser.parse_args(argv)
    try:
        if args.init:
            print(init(args.workspace))
        print(run(args.workspace, args.check, dt.date.fromisoformat(args.today) if args.today else None))
    except RuntimeError as exc:
        print(f"Not split: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
