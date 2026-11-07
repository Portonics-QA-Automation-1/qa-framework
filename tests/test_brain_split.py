"""workspace-brain's brain_split.py: every project's BRAIN.md stays a slim core,
with its detail moved word for word into brain/ (token plan, 2026-11-07).
Run: python3 -m unittest discover -s tests"""
import datetime as dt
import importlib.util
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "plugins/qa-framework/skills/workspace-brain/scripts/brain_split.py"
spec = importlib.util.spec_from_file_location("brain_split", SCRIPT)
split = importlib.util.module_from_spec(spec)
spec.loader.exec_module(split)

TODAY = dt.date(2026, 11, 7)


def brain(gotchas=8, decisions=8, filler=0):
    lines = ["# BRAIN – Demo app", "", "Last trained: 2026-11-07", "", "## 1. Purpose and scope", "", "- QA for Demo.", "",
             "## 7. Behaviour learned (app / system)", "", "**Login**",
             "- The OTP screen shows 6 boxes; a wrong OTP shows \"Invalid OTP\".",
             "- After login a lucky draw pop-up shows; Back closes it.", "",
             "**Wrapped header** (task #9, evidence", "`TestCase/evidence/x/`)", "- The pill folds after 3 s.", "",
             "## 8. Gotchas", ""]
    lines += [f"- **Gotcha number {n} is known** (task #{n}): it looks wrong but is fine;\n  details on line two."
              for n in range(gotchas)]
    lines += ["", "## 9. Open questions", "", "| Topic | Question |", "|---|---|", "| X | Is it 14 or 24? |", "",
              "## 10. Decisions (newest first; why in brackets)", "", "| Date | Decision |", "|---|---|"]
    lines += [f"| {(TODAY - dt.timedelta(days=n)).isoformat()} | **Rule {n} applies.** Long reason here (the user: why {n}) |"
              for n in range(decisions)]
    lines += ["", "## 11. Keeping this file right", "", "- Edit in place."]
    lines += [f"- filler {n} " + "x" * 200 for n in range(filler)]
    return "\n".join(lines) + "\n"


class SplitTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.home = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.addCleanup(shutil.rmtree, self.home, ignore_errors=True)
        patcher = mock.patch.dict(os.environ, {"HOME": str(self.home), "USERPROFILE": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def write(self, text):
        (self.root / "BRAIN.md").write_text(text, encoding="utf-8")

    def everything(self):
        return "\n".join(p.read_text(encoding="utf-8") for p in [self.root / "BRAIN.md"] + sorted((self.root / "brain").glob("*.md")))

    def test_a_small_brain_is_left_alone(self):
        self.write(brain())
        self.assertIn("nothing to move", split.run(self.root, today=TODAY))
        self.assertFalse((self.root / "brain").exists())

    def test_a_big_brain_is_split_without_losing_a_line(self):
        original = brain(gotchas=60, decisions=12, filler=150)
        self.write(original)
        report = split.run(self.root, today=TODAY)
        self.assertIn("Moved", report)
        core = (self.root / "BRAIN.md").read_text(encoding="utf-8")
        self.assertLess(len(core), len(original))
        everything = self.everything()
        self.assertEqual([l for l in original.split("\n") if l.strip() and l not in everything], [])
        # The core keeps one line per item and points to the detail.
        self.assertIn("- Gotcha number 3 is known", core)
        self.assertNotIn("details on line two", core)
        self.assertIn("Full text: `brain/gotchas.md`", core)
        self.assertIn("- Login", core)
        self.assertIn("- Wrapped header", core)
        self.assertNotIn("`TestCase/evidence/x/`)", core)
        # Recent decisions stay in full; older ones move with a one-line rule.
        self.assertIn("| 2026-11-07 | **Rule 0 applies.**", core)
        self.assertIn("- 2026-10-29: Rule 9 applies", core)
        self.assertIn("| 2026-10-29 | **Rule 9 applies.**", (self.root / "brain/decisions.md").read_text(encoding="utf-8"))
        self.assertTrue((self.root / "brain/playbooks.md").exists())
        # The previous file is kept outside the workspace.
        self.assertEqual((self.home / ".claude/backups/brain" / f"{self.root.name}-BRAIN.md").read_text(encoding="utf-8"),
                         original)
        # Running again changes nothing.
        self.assertIn("nothing to move", split.run(self.root, today=TODAY))

    def test_a_split_brain_moves_new_items_and_ageing_decisions(self):
        self.write(brain(gotchas=60, decisions=12, filler=150))
        split.run(self.root, today=TODAY)
        core = (self.root / "BRAIN.md").read_text(encoding="utf-8")
        core = core.replace("Full text: `brain/gotchas.md`", "- **A new gotcha learned today** (task #200): tap X.\n\n"
                            "Full text: `brain/gotchas.md`", 1)
        (self.root / "BRAIN.md").write_text(core, encoding="utf-8")
        with mock.patch.object(split, "KEEP_ROWS", 1):
            report = split.run(self.root, today=TODAY + dt.timedelta(days=3))
        self.assertIn("Moved", report)
        core = (self.root / "BRAIN.md").read_text(encoding="utf-8")
        self.assertIn("- A new gotcha learned today", core)
        self.assertNotIn("(task #200): tap X.", core)
        self.assertIn("(task #200): tap X.", (self.root / "brain/gotchas.md").read_text(encoding="utf-8"))
        self.assertNotIn("| 2026-11-04 |", core)
        self.assertIn("- 2026-11-04: Rule 3 applies", core)

    def test_an_item_written_straight_into_brain_gets_its_index_line(self):
        self.write(brain(gotchas=60, decisions=12, filler=150))
        split.run(self.root, today=TODAY)
        gotchas = self.root / "brain/gotchas.md"
        gotchas.write_text(gotchas.read_text(encoding="utf-8") + "- **Approved from a brain card** (task #300): Back.\n",
                           encoding="utf-8")
        behaviour = self.root / "brain/app-behaviour.md"
        behaviour.write_text(behaviour.read_text(encoding="utf-8") + "\n**Top Up**\n- Top Up asks for a PIN.\n",
                             encoding="utf-8")
        self.assertIn("Added 2 index line(s)", split.run(self.root, today=TODAY))
        core = (self.root / "BRAIN.md").read_text(encoding="utf-8")
        self.assertIn("- Approved from a brain card", core)
        self.assertIn("- Top Up", core)
        self.assertEqual(core.count("- Gotcha number 3 is known\n"), 1)
        self.assertIn("nothing to move", split.run(self.root, today=TODAY))

    def test_check_changes_nothing(self):
        original = brain(gotchas=60, decisions=12, filler=150)
        self.write(original)
        self.assertIn("Would move", split.run(self.root, check=True, today=TODAY))
        self.assertEqual((self.root / "BRAIN.md").read_text(encoding="utf-8"), original)
        self.assertFalse((self.root / "brain").exists())


if __name__ == "__main__":
    unittest.main()
