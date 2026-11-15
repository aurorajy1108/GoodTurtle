#!/usr/bin/env bash
# Run from the terminal that already exports DEEPSEEK_API_KEY.
set -euo pipefail
repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"
if [[ -z "${DEEPSEEK_API_KEY:-}" ]]; then
  echo 'Export DEEPSEEK_API_KEY in this terminal before starting.' >&2
  exit 1
fi
out="${1:-runs/api/deepseek_set1_ts038_nothinking_once}"
if [[ -e "$out" || -e "$out.launcher.log" || -e "$out.pid" ]]; then
  echo 'Output/log/PID already exists. Check the previous run; use a new output path for a new batch.' >&2
  exit 1
fi
python3 - <<'PY'
import json
from pathlib import Path
c=json.loads(Path('configs/loop.deepseek.json').read_text())
assert c['host']['model']==c['grader']['model']=='deepseek-v4-pro'
assert c['player']['model']=='deepseek-flash'
assert c['player']['extra_body']['thinking']['type']=='disabled'
assert 'reasoning_effort' not in c['player']['extra_body']
print('Verified: Pro host/grader; Flash player/default partner with thinking disabled.')
PY
mkdir -p "$(dirname "$out")"
nohup python3 scripts/study_20261102.py \
  --config configs/loop.deepseek.json \
  --suite all --sets 1 --directions primary --source-policy fixed \
  --source-puzzles TS015,TS014,TS028 \
  --team-puzzles TS038 --strategies solo,free_dialogue --repeat 1 \
  --dialogue-roles complementary --dialogue-scheduling adaptive \
  --dialogue-max-discussion 4 --dialogue-start A \
  --on-error stop --mode run --out "$out" \
  > "$out.launcher.log" 2>&1 < /dev/null &
pilot_pid=$!
echo "$pilot_pid" > "$out.pid"
echo "Launcher PID: $pilot_pid"
echo "Output: $out"
echo "Log: $out.launcher.log"
echo '12 CL games (A=15/14/28, B=13), then TS038 solo/free_dialogue once each; 14 total.'
echo 'Check status.json and API logs to confirm successful startup.'
