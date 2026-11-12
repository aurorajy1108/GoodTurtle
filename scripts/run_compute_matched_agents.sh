#!/usr/bin/env bash
set -euo pipefail
set +x
task_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$task_root"
if [[ $# -ne 1 ]]; then
  echo 'Usage: bash scripts/run_compute_matched_agents.sh PREPARED_OUTPUT_DIRECTORY' >&2
  exit 2
fi
if [[ -z "${DEEPSEEK_API_KEY:-}" && -f .env.local ]]; then source .env.local; fi
: "${DEEPSEEK_API_KEY:?Configure the ignored .env.local first}"
if [[ -x /usr/bin/caffeinate ]]; then /usr/bin/caffeinate -i -w "$$" & fi
exec python3.11 scripts/compute_matched_agents.py run --out "$1"
