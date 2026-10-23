#!/usr/bin/env python3
"""Replay scored submissions privately; no player and no model access to expected scores."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from turtle_loop.coverage import PROTOCOL, fact_specs, requirement_specs
from turtle_loop.dataset import load_dataset
from turtle_loop.engine import dump, grade_final, load_prompts, ProtocolError
from turtle_loop.host_context import build_story_context
from turtle_loop.providers import Client, APIError, resolve_env, validate_profile
from turtle_loop.grader import evaluate_final


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset',required=True,help='Private dataset JSON with coverage-v2 rubrics')
    parser.add_argument('--config',required=True,help='Model config; grader profile, or host when grader=host')
    parser.add_argument('--cases',required=True,help='JSON list: id, puzzle_id, submission, expected grade fields')
    parser.add_argument('--out',required=True,help='New output directory; never overwrite')
    parser.add_argument('--repeat',type=int,default=1,help='Independent calls per case, default 1')
    parser.add_argument('--dry-run',action='store_true',help='Validate/snapshot all inputs without model calls')
    args=parser.parse_args()
    if args.repeat<1:parser.error('--repeat must be positive')
    bank={p['id']:p for p in load_dataset(args.dataset)['puzzles']}
    config=json.loads(Path(args.config).read_text())
    profile=config.get('grader','host')
    profile=resolve_env(config['host'] if profile=='host' else profile)
    validate_profile(profile,require_key=not args.dry_run)
    cases=json.loads(Path(args.cases).read_text());prompts=load_prompts();inputs=[]
    for case in cases:
        p=bank[case['puzzle_id']]
        if p.get('grading_protocol')!=PROTOCOL:raise ValueError('check_grader requires coverage-v2 data')
        if not case['expected'] or set(case['expected'])-{'complete','partial_score','material_contradiction'}:
            raise ValueError('Expected fields: complete, partial_score, material_contradiction')
        inputs.append({'opening':p['opening'],'reference_answer':p['answer'],'story_context':build_story_context(p),
                       'rubric':p['rubric'],'completion_requirements':p['completion_requirements'],
                       'grading_notes':p.get('grading_notes',''),'submitted_explanation':case['submission'],
                       'grading_protocol':PROTOCOL,'required_facts':fact_specs(p['rubric']),
                       'required_completion':requirement_specs(p['completion_requirements'])})
    out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
    dump(out/'cases.json',cases);dump(out/'inputs.json',inputs);dump(out/'profile.json',profile)
    (out/'grader_prompt.txt').write_text(prompts['grader'])
    def append(name,row):
        with (out/name).open('a') as stream:stream.write(json.dumps(row,ensure_ascii=False)+'\n')
    rows=[]
    if not args.dry_run:
        client=Client(profile,'grader',lambda call:append('api_calls.jsonl',call))
        for repeat in range(1,args.repeat+1):
            for case,payload in zip(cases,inputs):
                row={'id':case['id'],'repeat':repeat,'expected':case['expected']}
                try:
                    grade,_=evaluate_final(client,prompts['grader'],payload,
                                           lambda repair:append('evidence_repairs.jsonl',{'id':case['id'],'repeat':repeat,**repair}))
                    row.update(grade=grade,passed=all(grade[k]==v for k,v in case['expected'].items()))
                except (APIError,ProtocolError) as exc:
                    row.update(error=str(exc),passed=False)
                rows.append(row);append('results.jsonl',row)
                print(json.dumps({'id':case['id'],'repeat':repeat,'passed':row['passed']}),flush=True)
                if 'error' in row:break
            if rows and 'error' in rows[-1]:break
    summary={'dry_run':args.dry_run,'planned_calls':len(cases)*args.repeat,'completed_calls':len(rows),
             'passed':sum(r['passed'] for r in rows),'errors':sum('error' in r for r in rows),
             'status':'Selected AI regression cases, not human gold or population accuracy'}
    dump(out/'summary.json',summary)
    return 0 if args.dry_run or (len(rows)==len(cases)*args.repeat and all(r['passed'] for r in rows)) else 1


if __name__=='__main__':raise SystemExit(main())
