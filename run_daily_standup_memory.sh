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

missing=0
for key in GRANOLA_API_KEY LINEAR_API_KEY AZURE_OPENAI_API_KEY; do
  if [ -z "${!key:-}" ]; then
    echo "Missing ${key}."
    missing=1
  fi
done

if [ "${missing}" -ne 0 ]; then
  echo
  echo "Daily Standup Memory requires Granola, Linear, and Azure OpenAI credentials."
  exit 1
fi

"${python_bin}" scripts/daily_standup_memory.py "$@"

echo
echo "Daily Standup Memory summary:"
echo "$(pwd)/${DAILY_STANDUP_OUT_DIR:-results/daily-standup-memory}/summary.md"
