#!/usr/bin/env python3
"""Replay independent question-label cases without a player or hidden expected labels."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from turtle_loop.dataset import load_dataset
from turtle_loop.engine import dump, load_prompts
from turtle_loop.host_context import build_story_context, host_payload, LABELS
from turtle_loop.providers import Client, APIError, resolve_env
from turtle_loop.host import answer_question


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', required=True, help='Private .json or .xlsx dataset')
    parser.add_argument('--config', required=True, help='Existing model config; uses host profile only')
    parser.add_argument('--cases', required=True, help='JSON list: id, puzzle_id, question, expected, optional history')
    parser.add_argument('--out', required=True, help='New output directory (never overwrite)')
    parser.add_argument('--repeat', type=int, default=1, help='Independent calls per case, default 1; no automatic retries of wrong labels')
    parser.add_argument('--dry-run', action='store_true', help='Validate and snapshot all inputs without model calls')
    args = parser.parse_args()
    if args.repeat < 1:
        parser.error('--repeat must be positive')
    puzzles = {p['id']:p for p in load_dataset(args.dataset)['puzzles']}
    config = json.loads(Path(args.config).read_text())
    config['host'] = resolve_env(config['host'])
    cases = json.loads(Path(args.cases).read_text())
    prompts = load_prompts()
    inputs = []
    for case in cases:
        if case['expected'] not in LABELS:
            raise ValueError('Invalid expected label')
        story = build_story_context(puzzles[case['puzzle_id']])
        inputs.append(host_payload(story, case.get('history', []), case['question']))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    dump(out/'cases.json', cases)
    dump(out/'inputs.json', inputs)
    dump(out/'config.json', config)
    (out/'host_prompt.txt').write_text(prompts['host'])
    (out/'host_review_prompt.txt').write_text(prompts['host_review'])
    def append(name, row):
        with (out/name).open('a') as stream:
            stream.write(json.dumps(row, ensure_ascii=False)+'\n')
    rows = []
    if not args.dry_run:
        client = Client(config['host'], 'host', lambda row: append('api_calls.jsonl', row))
        for repeat in range(1,args.repeat+1):
            for case, payload in zip(cases, inputs):
                row = {'id':case['id'], 'repeat':repeat, 'expected':case['expected']}
                try:
                    actual = answer_question(client, prompts['host'], payload, prompts['host_review'],
                                             lambda decision:append('host_reviews.jsonl',{'id':case['id'],'repeat':repeat,**decision})).text.strip()
                    row.update(actual=actual, passed=actual==case['expected'], valid_label=actual in LABELS)
                except APIError as exc:
                    row.update(error=str(exc), passed=False, valid_label=False)
                rows.append(row)
                append('results.jsonl',row)
                print(json.dumps(row),flush=True)
                # Stop on transport errors, not on semantic failures; preserve diagnostics.
                if 'error' in row:
                    break
            if rows and 'error' in rows[-1]:
                break
    summary = {'dry_run':args.dry_run, 'planned_calls':len(cases)*args.repeat,
               'completed_calls':len(rows), 'passed':sum(x['passed'] for x in rows),
               'errors':sum('error' in x for x in rows),
               'expected_labels_status':'AI draft pending human review; regression checks, not held-out accuracy estimate'}
    dump(out/'summary.json',summary)
    return 0 if args.dry_run or (len(rows)==len(cases)*args.repeat and all(x['passed'] for x in rows)) else 1

if __name__ == '__main__':
    raise SystemExit(main())
