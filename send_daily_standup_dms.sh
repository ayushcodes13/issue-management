#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  source ".env"
  set +a
fi

python_bin="${PYTHON_BIN:-python3}"
if [ -x ".venv/bin/python" ]; then
  python_bin=".venv/bin/python"
fi

"${python_bin}" scripts/send_daily_standup_dms.py "$@"
