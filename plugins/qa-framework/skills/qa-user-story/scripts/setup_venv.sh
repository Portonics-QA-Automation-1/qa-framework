#!/bin/sh
# Create (once) the Python environment the qa-user-story scripts need, then print its python path.
VENV="${HOME}/.cache/qa-framework/user-story-venv"
if ! "$VENV/bin/python" -c "import openpyxl, PIL, docx" >/dev/null 2>&1; then
  python3 -m venv "$VENV" >&2 && "$VENV/bin/pip" -q install openpyxl pillow python-docx >&2 || exit 1
fi
echo "$VENV/bin/python"
