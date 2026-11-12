#!/usr/bin/env python3
"""Plan, dry-run or execute the five requested CL sets and five team puzzles.

Default mode only writes a frozen plan: no model calls. All runs use a new output
directory and immutable code/data/config copies. See docs/study_20261102.md.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from turtle_loop.dataset import load_dataset
from turtle_loop.host_context import build_story_context
from turtle_loop.engine import dump
from turtle_loop.cli import configuration
from turtle_loop.experiments import make_plan, planned_games
from turtle_loop.costs import write_batch_costs
from turtle_loop.dialogue import add_dialogue_arguments, dialogue_settings
from scripts.team_sweep import snapshot

SETS={
 1:dict(anchor=13,positive=[15,16],negative=[14],neutral=[28]),
 2:dict(anchor=34,positive=[35],negative=[33],neutral=[12]),
 3:dict(anchor=22,positive=[47],negative=[45],neutral=[19]),
 4:dict(anchor=7,positive=[26],negative=[21],neutral=[31]),
 5:dict(anchor=38,positive=[46,32],negative=[45],neutral=[28]),
}
OWNERS={'TS038':'Aurora','TS002':'Kelly','TS014':'Amy','TS022':'April','TS042':'Shirley'}


def collect_costs(out, jobs):
    rows=[]
    for job in jobs:
        path=out/job['name']/'experiment_runs.json'
        if path.exists():
            for row in json.loads(path.read_text()):
                rows.append({**row,'run_dir':job['name']+'/'+row['run_dir']})
    write_batch_costs(out,rows)


def groups(selected, directions='primary'):
    if directions not in ('primary', 'bidirectional'):
        raise ValueError('Unknown directions mode')
    result=[]
    for n in selected:
        s=SETS[n];a=f'TS{s["anchor"]:03d}'
        for relation in ['positive','negative','neutral']:
            for number in s[relation]:
                other=f'TS{number:03d}'
                pairs=[[other,a]]+([[a,other]] if relation=='positive' and directions=='bidirectional' else [])
                for source,target in pairs:
                    result.append(dict(id=f'S{n}_{source}_{target}',set_id=n,puzzles=[source,target],
                        directed_pairs=[[source,target]],relation=relation,anchor=a,
                        analysis_role='primary' if target==a else 'exploratory',
                        relation_status='user_hypothesis_not_measured',direction='to_anchor' if target==a else 'to_positive'))
    return {'schema_version':2,'directions':directions,'source':'User fixed-target design, 2026-11-02',
            'interpretation':'Default: fixed anchor B. Optional reverse positive directions are exploratory. Negative/neutral only source. No inferred relations among non-anchor puzzles.',
            'groups':result}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--suite',choices=['continual','team','all'],default='all')
    p.add_argument('--sets',default='all',help='CL set numbers: all or comma-separated 1..5')
    p.add_argument('--source-puzzles',default='all',help='CL source A whitelist, e.g. TS015,TS014,TS028; default all sources in selected sets/directions')
    p.add_argument('--directions',choices=['primary','bidirectional'],default='primary',help='primary: fixed anchor B; bidirectional also adds exploratory reverse positive pairs')
    p.add_argument('--source-policy',choices=['fixed','per-repeat'],default='fixed',help='fixed: solve each A once per batch and reuse its complete public experience; per-repeat: independently regenerate A for each block')
    p.add_argument('--import-direct',help='Existing completed direct game to count once in the first scheduled block')
    p.add_argument('--memory',choices=['session','transcript','card','both'],default='session',help='session: original A Player messages continued into B (default); transcript/card/both: legacy new-conversation ablations')
    p.add_argument('--team-puzzles',default=','.join(OWNERS),help='Subset of TS038,TS002,TS014,TS022,TS042')
    p.add_argument('--repeat',type=int,default=3,help='Fresh B games per direction/condition; fixed source A is not repeated')
    p.add_argument('--strategies',default='solo,solo_reflect,independent,shared_buffer')
    p.add_argument('--sync-interval',type=int,default=4)
    add_dialogue_arguments(p)
    p.add_argument('--config',default='configs/loop.deepseek.json')
    p.add_argument('--dataset',default='data/annotations/turtle50_v4/private.json')
    p.add_argument('--seed',type=int,default=20261102,help='Scheduling only, not remote sampling seed')
    p.add_argument('--mode',choices=['plan','dry-run','run'],default='plan')
    p.add_argument('--on-error',choices=['stop','continue'],default='stop',help='Default stop prevents spending more calls after a failed game')
    p.add_argument('--out',required=True,help='New output directory; no automatic resume/overwrite')
    args=p.parse_args(argv)
    dialogue=dialogue_settings(args)
    selected=list(SETS) if args.sets=='all' else [int(n) for n in args.sets.split(',')]
    if not selected or len(set(selected))!=len(selected) or not set(selected)<=set(SETS):p.error('Invalid/duplicate sets')
    teams=args.team_puzzles.split(',')
    if not teams or len(set(teams))!=len(teams) or not set(teams)<=set(OWNERS):p.error('Invalid/duplicate team puzzles')
    if args.repeat<1 or args.sync_interval<1:p.error('repeat/sync-interval must be positive')
    data=load_dataset(args.dataset);bank={x['id']:x for x in data['puzzles']}
    args.dry_run=args.mode!='run';config=configuration(args)
    if config['max_questions']!=100:p.error('This study requires exactly 100 fresh submissions per game')
    if args.suite in ('continual','all') and args.memory=='session':
        if config['session_mode']!='persistent' or config['player']['provider']=='codex_cli':
            p.error('--memory session requires persistent API Player sessions; select --memory transcript for Codex CLI')
    # Model/provider choices come entirely from the explicit configuration.
    # Freeze them below; never substitute a Codex model for an API provider.
    g=groups(selected,args.directions);blocks={};clargs=None;teamargs=None
    if args.source_puzzles!='all':
        sources=args.source_puzzles.split(',')
        available={entry['directed_pairs'][0][0] for entry in g['groups']}
        if args.suite=='team' or not sources or len(sources)!=len(set(sources)) or not set(sources)<=available:
            p.error('--source-puzzles must select unique CL source IDs from the selected sets/directions')
        g['groups']=[entry for entry in g['groups'] if entry['directed_pairs'][0][0] in sources]
        g['source_selection']=sources
    out=Path(args.out).resolve()
    if out.exists():p.error('Output directory exists; choose a new one')
    # Validate everything before creating output or spending model calls.
    for pid in bank:build_story_context(bank[pid])
    out.mkdir(parents=True)
    snap=snapshot(out,data,config,list(bank.values()))
    dump(snap/'configs/study_groups.json',g)
    common=['--dataset',str(snap/'data/dataset.json'),'--config',str(snap/'configs/run.json'),
      '--repeat',str(args.repeat),'--seed',str(args.seed),'--quiet','--on-error',args.on_error]
    jobs=[]
    if args.suite in ['continual','all']:
        clargs=argparse.Namespace(command='continual',groups=str(snap/'configs/study_groups.json'),group='all',pair=None,
           controls='answer_only',control_source=None,source_feedback='answer',source_policy=args.source_policy,memory=args.memory,repeat=args.repeat,seed=args.seed)
        blocks['continual']=make_plan(clargs,bank)
        jobs.append(dict(name='continual',argv=[sys.executable,str(snap/'scripts/experiment.py'),'continual',*common,
          '--groups',str(snap/'configs/study_groups.json'),'--group','all','--memory',args.memory,'--controls','answer_only',
          '--source-feedback','answer','--source-policy',args.source_policy,'--out',str(out/'continual')]))
        if args.import_direct:
            jobs[-1]['argv'].extend(['--import-direct',str(Path(args.import_direct).resolve())])
    if args.suite in ['team','all']:
        teamargs=argparse.Namespace(command='team',puzzle=','.join(teams),strategies=args.strategies,repeat=args.repeat,seed=args.seed)
        blocks['team']=make_plan(teamargs,bank)
        jobs.append(dict(name='team',argv=[sys.executable,str(snap/'scripts/experiment.py'),'team',*common,
          '--puzzle',','.join(teams),'--strategies',args.strategies,'--sync-interval',str(args.sync_interval),
          '--dialogue-roles',args.dialogue_roles,'--dialogue-scheduling',args.dialogue_scheduling,
          '--dialogue-max-discussion',str(args.dialogue_max_discussion),'--dialogue-start',args.dialogue_start,
          '--out',str(out/'team')]))
    for job in jobs:
        if args.mode=='dry-run':job['argv'].append('--dry-run')
    hashes={str(x.relative_to(snap)):hashlib.sha256(x.read_bytes()).hexdigest() for x in snap.rglob('*') if x.is_file()}
    dump(out/'snapshot_hashes.json',hashes)
    counts={name:planned_games(bs,name,args.source_policy) for name,bs in blocks.items()}
    dump(out/'study_plan.json',dict(mode=args.mode,arguments=vars(args),groups=g,blocks=blocks,planned_games=counts,jobs=jobs,
      trajectory_review_owners=OWNERS,config=config,dialogue_policy=dialogue,host_versions={pid:build_story_context(x)['binding_version'] for pid,x in bank.items()},
      interpretation='CL weights unchanged. Default fixed anchor B and one frozen A experience per source puzzle per batch. Source answer revealed after A; fresh 100 for every B. B repeats are conditional on the frozen A, not independent A samples. Reverse positive directions are exploratory. Relation labels never reach players.',
      controls=f'direct, {args.memory}+complete source answer, answer_only. Session protocol preserves original A roles and forks the same frozen prefix for each B. Neutral source pairs target the same anchor. No arbitrary reverse negative/neutral target.'))
    print(json.dumps({'out':str(out),'mode':args.mode,'games':counts},ensure_ascii=False),flush=True)
    if args.mode=='plan':return 0
    state=dict(pid=os.getpid(),status='running',completed=[],active=None,mode=args.mode);dump(out/'status.json',state)
    try:
        for job in jobs:
            # Refuse mutated snapshots before each batch. No implicit fallback to live inputs.
            if any(hashlib.sha256((snap/name).read_bytes()).hexdigest()!=sha for name,sha in hashes.items()):
                raise ValueError('Snapshot changed')
            state['active']=job['name'];dump(out/'status.json',state)
            with (out/(job['name']+'.log')).open('w') as log:
                child=subprocess.Popen(job['argv'],cwd=snap,stdout=log,stderr=subprocess.STDOUT)
                state['child_pid']=child.pid;dump(out/'status.json',state)
                code=child.wait()
            collect_costs(out,jobs)
            state['completed'].append(dict(batch=job['name'],exit_code=code));dump(out/'status.json',state)
            if code and args.on_error=='stop':
                state.update(status='stopped_on_error',active=None);dump(out/'status.json',state);return code
    except KeyboardInterrupt:
        if 'child' in locals() and child.poll() is None:
            import signal
            child.send_signal(signal.SIGINT)
            try:child.wait(timeout=15)
            except subprocess.TimeoutExpired:child.terminate()
        collect_costs(out,jobs)
        state.update(status='interrupted',active=None);dump(out/'status.json',state);return 130
    except Exception as exc:
        state.update(status='error',active=None,error=str(exc));dump(out/'status.json',state);raise
    state.update(status='completed' if all(x['exit_code']==0 for x in state['completed']) else 'completed_with_errors',active=None)
    dump(out/'status.json',state)
    return 0 if state['status']=='completed' else 1


if __name__=='__main__':raise SystemExit(main())
