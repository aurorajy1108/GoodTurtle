#!/usr/bin/env python3
"""Two-turn, synthetic session transport check. No experiment performance claims."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from turtle_loop.providers import Client
from turtle_loop.engine import dump
from turtle_loop.costs import account_call, pricing_config, cost_summary
from turtle_loop.cli import configuration


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default='configs/loop.codex.json')
    parser.add_argument('--out', required=True, help='New directory for synthetic transport audit')
    parser.add_argument('--run', action='store_true', help='Make six small real calls; otherwise write plan only')
    args = parser.parse_args(argv)
    args.dry_run = not args.run
    config = configuration(args)
    out = Path(args.out); out.mkdir(parents=True, exist_ok=False)
    dump(out/'plan.json', {'synthetic': True, 'calls': 6, 'roles': ['host','player','grader'],
                         'purpose': 'native session continuity, role isolation and delta transport; not puzzle performance',
                         'mode': 'run' if args.run else 'plan'})
    if not args.run:
        return 0
    calls=[]; events=[]; results=[]; prices=pricing_config(config.get('pricing'))
    def audit(call):
        call={**call,'accounting':account_call(call,prices)}; calls.append(call)
        with (out/'api_calls.jsonl').open('a') as stream: stream.write(json.dumps(call,ensure_ascii=False)+'\n')
    def event(kind, **fields):
        events.append({'event':kind,**fields})
        dump(out/'sessions.json',events)
    try:
        for role,word in [('host','violet'),('player','copper'),('grader','marble')]:
            profile=config['host'] if role=='grader' and config.get('grader','host')=='host' else config[role]
            client=Client({**profile,'max_retries':0},role,audit)
            client.begin_game(out,event)
            system='This is a synthetic memory transport check. No tools. Remember the supplied code. Follow current task. Return only JSON in exactly this shape: {"code":"remembered code"}.'
            payload={'code':word,'task':'Reply with the code in the required JSON object.'}
            try:
                first=client.complete(system,json.dumps(payload))
                second=client.complete(system,json.dumps({**payload,'task':'Recall the initial code and reply in the same JSON shape.'}))
                assert json.loads(first.text)=={'code':word} and json.loads(second.text)=={'code':word}, 'Memory response mismatch'
                role_calls=[c for c in calls if c['role']==role]
                assert len(role_calls)==2 and role_calls[1]['previous_response_id']==role_calls[0]['response_id']
                results.append({'role':role,'passed':True,'same_lane':role_calls[0]['session_lane_id']==role_calls[1]['session_lane_id']})
            finally:
                client.close_game()
        ids={e['session_id'] for e in events if e['event']=='session_open'}
        assert len(ids)==3
        dump(out/'result.json',{'synthetic':True,'passed':True,'results':results})
        print(json.dumps({'passed':True,'calls':len(calls),'out':str(out)}))
        return 0
    finally:
        dump(out/'cost_summary.json',cost_summary([c['accounting'] for c in calls]))


if __name__ == '__main__': raise SystemExit(main())
