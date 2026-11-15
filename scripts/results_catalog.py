#!/usr/bin/env python3
"""List, validate and summarize canonical result archives; never call a model."""
import argparse
import csv
import gzip
import hashlib
import json
import statistics
import subprocess
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[1]


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def write_json(p,value):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def summarize(rows):
    groups=defaultdict(list)
    for r in rows:
        if r.get('role')!='target' or not r.get('primary',True) or r.get('duplicate_of'):
            continue
        source=r.get('source') if r['condition'] in ('answer_only','session') else None
        groups[(r['suite'],r['puzzle'],r['condition'],source)].append(r)
    result=[]
    for key,group in sorted(groups.items(),key=lambda item:tuple(str(k) for k in item[0])):
        complete=[r for r in group if r['status']=='completed']
        scores=[r['score'] for r in complete if r.get('score') is not None]
        result.append(dict(zip(('cohort','puzzle','condition','source'),key),
            n_completed=len(complete),n_incomplete=len(group)-len(complete),
            solved=sum(bool(r.get('success')) for r in complete),
            score_mean=statistics.mean(scores) if scores else None,
            score_sample_sd=statistics.stdev(scores) if len(scores)>1 else None,
            submissions_mean=statistics.mean(r['submissions'] for r in complete) if complete else None))
    return result


def locate(name,root=ROOT):
    root=Path(root).resolve()
    value=Path(name)
    if value.is_absolute() or '..' in value.parts:
        raise ValueError('Use a repository-relative path without ..')
    source=root/value
    if source.exists():
        return str(value)
    layout=read(root/'results/layout_migration.json')
    dest=layout.get('file_moves',{}).get(str(value))
    if dest and (root/dest).exists():
        return dest
    for old,new in sorted(layout.get('folder_moves',{}).items(),key=lambda x:-len(x[0])):
        if str(value)==old or str(value).startswith(old+'/'):
            candidate=new+str(value)[len(old):]
            if (root/candidate).exists():
                return candidate
    archive_index=root/layout.get('archive_file_index','results/archive_files.json.gz')
    if archive_index.exists():
        with gzip.open(archive_index,'rt') as f:index=json.load(f)
        if str(value) in index:
            return 'https://github.com/aurorajy1108/GoodTurtle/blob/'+layout['archive_commit']+'/'+quote(str(value))
    check=subprocess.run(['git','cat-file','-e',layout['archive_commit']+':'+str(value)],
                         cwd=root,capture_output=True)
    if check.returncode==0:
        return 'https://github.com/aurorajy1108/GoodTurtle/blob/'+layout['archive_commit']+'/'+quote(str(value))
    raise ValueError('No current file or archived file found for this path')


def validate(root=ROOT):
    root=Path(root);rows=read(root/'results/catalog.json');seen=set();checked=0;submissions=0
    for r in rows:
        if r['id'] in seen:raise ValueError('Duplicate catalog ID: '+r['id'])
        seen.add(r['id']);folder=(root/r['path']).resolve()
        if not folder.is_relative_to((root/'results/trajectories').resolve()):raise ValueError('Result path escapes canonical directory')
        metadata=read(folder/'archive_metadata.json')
        for name,h in metadata['source_files_sha256'].items():
            if Path(name).name!=name:raise ValueError('Unsafe frozen filename')
            omission=metadata.get('release_omitted_presentations',{}).get(name)
            if omission:
                allowed={'trajectory.html':'trajectory.md','shared_dialogue.html':'shared_dialogue.md','self_review.html':'self_review.md'}
                if name not in allowed or omission.get('replacement')!=allowed[name]:
                    raise ValueError('Invalid presentation omission')
                if (folder/name).exists() or not (folder/allowed[name]).is_file():
                    raise ValueError('Presentation replacement missing or old HTML retained')
                continue
            if name.endswith('.html') and name in metadata.get('presentation_changes',{}):
                expected=metadata['published_files_sha256'][name]
            else:expected=h
            if digest(folder/name)!=expected:raise ValueError(f'Frozen file changed: {r["id"]}/{name}')
            checked+=1
        events=[json.loads(l) for l in (folder/'trajectory.jsonl').read_text().splitlines() if l.strip()]
        turns=[e for e in events if e.get('event')=='submission']
        res=read(folder/'result.json')
        if len(turns)!=res['submissions'] or len(turns)!=r['submissions']:raise ValueError('Submission count differs: '+r['id'])
        if [t['index'] for t in turns]!=list(range(1,len(turns)+1)):raise ValueError('Submission order differs: '+r['id'])
        if (res['status'],res.get('success'),res.get('final_partial_score'))!=(r['status'],r.get('success'),r.get('score')):raise ValueError('Catalog changed outcome: '+r['id'])
        if (folder/'api_audit.jsonl.gz').exists():
            expected=metadata.get('published_files_sha256',{}).get('api_audit.jsonl.gz')
            if expected and digest(folder/'api_audit.jsonl.gz')!=expected:raise ValueError('API audit changed: '+r['id'])
            with gzip.open(folder/'api_audit.jsonl.gz','rt') as f:
                for line in f:json.loads(line)
        submissions+=len(turns)
    return {'games':len(rows),'copied_frozen_files_verified':checked,'submissions':submissions,
            'original_outcomes_unchanged':True,'semantic_certification':False}


def write_summary(root=ROOT):
    root=Path(root);rows=read(root/'results/catalog.json');stats=summarize(rows)
    write_json(root/'results/summary.json',stats)
    with (root/'results/summary.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,list(stats[0]));w.writeheader();w.writerows(stats)
    return stats


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='command',required=True)
    ls=sub.add_parser('list',help='List games; no model calls')
    ls.add_argument('--cohort',help='Exact cohort/suite name')
    ls.add_argument('--puzzle',help='Puzzle ID, e.g. TS038')
    ls.add_argument('--condition',help='Exact condition, e.g. session')
    sub.add_parser('check',help='Verify original payload hashes, counters, outcome metadata and gzip audit parsing')
    sub.add_parser('summarize',help='Rewrite results/summary.json and .csv; exclude source/appendix/duplicate/incomplete outcomes')
    loc=sub.add_parser('locate',help='Resolve an old path to its canonical file or full archive URL')
    loc.add_argument('path',help='Repository-relative historical path; no ..')
    a=p.parse_args()
    try:
        if not (ROOT/'results/catalog.json').exists():
            raise ValueError('Full experiment records are on Hugging Face. Run: python3 scripts/fetch_results.py')
        if a.command=='check':result=validate()
        elif a.command=='summarize':result=write_summary()
        elif a.command=='locate':result=locate(a.path)
        else:
            result=read(ROOT/'results/catalog.json')
            for field,filter_value in [('suite',a.cohort),('puzzle',a.puzzle),('condition',a.condition)]:
                if filter_value:result=[r for r in result if r.get(field)==filter_value]
            result=[{k:r.get(k) for k in ['id','suite','puzzle','source','condition','status','score','success','submissions','path']} for r in result]
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except (OSError,ValueError,KeyError) as e:p.error(str(e))


if __name__=='__main__':main()
