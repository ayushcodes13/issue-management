#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

./run_daily_standup_memory.sh "$@"

send_flag="${DAILY_STANDUP_SEND_SLACK_DMS:-false}"
if [ "${send_flag}" != "true" ]; then
  echo
  echo "Daily standup Slack DM sending is disabled."
  echo "Set DAILY_STANDUP_SEND_SLACK_DMS=true only when you want this command to send DMs."
  exit 0
fi

./send_daily_standup_dms.sh --validate-users
./send_daily_standup_dms.sh --send --yes
