#!/bin/sh
# Create (once) the Python environment the qa-browserstack-round scripts need, then print its python path.
VENV="${HOME}/.cache/qa-framework/qa-tools-venv"
if ! "$VENV/bin/python" -c "import openpyxl" >/dev/null 2>&1; then
  python3 -m venv "$VENV" >&2 && "$VENV/bin/pip" -q install openpyxl >&2 || exit 1
fi
echo "$VENV/bin/python"
