#!/usr/bin/env python3
"""Continue a stopped single-batch study in a new archive-preserving directory."""
import argparse
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from turtle_loop.engine import dump
from scripts.study_20261102 import collect_costs


def prepare(source, out):
    source,out=Path(source).resolve(),Path(out).resolve()
    if out.exists() or source in out.parents:
        raise ValueError('Use a new output directory outside the original study')
    status=json.loads((source/'status.json').read_text())
    if status['status'] not in ('stopped_on_error','interrupted','error'):
        raise ValueError('Source study must be stopped')
    plan=json.loads((source/'study_plan.json').read_text())
    if len(plan['jobs'])!=1:
        raise ValueError('Resume each single-batch study separately')
    old_hashes=json.loads((source/'snapshot_hashes.json').read_text())
    for name,sha in old_hashes.items():
        if hashlib.sha256((source/'runtime_snapshot'/name).read_bytes()).hexdigest()!=sha:
            raise ValueError('Original frozen snapshot changed: '+name)
    # A resume must keep the original host/context policy. Never overlay today's
    # engine onto old reference selection or model code.
    old_engine=(source/'runtime_snapshot/turtle_loop/engine.py').read_text()
    old_experiments=(source/'runtime_snapshot/turtle_loop/experiments.py').read_text()
    if 'def restore(' not in old_engine or '--resume' not in old_experiments:
        raise ValueError('This frozen study predates resume support; use its archived compatible recovery code. '
                         'Current host/context changes cannot be mixed into an old game.')
    shutil.copytree(source,out,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    snap=out/'runtime_snapshot'
    changes={}
    job=plan['jobs'][0]
    argv=[v.replace(str(source),str(out)) for v in job['argv']]
    if '--resume' not in argv: argv.append('--resume')
    argv[0]=sys.executable
    hashes={str(p.relative_to(snap)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in snap.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    dump(out/'snapshot_hashes.json',hashes)
    dump(out/'study_plan.json',{**plan,'jobs':[{**job,'argv':argv}], 'resumed_from':str(source)})
    record={'source':str(source),'out':str(out),'batch':job['name'],'argv':argv,
            'controller_overlay':changes,'original_snapshot_hashes':old_hashes,
            'policy':'Original files retained; copied histories, quotas, costs and completed A preserved. Models, prompts, packs, scoring and order unchanged.'}
    dump(out/'resume_manifest.json',record)
    dump(out/'status.json',{'status':'prepared_resume','resumed_from':str(source),'completed':[],'active':None})
    return record


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--from-study',required=True)
    p.add_argument('--out',required=True)
    p.add_argument('--mode',choices=['plan','run'],default='plan')
    args=p.parse_args(argv)
    record=prepare(args.from_study,args.out)
    out=Path(record['out']);batch=record['batch']
    print(json.dumps(record,ensure_ascii=False),flush=True)
    if args.mode=='plan':return 0
    state={'pid':os.getpid(),'status':'running','active':batch,'completed':[], 'mode':'resume',
           'resumed_from':record['source']}
    dump(out/'status.json',state)
    with (out/(batch+'_resume.log')).open('w') as log:
        child=subprocess.Popen(record['argv'],cwd=out/'runtime_snapshot',stdout=log,stderr=subprocess.STDOUT)
        state['child_pid']=child.pid;dump(out/'status.json',state)
        try:
            code=child.wait()
        except KeyboardInterrupt:
            child.send_signal(signal.SIGINT)
            try:child.wait(timeout=15)
            except subprocess.TimeoutExpired:child.terminate();child.wait()
            code=130
    collect_costs(out,[{'name':batch}])
    state.update(status='completed' if code==0 else 'interrupted' if code==130 else 'stopped_on_error',
                 active=None,completed=[{'batch':batch,'exit_code':code}])
    dump(out/'status.json',state)
    return code


if __name__=='__main__':raise SystemExit(main())
