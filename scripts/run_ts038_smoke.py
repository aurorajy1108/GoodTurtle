#!/usr/bin/env python3
"""Run TS038 solo/free_dialogue with verified local CA and explicit proxy settings.

Defaults to zero-call dry-run. Credentials stay in the child environment only.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import shlex
import signal
import ssl
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def child_environment(env_file, ca_file, proxy_mode, require_key):
    env = os.environ.copy()
    if require_key and not env.get('DEEPSEEK_API_KEY') and env_file:
        for line in env_file.read_text().splitlines():
            match = re.match(r'^\s*(?:export\s+)?DEEPSEEK_API_KEY\s*=\s*(.*?)\s*$', line)
            if match:
                words = shlex.split(match[1], comments=True)
                if len(words) != 1:
                    raise ValueError('Cannot safely parse DEEPSEEK_API_KEY in env file')
                env['DEEPSEEK_API_KEY'] = words[0]
    if require_key and not env.get('DEEPSEEK_API_KEY'):
        raise ValueError('Export DEEPSEEK_API_KEY or pass --env-file .env')
    # Load the trusted CA bundle now; never disable certificate verification.
    ssl.create_default_context(cafile=str(ca_file))
    env['SSL_CERT_FILE'] = str(ca_file)
    env['TURTLE_DEEPSEEK_PROXY_MODE'] = proxy_mode
    return env


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('dry-run', 'run'), default='dry-run')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--env-file', type=Path)
    parser.add_argument('--ca-file', type=Path, default=Path('/etc/ssl/cert.pem'))
    parser.add_argument('--proxy-mode', choices=('direct', 'system'), default='direct')
    parser.add_argument('--verified-dry-run', type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists():
        parser.error('Output exists; choose a new directory')
    env = child_environment(args.env_file, args.ca_file.resolve(), args.proxy_mode, args.mode == 'run')
    if args.verified_dry_run:
        reference = args.verified_dry_run.resolve()
        plan = json.loads((reference/'study_plan.json').read_text())
        if plan['mode'] != 'dry-run' or plan['planned_games'] != {'team': 2}:
            parser.error('Reference must be a completed TS038 two-game dry-run')
        if json.loads((reference/'status.json').read_text())['status'] != 'completed':
            parser.error('Reference dry-run did not complete')
        expected = json.loads((reference/'snapshot_hashes.json').read_text())
        for name, sha in expected.items():
            if hashlib.sha256((reference/'runtime_snapshot'/name).read_bytes()).hexdigest() != sha:
                parser.error('Reference snapshot hash mismatch')
    provenance = {'purpose': 'TS038 smoke; excluded from formal repeats',
                  'started_at': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
                  'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  'git_status': subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True),
                  'SSL_CERT_FILE': str(args.ca_file.resolve()),
                  'TURTLE_DEEPSEEK_PROXY_MODE': args.proxy_mode,
                  'verified_dry_run': str(args.verified_dry_run) if args.verified_dry_run else None}
    command = [sys.executable, str(ROOT/'scripts/study_20261102.py'), '--suite', 'team',
               '--team-puzzles', 'TS038', '--strategies', 'solo,free_dialogue', '--repeat', '1',
               '--dialogue-roles', 'complementary', '--dialogue-scheduling', 'adaptive',
               '--dialogue-max-discussion', '4', '--dialogue-start', 'A',
               '--config', 'configs/loop.deepseek.json', '--on-error', 'stop',
               '--mode', args.mode, '--out', str(out)]
    child = subprocess.Popen(command, cwd=ROOT, env=env)
    try:
        while child.poll() is None and not (out/'snapshot_hashes.json').exists():
            time.sleep(.1)
        if out.exists():
            (out/'smoke_provenance.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2)+'\n')
        return child.wait()
    except KeyboardInterrupt:
        child.send_signal(signal.SIGINT)
        return child.wait()


if __name__ == '__main__':
    raise SystemExit(main())
