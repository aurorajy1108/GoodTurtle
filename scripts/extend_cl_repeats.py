#!/usr/bin/env python3
"""Extend a completed fixed-prefix CL study without rerunning A or old B games."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from turtle_loop.engine import dump
from turtle_loop.dataset import load_dataset
from turtle_loop.experiments import make_plan,planned_games
from scripts.team_campaign import execute,common_hash,report
from scripts.supervise_campaign import notify


def read(path):return json.loads(Path(path).read_text())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare(reference,out,total_repeats=4):
    reference,out=Path(reference).resolve(),Path(out).resolve()
    if out.exists() or reference in out.parents:
        raise ValueError('Use a new output folder outside the original study')
    study_plan=read(reference/'study_plan.json')
    old_plan=read(reference/'continual/plan.json')
    old_rows=read(reference/'continual/experiment_runs.json')
    if (len(study_plan['jobs'])!=1 or study_plan['jobs'][0]['name']!='continual'
            or old_plan['source_policy']!='fixed' or old_plan['arguments']['memory']!='session'
            or any(r['status']!='completed' or r.get('simulation') for r in old_rows)):
        raise ValueError('Require a completed, real fixed-source raw-session CL study')
    old_repeats=old_plan['arguments']['repeat']
    if type(total_repeats) is not int or not old_repeats<total_repeats<=20:
        raise ValueError('Total repeats must exceed existing repeats, at most 20')
    original_hashes=read(reference/'snapshot_hashes.json')
    for name,digest in original_hashes.items():
        if sha(reference/'runtime_snapshot'/name)!=digest:
            raise ValueError('Original frozen snapshot changed: '+name)
    out.mkdir(parents=True)
    study=out/'study'
    shutil.copytree(reference,study,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    snapshot=study/'runtime_snapshot'
    overlay={}
    for name in ('turtle_loop/action_text.py','turtle_loop/experiments.py'):
        dest=snapshot/name
        overlay[name]={'before':sha(dest),'after':sha(ROOT/name)}
        shutil.copy2(ROOT/name,dest)
    # The user runs every model interface on DeepSeek. Legacy optional Codex
    # formatting is unnecessary for a unique typed action and must not be used.
    name='configs/player_format_repair.json'
    policy_path=snapshot/name
    if policy_path.exists():
        before=sha(policy_path)
        policy=read(policy_path)
        policy['max_codex_calls_per_game']=0
        dump(policy_path,policy)
        overlay[name]={'before':before,'after':sha(policy_path),
                       'reason':'Local verbatim recovery; no auxiliary Codex model calls'}
    # Models, Host/Grader code, prompts, private data, reference packs, retrieval,
    # pricing and limits retain their original bytes. No Host changes are made.
    for name,digest in original_hashes.items():
        if name not in overlay and sha(snapshot/name)!=digest:
            raise ValueError('Unapproved extension change: '+name)
    args=deepcopy(old_plan['arguments'])
    args.update(repeat=total_repeats,out=str(study/'continual'),resume=True,
                dataset=str(snapshot/'data/dataset.json'),config=str(snapshot/'configs/run.json'),
                groups=str(snapshot/'configs/study_groups.json'))
    bank={p['id']:p for p in load_dataset(args['dataset'])['puzzles']}
    blocks=make_plan(argparse.Namespace(**args),bank)
    block_map={b['block']:b for b in blocks}
    for block in old_plan['blocks']:
        updated=block_map.get(block['block'])
        if not updated or any(updated.get(k)!=block.get(k) for k in
                              ('source','target','repeat','conditions','source_policy')):
            raise ValueError('Existing condition definitions/order changed')
    sources={b['source'] for b in blocks}
    if (len([r for r in old_rows if r['condition']=='source'])!=len(sources)
            or {r['puzzle_id'] for r in old_rows if r['condition']=='source'}!=sources):
        raise ValueError('Missing or duplicate original A checkpoint')
    total=planned_games(blocks,'continual','fixed')
    preserved={r['run_dir']:{name:sha(study/'continual'/r['run_dir']/name) for name in
                    ('puzzle_private.json','prompts.json','api_calls.jsonl','trajectory.jsonl')}
               for r in old_rows}
    dump(study/'continual/plan.json',{**old_plan,'arguments':args,'blocks':blocks,
        'extension':{'original_study':str(reference),'original_repeats':old_repeats,
                     'total_repeats':total_repeats,'preserved_games':len(old_rows),'new_games':total-len(old_rows)}})
    argv=[s.replace(str(reference),str(study)) for s in study_plan['jobs'][0]['argv']]
    argv[0]=sys.executable
    argv[1]=str(snapshot/'scripts/experiment.py')
    # Assign owned paths explicitly: /var and /private/var aliases on macOS
    # otherwise defeat a plain string replacement and can point at the archive.
    for flag,key in (('--dataset','dataset'),('--config','config'),('--groups','groups'),('--out','out')):
        argv[argv.index(flag)+1]=args[key]
    argv[argv.index('--repeat')+1]=str(total_repeats)
    if '--resume' not in argv:argv.append('--resume')
    job={'name':'continual','argv':argv}
    dump(study/'study_plan.json',{**study_plan,'arguments':{**study_plan['arguments'],'repeat':total_repeats,'out':str(study)},
         'jobs':[job],'planned_games':{'continual':total},'extended_from':str(reference)})
    hashes={str(p.relative_to(snapshot)):sha(p) for p in snapshot.rglob('*')
            if p.is_file() and '__pycache__' not in p.parts}
    dump(study/'snapshot_hashes.json',hashes)
    dump(study/'status.json',{'status':'prepared_extension','active':None})
    task={'id':f'cl-set1-fixed-prefix-r1r{total_repeats}','kind':'continual','set':1,'target':'TS013','slot':'extension',
          'repeat':total_repeats,'repeat_offset':0,'folder':'study','argv':argv,'hashes':hashes,
          'protocol_hash':common_hash(hashes),'planned_games':total}
    manifest={'schema_version':1,'arguments':{'mode':'run','workers':1,'poll_seconds':10,'on_error':'stop'},
        'preset':'fixed-prefix-extension','runner':'jiayang','jobs':[task],'host_gate':None,
        'planned_games':total,'protocol_hash':task['protocol_hash'],'catalogue':[task],
        'source_policy':'Reuse the exact original A per puzzle for every B repeat; new B quotas are 100.',
        'repeat_policy':f'Preserve repeats 1..{old_repeats}; run only new repeats {old_repeats+1}..{total_repeats}.',
        'extension':{'reference':str(reference),'old_repeats':old_repeats,'total_repeats':total_repeats,
                     'preserved_games':len(old_rows),'new_games':total-len(old_rows),
                     'controller_overlay':overlay,'preserved_files':preserved,
                     'cost_policy':'Use this latest archive once. Do not add its copied historical costs to the original study costs again.'}}
    dump(out/'campaign.json',manifest)
    dump(out/'status.json',{'status':'prepared','active':{},'planned_games':total})
    (out/'experiments.md').write_text(f'# CL fixed-prefix repeat extension\n\n'
        f'{len(old_rows)} preserved games; {total-len(old_rows)} new games; {total} total. '
        f'Each condition reaches {total_repeats} repeats. A is never regenerated. '
        'Host, Grader, models, rubric, prompts and quota unchanged. Only typed-action parsing and fixed-A checkpoint selection change.\n\n'
        'Historical rows retain their original parser version. New repetitions use the recorded format overlay; report that cohort difference.\n')
    report(out)
    return manifest


def run(out):
    out=Path(out).resolve()
    import fcntl
    with (out/'launcher.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        manifest=read(out/'campaign.json')
        if read(out/'status.json')['status'] not in ('prepared',):
            raise ValueError('Existing run already started; resume its checked checkpoint instead')
        code=execute(out,manifest)
        if code:
            notify(out,'CL extension stopped','Checking the saved checkpoint; observed games and fixed A will be retained.')
            return subprocess.call([sys.executable,str(ROOT/'scripts/supervise_campaign.py'),
                '--campaign',str(out),'--out',str(out)+'_supervised','--interval','30',
                '--cooldown','60','--max-recoveries','3','--stall-seconds','2700','--notify','macos'],cwd=ROOT)
        notify(out,'CL extension complete','Set1 has completed four repeats per condition; all original A prefixes were reused.')
        return 0


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['prepare','run'])
    parser.add_argument('--reference',help='Completed frozen study folder, not campaign or individual game')
    parser.add_argument('--out',required=True,help='New campaign folder for prepare; existing prepared folder for run')
    parser.add_argument('--total-repeats',type=int,default=4,help='Cumulative repeats including preserved old games')
    args=parser.parse_args(argv)
    if args.command=='prepare':
        if not args.reference:parser.error('prepare requires --reference')
        result=prepare(args.reference,args.out,args.total_repeats)
        print(json.dumps({k:result['extension'][k] for k in ('preserved_games','new_games','total_repeats')}))
        return 0
    return run(args.out)


if __name__=='__main__':raise SystemExit(main())
