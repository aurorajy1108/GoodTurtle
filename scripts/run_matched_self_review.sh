#!/usr/bin/env bash
# Run an already prepared immutable control batch, with the local ignored key.
set -euo pipefail
set +x
task_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$task_root"
if [[ $# -ne 1 ]]; then
  echo 'Usage: bash scripts/run_matched_self_review.sh PREPARED_OUTPUT_DIRECTORY' >&2
  exit 2
fi
if [[ -z "${DEEPSEEK_API_KEY:-}" && -f .env.local ]]; then
  source .env.local
fi
if [[ -z "${DEEPSEEK_API_KEY:-}" ]]; then
  echo 'Set DEEPSEEK_API_KEY or save export DEEPSEEK_API_KEY=... in ignored .env.local.' >&2
  exit 2
fi
if [[ "$(uname -s)" == Darwin ]]; then
  caffeinate -i -w "$$" &
fi
exec python3.11 scripts/matched_self_review.py run --out "$1"
