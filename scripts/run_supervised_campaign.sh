#!/usr/bin/env bash
# Supervise one existing stopped campaign; do not launch a duplicate fresh batch.
set -euo pipefail
set +x
repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"
if [[ $# -ne 2 ]]; then
  echo 'Usage: bash scripts/run_supervised_campaign.sh STOPPED_CAMPAIGN_OR_SUPERVISOR NEW_OUT' >&2
  exit 2
fi
if [[ -z "${DEEPSEEK_API_KEY:-}" && -f .env.local ]]; then
  source .env.local
fi
: "${DEEPSEEK_API_KEY:?Configure the ignored .env.local before supervision}"
# Keep an awake Mac from idling to sleep while this supervisor runs. This does
# not wake a closed/offline machine or prevent deliberate shutdown.
if [[ -x /usr/bin/caffeinate ]]; then
  /usr/bin/caffeinate -i -w "$$" &
fi
exec python3.11 scripts/supervise_campaign.py --campaign "$1" --out "$2" \
  --interval 30 --cooldown 60 --max-recoveries 3 --stall-seconds 2700 --notify macos
