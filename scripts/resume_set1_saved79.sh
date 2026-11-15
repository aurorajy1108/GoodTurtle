#!/usr/bin/env bash
# Continue the saved Set 1 rollout; do not rerun the diagnostic gate or A prefix.
set -euo pipefail
repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"
: "${DEEPSEEK_API_KEY:?Export DEEPSEEK_API_KEY in this terminal first}"
out="${1:-runs/api/20261111_deepseek_set1_v11_json_resume01}"
if [[ -e "$out" || -e "$out.launcher.log" || -e "$out.pid" ]]; then
  echo 'Output/log/PID exists. Inspect that continuation before launching another.' >&2
  exit 1
fi
mkdir -p "$(dirname "$out")"
nohup python3 scripts/resume_study.py \
  --from-study runs/api/20261110_deepseek_set1_v11_once \
  --out "$out" --repair-player-json --mode run \
  > "$out.launcher.log" 2>&1 < /dev/null &
resume_pid=$!
echo "$resume_pid" > "$out.pid"
echo "Launcher PID: $resume_pid"
echo "Output: $out"
echo "Log: $out.launcher.log"
echo 'Reuses the 20 passed Host diagnostics and 78 completed questions.'
echo 'Submits saved question 79 to Host first; Player does not generate it again.'
echo 'Keeps original models/prompts/Host/scoring, current quota and recorded costs; then continues the remaining CL plan.'
echo 'Check status.json and the launcher log; the PID alone does not confirm successful startup.'
