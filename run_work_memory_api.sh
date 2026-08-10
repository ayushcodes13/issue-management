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

for arg in "$@"; do
  if [ "${arg}" = "--help" ] || [ "${arg}" = "-h" ]; then
    "${python_bin}" scripts/work_memory_api.py "$@"
    exit 0
  fi
done

missing=0
for key in GRANOLA_API_KEY LINEAR_API_KEY AZURE_OPENAI_API_KEY; do
  if [ -z "${!key:-}" ]; then
    echo "Missing ${key}."
    missing=1
  fi
done

if [ "${missing}" -ne 0 ]; then
  echo
  echo "The API runner is the scheduled/production path and requires real API secrets."
  echo "Update .env locally or GitHub Actions secrets before running it."
  exit 1
fi

"${python_bin}" scripts/work_memory_api.py "$@"

echo
echo "Work Memory API summary:"
echo "$(pwd)/${WORK_MEMORY_OUT_DIR:-results/work-memory}/summary.md"
