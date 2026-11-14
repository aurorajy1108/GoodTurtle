"""CLI for import, preflight, isolated API trials and an explicitly synthetic demo."""
import argparse
import hashlib
import json
import sys
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from .dataset import load_dataset, overview
from .engine import Recorder, dump, load_prompts, play, summarize_batch
from .providers import Client, Reply, resolve_env, validate_profile
from .costs import pricing_config
from .host_context import context_policy

ROOT = Path(__file__).resolve().parents[1]


def configuration(args):
    raw = json.loads(Path(args.config).read_text()) if args.config else {'max_questions': 100}
    allowed = {'host', 'player', 'grader', 'max_questions', 'pricing', 'context_policy', 'session_mode'}
    if set(raw) - allowed:
        raise ValueError(f'Unknown experiment settings: {set(raw)-allowed}')
    for role in ('host', 'player', 'grader'):
        override = getattr(args, role, None)
        if override:
            provider, separator, model = override.partition(':')
            if not separator or not model:
                raise ValueError(f'--{role} must be provider:exact-model-id')
            raw[role] = {'provider': provider, 'model': model, 'max_output_tokens': 4096}
    for role in ('host', 'player'):
        if not isinstance(raw.get(role), dict):
            raise ValueError(f'Configure {role} in --config or pass --{role} provider:model')
    if raw.get('grader', 'host') == 'host':
        raw['grader'] = deepcopy(raw['host'])
    if not isinstance(raw['grader'], dict):
        raise ValueError('grader must be a profile object or "host"')
    raw = resolve_env(raw)
    raw['pricing'] = pricing_config(raw.get('pricing'))
    raw['context_policy'] = context_policy(raw.get('context_policy'))
    raw.setdefault('session_mode', 'persistent')
    if raw['session_mode'] not in ('persistent', 'replay'):
        raise ValueError('session_mode must be persistent or replay')
    raw.setdefault('max_questions', 100)
    if type(raw['max_questions']) is not int or not 1 <= raw['max_questions'] <= 100:
        raise ValueError('max_questions must be an integer from 1 to 100')
    truncation = getattr(args, 'host_on_output_truncation', None)
    if truncation:
        if not isinstance(raw.get('host'), dict):
            raise ValueError('host profile required to set --host-on-output-truncation')
        raw['host'] = {**raw['host'], 'on_output_truncation': truncation}
    for role in ('host', 'player', 'grader'):
        validate_profile(raw[role], require_key=not args.dry_run)
    return raw


def choose(data, selection):
    if selection == 'all':
        return data['puzzles']
    names = selection.split(',')
    if len(names) != len(set(names)):
        raise ValueError('Duplicate puzzle ID in --puzzle')
    bank = {p['id']: p for p in data['puzzles']}
    if set(names) - set(bank):
        raise ValueError(f'Unknown puzzle IDs: {sorted(set(names)-set(bank))}')
    return [bank[n] for n in names]


def batch(args):
    data = load_dataset(args.dataset)
    puzzles = choose(data, args.puzzle)
    config = configuration(args)  # Validate all keys/models BEFORE any billable request.
    if args.repeat < 1:
        raise ValueError('--repeat must be positive')
    folder = Path(args.out) if args.out else ROOT / 'runs/api' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+uuid.uuid4().hex[:8])
    folder.mkdir(parents=True, exist_ok=False)
    prompts = load_prompts()
    dump(folder/'dataset_audit.json', overview(data))
    dump(folder/'batch_config.json', {'models_and_budget': config, 'puzzle_ids': [p['id'] for p in puzzles],
                                    'repeats': args.repeat, 'source': data.get('source'),
                                    'source_file_sha256': hashlib.sha256(Path(args.dataset).read_bytes()).hexdigest(),
                                    'context_policy': config['session_mode'] + '; role-isolated; no tools',
                                    'prompt_sha256': {k: hashlib.sha256(v.encode()).hexdigest() for k, v in prompts.items()},
                                    'dry_run': args.dry_run})
    entries = []
    print(f'Output: {folder}', flush=True)
    for puzzle in puzzles:
        for repeat in range(1, args.repeat+1):
            name = f"{puzzle['id']}_r{repeat:02d}"
            recorder = Recorder(folder/name, puzzle, config, prompts, echo=not args.quiet)
            initial = recorder.report('dry_run' if args.dry_run else 'running', None)
            metadata = {'puzzle_id': puzzle['id'], 'story_family': puzzle.get('story_family', ''),
                        'quality_status': puzzle.get('quality_status', ''), 'repeat': repeat, 'run_dir': name}
            entries.append({**metadata, **initial})
            summarize_batch(folder, entries)
            if not args.quiet:
                print(f'Live trajectory: {folder/name/"trajectory.html"}', flush=True)
            if args.dry_run:
                result = recorder.report('dry_run', 'no_model_calls')
            else:
                clients = {role: Client(config[role], role, recorder.audit) for role in ('host', 'player', 'grader')}
                result = play(puzzle, config, recorder, clients, prompts)
            entries[-1] = {**metadata, **result}
            summarize_batch(folder, entries)
            print(f"{name}: {result['status']}; count={result['counted_questions']}; score={result['final_partial_score']}", flush=True)
            # Fail fast on authentication/API/protocol problems; never spend the rest of a batch blindly.
            if result['status'] in ('error', 'interrupted'):
                return 130 if result['status'] == 'interrupted' else 1
    return 0


class DemoClient:
    """Scripted fixture, never a model evaluation or a substitute for real credentials."""
    def __init__(self, role, audit):
        self.role, self.audit, self.i = role, audit, 0

    def complete(self, system, user):
        self.i += 1
        if self.role == 'player':
            values = [{'type': 'question', 'text': 'Did rain cause her to pick up the umbrella?'},
                      {'type': 'final', 'text': 'She used it to stay dry in the rain.'},
                      {'type': 'question', 'text': 'Did it help her reach the bag?'},
                      {'type': 'final', 'text': 'She used the umbrella to retrieve her bag from a high shelf.'}]
            text = json.dumps(values[self.i-1])
        elif self.role == 'host':
            text = 'no' if self.i == 1 else 'yes'
        else:
            credit = 0 if self.i == 1 else 1
            text = json.dumps({'checkpoints': [{'id': 'C1', 'credit': credit,
                                               'evidence': '' if not credit else 'retrieve her bag from a high shelf',
                                               'reason': 'Scripted fixture judgment'}],
                               'material_contradiction': not bool(credit),
                               'irrelevant': False, 'rubric_conflict': False, 'full_solution': bool(credit),
                               'completion_note': 'Scripted full-narrative judgment'})
        self.audit({'role': self.role, 'status': 'mock', 'text': text, 'usage': {}, 'seconds': 0,
                    'request': {'system': system, 'user': user}})
        return Reply(text, {}, model='scripted-fixture')


def demo(args):
    folder = Path(args.out) if args.out else ROOT/'runs/api'/('demo_'+uuid.uuid4().hex[:8])
    folder.mkdir(parents=True, exist_ok=False)
    puzzle = {'id': 'DEMO', 'opening': 'In a dry room, she picked up an umbrella to get her bag. Why?',
              'answer': 'She used the umbrella to retrieve her bag from a high shelf.',
              'rubric': [{'id': 'C1', 'weight': 1, 'criterion': 'Umbrella retrieves bag from high shelf.'}]}
    config = {'max_questions': 4, 'mode': 'scripted_demo_NOT_model_performance'}
    prompts = load_prompts()
    recorder = Recorder(folder/'DEMO_r01', puzzle, config, prompts)
    clients = {role: DemoClient(role, recorder.audit) for role in ('host', 'player', 'grader')}
    result = play(puzzle, config, recorder, clients, prompts)
    summarize_batch(folder, [{'puzzle_id': 'DEMO', 'repeat': 1, 'run_dir': 'DEMO_r01', **result}])
    print(f'SCRIPTED DEMO ONLY: {folder}/index.html')
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    inspect = sub.add_parser('inspect', help='Read workbook/rubric without any model calls')
    inspect.add_argument('--dataset', required=True)
    importer = sub.add_parser('import', help='Create private dataset, public openings and audit JSON')
    importer.add_argument('--dataset', required=True)
    importer.add_argument('--out', required=True)
    run = sub.add_parser('run', help='Play one or more puzzles through configured APIs')
    run.add_argument('--dataset', required=True)
    run.add_argument('--puzzle', default='TS002', help='ID, comma-separated IDs, or all')
    run.add_argument('--config', help='JSON configuration, e.g. configs/loop.openai.json')
    for role in ('host', 'player', 'grader'):
        run.add_argument('--'+role, help='Override role as provider:exact-model-id')
    run.add_argument('--host-on-output-truncation', choices=['human', 'auto'],
                     help='human (default): retry once then ask for a label; '
                          'auto: retry twice, then one no-thinking attempt (overnight)')
    run.add_argument('--repeat', type=int, default=1)
    run.add_argument('--out', help='New output directory; never overwrite an existing experiment')
    run.add_argument('--dry-run', action='store_true', help='Save frozen inputs without model calls')
    run.add_argument('--quiet', action='store_true')
    sample = sub.add_parser('demo', help='Offline scripted plumbing demo, not a model benchmark')
    sample.add_argument('--out')
    args = parser.parse_args(argv)
    try:
        if args.command in ('inspect', 'import'):
            data = load_dataset(args.dataset)
            if args.command == 'inspect':
                print(json.dumps(overview(data), ensure_ascii=False, indent=2))
            else:
                folder = Path(args.out)
                folder.mkdir(parents=True, exist_ok=False)
                dump(folder/'private.json', data)
                dump(folder/'audit.json', overview(data))
                (folder/'public.jsonl').write_text(''.join(json.dumps({'id': p['id'], 'opening': p['opening']}, ensure_ascii=False)+'\n' for p in data['puzzles']))
                print(f'Imported {len(data["puzzles"])} puzzles into {folder}')
            return 0
        return demo(args) if args.command == 'demo' else batch(args)
    except (ValueError, KeyError, OSError) as exc:
        print(f'Cannot run: {exc}', file=sys.stderr)
        return 2
