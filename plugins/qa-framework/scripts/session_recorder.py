#!/usr/bin/env python3
"""Record a test session as video, only when the QA member asked for it (agent-protocol section 4d).

  session_recorder.py check  [--target android|ios-sim|screen]
  session_recorder.py begin  --dir <round>/recordings --mode full|case --target android|ios-sim|screen
                             [--device <serial or udid>] [--region X,Y,W,H --scale S [--screen N]]
                             [--keep all|failed] [--days 7] [--root <evidence root>]
  session_recorder.py case-start --dir D --case TC-001
  session_recorder.py case-end   --dir D --case TC-001 --result Passed|Failed|Blocked|"Needs Review"
  session_recorder.py pause  --dir D        (before any login number, OTP or PIN is typed)
  session_recorder.py resume --dir D [--region X,Y,W,H --scale S]   (after the value is in; new region if moved)
  session_recorder.py end    --dir D        (stops, compresses, writes recordings.md)
  session_recorder.py keep   --dir D --case TC-001   (never cleaned: e.g. attached to a bug)
  session_recorder.py share  --dir D [--case TC-001] --to <folder> [--max-mb 19]
  session_recorder.py clean  --root <evidence root> [--days 7]

Modes: full = one video of the whole round with a chapter per case (recordings.md lists the times);
case = one clip per case. --keep failed (case mode) keeps only clips of cases that did not pass.

Every clip is compressed (H.264, 720p, low frame rate) the moment it stops and the raw recording is deleted,
so only the small copy takes space. `share` makes a copy that fits a chat message (Google Chat via the
connector's outbox: 20 MB), cut to one case and split into parts when needed. Old clips are deleted by
`clean` (also run by `begin --root`) after --days, except kept ones.

Recorders: android = scrcpy (no time limit; falls back to adb screenrecord in 3-minute pieces), ios-sim =
xcrun simctl (macOS only), screen = ffmpeg capturing a screen region (the App Live browser window; macOS
needs the Screen Recording permission for the app that runs this). ffmpeg does the compression. Works on
macOS, Windows and Linux; `check` says what is missing and how to install it.
"""
import argparse
import datetime as dt
import json
import math
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

STATE = "recording.json"
INDEX = "recordings.md"
KEEP_DAYS = 7
SHARE_MB = 19
FPS = 10
HEIGHT = 720
MIN_SHARE_KBPS = 250
ADB_PIECE_SECONDS = 170

INSTALL = {
    "ffmpeg": {"darwin": "brew install ffmpeg", "win32": "winget install Gyan.FFmpeg", "linux": "sudo apt install ffmpeg"},
    "scrcpy": {"darwin": "brew install scrcpy", "win32": "winget install Genymobile.scrcpy",
               "linux": "sudo apt install scrcpy"},
}


class RecorderError(Exception):
    pass


def platform_key():
    return "win32" if os.name == "nt" else ("darwin" if sys.platform == "darwin" else "linux")


def tool(name):
    return shutil.which(name)


def adb():
    found = tool("adb")
    if found:
        return found
    for base in (os.environ.get("ANDROID_HOME"), os.environ.get("ANDROID_SDK_ROOT"),
                 str(Path.home() / "Library/Android/sdk"), str(Path.home() / "AppData/Local/Android/Sdk"),
                 str(Path.home() / "Android/Sdk")):
        if base:
            path = Path(base) / "platform-tools" / ("adb.exe" if os.name == "nt" else "adb")
            if path.exists():
                return str(path)
    return None


def now():
    return time.time()


def stamp(seconds):
    seconds = int(round(seconds))
    return f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"


def safe(name):
    return re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-") or "clip"


# ---------- state ----------

def load(folder):
    path = Path(folder) / STATE
    if not path.exists():
        raise RecorderError(f"No recording was begun in {folder} (run `begin` first).")
    return json.loads(path.read_text(encoding="utf-8"))


def save(folder, state):
    (Path(folder) / STATE).write_text(json.dumps(state, indent=2), encoding="utf-8")


# ---------- processes ----------

def launch(cmd, log_path):
    kwargs = {"stdin": subprocess.DEVNULL}
    log = open(log_path, "ab")
    kwargs.update(stdout=log, stderr=subprocess.STDOUT)
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | 0x08000000  # CREATE_NO_WINDOW
    else:
        kwargs["start_new_session"] = True
    try:
        return subprocess.Popen(cmd, **kwargs).pid
    finally:
        log.close()


def alive(pid):
    if not pid:
        return False
    if os.name == "nt":
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True).stdout
        return str(pid) in out
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    try:  # a finished child that nobody reaped yet
        done, _ = os.waitpid(pid, os.WNOHANG)
        return done == 0
    except ChildProcessError:
        return True


def wait_gone(pid, seconds):
    end = now() + seconds
    while now() < end:
        if not alive(pid):
            return True
        time.sleep(0.3)
    return not alive(pid)


def interrupt(pid, seconds=20):
    """Stop a recorder the way Ctrl+C does, so it finishes its file."""
    if not alive(pid):
        return
    try:
        os.kill(pid, signal.CTRL_BREAK_EVENT if os.name == "nt" else signal.SIGINT)
    except (OSError, AttributeError, ValueError):
        pass
    if wait_gone(pid, seconds):
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)
    else:
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
    wait_gone(pid, 5)


# ---------- recorders ----------

def avfoundation_screen(index):
    out = subprocess.run([tool("ffmpeg"), "-hide_banner", "-f", "avfoundation", "-list_devices", "true", "-i", ""],
                         capture_output=True, text=True).stderr
    for line in out.splitlines():
        found = re.search(r"\[(\d+)\] Capture screen (\d+)", line)
        if found and int(found.group(2)) == index:
            return found.group(1)
    raise RecorderError("ffmpeg sees no screen to capture. On macOS give the app that runs this the Screen "
                        "Recording permission (System Settings > Privacy & Security > Screen Recording).")


def even(value):
    value = int(round(value))
    return value - value % 2


def screen_command(state, path):
    ffmpeg = tool("ffmpeg")
    if not ffmpeg:
        raise RecorderError("ffmpeg is missing: " + INSTALL["ffmpeg"][platform_key()])
    x, y, w, h = (float(v) for v in state["region"])
    scale = float(state.get("scale") or 1)
    x, y, w, h = even(x * scale), even(y * scale), even(w * scale), even(h * scale)
    encode = ["-vf", f"scale=-2:'min({HEIGHT},ih)'", "-c:v", "libx264", "-preset", "veryfast", "-crf", "30",
              "-pix_fmt", "yuv420p", str(path)]
    key = platform_key()
    if key == "darwin":
        device = avfoundation_screen(int(state.get("screen") or 0))
        return [ffmpeg, "-hide_banner", "-nostdin", "-y", "-f", "avfoundation", "-capture_cursor", "1",
                "-framerate", str(FPS), "-i", f"{device}:none",
                "-vf", f"crop={w}:{h}:{x}:{y},scale=-2:'min({HEIGHT},ih)'", *encode[2:]]
    if key == "win32":
        return [ffmpeg, "-hide_banner", "-nostdin", "-y", "-f", "gdigrab", "-framerate", str(FPS),
                "-offset_x", str(x), "-offset_y", str(y), "-video_size", f"{w}x{h}", "-i", "desktop", *encode]
    display = os.environ.get("DISPLAY", ":0")
    return [ffmpeg, "-hide_banner", "-nostdin", "-y", "-f", "x11grab", "-framerate", str(FPS),
            "-video_size", f"{w}x{h}", "-i", f"{display}+{x},{y}", *encode]


def start_part(folder, state, clip):
    """Start recording one part of a clip and check it really records; returns the part record."""
    part = launch_part(folder, state, clip)
    healthy(Path(folder) / ".raw" / "recorder.log", part)
    return part


def log_tail(log):
    try:
        return " ".join(Path(log).read_text(encoding="utf-8", errors="replace").split()[-40:])
    except OSError:
        return ""


def frames(log):
    """Frames ffmpeg reports so far (its file may stay empty for a while: Matroska is written in clusters)."""
    try:
        found = re.findall(rb"frame= *(\d+)", Path(log).read_bytes()[-4000:])
    except OSError:
        return 0
    return int(found[-1]) if found else 0


def healthy(log, part, seconds=10):
    """A recorder that dies or writes nothing (e.g. macOS without the Screen Recording permission) is
    stopped and reported, instead of leaving a round with an empty video."""
    end = now() + seconds
    while now() < end:
        if not alive(part["pid"]):
            if part["recorder"] == "adb":
                break
            raise RecorderError(f"The {part['recorder']} recorder stopped at once: {log_tail(log)}")
        if part["recorder"] not in ("ffmpeg", "scrcpy"):
            time.sleep(2)
            return
        if any(Path(f).exists() and Path(f).stat().st_size > 0 for f in part["files"]) or frames(log) > 0:
            return
        time.sleep(0.5)
    interrupt(part["pid"], 3)
    hint = (" On macOS give the app that runs the agent (Claude, Terminal or the Execute.io connector) the Screen "
            "Recording permission: System Settings > Privacy & Security > Screen Recording, then start again."
            if part["recorder"] == "ffmpeg" and platform_key() == "darwin" else "")
    raise RecorderError(f"The {part['recorder']} recorder wrote nothing in {seconds} s.{hint} {log_tail(log)}".strip())


def launch_part(folder, state, clip):
    folder = Path(folder)
    raw = folder / ".raw"
    raw.mkdir(exist_ok=True)
    number = sum(len(c["parts"]) for c in state["clips"]) + 1
    base = raw / f"{safe(clip['name'])}-{number}"
    log = raw / "recorder.log"
    target, device = state["target"], state.get("device")
    if target == "android":
        if tool("scrcpy"):
            path = base.with_suffix(".mkv")
            cmd = [tool("scrcpy"), "--no-playback", "--no-audio", "--max-size", "1280", "--video-bit-rate", "1M",
                   "--max-fps", "15", f"--record={path}"]
            if device:
                cmd[1:1] = ["-s", device]
            return {"recorder": "scrcpy", "pid": launch(cmd, log), "files": [str(path)], "started": now()}
        if not adb():
            raise RecorderError("Neither scrcpy nor adb is installed: " + INSTALL["scrcpy"][platform_key()])
        cmd = [sys.executable, "-I", str(Path(__file__).resolve()), "_adb-loop", "--base", str(base)]
        if device:
            cmd += ["--device", device]
        return {"recorder": "adb", "pid": launch(cmd, log), "files": [], "base": str(base), "started": now()}
    if target == "ios-sim":
        if platform_key() != "darwin" or not tool("xcrun"):
            raise RecorderError("The iOS simulator can be recorded on macOS only (Xcode's xcrun).")
        path = base.with_suffix(".mp4")
        cmd = ["xcrun", "simctl", "io", device or "booted", "recordVideo", "--codec=h264", "--force", str(path)]
        return {"recorder": "simctl", "pid": launch(cmd, log), "files": [str(path)], "started": now()}
    if target == "screen":
        path = base.with_suffix(".mkv")
        return {"recorder": "ffmpeg", "pid": launch(screen_command(state, path), log), "files": [str(path)],
                "started": now()}
    raise RecorderError(f"Unknown target {target}")


def stop_part(state, part):
    if part["recorder"] == "adb":
        Path(part["base"] + ".stop").write_text("stop", encoding="utf-8")
        cmd = [adb()] + (["-s", state["device"]] if state.get("device") else []) + [
            "shell", "pkill", "-2", "screenrecord"]
        subprocess.run(cmd, capture_output=True)
        wait_gone(part["pid"], 90)
        listed = Path(part["base"] + ".parts.json")
        part["files"] = json.loads(listed.read_text(encoding="utf-8")) if listed.exists() else []
    else:
        interrupt(part["pid"])
    part["files"] = [f for f in part["files"] if Path(f).exists() and Path(f).stat().st_size > 0]
    part["seconds"] = round(now() - part.pop("started"), 1)
    part.pop("pid", None)
    return part


def adb_loop(base, device=None):
    """Runs detached: adb screenrecord stops after 3 minutes, so record in pieces until told to stop,
    then pull the pieces off the device."""
    base = Path(base)
    stop = Path(str(base) + ".stop")
    cmd = [adb()] + (["-s", device] if device else [])
    remote, files = [], []
    number = 0
    while not stop.exists():
        number += 1
        path = f"/sdcard/tf-rec-{base.name}-{number}.mp4"
        remote.append(path)
        subprocess.run(cmd + ["shell", "screenrecord", "--bit-rate", "1000000", "--time-limit",
                              str(ADB_PIECE_SECONDS), path], capture_output=True)
    time.sleep(1)
    for number, path in enumerate(remote, 1):
        local = Path(f"{base}-{number}.mp4")
        subprocess.run(cmd + ["pull", path, str(local)], capture_output=True)
        subprocess.run(cmd + ["shell", "rm", "-f", path], capture_output=True)
        if local.exists():
            files.append(str(local))
    Path(str(base) + ".parts.json").write_text(json.dumps(files), encoding="utf-8")


# ---------- compression and sharing ----------

def probe_seconds(path):
    probe = tool("ffprobe")
    if not probe:
        return None
    out = subprocess.run([probe, "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1",
                          str(path)], capture_output=True, text=True).stdout.strip()
    try:
        return float(out)
    except ValueError:
        return None


def compress(files, out):
    """Join the raw parts of a clip into one small MP4; the raw files are deleted. Without ffmpeg the raw
    parts are kept as they are (and `check` says how to install it)."""
    files = [Path(f) for f in files if Path(f).exists()]
    if not files:
        return []
    ffmpeg = tool("ffmpeg")
    if not ffmpeg:
        kept = []
        for number, path in enumerate(files, 1):
            dest = out.with_name(f"{out.stem}{'' if len(files) == 1 else f'-part{number}'}{path.suffix}")
            shutil.move(str(path), dest)
            kept.append(str(dest))
        return kept
    listing = out.with_suffix(".txt")
    listing.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in files), encoding="utf-8")
    result = subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
                             "-i", str(listing), "-an", "-vf", f"fps={FPS},scale=-2:'min({HEIGHT},ih)'",
                             "-c:v", "libx264", "-preset", "veryfast", "-crf", "30", "-pix_fmt", "yuv420p",
                             "-movflags", "+faststart", str(out)], capture_output=True, text=True)
    listing.unlink(missing_ok=True)
    if result.returncode != 0 or not out.exists():
        raise RecorderError(f"Compressing {out.name} failed: {result.stderr.strip()[-300:]}")
    for path in files:
        path.unlink(missing_ok=True)
    return [str(out)]


def fit(source, dest, max_bytes, start=None, length=None):
    """Write `dest` (one file, or dest-part1.mp4 … when needed) under max_bytes; returns the files."""
    ffmpeg = tool("ffmpeg")
    source = Path(source)
    if start is None and source.stat().st_size <= max_bytes and source.suffix == ".mp4":
        shutil.copy2(source, dest)
        return [dest]
    if not ffmpeg:
        raise RecorderError("ffmpeg is needed to cut or shrink the clip: " + INSTALL["ffmpeg"][platform_key()])
    seconds = length or probe_seconds(source) or 60
    kbps = max_bytes * 8 * 0.9 / seconds / 1000
    pieces = 1 if kbps >= MIN_SHARE_KBPS else math.ceil(MIN_SHARE_KBPS / kbps)
    piece = seconds / pieces
    rate = min(int(max_bytes * 8 * 0.9 / piece / 1000), 1500)
    made = []
    for number in range(pieces):
        target = dest if pieces == 1 else dest.with_name(f"{dest.stem}-part{number + 1}{dest.suffix}")
        begin = (start or 0) + number * piece
        cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{begin:.2f}", "-i", str(source),
               "-t", f"{piece:.2f}", "-an", "-vf", f"scale=-2:'min({HEIGHT},ih)'", "-c:v", "libx264",
               "-preset", "veryfast", "-b:v", f"{rate}k", "-maxrate", f"{rate}k", "-bufsize", f"{rate * 2}k",
               "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(target)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RecorderError(f"Making {target.name} failed: {result.stderr.strip()[-300:]}")
        made.append(target)
    return made


# ---------- commands ----------

def recorded_so_far(state):
    total = sum(p.get("seconds", 0) for c in state["clips"] if c["name"] == "session" for p in c["parts"])
    if state.get("active") and state["mode"] == "full":
        total += now() - state["active"]["started"]
    return total


def clip_named(state, name):
    for clip in state["clips"]:
        if clip["name"] == name:
            return clip
    clip = {"name": name, "parts": [], "files": []}
    state["clips"].append(clip)
    return clip


def finish_active(state):
    active = state.pop("active", None)
    if active:
        clip_named(state, active.pop("clip"))["parts"].append(stop_part(state, active))


def begin_active(folder, state, name):
    if state.get("paused") or state.get("active"):
        return
    part = start_part(folder, state, clip_named(state, name))
    part["clip"] = name
    state["active"] = part


def cmd_check(args):
    key = platform_key()
    lines, ok = [], True
    need = {"android": ["scrcpy|adb"], "ios-sim": ["xcrun"], "screen": ["ffmpeg"]}
    targets = [args.target] if args.target else list(need)
    if tool("ffmpeg"):
        lines.append("ffmpeg: found (compression and sharing work)")
    else:
        ok = False
        lines.append(f"ffmpeg: MISSING. Clips cannot be compressed or shared in parts. Install: {INSTALL['ffmpeg'][key]}")
    for target in targets:
        if target == "android":
            if tool("scrcpy"):
                lines.append("android: scrcpy found (no time limit)")
            elif adb():
                lines.append(f"android: adb only (3-minute pieces, joined later). Better: {INSTALL['scrcpy'][key]}")
            else:
                ok = False
                lines.append(f"android: MISSING scrcpy and adb. Install: {INSTALL['scrcpy'][key]}")
        elif target == "ios-sim":
            good = key == "darwin" and tool("xcrun")
            ok = ok and bool(good)
            lines.append("ios-sim: xcrun found" if good else "ios-sim: macOS with Xcode only")
        elif target == "screen":
            if key == "darwin":
                lines.append("screen: macOS asks once for the Screen Recording permission for the app running "
                             "this (System Settings > Privacy & Security > Screen Recording)")
            elif key == "linux" and not os.environ.get("DISPLAY"):
                lines.append("screen: no X display (DISPLAY is empty); Wayland desktops need an X session")
    print("\n".join(lines))
    return 0 if ok else 1


def cmd_begin(args):
    folder = Path(args.dir)
    if (folder / STATE).exists() and load(folder).get("ended") is None:
        raise RecorderError(f"A recording is already running in {folder}; run `end` first.")
    if args.root:
        clean(Path(args.root), args.days, quiet=True)
    if args.target == "screen" and not args.region:
        raise RecorderError("--target screen needs --region X,Y,W,H (the App Live window) and --scale")
    folder.mkdir(parents=True, exist_ok=True)
    state = {"mode": args.mode, "target": args.target, "device": args.device, "keep": args.keep,
             "days": args.days, "region": args.region.split(",") if args.region else None, "scale": args.scale,
             "screen": args.screen, "began": now(), "ended": None, "clips": [], "chapters": [], "paused": False}
    if args.mode == "full":
        begin_active(folder, state, "session")
    save(folder, state)
    print(f"Recording ({args.mode}) begun in {folder}" + (": the session is recording" if args.mode == "full" else
                                                          ": a clip starts at each case-start"))
    return 0


def cmd_case_start(args):
    state = load(args.dir)
    if state["mode"] == "full":
        state["chapters"].append({"case": args.case, "start": round(recorded_so_far(state), 1)})
    else:
        finish_active(state)
        state["current"] = args.case
        begin_active(args.dir, state, args.case)
    save(args.dir, state)
    print(f"{args.case}: recording" + (" (paused)" if state.get("paused") else ""))
    return 0


def cmd_case_end(args):
    state = load(args.dir)
    if state["mode"] == "full":
        for chapter in reversed(state["chapters"]):
            if chapter["case"] == args.case and "end" not in chapter:
                chapter.update(end=round(recorded_so_far(state), 1), result=args.result)
                break
        save(args.dir, state)
        print(f"{args.case}: chapter closed ({args.result})")
        return 0
    finish_active(state)
    state.pop("current", None)
    clip = clip_named(state, args.case)
    clip["result"] = args.result
    raw = [f for p in clip["parts"] for f in p["files"]]
    if state["keep"] == "failed" and args.result.lower() == "passed":
        for path in raw:
            Path(path).unlink(missing_ok=True)
        clip["files"], clip["dropped"] = [], True
        message = "passed, clip not kept (failed-only)"
    else:
        clip["files"] = compress(raw, Path(args.dir) / f"{safe(args.case)}.mp4")
        message = "clip saved: " + ", ".join(f"{Path(f).name} ({Path(f).stat().st_size / 1e6:.1f} MB)"
                                             for f in clip["files"])
    for part in clip["parts"]:
        part["files"] = []
    save(args.dir, state)
    print(f"{args.case}: {message}")
    return 0


def cmd_pause(args):
    state = load(args.dir)
    finish_active(state)
    state["paused"] = True
    save(args.dir, state)
    print("Recording paused")
    return 0


def cmd_resume(args):
    state = load(args.dir)
    state["paused"] = False
    if getattr(args, "region", None):  # the App Live window moved or was resized
        state["region"], state["scale"] = args.region.split(","), args.scale or state.get("scale")
    name = "session" if state["mode"] == "full" else state.get("current")
    if name:
        begin_active(args.dir, state, name)
    save(args.dir, state)
    print("Recording resumed" if name else "Recording will start at the next case")
    return 0


def cmd_end(args):
    folder = Path(args.dir)
    state = load(folder)
    finish_active(state)
    if state["mode"] == "full":
        clip = clip_named(state, "session")
        clip["files"] = compress([f for p in clip["parts"] for f in p["files"]], folder / "session.mp4")
        for part in clip["parts"]:
            part["files"] = []
    elif state.get("current"):
        args.case, args.result = state["current"], "Not run"
        save(folder, state)
        cmd_case_end(args)
        state = load(folder)
    state["ended"] = now()
    shutil.rmtree(folder / ".raw", ignore_errors=True)
    save(folder, state)
    write_index(folder, state)
    print((folder / INDEX).read_text(encoding="utf-8"))
    return 0


def write_index(folder, state):
    when = dt.datetime.fromtimestamp(state["began"]).strftime("%Y-%m-%d %H:%M")
    lines = [f"# Recordings ({state['mode']}, {state['target']}, {when})", "",
             f"Deleted after {state['days']} days unless kept (`session_recorder.py keep`). Recording pauses while "
             "login values are typed.", ""]
    for clip in state["clips"]:
        for path in clip["files"]:
            lines.append(f"- `{Path(path).name}` {clip.get('result', '')} ({Path(path).stat().st_size / 1e6:.1f} MB)"
                         .replace("  ", " "))
        if clip.get("dropped"):
            lines.append(f"- {clip['name']}: Passed, not kept (failed-only)")
    if state["chapters"]:
        lines += ["", "Cases in session.mp4:", ""]
        lines += [f"- {stamp(c['start'])}–{stamp(c.get('end', c['start']))} {c['case']} {c.get('result', '')}".rstrip()
                  for c in state["chapters"]]
    (folder / INDEX).write_text("\n".join(lines) + "\n", encoding="utf-8")


def cmd_keep(args):
    state = load(args.dir)
    name = "session" if state["mode"] == "full" else args.case
    clip_named(state, name)["kept"] = True
    save(args.dir, state)
    print(f"{name}: kept (not cleaned)")
    return 0


def cmd_share(args):
    folder, out = Path(args.dir), Path(args.to)
    out.mkdir(parents=True, exist_ok=True)
    state = load(folder)
    max_bytes = int(args.max_mb * 1024 * 1024)
    made = []
    if state["mode"] == "full":
        session = clip_named(state, "session")["files"]
        if not session:
            raise RecorderError("The session has no video yet (run `end` first).")
        if args.case:
            chapter = next((c for c in reversed(state["chapters"]) if c["case"] == args.case), None)
            if not chapter:
                raise RecorderError(f"{args.case} is not in this session")
            start, stop = chapter["start"], chapter.get("end") or chapter["start"] + 60
            made = fit(session[0], out / f"{safe(args.case)}.mp4", max_bytes, start, max(stop - start, 1))
        else:
            made = fit(session[0], out / "session.mp4", max_bytes)
    else:
        names = [args.case] if args.case else [c["name"] for c in state["clips"] if c["files"]]
        for name in names:
            clip = clip_named(state, name)
            if not clip["files"]:
                raise RecorderError(f"{name} has no clip" + (" (it passed and only failed clips were kept)"
                                                              if clip.get("dropped") else ""))
            made += fit(clip["files"][0], out / f"{safe(name)}.mp4", max_bytes)
    print("\n".join(f"{p} ({p.stat().st_size / 1e6:.1f} MB)" for p in map(Path, made)))
    return 0


def clean(root, days, quiet=False):
    freed, cutoff = 0, now() - days * 86400
    for path in Path(root).rglob(STATE):
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not state.get("ended") or state["ended"] > cutoff:
            continue
        changed = False
        for clip in state["clips"]:
            if clip.get("kept"):
                continue
            for name in clip["files"]:
                file = Path(name)
                if file.exists():
                    freed += file.stat().st_size
                    file.unlink()
            if clip["files"]:
                clip["files"], clip["cleaned"], changed = [], True, True
        if changed:
            path.write_text(json.dumps(state, indent=2), encoding="utf-8")
            write_index(path.parent, state)
    if not quiet or freed:
        print(f"Cleaned recordings older than {days} days: {freed / 1e6:.1f} MB freed")
    return freed


def cmd_clean(args):
    clean(Path(args.root), args.days)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("check")
    p.add_argument("--target", choices=["android", "ios-sim", "screen"])
    p = sub.add_parser("begin")
    p.add_argument("--dir", required=True)
    p.add_argument("--mode", choices=["full", "case"], required=True)
    p.add_argument("--target", choices=["android", "ios-sim", "screen"], required=True)
    p.add_argument("--device")
    p.add_argument("--region")
    p.add_argument("--scale", type=float, default=1.0)
    p.add_argument("--screen", type=int, default=0)
    p.add_argument("--keep", choices=["all", "failed"], default="all")
    p.add_argument("--days", type=int, default=KEEP_DAYS)
    p.add_argument("--root")
    for name in ("case-start", "case-end", "keep"):
        p = sub.add_parser(name)
        p.add_argument("--dir", required=True)
        p.add_argument("--case", required=name != "keep")
        if name == "case-end":
            p.add_argument("--result", required=True)
    for name in ("pause", "resume", "end"):
        p = sub.add_parser(name)
        p.add_argument("--dir", required=True)
        if name == "resume":
            p.add_argument("--region")
            p.add_argument("--scale", type=float)
    p = sub.add_parser("share")
    p.add_argument("--dir", required=True)
    p.add_argument("--case")
    p.add_argument("--to", required=True)
    p.add_argument("--max-mb", type=float, default=SHARE_MB)
    p = sub.add_parser("clean")
    p.add_argument("--root", required=True)
    p.add_argument("--days", type=int, default=KEEP_DAYS)
    p = sub.add_parser("_adb-loop")
    p.add_argument("--base", required=True)
    p.add_argument("--device")
    args = parser.parse_args(argv)
    if args.command == "_adb-loop":
        adb_loop(args.base, args.device)
        return 0
    handler = {"check": cmd_check, "begin": cmd_begin, "case-start": cmd_case_start, "case-end": cmd_case_end,
               "pause": cmd_pause, "resume": cmd_resume, "end": cmd_end, "keep": cmd_keep, "share": cmd_share,
               "clean": cmd_clean}[args.command]
    try:
        return handler(args)
    except RecorderError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
