#!/usr/bin/env bash
set -euo pipefail

skill_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repo_dir="$(cd "${skill_dir}/../.." && pwd)"

cd "${repo_dir}"
./post_dev_smoke.sh
