#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  source ".env"
  set +a
fi

missing=0
for key in LINEAR_API_KEY SLACK_BOT_TOKEN DEV_SMOKE_CHANNEL_ID; do
  if [ -z "${!key:-}" ]; then
    echo "Missing ${key}."
    missing=1
  fi
done

if [ "${missing}" -ne 0 ]; then
  echo
  echo "Update .env first. See .env.example for the exact names."
  exit 1
fi

export AUDIT_MODE="${AUDIT_MODE:-dev-smoke}"
export AUDIT_OUT_DIR="${AUDIT_OUT_DIR:-results}"
export POST_TO_SLACK=true

python3 src/post_weekly_audit.py --post
