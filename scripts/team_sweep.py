#!/usr/bin/env python3
"""Freeze inputs and run repeated, paired team comparisons with bounded concurrency."""
import argparse
import hashlib
import json
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from turtle_loop.cli import configuration, choose
from turtle_loop.dataset import load_dataset
from turtle_loop.engine import dump
from turtle_loop.experiments import make_plan, stats, write_reports
from turtle_loop.host_context import build_story_context
from turtle_loop.providers import resolve_env, validate_profile
from turtle_loop.dialogue import add_dialogue_arguments, dialogue_settings
from scripts.render_trajectories import render


def snapshot(out, dataset, config, puzzles, partner=None):
    snap = out / 'runtime_snapshot'
    snap.mkdir()
    for name in ('turtle_loop', 'prompts'):
        shutil.copytree(ROOT / name, snap / name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    (snap / 'scripts').mkdir()
    shutil.copy2(ROOT / 'scripts/experiment.py', snap / 'scripts/experiment.py')
    shutil.copy2(ROOT / 'scripts/audit_sweep.py', snap / 'scripts/audit_sweep.py')
    (snap / 'configs').mkdir()
    policy=ROOT/'configs/player_format_repair.json'
    if policy.exists():shutil.copy2(policy,snap/'configs/player_format_repair.json')
    dump(snap / 'configs/run.json', config)
    if partner is not None:
        dump(snap / 'configs/partner.json', partner)
    bindings = json.loads((ROOT / 'configs/host_bindings.json').read_text())
    bindings = {p['id']: bindings[p['id']] for p in puzzles if p['id'] in bindings}
    dump(snap / 'configs/host_bindings.json', bindings)
    for binding in bindings.values():
        for field in ('overlay_pack', 'legacy_pack'):
            if binding.get(field):
                source = (ROOT / binding[field]).resolve()
                relative = source.relative_to(ROOT.resolve())
                destination = snap / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
    (snap / 'data').mkdir(exist_ok=True)
    dump(snap / 'data/dataset.json', {**dataset, 'puzzles': puzzles})
    hashes = {str(p.relative_to(snap)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in snap.rglob('*') if p.is_file()}
    dump(out / 'snapshot_hashes.json', hashes)
    return snap


def summarize(out):
    """Rebuild from disk so a stopped launcher never loses completed results."""
    manifest = json.loads((out / 'sweep.json').read_text())
    rows, blocks = [], []
    for job in manifest['jobs']:
        folder = out / 'batches' / job['puzzle_id']
        plan = folder / 'plan.json'
        if not plan.exists():
            continue
        local_blocks = json.loads(plan.read_text())['blocks']
        blocks.extend(local_blocks)
        for block in local_blocks:
            for condition in block['conditions']:
                game = folder / (block['block'] + '_' + condition)
                if not (game / 'result.json').exists():
                    continue
                result = json.loads((game / 'result.json').read_text())
                if (game / 'superseded.json').exists():
                    result = {**result, 'status': 'superseded', 'success': None}
                rows.append({**result, 'block': block['block'], 'condition': condition,
                             'puzzle_id': block['target'], 'target': block['target'],
                             'repeat': block['repeat'], 'run_dir': str(game.relative_to(out))})
    write_reports(out, rows, blocks, 'team')
    completed = [r for r in rows if r['status'] == 'completed']
    errors = [r for r in rows if r['status'] in ('error', 'interrupted', 'needs_review')]
    expected = manifest['planned_games']
    summary = {'planned_games': expected, 'recorded_games': len(rows),
               'completed_games': len(completed), 'solved_games': sum(r['success'] for r in completed),
               'invalid_games': len(errors), 'running_games': sum(r['status'] == 'running' for r in rows),
               'all_completed': len(completed) == expected,
               'statuses': [{k: r.get(k) for k in ('run_dir', 'status', 'counted_questions',
                                                  'success', 'final_partial_score', 'error')} for r in rows]}
    dump(out / 'progress.json', summary)
    lines = ['# 重复双 agent 实验', '',
             f"完成 {len(completed)}/{expected} 局；完整解出 {summary['solved_games']} 局；异常／待审核 {len(errors)} 局。", '',
             '| 题目 | 条件 | 完成/计划 | 完整解出 | 最终部分分均值 | 样本方差 | 消耗次数均值 | 消耗次数样本方差 |',
             '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    def fmt(x):
        return '—' if x is None else f'{x:.4g}'
    for job in manifest['jobs']:
        for condition in manifest['strategies']:
            local = [r for r in completed if r['puzzle_id'] == job['puzzle_id'] and r['condition'] == condition]
            score = stats([r['final_partial_score'] for r in local if r['final_partial_score'] is not None])
            count = stats([r['counted_questions'] for r in local])
            lines.append(f"| {job['puzzle_id']} | {condition} | {len(local)}/{manifest['repeat']} | "
                         f"{sum(r['success'] for r in local)} | {fmt(score['mean'])} | {fmt(score['sample_variance'])} | "
                         f"{fmt(count['mean'])} | {fmt(count['sample_variance'])} |")
    lines += ['', '错误／不完整提交计一次；成功交卷单列。失败的 100 次是预算消耗，不是成功解题时间。', '',
              '重复次数较少；题目按叙事复杂度预先选择，难度未由独立测量验证。不能把随机重复等同消除偏差。',
              'solo 和 shared_buffer 每步一次 solver 调用；shared_buffer 双方轮流按角色探索，每 N 次完成提交同步问答，同步前仅公开已问问题的文本以避免重复；solo_reflect、discuss、independent 每步三次。相同模型的 discuss 与 solo_reflect 仅调用角色标签不同，不能据此证明两个 agent 优于一个。',
              'independent 的第二份提案看不到第一份提案；合并者可看到双方提案。所有策略仅看当前局公开历史。',
              '比较按题目和重复编号配对，另报告相对 solo_reflect 的调用次数控制对照；token 数仍可能不同。',
              'seed 只控制执行顺序，不控制服务端采样。顺序循环平衡：重复数不是条件数的倍数时各位置不能完全均衡。', '',
              '[完整轨迹](trajectories.html) · [逐局结果](experiment_runs.csv) · [配对差异](contrasts.csv) · [分题统计](condition_summary_by_puzzle.json) · [三调用对照](reflection_contrasts.json)']
    (out / 'results_zh.md').write_text('\n'.join(lines) + '\n')
    render(out, out / 'trajectories.html')
    return summary


def validate_finished(out):
    manifest = json.loads((out / 'sweep.json').read_text())
    expected = {f"batches/{job['puzzle_id']}/{job['puzzle_id']}_r{repeat:02d}_{condition}"
                for job in manifest['jobs'] for repeat in range(1, manifest['repeat'] + 1)
                for condition in manifest['strategies']}
    hashes = json.loads((out / 'snapshot_hashes.json').read_text())
    changed = [name for name, sha in hashes.items()
               if not (out / 'runtime_snapshot' / name).exists()
               or hashlib.sha256((out / 'runtime_snapshot' / name).read_bytes()).hexdigest() != sha]
    checks = []
    for path in sorted((out / 'batches').glob('*/*/result.json')):
        r = json.loads(path.read_text())
        checks.append({'run': str(path.parent.relative_to(out)), 'status': r['status'],
                       'count_consistent': r['counted_questions'] == r['host_questions'] + r['rejected_finals'],
                       'budget_respected': r['submissions'] <= 100 and r['counted_questions'] <= 100,
                       'no_pending': r['pending_feedback'] == 0})
    observed = {c['run'] for c in checks}
    dry_run = manifest['dry_run']
    dump(out / 'validation.json', {'snapshot_changed': changed, 'games': checks,
         'dry_run': dry_run, 'missing_games': sorted(expected - observed),
         'unexpected_games': sorted(observed - expected), 'coverage_complete': expected == observed,
         'passed': not changed and bool(checks) and expected == observed and all(c['count_consistent'] and c['budget_respected']
                   and c['no_pending'] and c['status'] == ('dry_run' if dry_run else 'completed') for c in checks),
         'scope': 'Artifact and accounting checks only, not host semantic accuracy. See progress for planned coverage.'})


def stop_owned_workers(active, exited):
    """Only signal processes started by this launcher; bounded shutdown on errors."""
    import os
    import signal
    for sig, seconds in ((signal.SIGINT, 10), (signal.SIGTERM, 5), (signal.SIGKILL, 5)):
        remaining = [(pid, process) for pid, (process, _) in active.items() if process.poll() is None]
        if not remaining:
            break
        for _, process in remaining:
            try:
                os.killpg(process.pid, sig)
            except ProcessLookupError:
                pass
        deadline = time.monotonic() + seconds
        for _, process in remaining:
            try:
                process.wait(timeout=max(.01, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                pass
    for pid, (process, log) in active.items():
        exited[pid] = process.poll()
        log.close()
    active.clear()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dataset', help='Private .json or .xlsx; required for a new sweep')
    p.add_argument('--config', help='Loop model configuration; required for a new sweep')
    p.add_argument('--partner-config', help='Optional second solver profile JSON; defaults to player')
    p.add_argument('--puzzles', default='TS023,TS032,TS033', help='Distinct comma-separated IDs')
    p.add_argument('--repeat', type=int, default=3, help='Independent games per puzzle and condition')
    p.add_argument('--strategies', default='solo,solo_reflect,independent,shared_buffer')
    p.add_argument('--sync-interval', type=int, default=4, help='shared_buffer synchronization interval in completed submissions')
    add_dialogue_arguments(p)
    p.add_argument('--on-error', choices=['continue','stop'], default='continue',
                   help='continue records failures and schedules remaining independent games; stop prevents new jobs after a failed batch')
    p.add_argument('--workers', type=int, default=3, help='Concurrent puzzle batches, 1–4')
    p.add_argument('--seed', type=int, default=20261023, help='Scheduling only, not model sampling')
    p.add_argument('--out', required=True, help='New directory; existing directory only for --summarize-only')
    p.add_argument('--poll-seconds', type=float, default=20, help='Refresh status and HTML every 1–60 seconds')
    p.add_argument('--dry-run', action='store_true', help='Snapshot and exercise scheduling with zero model calls')
    p.add_argument('--summarize-only', action='store_true', help='Rebuild reports from an existing sweep, no model calls')
    args = p.parse_args(argv)
    out = Path(args.out).resolve()
    if args.summarize_only:
        summarize(out)
        return 0
    if not args.dataset or not args.config:
        p.error('--dataset and --config are required for new sweeps')
    dialogue=dialogue_settings(args)
    if not 1 <= args.workers <= 4 or args.repeat < 1 or not 1 <= args.poll_seconds <= 60:
        p.error('workers must be 1–4, repeat positive, poll-seconds 1–60')
    ids = args.puzzles.split(',')
    if len(ids) != len(set(ids)):
        p.error('puzzle IDs must be unique')
    data = load_dataset(args.dataset)
    puzzles = choose(data, args.puzzles)
    config = configuration(args)
    partner = resolve_env(json.loads(Path(args.partner_config).read_text())) if args.partner_config else None
    if partner is not None:
        validate_profile(partner, require_key=not args.dry_run)
    for puzzle in puzzles:
        build_story_context(puzzle)  # Validate every binding before spending any calls.
    args.command, args.puzzle = 'team', args.puzzles
    make_plan(args, {q['id']: q for q in puzzles})  # Validate strategies before creating output.
    out.mkdir(parents=True, exist_ok=False)
    snap = snapshot(out, data, config, puzzles, partner)
    jobs = [{'puzzle_id': q['id'], 'seed': args.seed + i} for i, q in enumerate(puzzles)]
    random.Random(args.seed).shuffle(jobs)
    manifest = {'arguments': vars(args), 'repeat': args.repeat, 'strategies': args.strategies.split(','),
                'dialogue_policy':dialogue,
                'planned_games': len(jobs) * args.repeat * len(args.strategies.split(',')),
                'jobs': jobs, 'dry_run': args.dry_run,
                'selection': 'Prespecified narrative-complexity candidates; not empirically established difficulty.',
                'model_identity': 'Requested model pinned; Codex event stream may not verify returned model.'}
    dump(out / 'sweep.json', manifest)
    (out / 'batches').mkdir()
    commands = {}
    for job in jobs:
        pid = job['puzzle_id']
        commands[pid] = [sys.executable, str(snap / 'scripts/experiment.py'), 'team',
                        '--dataset', str(snap / 'data/dataset.json'), '--config', str(snap / 'configs/run.json'),
                        '--puzzle', pid, '--repeat', str(args.repeat), '--seed', str(job['seed']),
                        '--strategies', args.strategies, '--sync-interval', str(args.sync_interval), '--on-error', args.on_error, '--quiet', '--out', str(out / 'batches' / pid)]
        commands[pid].extend(['--dialogue-roles',args.dialogue_roles,'--dialogue-scheduling',args.dialogue_scheduling,
                             '--dialogue-max-discussion',str(args.dialogue_max_discussion),'--dialogue-start',args.dialogue_start])
        if args.dry_run:
            commands[pid].append('--dry-run')
        if partner is not None:
            commands[pid].extend(['--partner-config', str(snap / 'configs/partner.json')])
    dump(out / 'commands.json', commands)
    pending, active, exited, processes = jobs.copy(), {}, {}, {}
    last, stopped = None, False
    print(f'Output: {out}\nPlanned games: {manifest["planned_games"]}', flush=True)
    try:
        while pending or active:
            while pending and len(active) < args.workers and not stopped:
                job = pending.pop(0)
                pid = job['puzzle_id']
                log = (out / (pid + '.log')).open('w')
                process = subprocess.Popen(commands[pid], stdout=log, stderr=subprocess.STDOUT,
                                           cwd=snap, start_new_session=True)
                active[pid] = (process, log)
                processes[pid] = process.pid
                dump(out / 'processes.json', processes)
            for pid, (process, log) in list(active.items()):
                if process.poll() is not None:
                    exited[pid] = process.returncode
                    log.close()
                    del active[pid]
                    stopped |= process.returncode != 0 and (args.on_error == 'stop' or process.returncode in (130, -2, -15))
                    dump(out / 'exit_codes.json', exited)
            progress = summarize(out)
            status = [(r['run_dir'], r['status'], r['counted_questions']) for r in progress['statuses']]
            if status != last:
                print(json.dumps({'games': status, 'exit_codes': exited}), flush=True)
                last = status
            if stopped and not active:
                break
            if active or pending:
                time.sleep(args.poll_seconds)
    except (KeyboardInterrupt, Exception) as exc:
        stop_owned_workers(active, exited)
        dump(out / 'exit_codes.json', exited)
        dump(out / 'launcher_error.json', {'type': type(exc).__name__, 'error': str(exc),
                                         'unstarted': pending, 'exit_codes': exited})
        summarize(out)
        return 130 if isinstance(exc, KeyboardInterrupt) else 1
    summarize(out)
    validate_finished(out)
    dump(out / 'completion.json', {'exit_codes': exited, 'unstarted': pending,
                                  'all_batches_finished': not pending and not active,
                                  'dry_run': args.dry_run})
    return 1 if stopped or any(code != 0 for code in exited.values()) else 0


if __name__ == '__main__':
    raise SystemExit(main())
