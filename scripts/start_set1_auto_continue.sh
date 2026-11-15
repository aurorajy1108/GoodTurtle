#!/usr/bin/env bash
set -euo pipefail
repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"
: "${DEEPSEEK_API_KEY:?Export DEEPSEEK_API_KEY in this terminal first}"
out="${1:-runs/api/20261111_set1_auto_continue_v2}"
source_study="${2:-runs/api/20261111_set1_auto_continue}"
if [[ -e "$out" || -e "$out.launcher.log" || -e "$out.pid" ]]; then
  echo 'Output/log/PID exists; inspect the existing supervisor before launching another.' >&2
  exit 1
fi
mkdir -p "$(dirname "$out")"
nohup python3 scripts/auto_continue.py \
  --from-study "$source_study" \
  --out "$out" --mode run --max-continuations 3 \
  > "$out.launcher.log" 2>&1 < /dev/null &
supervisor_pid=$!
echo "$supervisor_pid" > "$out.pid"
echo "Supervisor PID: $supervisor_pid"
echo "Output: $out"
echo "Log: $out.launcher.log"
echo 'Selects the latest durable stopped checkpoint; preserves completed games, answered questions and passed Host diagnostics.'
echo 'Fixed-position local extraction, then bounded Codex formatting if needed; no hidden answers or completed-game reruns.'
