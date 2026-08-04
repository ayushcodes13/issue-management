#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
if [[ -x ".venv/bin/python" ]]; then
  .venv/bin/python scripts/send_dms.py "$@"
else
  python3 scripts/send_dms.py "$@"
fi
