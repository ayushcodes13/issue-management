#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
label="com.bynd.daily-standup-memory"
plist_path="${HOME}/Library/LaunchAgents/${label}.plist"
logs_dir="${repo_dir}/logs"

mkdir -p "${logs_dir}" "${HOME}/Library/LaunchAgents"

cat > "${plist_path}" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>${label}</string>

    <key>ProgramArguments</key>
    <array>
      <string>/bin/zsh</string>
      <string>-lc</string>
      <string>cd "${repo_dir}" &amp;&amp; ./run_daily_standup_auto.sh</string>
    </array>

    <key>StartCalendarInterval</key>
    <array>
      <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>10</integer><key>Minute</key><integer>30</integer></dict>
      <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>10</integer><key>Minute</key><integer>30</integer></dict>
      <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>10</integer><key>Minute</key><integer>30</integer></dict>
      <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>10</integer><key>Minute</key><integer>30</integer></dict>
      <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>10</integer><key>Minute</key><integer>30</integer></dict>
    </array>

    <key>StandardOutPath</key>
    <string>${logs_dir}/daily-standup-memory.out.log</string>

    <key>StandardErrorPath</key>
    <string>${logs_dir}/daily-standup-memory.err.log</string>

    <key>RunAtLoad</key>
    <false/>
  </dict>
</plist>
PLIST

launchctl unload "${plist_path}" >/dev/null 2>&1 || true
launchctl load "${plist_path}"

echo "Installed ${label}"
echo "Plist: ${plist_path}"
echo "Logs: ${logs_dir}/daily-standup-memory.out.log and .err.log"
echo
echo "Manual trigger:"
echo "launchctl start ${label}"
echo
echo "Disable:"
echo "launchctl unload ${plist_path}"
