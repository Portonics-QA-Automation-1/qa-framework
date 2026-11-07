"""session_recorder.py: a test session is recorded only when the QA member asks, as one full video or a clip per
case, compressed as soon as it stops, shared in chat-sized pieces and cleaned after the kept days (2026-11-07).
The device recorders are replaced by ffmpeg's test pattern, so this runs without a device.
Run: python3 -m unittest discover -s tests"""
import importlib.util
import json
import shutil
import subprocess
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "plugins/qa-framework/scripts/session_recorder.py"
spec = importlib.util.spec_from_file_location("session_recorder", SCRIPT)
rec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rec)


def fake_start(folder, state, clip, seconds=4):
    """A part that 'recorded' `seconds` of video, made with ffmpeg's test source."""
    raw = Path(folder) / ".raw"
    raw.mkdir(exist_ok=True)
    path = raw / f"{rec.safe(clip['name'])}-{len(clip['parts']) + 1}-{time.time_ns()}.mkv"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i", f"testsrc2=size=1080x2400:rate=15",
                    "-t", str(seconds), "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", str(path)], check=True)
    return {"recorder": "fake", "pid": 0, "files": [str(path)], "started": time.time() - seconds}


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "needs ffmpeg")
class RecorderTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        patch = mock.patch.object(rec, "start_part", fake_start)
        patch.start()
        self.addCleanup(patch.stop)
        self.dir = self.root / "round-1" / "recordings"

    def run_cmd(self, *args):
        out = StringIO()
        with redirect_stdout(out):
            code = rec.main(list(args))
        self.assertEqual(code, 0, out.getvalue())
        return out.getvalue()

    def begin(self, mode, keep="all"):
        self.run_cmd("begin", "--dir", str(self.dir), "--mode", mode, "--target", "android", "--keep", keep)

    def test_case_mode_keeps_only_failed_clips_compressed(self):
        self.begin("case", keep="failed")
        self.run_cmd("case-start", "--dir", str(self.dir), "--case", "TC-001")
        self.run_cmd("pause", "--dir", str(self.dir))
        self.run_cmd("resume", "--dir", str(self.dir))
        self.assertIn("clip saved", self.run_cmd("case-end", "--dir", str(self.dir), "--case", "TC-001",
                                                 "--result", "Failed"))
        self.run_cmd("case-start", "--dir", str(self.dir), "--case", "TC-002")
        self.assertIn("not kept", self.run_cmd("case-end", "--dir", str(self.dir), "--case", "TC-002",
                                               "--result", "Passed"))
        index = self.run_cmd("end", "--dir", str(self.dir))
        self.assertIn("TC-001.mp4", index)
        self.assertIn("TC-002: Passed, not kept", index)
        clip = self.dir / "TC-001.mp4"
        self.assertAlmostEqual(rec.probe_seconds(clip), 8, delta=1)  # both parts joined
        height = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=height",
                                 "-of", "csv=p=0", str(clip)], capture_output=True, text=True).stdout.strip()
        self.assertEqual(height, "720")  # compressed, not the raw 2400
        self.assertFalse((self.dir / ".raw").exists())
        self.assertFalse((self.dir / "TC-002.mp4").exists())

    def test_full_mode_has_a_chapter_per_case_and_shares_one_case(self):
        self.begin("full")
        self.run_cmd("case-start", "--dir", str(self.dir), "--case", "TC-001")
        self.run_cmd("case-end", "--dir", str(self.dir), "--case", "TC-001", "--result", "Passed")
        self.run_cmd("case-start", "--dir", str(self.dir), "--case", "TC-002")
        self.run_cmd("case-end", "--dir", str(self.dir), "--case", "TC-002", "--result", "Failed")
        index = self.run_cmd("end", "--dir", str(self.dir))
        self.assertIn("session.mp4", index)
        self.assertIn("TC-002 Failed", index)
        outbox = self.root / "outbox"
        shared = self.run_cmd("share", "--dir", str(self.dir), "--case", "TC-002", "--to", str(outbox))
        self.assertIn("TC-002.mp4", shared)
        self.assertTrue((outbox / "TC-002.mp4").exists())

    def test_share_splits_what_does_not_fit_a_message(self):
        self.begin("case")
        with mock.patch.object(rec, "start_part", lambda f, s, c: fake_start(f, s, c, seconds=20)):
            self.run_cmd("case-start", "--dir", str(self.dir), "--case", "TC-003")
            self.run_cmd("case-end", "--dir", str(self.dir), "--case", "TC-003", "--result", "Failed")
        self.run_cmd("end", "--dir", str(self.dir))
        outbox = self.root / "outbox"
        with mock.patch.object(rec, "MIN_SHARE_KBPS", 60):
            self.run_cmd("share", "--dir", str(self.dir), "--case", "TC-003", "--to", str(outbox), "--max-mb", "0.1")
        parts = sorted(outbox.glob("TC-003-part*.mp4"))
        self.assertGreater(len(parts), 1)
        for part in parts:
            self.assertLessEqual(part.stat().st_size, 0.1 * 1024 * 1024 * 1.15)

    def test_clean_deletes_old_clips_but_not_kept_ones(self):
        self.begin("case")
        for case in ("TC-001", "TC-002"):
            self.run_cmd("case-start", "--dir", str(self.dir), "--case", case)
            self.run_cmd("case-end", "--dir", str(self.dir), "--case", case, "--result", "Failed")
        self.run_cmd("end", "--dir", str(self.dir))
        self.run_cmd("keep", "--dir", str(self.dir), "--case", "TC-002")
        state = json.loads((self.dir / rec.STATE).read_text())
        state["ended"] -= 8 * 86400
        (self.dir / rec.STATE).write_text(json.dumps(state))
        self.assertIn("freed", self.run_cmd("clean", "--root", str(self.root), "--days", "7"))
        self.assertFalse((self.dir / "TC-001.mp4").exists())
        self.assertTrue((self.dir / "TC-002.mp4").exists())

    def test_a_recording_is_not_begun_twice(self):
        self.begin("case")
        out = StringIO()
        with redirect_stdout(out), mock.patch("sys.stderr", StringIO()):
            self.assertEqual(rec.main(["begin", "--dir", str(self.dir), "--mode", "full", "--target", "android"]), 2)


if __name__ == "__main__":
    unittest.main()
