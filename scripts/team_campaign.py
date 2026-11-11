#!/usr/bin/env python3
"""Explicit worker slots, immutable studies, bounded parallel runs and merged results."""
import argparse
import csv
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.study_20261102 import main as prepare_study
from scripts.team_sweep import stop_owned_workers
from turtle_loop.cli import configuration
from turtle_loop.costs import merge_summaries
from turtle_loop.engine import dump
from turtle_loop.experiments import stats

SPEC=ROOT/'configs/team_campaign_20261111.json'


def catalogue(preset='full', positive='15'):
    spec=json.loads(SPEC.read_text());tasks=[]
    repeat=spec['repeats_per_slot'] if preset=='full' else 1
    for entry in spec['cl']:
        pos=entry['positive'] if entry['set']!=1 or positive=='15' else (
            [entry['optional_positive']] if positive=='16' else entry['positive']+[entry['optional_positive']])
        sources={p:relation for relation,ids in [('positive',pos),('negative',entry['negative']),('neutral',entry['neutral'])]
                 for p in ids if preset=='full' or relation=='positive'}
        for seat,owners in entry['slots'].items():
            tasks.append(dict(id=f"cl-set{entry['set']}-{seat}",kind='continual',set=entry['set'],
                target=entry['target'],sources=sources,slot=seat,suggested_runners=owners,
                repeat=repeat,repeat_offset=0 if seat=='a' else spec['repeats_per_slot'],
                conditions=spec['cl_conditions'],planned_games=len(sources)*(1+repeat*len(spec['cl_conditions']))))
    for entry in spec['mas']:
        for seat,owners in entry['slots'].items():
            tasks.append(dict(id=f"mas-{entry['puzzle'].lower()}-{seat}",kind='team',target=entry['puzzle'],
                slot=seat,suggested_runners=owners,review_owner=entry['review_owner'],repeat=repeat,
                repeat_offset=0 if seat=='a' else spec['repeats_per_slot'],
                conditions=spec['mas_strategies'],planned_games=repeat*len(spec['mas_strategies'])))
    return tasks


def select_tasks(tasks, selection):
    ids=selection.split(',') if selection!='all' else [t['id'] for t in tasks]
    bank={t['id']:t for t in tasks}
    if not ids or len(ids)!=len(set(ids)) or set(ids)-set(bank):
        raise ValueError('Select unique known task IDs (use list), or all only for one coordinator')
    return [bank[name] for name in ids]


def list_text(tasks):
    lines=['| Task | 建议执行人（候选二选一） | 目标B/题号 | A来源或策略 | 重复编号 | 局数 |',
           '| --- | --- | --- | --- | --- | ---: |']
    for t in tasks:
        source=', '.join(f'{p[2:]}:{r}' for p,r in t.get('sources',{}).items()) if t['kind']=='continual' else ', '.join(t['conditions'])
        repeats=','.join(str(i+t['repeat_offset']) for i in range(1,t['repeat']+1))
        lines.append('| '+' | '.join([t['id'],' / '.join(t['suggested_runners']),t['target'],source,repeats,str(t['planned_games'])])+' |')
    return '\n'.join(lines)+f"\n\nTotal: {sum(t['planned_games'] for t in tasks)} games.\n"


def verify(snapshot, hashes):
    if any(not (snapshot/name).is_file() or hashlib.sha256((snapshot/name).read_bytes()).hexdigest()!=sha
           for name,sha in hashes.items()):
        raise ValueError('Frozen snapshot changed; no further calls allowed')


def common_hash(hashes):
    # Groups and scheduling differ across slots; model, story, code and prompts must not.
    common={k:v for k,v in hashes.items() if k.startswith(('turtle_loop/','prompts/','data/'))
            or k in ('configs/run.json','configs/host_bindings.json','configs/player_format_repair.json')}
    return hashlib.sha256(json.dumps(common,sort_keys=True).encode()).hexdigest()


def prepare(args):
    definition=SPEC.read_bytes()
    tasks=select_tasks(catalogue(args.preset,args.set1_positive),args.tasks)
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,64}',args.runner):raise ValueError('runner must be a short letters/digits/_/- ID')
    if not 1<=args.workers<=12 or not 1<=args.poll_seconds<=30:raise ValueError('workers 1..12; poll-seconds 1..30')
    config=configuration(argparse.Namespace(config=args.config,dry_run=args.mode!='run'))
    if config['max_questions']!=100 or config['session_mode']!='persistent':raise ValueError('Campaign requires persistent sessions and 100 submissions')
    if any(t['kind']=='continual' for t in tasks) and config['player']['provider']=='codex_cli':
        raise ValueError('Raw CL session campaign requires an API Player')
    out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=False)
    jobs=[]
    for t in tasks:
        folder=out/'tasks'/t['id']
        seed=args.seed+next(i for i,x in enumerate(catalogue('full',args.set1_positive)) if x['id']==t['id'])
        argv=['--suite',t['kind'],'--repeat',str(t['repeat']),'--seed',str(seed),'--config',str(Path(args.config).resolve()),
              '--dataset',str(Path(args.dataset).resolve()),'--mode','plan','--on-error','stop','--out',str(folder)]
        if t['kind']=='continual':
            argv+=['--sets',str(t['set']),'--source-puzzles',','.join(t['sources']),'--directions','primary',
                   '--memory','session','--source-policy','fixed']
        else:
            argv+=['--team-puzzles',t['target'],'--strategies',','.join(t['conditions']),
                '--dialogue-roles','complementary','--dialogue-scheduling','adaptive',
                '--dialogue-max-discussion','4','--dialogue-start','A']
        if prepare_study(argv):raise ValueError('Failed to prepare '+t['id'])
        plan=json.loads((folder/'study_plan.json').read_text())
        if sum(plan['planned_games'].values())!=t['planned_games'] or len(plan['jobs'])!=1:
            raise ValueError('Unexpected study size or suites')
        job=plan['jobs'][0];command=job['argv'][:]
        if args.mode=='dry-run':command+=['--dry-run']
        plan.update(mode=args.mode,arguments={**plan['arguments'],'mode':args.mode},jobs=[{**job,'argv':command}])
        dump(folder/'study_plan.json',plan)
        dump(folder/'assignment.json',{**t,'runner':args.runner,'preset':args.preset})
        dump(folder/'status.json',{'status':'prepared','active':None})
        hashes=json.loads((folder/'snapshot_hashes.json').read_text())
        jobs.append({**t,'folder':str(folder.relative_to(out)),'argv':command,'hashes':hashes,
                     'protocol_hash':common_hash(hashes)})
    if len({j['protocol_hash'] for j in jobs})!=1:raise ValueError('Code, models or stories changed during preparation')
    gate=None
    if args.host_gate=='auto' and any(t.get('set')==1 for t in tasks):
        snap=out/jobs[0]['folder']/'runtime_snapshot'
        for src,dest in [('scripts/check_host.py','scripts/check_host.py'),
                         ('configs/host_regression_set1_v11.json','configs/campaign_host_gate.json')]:
            shutil.copy2(ROOT/src,snap/dest)
            jobs[0]['hashes'][dest]=hashlib.sha256((snap/dest).read_bytes()).hexdigest()
        dump(out/jobs[0]['folder']/'snapshot_hashes.json',jobs[0]['hashes'])
        gate={'snapshot':str(snap.relative_to(out)),'checks':20,'argv':[sys.executable,str(snap/'scripts/check_host.py'),
            '--dataset',str(snap/'data/dataset.json'),'--config',str(snap/'configs/run.json'),
            '--cases',str(snap/'configs/campaign_host_gate.json'),'--repeat','1','--out',str(out/'host_gate')]}
    if SPEC.read_bytes()!=definition:raise ValueError('Campaign definition changed during preparation')
    dump(out/'campaign_definition.json',json.loads(definition))
    manifest={'schema_version':1,'arguments':vars(args),'preset':args.preset,'runner':args.runner,'jobs':jobs,
        'design_hash':hashlib.sha256(definition+args.set1_positive.encode()).hexdigest(),
        'planned_games':sum(t['planned_games'] for t in tasks),'protocol_hash':jobs[0]['protocol_hash'],
        'host_gate':gate,'catalogue':catalogue(args.preset,args.set1_positive),
        'source_policy':'A fixed within each slot batch; separate people/slots produce separate A prefixes. Two B repeats per prefix, no resampling for success.',
        'repeat_policy':'a maps to 1/2; b maps to 3/4. Seed schedules order only. Smoke results are excluded from full collection.'}
    dump(out/'campaign.json',manifest)
    (out/'experiments.md').write_text(list_text(tasks))
    dump(out/'status.json',{'status':'prepared','tasks':{t['id']:'planned' for t in tasks}})
    report(out)
    return out,manifest


def rows_for(out,manifest):
    rows=[]
    for task in manifest['jobs']:
        path=out/task['folder']/task['kind']/'experiment_runs.json'
        for row in json.loads(path.read_text()) if path.exists() else []:
            # Batch rows are finalized only after a whole game. The per-game
            # result is atomically refreshed after each turn and owns live usage.
            result=path.parent/row['run_dir']/'result.json'
            if result.exists():row={**row,**json.loads(result.read_text())}
            source=row['condition'] in ('source','control_source')
            rows.append({**row,'task_id':task['id'],'runner':manifest['runner'],'slot':task['slot'],
                'kind':task['kind'],'set':task.get('set'),'preset':manifest['preset'],
                'global_repeat':None if source else row['repeat']+task['repeat_offset'],
                'run_id':task['id']+':'+row['run_dir'],
                'run_dir':str(Path(task['folder'])/task['kind']/row['run_dir'])})
    return rows


def csv_rows(path,rows,fields):
    with path.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)


def report(out,manifests=None):
    out=Path(out)
    sources=manifests or [(out,json.loads((out/'campaign.json').read_text()))]
    rows=[];seen=set();seen_tasks=set();summaries=[]
    for root,manifest in sources:
        for job in manifest['jobs']:
            if job['id'] in seen_tasks:raise ValueError('Duplicate task slot across inputs: '+job['id'])
            seen_tasks.add(job['id'])
        for row in rows_for(root,manifest):
            if row['run_id'] in seen:raise ValueError('Duplicate rollout: '+row['run_id'])
            seen.add(row['run_id'])
            if root!=out:row['run_dir']=os.path.relpath(root/row['run_dir'],out)
            rows.append(row)
        gate=root/'host_gate/cost_summary.json'
        if gate.exists():summaries.append(json.loads(gate.read_text()))
    summaries += [r['costs'] for r in rows if r.get('costs')]
    dump(out/'cost_summary.json',merge_summaries(summaries))
    dump(out/'experiment_runs.json',rows)
    csv_rows(out/'experiment_runs.csv',rows,['run_id','task_id','runner','kind','set','source','target','condition',
        'global_repeat','status','success','counted_questions','submissions','final_partial_score','source_context_sha256','run_dir'])
    grouped=defaultdict(list)
    for row in rows:grouped[(row['kind'],row.get('set'),row.get('source'),row['target'],row['condition'])].append(row)
    performance=[]
    for key,local in grouped.items():
        done=[r for r in local if r['status']=='completed']
        performance.append(dict(zip(('kind','set','source','target','condition'),key),
            completed=len(done),recorded=len(local),successes=sum(r['success'] is True for r in done),
            success_rate=sum(r['success'] is True for r in done)/len(done) if done else None,
            global_repeats=sorted({r['global_repeat'] for r in done if r['global_repeat'] is not None}),
            expected_full_repeats=[1,2,3,4] if sources[0][1]['preset']=='full' and key[-1] not in ('source','control_source') else None,
            question_consumption=stats([r['counted_questions'] for r in done]),
            solved_question_count=stats([r['counted_questions'] for r in done if r['success']]),
            partial_score=stats([r['final_partial_score'] for r in done if r.get('final_partial_score') is not None]),
            source_prefix_hashes=sorted({r['source_context_sha256'] for r in local if r.get('source_context_sha256')})))
    dump(out/'performance.json',performance)
    expected=sum(m['planned_games'] for _,m in sources)
    progress={'planned_games':expected,'recorded_games':len(rows),
        'completed_games':sum(r['status']=='completed' for r in rows),
        'dry_run_games':sum(r['status']=='dry_run' for r in rows),
        'invalid_games':sum(r['status'] in ('error','interrupted','needs_review') for r in rows),
        'selected_tasks':sorted(seen_tasks),'missing_campaign_slots':sorted({t['id'] for t in sources[0][1]['catalogue']}-seen_tasks),
        'updated_at':time.time(),'source_policy':sources[0][1]['source_policy']}
    dump(out/'progress.json',progress)
    links=''.join('<tr>'+''.join('<td>'+html.escape(str(r.get(k,'')))+'</td>' for k in
        ('task_id','global_repeat','condition','status','counted_questions','final_partial_score'))+
        '<td><a href="'+html.escape(r['run_dir']+'/trajectory.html',quote=True)+'">trajectory</a></td></tr>' for r in rows)
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Team campaign</title>'
        '<h1>Team campaign</h1><p>Recorded '+str(len(rows))+'/'+str(expected)+' games.</p>'
        '<p><a href="status.json">Status</a> · <a href="experiments.md">Plan</a> · <a href="performance.json">Performance</a> · '
        '<a href="cost_summary.json">Token costs</a> · <a href="experiment_runs.csv">CSV</a></p>'
        '<table border="1"><tr><th>Task</th><th>Repeat</th><th>Condition</th><th>Status</th><th>Questions</th><th>Score</th><th>View</th></tr>'+links+'</table>')
    return rows


def execute(out,manifest):
    active={};exited={};pending=list(manifest['jobs']);state={'pid':os.getpid(),'status':'running',
        'tasks':{j['id']:'planned' for j in pending},'active':{},'max_active_workers':0}
    args=manifest['arguments'];failed=False
    def event(kind,**values):
        with (out/'events.jsonl').open('a') as stream:
            stream.write(json.dumps({'time':time.time(),'event':kind,**values})+'\n')
    def save():dump(out/'status.json',state);report(out)
    def start(identifier,argv,folder):
        log=(out/(identifier+'.log')).open('w')
        try:process=subprocess.Popen(argv,cwd=folder,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        except BaseException:log.close();raise
        active[identifier]=(process,log);state['active'][identifier]=process.pid
        state['max_active_workers']=max(state['max_active_workers'],len(active))
        event('process_started',task=identifier,pid=process.pid,active_count=len(active))
        return process
    try:
        gate=manifest['host_gate']
        if gate and args['mode']=='run':
            verify(out/manifest['jobs'][0]['folder']/'runtime_snapshot',manifest['jobs'][0]['hashes'])
            proc=start('host_gate',gate['argv'],out/gate['snapshot']);save()
            code=proc.wait();active.pop('host_gate')[1].close();state['active'].pop('host_gate')
            result=out/'host_gate/summary.json';summary=json.loads(result.read_text()) if result.exists() else {}
            if code or summary.get('passed')!=gate['checks'] or summary.get('completed_calls')!=gate['checks'] or summary.get('errors'):
                state.update(status='stopped_on_host_gate');save();return 1
            state['host_gate_passed']=True
        while pending or active:
            while pending and len(active)<args['workers']:
                job=pending.pop(0);folder=out/job['folder'];verify(folder/'runtime_snapshot',job['hashes'])
                proc=start(job['id'],job['argv'],folder/'runtime_snapshot')
                state['tasks'][job['id']]='running'
                dump(folder/'status.json',{'status':'running','child_pid':proc.pid,'active':job['kind']})
                save()
            for identifier,(proc,log) in list(active.items()):
                code=proc.poll()
                if code is None:continue
                log.close();del active[identifier];state['active'].pop(identifier)
                event('process_finished',task=identifier,exit_code=code,active_count=len(active))
                job=next(j for j in manifest['jobs'] if j['id']==identifier)
                rows=rows_for(out,{**manifest,'jobs':[job]})
                valid='dry_run' if args['mode']=='dry-run' else 'completed'
                complete=not code and len(rows)==job['planned_games'] and all(r['status']==valid for r in rows)
                failed|=not complete
                state['tasks'][identifier]='completed' if complete else 'error'
                dump(out/job['folder']/'status.json',{'status':'completed' if complete else 'stopped_on_error',
                    'active':None,'exit_code':code,'completed':[{'batch':job['kind'],'exit_code':code}]})
                if not complete and args['on_error']=='stop':
                    state['status']='stopped_on_error';save();return 1
            save()
            if active:time.sleep(args['poll_seconds'])
        state['status']='completed_with_errors' if failed else 'completed';return int(failed)
    except KeyboardInterrupt:
        state['status']='interrupted';return 130
    except Exception as exc:
        state.update(status='error',error=str(exc));raise
    finally:
        cancelled=list(active);stop_owned_workers(active,exited)
        for identifier in cancelled:
            state['active'].pop(identifier,None)
            event('process_cancelled',task=identifier)
            if identifier in state['tasks']:
                state['tasks'][identifier]='cancelled'
                job=next(j for j in manifest['jobs'] if j['id']==identifier)
                dump(out/job['folder']/'status.json',{'status':'interrupted','active':None})
        save()


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    listing=sub.add_parser('list');listing.add_argument('--preset',choices=['smoke','full'],default='full')
    listing.add_argument('--set1-positive',choices=['15','16','both'],default='15')
    start=sub.add_parser('start')
    start.add_argument('--preset',choices=['smoke','full'],default='smoke')
    start.add_argument('--runner',required=True,help='Actual person ID; metadata only, never sent to solvers')
    start.add_argument('--tasks',required=True,help='Comma-separated task slots from list; all for ONE coordinator only')
    start.add_argument('--workers',type=int,default=2,help='Concurrent independent slot batches, 1..12')
    start.add_argument('--set1-positive',choices=['15','16','both'],default='15')
    start.add_argument('--config',default=str(ROOT/'configs/loop.deepseek.json'))
    start.add_argument('--dataset',default=str(ROOT/'data/annotations/turtle50_v4/private.json'))
    start.add_argument('--seed',type=int,default=20261111,help='Scheduling only; not API sampling')
    start.add_argument('--host-gate',choices=['auto','none'],default='auto',help='auto: 20 Set1 diagnostics if selecting CL Set1; other sets are not thereby validated')
    start.add_argument('--on-error',choices=['stop','continue'],default='stop',help='After a slot failure stop own workers, or continue other independent slots. Failed games never regenerated.')
    start.add_argument('--poll-seconds',type=float,default=2)
    start.add_argument('--mode',choices=['plan','dry-run','run'],default='plan')
    start.add_argument('--out',required=True)
    collect=sub.add_parser('collect');collect.add_argument('--inputs',nargs='+',required=True)
    collect.add_argument('--out',required=True)
    args=parser.parse_args(argv)
    try:
        if args.command=='list':print(list_text(catalogue(args.preset,args.set1_positive)));return 0
        if args.command=='collect':
            paths=[Path(p).resolve() for p in args.inputs]
            manifests=[(p,json.loads((p/'campaign.json').read_text())) for p in paths]
            if len({(m['preset'],m['protocol_hash'],m.get('design_hash'),m.get('arguments',{}).get('mode')) for _,m in manifests})!=1:
                raise ValueError('Do not mix smoke/full, dry/live, positive-source choices or code/model/story versions')
            task_ids=[j['id'] for _,m in manifests for j in m['jobs']]
            if len(task_ids)!=len(set(task_ids)):raise ValueError('Duplicate task slot; choose one audited rollout, never count reruns twice')
            out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=False)
            report(out,manifests);dump(out/'collection.json',{'inputs':list(map(str,paths))})
            (out/'experiments.md').write_text(list_text([j for _,m in manifests for j in m['jobs']]))
            dump(out/'status.json',{'status':'collected','inputs':list(map(str,paths))});return 0
        out,manifest=prepare(args)
        print(list_text(manifest['jobs']),flush=True)
        return execute(out,manifest) if args.mode!='plan' else 0
    except (ValueError,KeyError,OSError) as exc:
        print('Cannot run campaign:',exc,file=sys.stderr);return 2


if __name__=='__main__':raise SystemExit(main())
