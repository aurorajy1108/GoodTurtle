#!/usr/bin/env python3
"""Publish a read-only live dashboard beside already-served experiment artifacts.

Example: python3 scripts/watch_progress.py --publish runs/api/batch/web \
    --batch runs/api/batch/web/run=/run --batch runs/api/rerun/web/run=/retry
Only this publisher's HTML and JSON are written; experiment records stay intact.
"""
import argparse
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path


def read_json(path, default=None):
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def read_events(path):
    try:
        lines = path.read_text().splitlines()
    except FileNotFoundError:
        return []
    rows = []
    for line in lines:
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue  # A live writer may still be appending its last record.
    return rows


def collect_game(folder, batch_name, prefix, metadata=None):
    metadata = metadata or {}
    events = read_events(folder/'trajectory.jsonl')
    result = read_json(folder/'result.json', {})
    config = read_json(folder/'config.json', {})
    start = next((e for e in events if e.get('event') == 'start'), {})
    turns = {}
    scores = []
    for event in events:
        kind = event.get('event')
        if kind == 'submission':
            turns[event['index']] = {k: event.get(k) for k in ('index', 'type', 'text', 'timestamp')}
        elif kind in ('host_feedback', 'evaluation'):
            turn = turns.get(event.get('submission'))
            if turn is not None:
                turn['feedback'] = event.get('label')
            score = event.get('partial_score') if kind == 'evaluation' else None
            if type(score) in (int, float) and math.isfinite(score):
                scores.append({'submission': event['submission'], 'score': score})
                if turn is not None:
                    turn['score'] = score
    calls = read_events(folder/'api_calls.jsonl')
    costs = [c.get('accounting', {}).get('estimated_cost_usd') for c in calls]
    known_costs = [c for c in costs if type(c) in (int, float)]
    url = prefix.rstrip('/') + '/' + folder.name
    error = result.get('error')
    if error and calls and calls[-1].get('status') == 'ok' and not calls[-1].get('text', '').strip():
        error = 'Player 返回了空白文本，实验已停止。'
    return {
        'id': batch_name+'/'+folder.name, 'batch': batch_name,
        'puzzle_id': start.get('puzzle_id', folder.name.split('_')[0]),
        'condition': metadata.get('condition') or next((c for c in ('answer_only','direct','session','transcript','source') if folder.name.endswith('_'+c)), 'direct'),
        'source_puzzle': metadata.get('source'), 'name': folder.name,
        'status': result.get('status', 'starting'), 'error': error,
        'budget': config.get('max_questions', start.get('budget', 100)),
        'submissions': max(len(turns), result.get('submissions', 0)),
        'pending_feedback': sum('feedback' not in t for t in turns.values()),
        'score': scores[-1]['score'] if scores else result.get('final_partial_score'),
        'best_score': max((s['score'] for s in scores), default=result.get('best_partial_score')),
        'scores': scores, 'turns': list(turns.values()),
        'elapsed_seconds': result.get('elapsed_seconds', 0),
        'started_at': start.get('timestamp'),
        'last_activity': (calls[-1] if calls else events[-1] if events else {}).get('timestamp'),
        'api_calls': len(calls), 'successful_calls': sum(c.get('status') == 'ok' for c in calls),
        'total_tokens': sum(c.get('usage', {}).get('total_tokens', 0) or 0 for c in calls),
        'cost_usd': sum(known_costs) if len(known_costs) == len(costs) and costs else None,
        'models': {role: config.get(role, {}).get('model', '—') for role in ('player', 'host', 'grader')},
        'links': {name: url+'/'+filename for name, filename in {
            'trajectory': 'trajectory.html', 'result': 'result.json',
            'tokens': 'token_costs.csv', 'costs': 'cost_summary.json'}.items()},
    }


def collect(batches):
    games = []
    for folder, prefix in batches:
        rows = read_json(folder/'experiment_runs.json', []) or []
        metadata = {row['run_dir']:row for row in rows if row.get('run_dir')}
        name = folder.parent.name if folder.name == 'continual' else folder.parent.parent.name
        for path in sorted(folder.glob('*/trajectory.jsonl'), key=lambda p: p.stat().st_mtime):
            games.append(collect_game(path.parent, name, prefix, metadata.get(path.parent.name)))
    return {'updated_at': datetime.now(timezone.utc).isoformat(), 'games': games}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', type=Path, required=True)
    parser.add_argument('--batch', action='append', required=True, help='Batch folder=served URL prefix')
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args()
    batches = []
    for spec in args.batch:
        folder, separator, prefix = spec.rpartition('=')
        if not separator or not prefix.startswith('/') or '..' in prefix.split('/'):
            parser.error('--batch must be folder=/url-prefix')
        batches.append((Path(folder).resolve(), prefix))
    args.publish.mkdir(parents=True, exist_ok=True)
    template = Path(__file__).resolve().parents[1]/'turtle_loop/web/progress.html'
    (args.publish/'index.html').write_text(template.read_text())
    while True:
        data = collect(batches)
        tmp = args.publish/'progress.json.tmp'
        tmp.write_text(json.dumps(data, ensure_ascii=False, allow_nan=False))
        tmp.replace(args.publish/'progress.json')
        if args.once:
            break
        time.sleep(2)


if __name__ == '__main__':
    main()
