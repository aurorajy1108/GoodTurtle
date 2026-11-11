#!/usr/bin/env bash
# Run in the terminal that already exported DEEPSEEK_API_KEY.
set -euo pipefail
repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"
: "${DEEPSEEK_API_KEY:?Export DEEPSEEK_API_KEY in this terminal first}"
out="${1:-runs/api/20261111_deepseek_set1_raw_session_once}"
if [[ -e "$out" || -e "$out.launcher.log" || -e "$out.pid" ]]; then
  echo 'Output/log/PID exists. Inspect it before choosing a new path.' >&2
  exit 1
fi
mkdir -p "$(dirname "$out")"
nohup python3 scripts/run_set1_verified.py --mode run --out "$out" \
  > "$out.launcher.log" 2>&1 < /dev/null &
run_pid=$!
echo "$run_pid" > "$out.pid"
echo "Launcher PID: $run_pid"
echo "Output: $out"
echo "Log: $out.launcher.log"
echo '20 host diagnostic calls first; CL starts only if all pass.'
echo 'CL: A=15/14/28, B=13; direct/session/answer_only once each. 12 fresh games; no MAS.'
echo 'session continues the original A Player messages, reveals the full A answer, then resets B to 100 submissions.'
echo 'Check status.json and logs to confirm startup. The PID alone does not confirm API access.'
