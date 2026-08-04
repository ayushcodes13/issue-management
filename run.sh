#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  source ".env"
  set +a
fi

if [ -z "${LINEAR_API_KEY:-}" ]; then
  echo "Missing LINEAR_API_KEY."
  echo "Create .env from .env.example, or run:"
  echo "export LINEAR_API_KEY"
  exit 1
fi

export AUDIT_MODE="${AUDIT_MODE:-manual-preview}"
export AUDIT_OUT_DIR="${AUDIT_OUT_DIR:-results}"

python_bin="${PYTHON_BIN:-python3}"
if [ -x ".venv/bin/python" ]; then
  python_bin=".venv/bin/python"
fi

"${python_bin}" scripts/review.py

echo
echo "Markdown report:"
echo "$(pwd)/${AUDIT_OUT_DIR}/summary.md"
