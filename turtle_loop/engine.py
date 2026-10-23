"""Deterministic counting, score calculation and public/private context separation."""
import csv
import html
import json
import math
import statistics
import shutil
import time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from .providers import APIError
from .host_context import build_story_context, host_payload

LABELS = {'yes', 'no', 'yes and no', 'irrelevant'}
ROOT = Path(__file__).resolve().parents[1]


class ProtocolError(ValueError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


def dump(path, data):
    path = Path(path)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    temp.replace(path)


def parse_action(text, force_final=False):
    try:
        value = json.loads(text)
    except (ValueError, TypeError):
        raise ProtocolError('Player must return one JSON object, without markdown') from None
    if (not isinstance(value, dict) or set(value) != {'type', 'text'} or
            value['type'] not in ('question', 'final') or not isinstance(value['text'], str)
            or not value['text'].strip()):
        raise ProtocolError('Player JSON must contain type=question|final and nonempty text')
    if force_final and value['type'] != 'final':
        raise ProtocolError('Player violated mandatory final instruction; no question was sent to host')
    return value


def grade_final(text, rubric):
    try:
        value = json.loads(text)
    except (ValueError, TypeError):
        raise ProtocolError('Evaluator must return JSON, without markdown') from None
    flags = {'material_contradiction', 'irrelevant', 'rubric_conflict'}
    if not isinstance(value, dict) or set(value) != flags | {'checkpoints', 'full_solution', 'completion_note'}:
        raise ProtocolError('Invalid evaluator fields')
    if any(type(value[k]) is not bool for k in flags | {'full_solution'}):
        raise ProtocolError('Evaluator flags must be JSON booleans')
    if not isinstance(value['completion_note'], str) or not value['completion_note'].strip():
        raise ProtocolError('Evaluator must explain its full-narrative decision privately')
    checkpoints = value['checkpoints']
    if not isinstance(checkpoints, list) or len(checkpoints) != len(rubric):
        raise ProtocolError('Evaluator must score every checkpoint exactly once')
    indexed = {}
    for row in checkpoints:
        if not isinstance(row, dict) or set(row) != {'id', 'credit', 'evidence', 'reason'}:
            raise ProtocolError('Invalid checkpoint fields')
        if (not isinstance(row['id'], str) or row['id'] in indexed
                or type(row['credit']) not in (int, float) or row['credit'] not in (0, 0.5, 1)
                or any(not isinstance(row[k], str) for k in ('evidence', 'reason'))):
            raise ProtocolError('Invalid/duplicate checkpoint ID or credit; use 0/0.5/1')
        if row['credit'] > 0 and not row['evidence'].strip():
            raise ProtocolError('Positive credit must include submission evidence')
        indexed[row['id']] = row
    if set(indexed) != {r['id'] for r in rubric}:
        raise ProtocolError('Evaluator returned wrong checkpoint IDs')
    score = sum(Decimal(str(r['weight'])) * Decimal(str(indexed[r['id']]['credit'])) for r in rubric)
    if value['irrelevant'] and score != 0:
        raise ProtocolError('Irrelevant answer cannot also receive positive credit')
    complete = (value['full_solution'] and all(r['credit'] == 1 for r in checkpoints)
                and not any(value[k] for k in flags))
    label = ('yes' if complete else 'irrelevant' if value['irrelevant'] else
             'yes and no' if score > 0 or value['rubric_conflict'] else 'no')
    return {**value, 'partial_score': float(score), 'complete': complete, 'label': label}


class Recorder:
    def __init__(self, folder, puzzle, config, prompts, echo=True):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=False)
        self.turns, self.calls, self.echo = [], [], echo
        self.opening = puzzle['opening']
        self.simulation = config.get('mode') == 'scripted_demo_NOT_model_performance'
        self.start = time.monotonic()
        dump(self.folder / 'puzzle_private.json', puzzle)
        dump(self.folder / 'config.json', config)
        dump(self.folder / 'prompts.json', prompts)
        self.event('start', puzzle_id=puzzle['id'], budget=config['max_questions'])

    def append(self, filename, value):
        with (self.folder / filename).open('a') as stream:
            stream.write(json.dumps({'timestamp': now(), **value}, ensure_ascii=False, allow_nan=False) + '\n')
            stream.flush()

    def event(self, kind, **fields):
        self.append('trajectory.jsonl', {'event': kind, **fields})

    def audit(self, value):
        self.calls.append(value)
        self.append('api_calls.jsonl', value)

    def report(self, status, stop_reason, error=None):
        questions = sum(t['type'] == 'question' for t in self.turns)
        finals = [t for t in self.turns if t['type'] == 'final']
        graded = [t['grade'] for t in finals if 'grade' in t]
        rejected = sum(not g['complete'] for g in graded)
        success = any(g['complete'] for g in graded)
        last = finals[-1].get('grade') if finals else None
        usage = {}
        for role in sorted({'player', 'host', 'grader'} | {c['role'] for c in self.calls}):
            calls = [c for c in self.calls if c['role'] == role]
            totals = {}
            for c in calls:
                for k, v in c.get('usage', {}).items():
                    if type(v) in (int, float):
                        totals[k] = totals.get(k, 0) + v
            usage[role] = {'http_attempts': len(calls),
                           'successful_responses': sum(c['status'] in ('ok', 'mock') for c in calls),
                           'seconds': sum(c.get('seconds', 0) for c in calls),
                           'provider_reported_usage': totals}
        result = {'status': status, 'stop_reason': stop_reason, 'simulation': self.simulation,
                  'success': success if status == 'completed' else None,
                  'host_questions': questions, 'final_attempts': len(finals),
                  'rejected_finals': rejected, 'counted_questions': questions + rejected,
                  'submissions': len(self.turns),
                  'pending_feedback': sum('label' not in t for t in self.turns),
                  'forced_final': any(t.get('forced') for t in finals),
                  'final_partial_score': last['partial_score'] if last else None,
                  'best_partial_score': max((g['partial_score'] for g in graded), default=None),
                  'latest_final': finals[-1]['text'] if finals else None,
                  'latest_grade': last, 'elapsed_seconds': time.monotonic()-self.start,
                  'usage': usage, 'error': error, 'human_review_status': 'pending'}
        dump(self.folder / 'result.json', result)
        self.render(result)
        if status != 'running' and not (self.folder/'human_review.csv').exists():
            shutil.copyfile(self.folder/'review_template.csv', self.folder/'human_review.csv')
        return result

    def render(self, result):
        lines = ['# Turtle Soup trajectory', '', self.opening, '',
                 f"Status: {result['status']} | counted questions: {result['counted_questions']} | "
                 f"submissions: {result['submissions']} | final partial score: {result['final_partial_score']}", '']
        cards = []
        review = []
        for turn in self.turns:
            label = turn.get('label', '[pending]')
            lines.extend([f"## {turn['index']} · {turn['type']}" + (' · mandatory final' if turn['forced'] else ''),
                          '', turn['text'], '', f'Host: {label}', ''])
            details = ''
            if 'grade' in turn:
                private = json.dumps(turn['grade'], ensure_ascii=False, indent=2)
                lines.extend(['<details><summary>Private evaluator result (not sent to player)</summary>',
                              '', '```json', private, '```', '</details>', ''])
                details = '<details><summary>Private evaluation</summary><pre>' + html.escape(private) + '</pre></details>'
            cards.append(f"<article><h2>{turn['index']} · {html.escape(turn['type'])}"
                         + (' · mandatory final' if turn['forced'] else '') + '</h2><pre>'
                         + html.escape(turn['text']) + '</pre><p>Host: <strong>' + html.escape(label)
                         + '</strong></p>' + details + '</article>')
            review.append({'submission': turn['index'], 'type': turn['type'], 'text': turn['text'],
                           'host_label': label, 'reviewer_label': '', 'notes': ''})
        (self.folder / 'trajectory.md').write_text('\n'.join(lines))
        refresh = '<meta http-equiv="refresh" content="5">' if result['status'] == 'running' else ''
        (self.folder / 'trajectory.html').write_text(
            '<!doctype html><meta charset="utf-8">' + refresh + '<title>Turtle Soup trajectory</title>'
            '<style>body{font:16px/1.6 system-ui;max-width:1000px;margin:32px auto;padding:0 20px;background:#f6f7fa}'
            'article{background:white;padding:18px;margin:16px 0;border:1px solid #ddd;border-radius:10px}'
            'pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}summary{cursor:pointer}</style>'
            '<h1>Turtle Soup trajectory</h1>'
            + ('<p><strong>SCRIPTED DEMO — not model performance</strong></p>' if result['simulation'] else '')
            + '<pre>' + html.escape(self.opening) + '</pre><p>'
            + html.escape(f"{result['status']} · count {result['counted_questions']} · score {result['final_partial_score']}")
            + '</p>' + ''.join(cards))
        # Model-owned snapshot: never overwrite a human's separate annotation file.
        with (self.folder / 'review_template.csv').open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=['submission', 'type', 'text', 'host_label', 'reviewer_label', 'notes'])
            writer.writeheader()
            writer.writerows(review)


def load_prompts():
    return {role: (ROOT / f'prompts/loop_{role}_v1.txt').read_text() for role in ('player', 'host', 'grader')}


def play(puzzle, config, recorder, clients, prompts, player_context=None):
    limit = config['max_questions']
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError('max_questions must be an integer from 1 to 100')
    history = []  # Only public player submissions and four-label feedback.
    counted = 0
    recorder.report('running', None)
    # A stale fingerprint or missing host pack must not leave a batch looking
    # permanently running. No model calls have been made at this point.
    try:
        story_context = build_story_context(puzzle)
        dump(recorder.folder / 'host_context.json', story_context)
    except (ValueError, KeyError, OSError) as exc:
        recorder.event('error', phase='host_context', error_type=type(exc).__name__, message=str(exc))
        return recorder.report('error', 'host_context_error', str(exc))
    try:
        while True:
            forced = counted >= limit - 1
            control = (f'Total limit: {limit} submissions including questions and unsuccessful finals. '
                       f'Used question-equivalents: {counted}. '
                       + ('This is the mandatory last turn. Return type=final NOW, even if uncertain.'
                          if forced else f'At slot {limit}, you MUST submit a final explanation.'))
            payload = {'opening': puzzle['opening'], 'visible_history': history, 'turn_control': control}
            if player_context is not None:
                payload['prior_experience'] = player_context
            player_input = json.dumps(payload, ensure_ascii=False)
            reply = clients['player'].complete(prompts['player'], player_input)
            action = parse_action(reply.text, forced)
            turn = {'index': len(recorder.turns)+1, **action, 'forced': forced}
            recorder.turns.append(turn)
            recorder.event('submission', **turn, raw_player_output=reply.text)
            recorder.report('running', None)
            if action['type'] == 'question':
                counted += 1
                host_input = json.dumps(host_payload(story_context, history, action['text']), ensure_ascii=False)
                response = clients['host'].complete(prompts['host'], host_input)
                label = response.text.strip()
                if label not in LABELS:
                    raise ProtocolError('Host returned an invalid label; raw output saved in api_calls.jsonl')
                turn['label'] = label
                recorder.event('host_feedback', submission=turn['index'], label=label, raw=response.text)
            else:
                grader_input = json.dumps({'opening': puzzle['opening'], 'reference_answer': puzzle['answer'],
                                           'story_context': story_context,
                                           'rubric': puzzle['rubric'],
                                           'completion_requirements': puzzle.get('completion_requirements', []),
                                           'grading_notes': puzzle.get('grading_notes', ''),
                                           'submitted_explanation': action['text']}, ensure_ascii=False)
                response = clients['grader'].complete(prompts['grader'], grader_input)
                grade = grade_final(response.text, puzzle['rubric'])
                turn.update(grade=grade, label=grade['label'])
                recorder.event('evaluation', submission=turn['index'], **grade, raw=response.text)
                if not grade['complete']:
                    counted += 1
            history.append({'type': action['type'], 'text': action['text'], 'feedback': turn['label']})
            if recorder.echo:
                print(f"[{puzzle['id']} #{turn['index']} {action['type']}] {action['text']}\nHost: {turn['label']}", flush=True)
            if action['type'] == 'final':
                if grade['rubric_conflict']:
                    return recorder.report('needs_review', 'rubric_conflict')
                if grade['complete']:
                    return recorder.report('completed', 'solved')
                if forced:
                    return recorder.report('completed', 'budget_exhausted')
            recorder.report('running', None)
    except KeyboardInterrupt:
        recorder.event('interrupted', reason='user_interrupt')
        return recorder.report('interrupted', 'user_interrupt')
    except (APIError, ProtocolError) as exc:
        recorder.event('error', error_type=type(exc).__name__, message=str(exc))
        return recorder.report('error', type(exc).__name__, str(exc))


def summarize_batch(folder, entries):
    completed = [r for r in entries if r['status'] == 'completed']
    solved = [r for r in completed if r['success']]
    def stats(values):
        return {'n': len(values), 'mean': statistics.mean(values) if values else None,
                'population_variance': statistics.pvariance(values) if values else None,
                'sample_variance': statistics.variance(values) if len(values) > 1 else None}
    summary = {'simulation': any(r.get('simulation', False) for r in entries), 'runs': entries, 'attempted_games': sum(r['status'] != 'dry_run' for r in entries),
               'error_games': sum(r['status'] == 'error' for r in entries),
               'interrupted_games': sum(r['status'] == 'interrupted' for r in entries),
               'needs_review_games': sum(r['status'] == 'needs_review' for r in entries),
               'completed_games': len(completed), 'solved_games': len(solved),
               'success_rate_completed': len(solved)/len(completed) if completed else None,
               'counted_questions_completed': stats([r['counted_questions'] for r in completed]),
               'counted_questions_success_only': stats([r['counted_questions'] for r in solved]),
               'final_partial_scores_completed': stats([r['final_partial_score'] for r in completed
                                                        if r['final_partial_score'] is not None]),
               'note': 'Errors, interrupted and needs_review runs remain visible and are excluded from completed-game rates. Scores are provisional model judgments.'}
    dump(Path(folder)/'summary.json', summary)
    columns = ['puzzle_id', 'story_family', 'quality_status', 'repeat', 'status', 'success', 'host_questions', 'rejected_finals',
               'counted_questions', 'submissions', 'final_partial_score', 'best_partial_score', 'stop_reason', 'run_dir']
    with (Path(folder)/'performance.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(entries)
    items = ''.join('<li><a href="' + html.escape(r['run_dir'], quote=True) + '/trajectory.html">'
                    + html.escape(f"{r['puzzle_id']} repeat {r['repeat']}: {r['status']} / score {r['final_partial_score']} / count {r['counted_questions']}")
                    + '</a></li>' for r in entries)
    (Path(folder)/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Turtle Soup runs</title>'
                                        '<h1>Turtle Soup experiment</h1>'
                                        + ('<p>SCRIPTED DEMO — not model performance</p>' if summary['simulation'] else '')
                                        + '<ul>' + items + '</ul>')
    return summary
