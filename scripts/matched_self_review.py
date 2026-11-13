#!/usr/bin/env python3
"""Budget-matched single-solver control using a frozen, completed MAS study."""
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from turtle_loop.engine import Recorder, dump, play, saved_grader_reason_recovery
from turtle_loop.matched_self_review import MatchedSelfReviewPlayer, solver_usage, saved_action_recovery
from turtle_loop.providers import Client
from turtle_loop.transport_recovery import saved_transport_recovery
from turtle_loop.host_output_recovery import saved_host_output_recovery


def read(path, default=None):
    return json.loads(Path(path).read_text()) if Path(path).exists() else default


def calls(path):
    return [json.loads(s) for s in Path(path).read_text().splitlines()] if Path(path).exists() else []


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def solo_base_prompts(reference, shared_prompts):
    """Keep frozen judging prompts, but take Player instructions from real solo."""
    solo = read(Path(reference)/'team/TS038_r01_solo/prompts.json')
    if not solo or any(solo.get(k) != v for k, v in shared_prompts.items() if k != 'player'):
        raise ValueError('Solo and MAS reference judging prompts differ')
    if 'SHARED DIALOGUE PROTOCOL' in solo['player'] or 'one of two independent solvers' in solo['player']:
        raise ValueError('Solo reference contains MAS role instructions')
    return {**shared_prompts, 'player': solo['player']}


def prepare(reference, out):
    reference, out = Path(reference).resolve(), Path(out).resolve()
    hashes = read(reference/'snapshot_hashes.json')
    if not hashes:
        raise ValueError('Reference must be a frozen study with snapshot_hashes.json')
    frozen = reference/'runtime_snapshot'
    for name, digest in hashes.items():
        if sha(frozen/name) != digest:
            raise ValueError('Reference snapshot changed: '+name)
    specs = []
    for repeat in (1, 2):
        game = reference/f'team/TS038_r{repeat:02}_free_dialogue'
        result, raw = read(game/'result.json'), calls(game/'api_calls.jsonl')
        config = read(game/'config.json')
        if not result or result['status'] != 'completed' or config['max_questions'] != 100:
            raise ValueError('Two completed TS038 reference games with quota 100 are required')
        actors = [c for c in raw if c.get('role') in ('player', 'partner')]
        if any(c.get('model_requested') != config['player']['model'] or
               c.get('request', {}).get('thinking') != {'type': 'disabled'} for c in actors):
            raise ValueError('Reference actor profiles differ from non-thinking single-player control')
        usage = solver_usage(raw)
        specs.append({'repeat': repeat, 'generation_cap': usage['generations'],
            'output_token_cap': usage['output_tokens'], 'submission_cap': 100,
            'reference_game': str(game), 'reference_calls_sha256': sha(game/'api_calls.jsonl'),
            'reference_result_sha256': sha(game/'result.json'), 'reference_usage': usage,
            'unknown_reference_calls': len([c for c in actors if c.get('status') != 'ok'])})
    # The private scoring data, Host examples, retrieval and models are frozen;
    # only the single-solver policy and explicit budget-stop hook are new.
    out.mkdir(parents=True, exist_ok=False)
    snapshot = out/'runtime_snapshot'
    shutil.copytree(frozen, snapshot, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    shutil.copytree(ROOT/'turtle_loop', snapshot/'turtle_loop', dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    shutil.copy2(ROOT/'scripts/matched_self_review.py', snapshot/'scripts/matched_self_review.py')
    first = reference/'team/TS038_r01_free_dialogue'
    config, prompts, puzzle = [read(first/n) for n in ('config.json', 'prompts.json', 'puzzle_private.json')]
    if config['player']['provider'] != 'deepseek' or config['session_mode'] != 'persistent':
        raise ValueError('This runner currently supports persistent DeepSeek actors')
    for repeat in (1, 2):
        source = reference/f'team/TS038_r{repeat:02}_free_dialogue'
        if any(read(source/n) != v for n, v in [('config.json', config), ('puzzle_private.json', puzzle), ('prompts.json', prompts)]):
            raise ValueError('Reference repeats have different frozen inputs')
    prompts = solo_base_prompts(reference, prompts)
    dump(snapshot/'configs/matched_inputs.json', {'config': config, 'prompts': prompts, 'puzzle': puzzle})
    policy = read(snapshot/'configs/player_format_repair.json')
    policy['max_codex_calls_per_game'] = 0
    dump(snapshot/'configs/player_format_repair.json', policy)
    plan = {'schema_version': 2, 'solver_prompt_version': 'solo-base-v2-no-mas-role',
        'condition': 'solo_self_review_matched', 'puzzle_id': 'TS038',
        'reference_study': str(reference), 'repeats': specs, 'planned_games': 2,
        'matching': 'Available solver generation-count and generated-output-token caps. Input/cache tokens and actual cost are not fixed.',
        'schedule': 'Uniform deterministic floor differences across slots 1..99; no extra notes at slot 100. One solver/lane for all phases.',
        'safety': 'No reference gameplay, solution, rubric or private score is sent to the Player. Early solutions stop. Format retries consume solver budget. Unknown API usage remains unknown.',
        'known_limitations': ['Historical MAS comparison; not randomized concurrent repeats.',
            'TS038 original rubric repeats wife identity across checkpoints; unresolved Host/reference ambiguities remain frozen.',
            'Reference repeat 2 has an unobserved actor call, excluded from its known-token budget and reported separately.']}
    dump(snapshot/'configs/matched_plan.json', plan)
    dump(out/'plan.json', plan)
    snapshot_hashes = {str(p.relative_to(snapshot)): sha(p) for p in snapshot.rglob('*')
                       if p.is_file() and '__pycache__' not in p.parts}
    dump(out/'snapshot_hashes.json', snapshot_hashes)
    dump(out/'status.json', {'status': 'prepared', 'planned_games': 2, 'active': {}, 'completed_games': 0})
    dashboard(out)
    return out


def worker(out, repeat, resume=False):
    out = Path(out).resolve()
    data = read(ROOT/'configs/matched_inputs.json')
    plan = read(ROOT/'configs/matched_plan.json')
    spec = next(s for s in plan['repeats'] if s['repeat'] == repeat)
    game = out/f'TS038_r{repeat:02}_solo_self_review_matched'
    previous = read(game/'result.json')
    if previous and previous['status'] == 'completed':
        return 0
    rec = (Recorder.restore(game, data['puzzle'], data['config'], data['prompts'], echo=True)
           if resume else Recorder(game, data['puzzle'], data['config'], data['prompts'], echo=True))
    cs = {r: Client(data['config'][r], r, rec.audit) for r in ('host', 'grader')}
    cs['player'] = MatchedSelfReviewPlayer(data['config']['player'], rec, spec)
    result = play(data['puzzle'], data['config'], rec, cs, data['prompts'])
    dump(game/'solver_compute.json', cs['player'].status())
    return 0 if result['status'] == 'completed' else 1


def dashboard(out):
    plan = read(out/'plan.json')
    rows, costs = [], []
    for spec in plan['repeats']:
        game = out/f"TS038_r{spec['repeat']:02}_solo_self_review_matched"
        result = read(game/'result.json', {})
        compute = read(game/'solver_compute.json', {})
        row = {'repeat': spec['repeat'], 'condition': plan['condition'], 'run_dir': game.name,
               **result, 'solver_compute': compute}
        rows.append(row)
        if result.get('costs'):
            costs.append(result['costs'])
        notes = [c for c in calls(game/'api_calls.jsonl') if c.get('self_review_phase') in ('draft', 'review') and c.get('status') == 'ok']
        if game.exists():
            (game/'self_review.html').write_text('<!doctype html><meta charset="utf-8"><title>Single-solver notes</title>'
                '<h1>Single-solver draft / review notes</h1><a href="trajectory.html">External trajectory</a>' + ''.join(
                    '<details><summary>'+html.escape(f"Slot {c['self_review_slot']} · {c['self_review_phase']}")+
                    '</summary><pre style="white-space:pre-wrap">'+html.escape(c['text'])+'</pre></details>' for c in notes))
    from turtle_loop.costs import merge_summaries
    dump(out/'cost_summary.json', merge_summaries(costs))
    dump(out/'experiment_runs.json', rows)
    comparison = []
    for spec, row in zip(plan['repeats'], rows):
        reference = Path(spec['reference_game'])
        if sha(reference/'api_calls.jsonl') != spec['reference_calls_sha256'] or sha(reference/'result.json') != spec['reference_result_sha256']:
            raise ValueError('Historical reference files changed after matching budgets were frozen')
        for condition, game, result in [('original_solo', reference.parent/reference.name.replace('free_dialogue', 'solo'), None),
                                         ('free_dialogue', reference, None),
                                         (plan['condition'], out/row['run_dir'], row)]:
            result = result or read(game/'result.json', {})
            raw = calls(game/'api_calls.jsonl')
            compute = solver_usage(raw) if raw else {}
            caps = spec if condition == plan['condition'] else {}
            comparison.append({'repeat': spec['repeat'], 'condition': condition,
                **{k: result.get(k) for k in ('status', 'success', 'submissions', 'counted_questions',
                                            'final_partial_score', 'stop_reason')},
                'actor_compute': compute,
                'generation_cap': caps.get('generation_cap'), 'output_token_cap': caps.get('output_token_cap'),
                'output_budget_utilization': compute.get('output_tokens', 0)/caps['output_token_cap'] if caps else None,
                'trajectory': str(game/'trajectory.html')})
    dump(out/'comparison.json', comparison)
    (out/'comparison.md').write_text('# TS038 self-review control (live)\n\n'
        'Equal available actor generation/output-token caps; actual input, cache hits and costs may differ. '
        'Incomplete or errored games are not performance conclusions. Scores use the frozen original rubric and need human review.\n\n'
        '| Repeat | Condition | Status | Submissions | Score | Actor generations | Actor output tokens | Output-budget use |\n'
        '| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |\n'+''.join(
            '| '+' | '.join(str(x) for x in (r['repeat'], r['condition'], r['status'], r['submissions'],
                r['final_partial_score'], r['actor_compute'].get('generations', 0), r['actor_compute'].get('output_tokens', 0),
                round(r['output_budget_utilization'], 3) if r['output_budget_utilization'] is not None else '—'))+' |\n'
            for r in comparison)+'\nTwo historical repeats on one puzzle cannot establish a general MAS advantage. '
        'Reference MAS repeat 2 includes an additional unobserved actor request, whose token usage is not invented.\n')
    table = ''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in (
        r['repeat'], r.get('status', 'planned'), r.get('submissions', 0), r.get('final_partial_score'),
        r['solver_compute'].get('generations', 0), r['solver_compute'].get('output_tokens', 0)))+
        '<td><a href="'+r['run_dir']+'/trajectory.html">Trajectory</a> · <a href="'+r['run_dir']+
        '/self_review.html">Self review</a></td></tr>' for r in rows)
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="30">'
        '<h1>TS038 · compute-budget-matched single-agent self-review</h1><p>'+html.escape(plan['matching'])+
        '</p><a href="plan.json">Frozen plan</a> · <a href="status.json">Status</a> · '
        '<a href="cost_summary.json">All-role token costs</a> · <a href="comparison.md">Solo / MAS / self-review comparison</a> · <a href="alerts.jsonl">Alerts</a>'
        '<table border="1"><tr><th>Repeat</th><th>Status</th><th>Submissions</th><th>Score</th>'
        '<th>Actor generations</th><th>Actor output tokens</th><th>Inspect</th></tr>'+table+'</table>')
    return rows


def authorize_recovery(game):
    config, puzzle, previous = [read(game/n) for n in ('config.json', 'puzzle_private.json', 'result.json')]
    raw, events = calls(game/'api_calls.jsonl'), calls(game/'trajectory.jsonl')
    turns = []
    for e in events:
        if e['event'] == 'submission':
            turns.append({k: e[k] for k in ('index', 'type', 'text', 'forced')})
        elif e['event'] in ('evaluation', 'host_feedback'):
            turns[e['submission']-1]['label'] = e['label']
            if e['event'] == 'evaluation':
                turns[e['submission']-1]['grade'] = e
    from turtle_loop.private_note_recovery import saved_private_note_recovery
    proof=saved_private_note_recovery(previous,raw,turns,config,game)
    if proof:
        dump(game/'private_note_recovery.json',proof)
        return 'retain_truncated_private_note'
    proof = saved_host_output_recovery(previous, raw, turns, config, game)
    if proof:
        dump(game/'host_output_recovery.json',proof)
        return 'saved_host_'+proof['mode']
    proof = saved_action_recovery(previous, raw, turns, config, game)
    if proof:
        dump(game/'self_review_action_recovery.json', proof)
        return 'local_inline_action_envelope_only'
    proof = saved_transport_recovery(previous, raw, turns, config, game)
    if proof:
        dump(game/'transport_recovery.json', proof)
        return 'exact_transport_request'
    proof = saved_grader_reason_recovery(previous, raw, turns, config, puzzle, missing_coverage=True)
    if proof:
        dump(game/'grader_coverage_completion.json', proof)
        return 'complete_missing_evidence_only'
    return None


def execute(out):
    out = Path(out).resolve()
    # Duplicate launch protection; do not start another worker over the same log.
    import fcntl
    lock = (out/'runner.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    hashes = read(out/'snapshot_hashes.json')
    snapshot = out/'runtime_snapshot'
    for name, digest in hashes.items():
        if sha(snapshot/name) != digest:
            raise ValueError('Frozen self-review runtime changed: '+name)
    from scripts.supervise_campaign import notify
    state = {'status': 'running', 'pid': os.getpid(), 'active': {}, 'planned_games': 2,
             'completed_games': 0, 'recoveries': {}}
    active, pending, failed = {}, [], False
    for repeat in (1, 2):
        game = out/f'TS038_r{repeat:02}_solo_self_review_matched'
        result = read(game/'result.json')
        if result and result['status'] == 'completed':
            continue
        if result and not authorize_recovery(game):
            raise ValueError('Stopped game needs manual review; it will not be resampled: '+str(game))
        pending.append((repeat, bool(result)))
    try:
        while pending or active:
            for repeat, resume in pending:
                command = [sys.executable, str(snapshot/'scripts/matched_self_review.py'),
                           'worker', '--out', str(out), '--repeat', str(repeat)]
                if resume:
                    command.append('--resume')
                log = (out/f'repeat_{repeat}.log').open('a')
                process = subprocess.Popen(command, cwd=snapshot, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                active[repeat] = process, log
                state['active'][str(repeat)] = process.pid
            pending = []
            for repeat, (process, log) in list(active.items()):
                if process.poll() is None:
                    continue
                log.close()
                del active[repeat]
                del state['active'][str(repeat)]
                game = out/f'TS038_r{repeat:02}_solo_self_review_matched'
                result = read(game/'result.json', {})
                if process.returncode == 0 and result.get('status') == 'completed':
                    notify(out, 'self-review complete', f"TS038 repeat {repeat}: score {result['final_partial_score']}, submissions {result['submissions']}.")
                    continue
                attempts = state['recoveries'].get(str(repeat), 0)
                repair = authorize_recovery(game) if result else None
                if repair and attempts < 3:
                    state['recoveries'][str(repeat)] = attempts+1
                    notify(out, 'recovering', f'TS038 repeat {repeat}: {repair}; preserving observed outputs and quota.')
                    pending.append((repeat, True))
                else:
                    failed = True
                    notify(out, 'attention required', f"TS038 repeat {repeat} paused: {result.get('error', 'worker process failed')}. No automatic resampling.")
            rows = dashboard(out)
            state.update(updated_at=time.time(), completed_games=sum(r.get('status') == 'completed' for r in rows))
            dump(out/'status.json', state)
            if active or pending:
                time.sleep(10)
        state['status'] = 'requires_attention' if failed else 'completed'
        return 1 if failed else 0
    finally:
        for process, log in active.values():
            if process.poll() is None:
                os.killpg(process.pid, 2)
                try:
                    process.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, 15)
            log.close()
        state['active'] = {}
        if state['status'] == 'running':
            state['status'] = 'interrupted'
        dump(out/'status.json', state)
        dashboard(out)
        lock.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'run', 'worker', 'status'])
    parser.add_argument('--out', required=True, help='New output folder for prepare; existing folder otherwise')
    parser.add_argument('--reference', help='Completed frozen study with TS038 free_dialogue repeats 1 and 2')
    parser.add_argument('--repeat', type=int, choices=[1, 2], help='Internal worker repeat')
    parser.add_argument('--resume', action='store_true', help='Internal: use verified saved session checkpoint')
    args = parser.parse_args(argv)
    if args.command == 'prepare':
        if not args.reference:
            parser.error('prepare requires --reference')
        prepare(args.reference, args.out)
        print(args.out)
        return 0
    if args.command == 'worker':
        if not args.repeat:
            parser.error('worker requires --repeat')
        return worker(args.out, args.repeat, args.resume)
    if args.command == 'status':
        dashboard(Path(args.out))
        print(json.dumps(read(Path(args.out)/'status.json'), ensure_ascii=False, indent=2))
        return 0
    return execute(args.out)


if __name__ == '__main__':
    raise SystemExit(main())
