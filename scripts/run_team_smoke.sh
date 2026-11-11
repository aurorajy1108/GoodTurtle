#!/usr/bin/env bash
# Focused pilot: positive-source CL only, or one repeat of each MAS condition.
set -euo pipefail
repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"
if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo 'Usage: bash scripts/run_team_smoke.sh RUNNER TASKS [OUT]' >&2
  exit 2
fi
: "${DEEPSEEK_API_KEY:?Export DEEPSEEK_API_KEY in this terminal first}"
runner="$1"
tasks="$2"
out="${3:-runs/api/smoke_${runner}_$(date +%Y%m%d_%H%M%S)}"
exec python3 scripts/team_campaign.py start --preset smoke --runner "$runner" --tasks "$tasks" \
  --workers 1 --mode run --out "$out"
