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

out_dir="${DAILY_STANDUP_OUT_DIR:-results/daily-standup-memory}"
while [ "$#" -gt 0 ]; do
  case "$1" in
    --out-dir)
      shift
      out_dir="${1:-${out_dir}}"
      ;;
    --out-dir=*)
      out_dir="${1#*=}"
      ;;
  esac
  shift || true
done

echo
echo "Daily Standup Memory summary:"
echo "$(pwd)/${out_dir}/summary.md"
