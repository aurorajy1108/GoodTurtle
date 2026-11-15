#!/usr/bin/env python3
"""Bounded format-only recovery supervisor. Never regenerate completed games."""
import argparse
import contextlib
import hashlib
import html
import json
import os
import shutil
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.resume_study import main as resume_main, prepare
from turtle_loop.engine import dump, now


def resolve_source(source):
    source=Path(source).resolve()
    if (source/'study_plan.json').exists() or (source/'study/study_plan.json').exists():return source
    state=json.loads((source/'status.json').read_text())
    if state.get('status') not in ('requires_attention','recovery_limit_reached','interrupted'):
        raise ValueError('Supervisor is not stopped; refusing to duplicate an active or completed study')
    for attempt in reversed(state.get('attempts',[])):
        candidate=Path(attempt['out']).resolve()
        if candidate.is_relative_to(source) and (candidate/'study_plan.json').exists():return candidate
    raise ValueError('Stopped supervisor has no durable continuation checkpoint')


def stopped_player_reply(source):
    source=Path(source)
    if (source/'study/study_plan.json').exists():source=source/'study'
    plan=json.loads((source/'study_plan.json').read_text())
    if len(plan['jobs'])!=1:raise ValueError('Only one CL batch is supported by this supervisor')
    batch=source/plan['jobs'][0]['name']
    rows=json.loads((batch/'experiment_runs.json').read_text())
    pending=[r for r in rows if r['status']!='completed']
    if len(pending)!=1:raise ValueError('Expected exactly one stopped game; completed games are never rerun')
    game=batch/pending[0]['run_dir']
    result=json.loads((game/'result.json').read_text())
    calls=[json.loads(x) for x in (game/'api_calls.jsonl').read_text().splitlines()]
    players=[c for c in calls if c.get('role')=='player']
    if (result.get('status')!='error' or result.get('stop_reason')!='ProtocolError'
            or not players or players[-1].get('status')!='ok'
            or players[-1].get('finish_reason')!='stop' or result.get('pending_feedback')):
        raise ValueError('Not a complete, unanswered Player format failure; no automatic puzzle rerun')
    last=players[-1]
    return {'game':pending[0]['run_dir'],'submissions':result['submissions'],
            'response_id':last.get('response_id'),
            'raw_sha256':hashlib.sha256(last['text'].encode()).hexdigest()}


def run(source, out, max_continuations=3, mode='plan'):
    source,out=resolve_source(source),Path(out).resolve()
    if out.exists() or source in out.parents:raise ValueError('Use a new output root outside the source')
    fingerprint=stopped_player_reply(source)
    out.mkdir(parents=True)
    files=['turtle_loop/engine.py','turtle_loop/sessions.py','turtle_loop/providers.py',
           'turtle_loop/player_format.py','configs/player_format_repair.json',
           'scripts/resume_study.py','scripts/auto_continue.py']
    pinned={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in files}
    state={'pid':os.getpid(),'status':'prepared' if mode=='plan' else 'running',
           'mode':mode,'source':str(source),'attempts':[],'max_continuations':max_continuations,
           'controller_files':pinned,'policy':'Only format recovery; preserve quota, history and completed games. Cost from latest continuation only.'}
    dump(out/'status.json',state)
    seen=set()
    def event(kind,**data):
        with (out/'events.jsonl').open('a') as f:f.write(json.dumps({'timestamp':now(),'event':kind,**data})+'\n')
    def cost(current):
        path=current/'cost_summary.json'
        if path.exists():shutil.copy2(path,out/'cost_summary.json')
    try:
        for number in range(1,max_continuations+1):
            identity=json.dumps(fingerprint,sort_keys=True)
            if identity in seen:raise ValueError('Same failed reply already repaired once; refusing repeated Codex resampling')
            seen.add(identity)
            if any(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=sha for name,sha in pinned.items()):
                raise ValueError('Repair controller changed during the supervised run')
            current=out/f'continuation_{number:02d}'
            state.update(status='prepared' if mode=='plan' else 'running',active_dir=str(current))
            state['attempts'].append({'out':str(current),'saved_reply':fingerprint})
            dump(out/'status.json',state);event('continuation_prepared',number=number,**fingerprint)
            relative=current.name+'/continual/index.html'
            (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Automatic continuation</title>'
                '<h1>Automatic continuation</h1><p><a href="status.json">Status</a></p>'
                '<p><a href="'+html.escape(relative,quote=True)+'">Latest trajectories</a></p>'
                '<p><a href="cost_summary.json">Cumulative token costs (no duplicate archives)</a></p>')
            if mode=='plan':
                prepare(source,current,auto_player_format=True)
                cost(current);return 0
            with (out/f'continuation_{number:02d}.log').open('w') as log, \
                 contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
                code=resume_main(['--from-study',str(source),'--out',str(current),
                                  '--auto-player-format','--mode','run'])
            cost(current);state['attempts'][-1]['exit_code']=code
            if code==0:
                state.update(status='completed',active_dir=None);return 0
            if code==130:
                state.update(status='interrupted',active_dir=None);return 130
            fingerprint=stopped_player_reply(current)
            event('new_format_failure',number=number,**fingerprint)
            source=current
        state.update(status='recovery_limit_reached',active_dir=None)
        return 1
    except (ValueError,KeyError,OSError,RuntimeError) as exc:
        state.update(status='requires_attention',error=str(exc),active_dir=None)
        event('requires_attention',error=str(exc));return 1
    except KeyboardInterrupt:
        state.update(status='interrupted',active_dir=None);return 130
    finally:dump(out/'status.json',state)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--from-study',required=True,help='Stopped study or verified-run root')
    p.add_argument('--out',required=True,help='New supervisor root')
    p.add_argument('--mode',choices=['plan','run'],default='plan',help='plan performs offline preparation only')
    p.add_argument('--max-continuations',type=int,default=3,help='Maximum format-recovery subprocesses, 1..10')
    args=p.parse_args(argv)
    if not 1<=args.max_continuations<=10:p.error('max-continuations must be 1..10')
    return run(args.from_study,args.out,args.max_continuations,args.mode)


if __name__=='__main__':raise SystemExit(main())
