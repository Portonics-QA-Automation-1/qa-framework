#!/usr/bin/env python3
"""List and download Firebase App Distribution builds (Android APK, iOS IPA) with the QA member's Firebase login.

  firebase_builds.py check
  firebase_builds.py apps     --project <id>
  firebase_builds.py list     --project <id> [--app <name or app id>] [--match <text>] [--limit N] [--json]
  firebase_builds.py download --project <id> --app <name or app id> --version <x.y.z[-suffix]> [--build N]
                              [--out <folder>] [--yes]

Access: the QA member runs `firebase login` once on their own computer; it lasts until `firebase logout`.
The script borrows that login through the installed firebase-tools package (npm), so no key or password is
asked, stored or printed. Works on macOS, Windows and Linux (needs Python 3 and Node with firebase-tools
installed by npm, not the standalone binary). Set FIREBASE_TOOLS_DIR if the package is not in `npm root -g`.

--app matches an app id, else the app's display name (exact first, then a case-insensitive part).
`download` without --yes only prints what it would download (file name, size, free disk) and exits 3, so an
agent can show that in the Approve card and run again with --yes after the QA member's yes.
TestFlight builds are not in Firebase: Apple allows no download of a TestFlight build.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

FAD = "https://firebaseappdistribution.googleapis.com/v1"
MGMT = "https://firebase.googleapis.com/v1beta1"
DISK_MARGIN = 500 * 1024 * 1024

TOKEN_JS = """
const ft = process.argv[1];
const {configstore} = require(ft + '/lib/configstore');
const auth = require(ft + '/lib/auth');
const t = configstore.get('tokens');
if (!t || !t.refresh_token) { console.error('NOT_LOGGED_IN'); process.exit(2); }
auth.getAccessToken(t.refresh_token, []).then(a => process.stdout.write(a.access_token))
  .catch(e => { console.error('TOKEN_FAILED ' + e.message); process.exit(2); });
"""


def firebase_tools_dir():
    env = os.environ.get("FIREBASE_TOOLS_DIR")
    if env:
        return Path(env)
    npm = shutil.which("npm")
    if not npm:
        sys.exit("npm not found: install Node.js and then `npm install -g firebase-tools`")
    root = subprocess.run([npm, "root", "-g"], capture_output=True, text=True).stdout.strip()
    path = Path(root) / "firebase-tools"
    if not (path / "lib" / "auth.js").exists():
        sys.exit(f"firebase-tools not found in {root}: run `npm install -g firebase-tools`, "
                 "or set FIREBASE_TOOLS_DIR")
    return path


def access_token():
    node = shutil.which("node")
    if not node:
        sys.exit("node not found: install Node.js")
    res = subprocess.run([node, "-e", TOKEN_JS, str(firebase_tools_dir())], capture_output=True, text=True)
    if res.returncode != 0 or not res.stdout:
        if "NOT_LOGGED_IN" in res.stderr:
            sys.exit("Not signed in to Firebase: the QA member runs `firebase login` once on this computer")
        sys.exit("Firebase login could not be used (expired or revoked?): the QA member runs "
                 "`firebase login --reauth`")
    return res.stdout.strip()


def get(url, token):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            msg = json.load(e).get("error", {}).get("message", "")
        except ValueError:
            msg = ""
        if e.code in (401, 403):
            sys.exit(f"HTTP {e.code}: this Firebase login has no App Distribution access to it ({msg[:150]}). "
                     "Ask the Firebase project owner for the 'Firebase App Distribution Admin' role.")
        sys.exit(f"HTTP {e.code}: {msg[:200]}")


def apps(project, token):
    out = []
    for kind, platform, idkey in (("androidApps", "android", "packageName"), ("iosApps", "ios", "bundleId")):
        data = get(f"{MGMT}/projects/{project}/{kind}?pageSize=100", token)
        for a in data.get("apps", []):
            out.append({"app_id": a["appId"], "name": a.get("displayName", ""), "platform": platform,
                        "id": a.get(idkey, "")})
    return out


def pick_apps(all_apps, query):
    if not query:
        return all_apps
    for key in ("app_id", "name"):
        hit = [a for a in all_apps if a[key].lower() == query.lower()]
        if hit:
            return hit
    hit = [a for a in all_apps if query.lower() in a["name"].lower()]
    if not hit:
        sys.exit(f"No app matches '{query}'. Apps: " + ", ".join(a["name"] for a in all_apps))
    return hit


def releases(app, token, limit):
    number = app["app_id"].split(":")[1]
    url = f"{FAD}/projects/{number}/apps/{app['app_id']}/releases?pageSize={limit}"
    return get(url, token).get("releases", [])


def row(app, r):
    notes = (r.get("releaseNotes", {}).get("text") or "").strip().splitlines()
    return {"app": app["name"], "platform": app["platform"], "app_id": app["app_id"], "id": app["id"],
            "version": r.get("displayVersion"), "build": r.get("buildVersion"), "created": r.get("createTime"),
            "notes": notes[0][:80] if notes else "", "_uri": r.get("binaryDownloadUri")}


def remote_size(uri):
    req = urllib.request.Request(uri, headers={"Range": "bytes=0-0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            total = r.headers.get("Content-Range", "").rpartition("/")[2]
            return int(total) if total.isdigit() else int(r.headers.get("Content-Length") or 0)
    except (urllib.error.URLError, ValueError):
        return 0


def mb(n):
    return f"{n / 1024 / 1024:.1f} MB" if n else "unknown size"


def safe(text):
    return "".join(c if c.isalnum() or c in "._-() " else "_" for c in text).strip()


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("command", choices=["check", "apps", "list", "download"])
    p.add_argument("--project", default=os.environ.get("FIREBASE_PROJECT"))
    p.add_argument("--app")
    p.add_argument("--match", help="only versions containing this text")
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--version")
    p.add_argument("--build")
    p.add_argument("--out", default=str(Path.home() / "Downloads"))
    p.add_argument("--yes", action="store_true", help="really download (after the QA member's yes)")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    token = access_token()
    if a.command == "check":
        print("Firebase login usable" + (f"; project {a.project}: {len(apps(a.project, token))} apps"
                                         if a.project else ""))
        return
    if not a.project:
        sys.exit("--project (or FIREBASE_PROJECT) is required; the workspace conventions name it")
    all_apps = apps(a.project, token)
    if a.command == "apps":
        for x in all_apps:
            print(f"{x['platform']:8} {x['name']:32} {x['id']:36} {x['app_id']}")
        return

    rows = []
    for app in pick_apps(all_apps, a.app):
        limit = 100 if a.command == "download" or a.match else a.limit
        rows += [row(app, r) for r in releases(app, token, limit)]
    if a.match:
        rows = [r for r in rows if a.match.lower() in (r["version"] or "").lower()][:a.limit]

    if a.command == "list":
        if a.json:
            print(json.dumps([{k: v for k, v in r.items() if k != "_uri"} for r in rows], indent=1))
        for r in rows if not a.json else []:
            print(f"{r['platform']:8} {r['app']:28} {r['version']} ({r['build']})  {r['created'][:16]}  {r['notes']}")
        if not rows:
            print("No releases found")
        return

    if not a.app or not a.version:
        sys.exit("download needs --app and --version")
    hit = [r for r in rows if r["version"] == a.version and (not a.build or r["build"] == a.build)]
    if not hit:
        sys.exit(f"No release {a.version}" + (f" ({a.build})" if a.build else "") + " in that app. Newest: "
                 + ", ".join(f"{r['version']} ({r['build']})" for r in rows[:5]))
    if len({r["app_id"] for r in hit}) > 1:
        sys.exit("The version is in several apps; give a more exact --app: "
                 + ", ".join(sorted({r["app"] for r in hit})))
    r = max(hit, key=lambda x: x["created"] or "")
    if len(hit) > 1:
        print(f"{len(hit)} releases match; using the newest. Others: "
              + ", ".join(f"({x['build']}) {x['created'][:10]}" for x in hit if x is not r))
    if not r["_uri"]:
        sys.exit("This login can see the release but gets no download link (tester-only access?)")
    ext = ".apk" if r["platform"] == "android" else ".ipa"
    out_dir = Path(a.out).expanduser()
    target = out_dir / safe(f"{r['app']}-{r['version']}-({r['build']}){ext}")
    size = remote_size(r["_uri"])
    free = shutil.disk_usage(out_dir if out_dir.exists() else Path.home()).free
    print(f"Release: {r['app']} {r['version']} ({r['build']}), {r['created'][:16]}, {mb(size)}")
    print(f"Save as: {target}  (free disk: {mb(free)})")
    if target.exists() and size and target.stat().st_size == size:
        print("Already downloaded: " + str(target))
        return
    if size and free < size + DISK_MARGIN:
        sys.exit("Not enough free disk space for this build")
    if not a.yes:
        print("Not downloaded: run again with --yes after the QA member's yes")
        sys.exit(3)
    out_dir.mkdir(parents=True, exist_ok=True)
    part = target.with_name(target.name + ".part")
    with urllib.request.urlopen(r["_uri"], timeout=120) as resp, open(part, "wb") as f:
        shutil.copyfileobj(resp, f, 1024 * 1024)
    if size and part.stat().st_size != size:
        part.unlink()
        sys.exit("Download incomplete; try again")
    part.replace(target)
    print("Downloaded: " + str(target))


if __name__ == "__main__":
    main()
