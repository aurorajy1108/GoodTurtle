#!/usr/bin/env bash
# Each selected slot: two repeats; bounded concurrency across independent slots.
set -euo pipefail
repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"
if [[ $# -lt 2 || $# -gt 4 ]]; then
  echo 'Usage: bash scripts/run_team_batch.sh RUNNER TASKS [WORKERS=2] [OUT]' >&2
  exit 2
fi
: "${DEEPSEEK_API_KEY:?Export DEEPSEEK_API_KEY in this terminal first}"
runner="$1"
tasks="$2"
workers="${3:-2}"
out="${4:-runs/api/full_${runner}_$(date +%Y%m%d_%H%M%S)}"
exec python3 scripts/team_campaign.py start --preset full --runner "$runner" --tasks "$tasks" \
  --workers "$workers" --mode run --out "$out"
