#!/usr/bin/env python3
"""Upload an APK or IPA to BrowserStack App Live, or check the App Live API key.

  bs_upload.py check
  bs_upload.py upload <path to .apk or .ipa> [--custom-id <label>]

Reads BROWSERSTACK_USERNAME and BROWSERSTACK_ACCESS_KEY from ~/.config/browserstack.env
(or the file in $BROWSERSTACK_ENV). The values are passed to curl through a config file on
stdin, so they never show in the process list or in the output.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

API = "https://api-cloud.browserstack.com/app-live"


def creds():
    path = Path(os.environ.get("BROWSERSTACK_ENV", "~/.config/browserstack.env")).expanduser()
    if not path.exists():
        sys.exit(f"{path} not found: fill in BROWSERSTACK_USERNAME and BROWSERSTACK_ACCESS_KEY")
    vals = {}
    for line in path.read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            vals[k.strip()] = v.strip().strip('"').strip("'")
    user, key = vals.get("BROWSERSTACK_USERNAME"), vals.get("BROWSERSTACK_ACCESS_KEY")
    if not user or not key:
        sys.exit(f"{path}: BROWSERSTACK_USERNAME or BROWSERSTACK_ACCESS_KEY is empty")
    return user, key


def curl(args):
    user, key = creds()
    cfg = f'user = "{user}:{key}"\n'
    res = subprocess.run(["curl", "-sS", "-K", "-", "-w", "\n%{http_code}"] + args,
                         input=cfg, capture_output=True, text=True)
    body, _, code = res.stdout.rpartition("\n")
    return code, body, res.stderr


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("check", "upload"):
        sys.exit(__doc__)
    if sys.argv[1] == "check":
        code, _, err = curl([f"{API}/recent_apps"])
        print(f"HTTP {code}" + (" - key works and has App Live" if code == "200" else f" {err.strip()}"))
        sys.exit(0 if code == "200" else 1)

    app = Path(sys.argv[2]).expanduser()
    if app.suffix.lower() not in (".apk", ".aab", ".ipa") or not app.is_file():
        sys.exit(f"not an .apk/.aab/.ipa file: {app}")
    args = ["-X", "POST", f"{API}/upload", "-F", f"file=@{app}"]
    if "--custom-id" in sys.argv:
        args += ["-F", f"custom_id={sys.argv[sys.argv.index('--custom-id') + 1]}"]
    code, body, err = curl(args)
    if code != "200":
        sys.exit(f"upload failed: HTTP {code} {body.strip()[:300]} {err.strip()}")
    print(json.dumps(json.loads(body)))


if __name__ == "__main__":
    main()
