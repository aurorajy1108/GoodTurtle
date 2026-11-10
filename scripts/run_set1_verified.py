#!/usr/bin/env python3
"""Freeze Set 1 once, pass a Host diagnostic gate, then run 12 fresh CL games."""
import argparse
import hashlib
import json
import shutil
import signal
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.study_20261102 import main as prepare_study, collect_costs
from turtle_loop.engine import dump
from turtle_loop.costs import merge_summaries
from turtle_loop.providers import resolve_env, validate_profile


def prepare(out, config, dataset, seed):
    out = Path(out).resolve()
    if out.exists():
        raise ValueError('Output exists; choose a new directory. No overwrite or old-prefix reuse.')
    out.mkdir(parents=True)
    study = out/'study'
    code = prepare_study(['--suite','continual','--sets','1',
        '--source-puzzles','TS015,TS014,TS028','--directions','primary',
        '--source-policy','fixed','--repeat','1','--seed',str(seed),
        '--config',str(Path(config).resolve()),'--dataset',str(Path(dataset).resolve()),
        '--on-error','stop','--mode','plan','--out',str(study)])
    if code:
        raise ValueError('Could not freeze study')
    snap = study/'runtime_snapshot'
    shutil.copy2(ROOT/'scripts/check_host.py',snap/'scripts/check_host.py')
    shutil.copy2(ROOT/'configs/host_regression_set1_v11.json',snap/'configs/host_regression.json')
    hashes = {str(p.relative_to(snap)):hashlib.sha256(p.read_bytes()).hexdigest()
              for p in snap.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    dump(study/'snapshot_hashes.json',hashes)
    plan = json.loads((study/'study_plan.json').read_text())
    if plan['planned_games'] != {'continual':12}:
        raise ValueError('Unexpected study size')
    gate = [sys.executable,str(snap/'scripts/check_host.py'),
        '--dataset',str(snap/'data/dataset.json'),'--config',str(snap/'configs/run.json'),
        '--cases',str(snap/'configs/host_regression.json'),'--repeat','1',
        '--out',str(out/'host_gate')]
    manifest = {'host_gate_argv':gate,'study_jobs':plan['jobs'],'planned_games':12,
        'planned_host_checks':len(json.loads((snap/'configs/host_regression.json').read_text())),
        'host_versions':plan['host_versions'],'source_puzzles':['TS015','TS014','TS028'],
        'target':'TS013','repeat':1,'source_policy':'fixed',
        'conditions':['direct','transcript','answer_only'],
        'source_answer_revealed':True,'fresh_budget_per_game':100,
        'host_gate_interpretation':'Source-grounded development diagnostics, not held-out host accuracy.',
        'old_trajectories_reused':False,'snapshot_hashes':hashes}
    dump(out/'run_manifest.json',manifest)
    dump(out/'status.json',{'status':'prepared','phase':None})
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Set 1 v11</title>'
        '<h1>Set 1</h1><p><a href="status.json">Status</a></p>'
        '<p><a href="host_gate/summary.json">Host diagnostic results</a></p>'
        '<p><a href="study/continual/index.html">CL trajectories</a></p>'
        '<p><a href="cost_summary.json">Combined recorded token costs</a></p>')
    return manifest


def execute(out, manifest):
    out = Path(out).resolve(); study = out/'study'; snap = study/'runtime_snapshot'
    state = {'status':'running','phase':None}
    child = None
    def check_snapshot():
        for name, sha in manifest['snapshot_hashes'].items():
            if hashlib.sha256((snap/name).read_bytes()).hexdigest() != sha:
                raise ValueError('Frozen input changed: '+name)
    def job(phase, argv):
        nonlocal child
        check_snapshot();state.update(phase=phase);dump(out/'status.json',state)
        with (out/(phase+'.log')).open('w') as log:
            child = subprocess.Popen(argv,cwd=snap,stdout=log,stderr=subprocess.STDOUT)
            state['child_pid']=child.pid;dump(out/'status.json',state)
            return child.wait()
    def costs():
        collect_costs(study,manifest['study_jobs'])
        summaries=[]
        for file in (out/'host_gate/cost_summary.json',study/'cost_summary.json'):
            if file.exists():summaries.append(json.loads(file.read_text()))
        dump(out/'cost_summary.json',merge_summaries(summaries))
    try:
        code=job('host_gate',manifest['host_gate_argv'])
        costs()
        if code:
            state.update(status='stopped_on_host_gate',exit_code=code)
            return code
        summary=json.loads((out/'host_gate/summary.json').read_text())
        if (summary['completed_calls'] != manifest['planned_host_checks']
                or summary['passed'] != manifest['planned_host_checks'] or summary['errors']):
            raise ValueError('Host gate incomplete; refusing CL games')
        state['host_gate_passed']=True
        code=job('continual',manifest['study_jobs'][0]['argv'])
        costs()
        if code == 0:
            runs=json.loads((study/'continual/experiment_runs.json').read_text())
            if len(runs)!=manifest['planned_games'] or any(r['status']!='completed' for r in runs):
                raise ValueError('CL exited without completing the planned games')
            state['completed_games']=len(runs)
        state.update(status='completed' if code==0 else 'stopped_on_error',exit_code=code)
        return code
    except KeyboardInterrupt:
        if child is not None and child.poll() is None:
            child.send_signal(signal.SIGINT)
            try:child.wait(timeout=15)
            except subprocess.TimeoutExpired:child.terminate();child.wait()
        costs();state.update(status='interrupted',exit_code=130)
        return 130
    except Exception:
        state.update(status='error')
        raise
    finally:
        dump(out/'status.json',state)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',required=True,help='New root directory; never resume or overwrite')
    p.add_argument('--mode',choices=['plan','run'],default='plan',help='plan freezes only; run gates and executes')
    p.add_argument('--config',default=str(ROOT/'configs/loop.deepseek.json'),help='Host/player/grader profiles, copied into snapshot')
    p.add_argument('--dataset',default=str(ROOT/'data/annotations/turtle50_v4/private.json'),help='Private dataset, copied into snapshot')
    p.add_argument('--seed',type=int,default=20261102,help='Scheduling seed only, not model sampling seed')
    args=p.parse_args(argv)
    if args.mode=='run':
        config=resolve_env(json.loads(Path(args.config).read_text()))
        for role in ('host','player','grader'):validate_profile(config[role])
    manifest=prepare(args.out,args.config,args.dataset,args.seed)
    print(json.dumps({'out':str(Path(args.out).resolve()),'mode':args.mode,
                      'host_checks':manifest['planned_host_checks'],'cl_games':12}),flush=True)
    return execute(args.out,manifest) if args.mode=='run' else 0


if __name__=='__main__':raise SystemExit(main())
