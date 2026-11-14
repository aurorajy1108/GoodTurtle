#!/usr/bin/env python3
"""Export a manifest of existing Set2 games; offline and independent of current engine."""
import argparse,csv,gzip,hashlib,html,json,math
from pathlib import Path
import shutil

FILES=('result.json','trajectory.jsonl','trajectory.md','trajectory.html','review_template.csv',
       'config.json','prompts.json','puzzle_private.json','host_context.json','runtime_context_policy.json',
       'pricing_snapshot.json','token_costs.csv','cost_summary.json','prior_experience.json','human_review.csv')
def read(p):return json.loads(p.read_text())
def lines(p):return [json.loads(x) for x in p.read_text().splitlines()]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def require(ok,msg):
    if not ok:raise ValueError(msg)

def audit(p,target):
    r=read(p/'result.json');cfg=read(p/'config.json');puz=read(p/'puzzle_private.json')
    events=lines(p/'trajectory.jsonl');sub=[e for e in events if e['event']=='submission']
    fb=[e for e in events if e['event'] in ('evaluation','host_feedback')]
    require(r['status']=='completed' and not r.get('error') and not r.get('simulation'),'Incomplete/simulated run')
    require([e['index'] for e in sub]==list(range(1,101)),'Submission sequence')
    invalid={e['index'] for e in sub if e['type']=='invalid'}
    notices={e['invalid_submission'] for e in events if e['event']=='protocol_intervention'}
    require(invalid==notices,'Invalid slots need explicit intervention notices')
    require(sorted(e['submission'] for e in fb)==[i for i in range(1,101) if i not in invalid],'Unique executed-action feedback')
    require(r['submissions']==cfg['max_questions']==100 and r['pending_feedback']==0,'Quota')
    finals=[e for e in fb if e['event']=='evaluation'];weights={x['id']:x['weight'] for x in puz['rubric']}
    for e in finals:
        require(math.isclose(sum(weights[c['id']]*c['credit'] for c in e['checkpoints']),e['partial_score'],abs_tol=1e-10),'Score arithmetic')
        if target:require((e['partial_score']==1)==e['complete'],'Score/completion alignment')
    require(sub[-1]['type']=='final' and finals,'Mandatory final')
    require(r['host_questions']==sum(e['type']=='question' for e in sub),'Question count')
    require(r['final_attempts']==len(finals),'Final count')
    require(r['rejected_finals']==sum(not e['complete'] for e in finals),'Rejected count')
    require(r['counted_questions']==r['host_questions']+r['rejected_finals']+len(invalid),'Budget accounting')
    require(r['final_partial_score']==finals[-1]['partial_score']==r['latest_grade']['partial_score'],'Last score')
    require(r['best_partial_score']==max(e['partial_score'] for e in finals),'Best score')
    require(r['latest_final']==sub[-1]['text'],'Last answer')
    require(r['success']==any(e['complete'] for e in finals),'Success')
    if target:
        require(puz['id']=='TS034','Wrong target')
        require(r['evaluation_versions']['host_binding_version']=='host-v17-ts034-witness-timeline-20261112','Wrong Host')
        require(puz['annotation_version']=='ts034-scoring-v6-aligned-20261111','Wrong grading version')
    return r,events

def publish(manifest,out):
    require(not out.exists(),'Output must be new')
    planned=read(manifest);require(len(planned['targets'])==35 and len(planned['sources'])==3,'Expected35B+3A')
    require(len({(m['source'],m['condition'],m['repeat']) for m in planned['targets']})==35,'Duplicate target')
    for m in planned['targets']+planned['sources']:audit(Path(m['run_dir']),m['condition']!='source')
    out.mkdir(parents=True);rows=[];vsets={k:set() for k in ('story_sha256','host_context_sha256','grading_sha256','prompts_sha256')}
    input_api_hashes=set();known=0.;unknown=0;target_calls=0;original_bytes=0
    for m in planned['targets']+planned['sources']:
        p=Path(m['run_dir']);r,events=audit(p,m['condition']!='source')
        rid=m['run_id'];dest=out/('sources' if m['condition']=='source' else 'games')/rid;dest.mkdir(parents=True)
        hashes={}
        for name in FILES:
            if (p/name).exists():shutil.copyfile(p/name,dest/name);hashes[name]=sha(p/name)
        if m['condition']=='session':
            continuation=read(p/'player_continuation.json');boundary=continuation['boundary']
            require(boundary['new_submission_budget']==100,'B budget boundary')
            source=next(s for s in planned['sources'] if s['source']==m['source'])
            require(boundary['completed_puzzle_full_answer']==read(Path(source['run_dir'])/'host_context.json')['canonical_solution'],'Official answer boundary')
            inherited=next(e for e in events if e['event']=='player_session_inherited')
            dump(dest/'transfer_boundary.json',{'boundary':boundary,'source_archive':'../../sources/'+source['run_id'],
                 'inherited_player_prefix_sha256':inherited['prefix_sha256'],'source_turns':inherited['source_turns']})
        raw=p/'api_calls.jsonl';source_api_sha=sha(raw);require(source_api_sha not in input_api_hashes,'Duplicate API audit')
        input_api_hashes.add(source_api_sha);original_bytes+=raw.stat().st_size
        count=aux=0;response_hashes=[]
        with gzip.GzipFile(filename=str(dest/'api_audit.jsonl.gz'),mode='wb',mtime=0,compresslevel=6) as zipped:
            for line in raw.open():
                c=json.loads(line);count+=1
                item={k:v for k,v in c.items() if k not in ('request','inherited_session')}
                if 'request' in c:item['request_sha256']=digest(c['request']);item['request_body_omitted_from_release']=True
                if 'inherited_session' in c:item['inherited_session_sha256']=digest(c['inherited_session'])
                zipped.write((json.dumps(item,ensure_ascii=False,allow_nan=False)+'\n').encode())
                aux+=int(c['role']=='format_repair' and c.get('status') in ('ok','success'))
                response_hashes.append(digest({k:c.get(k) for k in ('role','status','response_id','text','usage','accounting')}))
        cost=read(p/'cost_summary.json');require(cost==r['costs'] and cost['total']['calls']==count,'Cost/audit count')
        interventions=sum(e['event']=='protocol_intervention' for e in events)
        verification={'status':'passed','scope':'submission/feedback/counters/weighted scores/final answer/cost counters/source answer boundary',
          'semantic_review':'assistant_selected_cases_only; no blanket human certification','submissions':100,'api_attempts':count,
          'protocol_interventions':interventions,'feedback_count':sum(e['event'] in ('host_feedback','evaluation') for e in events),'auxiliary_successful_format_calls':aux,
          'source_api_calls_sha256':source_api_sha,'source_files_sha256':hashes,
          'source_run':str(p).split('/GoodTurtle/')[-1],'response_accounting_sequence_sha256':digest(response_hashes),
          'audit_request_bodies_omitted':True}
        dump(dest/'verification.json',verification)
        if m['condition']!='source':
            for k in vsets:vsets[k].add(r['evaluation_versions'][k])
            known+=cost['total'].get('known_estimated_cost_usd',0) or 0;unknown+=cost['total']['unknown_cost_calls'];target_calls+=count
        rows.append({'puzzle_id':read(p/'puzzle_private.json')['id'],'source':m['source'],'condition':m['condition'],'repeat':m['repeat'],
          'run_id':rid,'archive_dir':dest.relative_to(out).as_posix(),'score':r['final_partial_score'],'best_score':r['best_partial_score'],
          'solved':r['success'],'submissions':100,'host_binding':r['evaluation_versions']['host_binding_version'],
          'protocol_interventions':interventions,'feedback_count':sum(e['event'] in ('host_feedback','evaluation') for e in events),'auxiliary_successful_format_calls':aux,'source_api_calls_sha256':source_api_sha})
    require(all(len(v)==1 for v in vsets.values()),'Target protocol mismatch')
    require(sum(r['protocol_interventions']>0 for r in rows if r['condition']!='source')==2,'Expected2 marked protocol-intervention runs')
    dump(out/'runs.json',rows)
    with (out/'runs.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary=[]
    for src,cond in [('none','direct')]+[(s,c) for s in ('TS033','TS035','TS012') for c in ('answer_only','session')]:
        rr=[r for r in rows if r['source']==src and r['condition']==cond];require(len(rr)==5,'Unbalanced target group')
        summary.append({'source':src,'condition':cond,'n':5,'scores':[r['score'] for r in rr],'mean':sum(r['score'] for r in rr)/5,'solved':sum(r['solved'] for r in rr)})
    dump(out/'summary.json',summary)
    dump(out/'manifest.json',{'targets':35,'sources':3,'target_groups':7,'repeats_per_group':5,'target_versions':{k:next(iter(v)) for k,v in vsets.items()},
       'raw_api_bytes_retained_locally':original_bytes,'api_export':'full responses/errors/usage/accounting; request hashes only',
       'release_is_resumable_runtime':False,'new_api_calls':0,'original_target_scores_unchanged':True})
    dump(out/'target_costs.json',{'calls':target_calls,'unknown_cost_calls':unknown,'known_estimated_subtotal_usd':known,
       'estimated_total_usd':None if unknown else known,'actual_invoice_total':None,'basis':'standard_API_equivalent_not_actual_bill; target games only'})
    trs=''.join('<tr>'+''.join('<td>'+html.escape(str(r[k]))+'</td>' for k in ('puzzle_id','source','condition','repeat','score','solved'))+
      '<td><a href="'+r['archive_dir']+'/trajectory.html">HTML</a> · <a href="'+r['archive_dir']+'/trajectory.md">Markdown</a> · <a href="'+r['archive_dir']+'/trajectory.jsonl">JSONL</a></td></tr>' for r in rows)
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Set2 v17 — Zhen Qi</title><style>body{font:16px system-ui;max-width:1200px;margin:30px auto}table{border-collapse:collapse}td,th{border:1px solid #ddd;padding:8px}</style><h1>Set2 v17: 35 target games + 3 fixed sources</h1><p>Original model scores; selected assistant semantic review, not blanket human certification.</p><p><a href="README.md">English</a> · <a href="README.zh-CN.md">中文</a> · <a href="runs.csv">CSV</a> · <a href="figures/your_35.png">35-game chart</a></p><table><tr><th>Puzzle</th><th>Source</th><th>Condition</th><th>Repeat</th><th>Score</th><th>Solved</th><th>Trajectory</th></tr>'+trs+'</table>')
    return rows

def verify(out):
    rows=read(out/'runs.json');require(len(rows)==38,'38 archives')
    for r in rows:
        p=out/r['archive_dir'];result=read(p/'result.json');ev=lines(p/'trajectory.jsonl')
        require(len([e for e in ev if e['event']=='submission'])==100,'Published trajectory count')
        v=read(p/'verification.json')
        for n,h in v['source_files_sha256'].items():require(sha(p/n)==h,'Published bytes differ: '+str(p/n))
        calls=[json.loads(x) for x in gzip.decompress((p/'api_audit.jsonl.gz').read_bytes()).decode().splitlines()]
        require(len(calls)==v['api_attempts'],'Published audit count')
        require(digest([digest({k:c.get(k) for k in ('role','status','response_id','text','usage','accounting')}) for c in calls])==v['response_accounting_sequence_sha256'],'Response/accounting changed')
        require(result['final_partial_score']==r['score'],'Published score')
    return {'status':'passed','archives':38,'target_games':35,'source_games':3,'original_bytes_and_response_accounting_verified':True}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--verify-only',action='store_true');a=p.parse_args()
    if not a.verify_only:
        require(a.manifest is not None,'--manifest required')
        require(not a.out.exists(),'Output must be new')
        partial=a.out.with_name(a.out.name+'.partial')
        require(not partial.exists(),'Inspect existing partial export before retrying')
        publish(a.manifest,partial)
        verify(partial)
        partial.rename(a.out)
    print(json.dumps(verify(a.out)))
if __name__=='__main__':main()
