#!/bin/bash
# SessionStart hook (workspace-brain): shows what changed since CONTEXT.md and BRAIN.md were last
# written, and when the brain was last trained, so a new session can't miss unrecorded work.
# Prints no secrets. Always exits 0.
#
# Optional config: <workspace>/.claude/brain.conf (bash syntax), for example:
#   REPOS=("$HOME/PycharmProjects/TestForge")              # other git repos to report on
#   LOGIC_PATHS=("CLAUDE.md" "conventions" "$HOME/.claude/agents")  # relative to the workspace or absolute
#   EXCLUDE=("maestro/build" "uploads")                    # skipped in the change list
#   STALE_DAYS=1                                           # suggest training after this many days

WS="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
CTX="$WS/CONTEXT.md"
# In a repo that already tracks CONTEXT.md, the local live status is CONTEXT.local.md.
[ -f "$WS/CONTEXT.local.md" ] && CTX="$WS/CONTEXT.local.md"
CN=$(basename "$CTX")
BRAIN="$WS/BRAIN.md"
REPOS=()
LOGIC_PATHS=("CLAUDE.md" "AGENTS.md")
EXCLUDE=()
STALE_DAYS=1
MAX=40
[ -f "$WS/.claude/brain.conf" ] && . "$WS/.claude/brain.conf"

# The workspace itself is a git repo? Report on it too.
[ -d "$WS/.git" ] && REPOS=("$WS" "${REPOS[@]}")

mtime() { stat -f '%Sm' -t '%Y-%m-%d %H:%M' "$1" 2>/dev/null || date -r "$1" '+%Y-%m-%d %H:%M' 2>/dev/null; }

echo "=== Session start check ($(basename "$WS")) ==="

# 1. Files changed after CONTEXT.md (screenshots, build output and VCS folders skipped).
if [ ! -f "$CTX" ]; then
  echo "$CN is missing. Run /workspace-brain setup."
  changed=""
else
  echo "$CN last written: $(mtime "$CTX")"
  prune=(-path '*/.git' -o -path '*/node_modules' -o -path '*/.venv' -o -path '*/__pycache__' -o -path '*/.claude/hooks')
  for e in "${EXCLUDE[@]}"; do prune+=(-o -path "$WS/$e"); done
  changed=$(find "$WS" \( "${prune[@]}" \) -prune -o -type f -newer "$CTX" \
    -not -path "$WS/.claude/settings*" -not -name '*.png' -not -name '*.jpg' -not -name '*.jpeg' \
    -not -name '*.mp4' -not -name '.DS_Store' -not -name '*.log' -print 2>/dev/null)
  shots=$(find "$WS" \( -path '*/.git' -o -path '*/node_modules' \) -prune -o -type f -newer "$CTX" \
    \( -name '*.png' -o -name '*.jpg' \) -print 2>/dev/null | wc -l | tr -d ' ')
  if [ -n "$changed" ]; then
    n=$(printf '%s\n' "$changed" | wc -l | tr -d ' ')
    echo "WARNING: $n file(s) changed after $CN was written. $CN may be stale:"
    printf '%s\n' "$changed" | sed "s|$HOME|~|" | head -n "$MAX"
    [ "$n" -gt "$MAX" ] && echo "... and $((n - MAX)) more"
  fi
  [ "${shots:-0}" -gt 0 ] && echo "Also $shots new screenshot(s)."
fi

# 2. BRAIN.md: last written, last trained, logic files changed after it.
brain_stale=""
if [ ! -f "$BRAIN" ]; then
  echo "BRAIN.md is missing. Run /workspace-brain setup."
else
  trained=$(grep -m1 -oE 'Last trained: [0-9]{4}-[0-9]{2}-[0-9]{2}' "$BRAIN" | cut -d' ' -f3)
  echo "BRAIN.md last written: $(mtime "$BRAIN")${trained:+, last trained $trained}"
  paths=()
  for p in "${LOGIC_PATHS[@]}"; do
    case "$p" in /*) paths+=("$p") ;; *) paths+=("$WS/$p") ;; esac
  done
  brain_stale=$(find "${paths[@]}" -type f -newer "$BRAIN" -not -name '.DS_Store' \
    -not -path '*/.venv/*' -not -path '*/__pycache__/*' -not -path '*/node_modules/*' 2>/dev/null | head -n 15)
  if [ -n "$brain_stale" ]; then
    echo "NOTE: logic files changed after BRAIN.md. Check that BRAIN.md still describes them:"
    printf '%s\n' "$brain_stale" | sed "s|$HOME|~|"
  fi
  if [ -n "$trained" ] && [ -f "$CTX" ]; then
    age=$(( ( $(date +%s) - $(date -j -f '%Y-%m-%d' "$trained" +%s 2>/dev/null || date -d "$trained" +%s 2>/dev/null || date +%s) ) / 86400 ))
    if [ "$age" -ge "$STALE_DAYS" ] && [ "$CTX" -nt "$BRAIN" ]; then
      echo "TRAIN: BRAIN.md was last trained $age day(s) ago and $CN has newer work. Suggest /workspace-brain learn."
    fi
  elif [ -z "$trained" ]; then
    echo "TRAIN: BRAIN.md has no 'Last trained:' line. Suggest /workspace-brain learn."
  fi
fi

# 3. Git repos: branch, last commit, uncommitted changes.
for r in "${REPOS[@]}"; do
  [ -d "$r/.git" ] || continue
  st=$(git -C "$r" status --short 2>/dev/null)
  echo "--- $(basename "$r") ($(git -C "$r" rev-parse --abbrev-ref HEAD 2>/dev/null)): last commit $(git -C "$r" log -1 --format='%h %cd %s' --date=format:'%Y-%m-%d %H:%M' 2>/dev/null)"
  if [ -n "$st" ]; then
    echo "Uncommitted changes:"
    printf '%s\n' "$st" | head -n 20
  fi
done

if [ -n "$changed" ] || [ -n "$brain_stale" ]; then
  echo "ACTION: before naming a next step, reconcile these changes with $CN/BRAIN.md and tell the user what is missing."
fi
exit 0
