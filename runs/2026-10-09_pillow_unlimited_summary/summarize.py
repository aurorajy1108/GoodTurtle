"""Aggregate unlimited trials; never treats unfinished trials as failures/successes."""
import csv,hashlib,json,statistics
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
RUNS=HERE.parent

def stats(v):
 return dict(n=len(v),values=v,mean=statistics.mean(v) if v else None,population_variance=statistics.pvariance(v) if v else None,sample_variance=statistics.variance(v) if len(v)>1 else None)
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
rows=[];all_events=[];all_review=[]
lines=['# 枕头题：三次不限次数试跑完整轨迹','','本文件合并三局全部可见问题、host 标签、交卷和评分，保留各局边界。不是摘要，也不包含模型私有思维链。','']
for i in range(1,4):
 p=RUNS/f'2026-10-09_pillow_unlimited_{i:02d}'
 if not (p/'trajectory.jsonl').exists():continue
 es=[json.loads(x) for x in (p/'trajectory.jsonl').read_text().splitlines() if x.strip()]
 qs=[e for e in es if e['event']=='solver'];hs={e['query_index']:e['raw'] for e in es if e['event']=='host'}
 fs=[e for e in es if e['event']=='solver_final_attempt'];gs={e['attempt_index']:e for e in es if e['event']=='grader'}
 ss=[e['submission_index'] for e in es if e['event'] in ('solver','solver_final_attempt')]
 assert ss==list(range(1,len(ss)+1)),p
 assert [e['query_index'] for e in qs]==list(range(1,len(qs)+1)),p
 assert all(x in ('yes','no','yes and no') for x in hs.values()),p
 success=bool(gs and gs[max(gs)]['complete'])
 if success:
  assert len(hs)==len(qs) and len(gs)==len(fs)
  assert es[-1]['event']=='grader' and es[-1]['complete']
 config=json.loads((p/'config.json').read_text())
 rejected=sum(not g['complete'] for g in gs.values())
 status='solved' if success else ('paused_by_user' if config.get('status')=='paused_by_user' else 'in_progress')
 row=dict(run_id=p.name,status=status,questions=len(qs),host_answers=len(hs),pending_host_answers=len(qs)-len(hs),final_attempts=len(fs),rejected_finals=rejected,counted_questions=len(qs)+rejected,submissions=len(ss),complete_solution=success)
 rows.append(row)
 all_events.extend(dict(run_id=p.name,**e) for e in es)
 review_link=f'../{p.name}/human_review.csv' if (p/'human_review.csv').exists() else 'all_human_review.csv'
 lines += [f'## Run {i:02d}','',f"状态：{row['status']}；普通问题 {len(qs)}；错误交卷 {rejected}；计入错误交卷的提问数 {row['counted_questions']}；总提交 {len(ss)}；待 host 回答 {row['pending_host_answers']}。",'',f"[人工审核表]({review_link}) · [冻结评分标准](../{p.name}/grader_rubric.json)",'']
 for e in es:
  if e['event']=='solver':
   q=e['query_index'];question=json.loads(e['raw'])['text'];label=hs.get(q,'[pending]')
   lines += [f"### Q{q} · 提交 {e['submission_index']}",'',question,'',f'Host: **{label}**','']
   all_review.append(dict(run_id=p.name,query_index=q,submission_index=e['submission_index'],question=question,host_label=label))
  elif e['event']=='solver_final_attempt':
   a=e['attempt_index'];g=gs.get(a,{})
   lines += [f"### Final {a} · 提交 {e['submission_index']}",'',json.loads(e['raw'])['text'],'',f"Grader: **{g.get('verdict','[pending]')}**",'']
   if g:lines += ['私有评分依据（未发给 solver）：', '',json.dumps({k:v for k,v in g.items() if k not in ('event','recorded_at_utc')},ensure_ascii=False),'']
counts=Counter(e['raw'] for e in all_events if e['event']=='host')
summary=dict(protocol='unlimited questions and submissions; wrong final continues unless user pauses; strict full narrative and hand/arm',counting_rule='counted_questions = ordinary solver questions + rejected final submissions; a saved pending question counts once; successful final kept separately in submissions',runs=rows,completed_successes=sum(r['complete_solution'] for r in rows),requested_trials=3,all_complete=len(rows)==3 and all(r['complete_solution'] for r in rows),questions_to_success=stats([r['counted_questions'] for r in rows if r['complete_solution']]),host_questions_to_success=stats([r['questions'] for r in rows if r['complete_solution']]),submissions_to_success=stats([r['submissions'] for r in rows if r['complete_solution']]),observed_counted_questions=stats([r['counted_questions'] for r in rows]),observed_count_note='Descriptive counts at current checkpoint, not questions needed to solve; paused games are unfinished, not failures.',host_labels=dict(counts),host_semantic_accuracy=None)
dump(HERE/'summary.json',summary)
(HERE/'all_trajectories.md').write_text('\n'.join(lines))
(HERE/'all_trajectories.jsonl').write_text(''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in all_events))
with (HERE/'runs.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
# Append newly answered questions; never rewrite existing human annotations.
review_path=HERE/'all_human_review.csv'
fields=['run_id','query_index','submission_index','question','host_label','reviewer_label','acceptable','issue_type','notes']
existing={}
needs_header=not review_path.exists()
if review_path.exists():
 with review_path.open(newline='') as f:
  reader=csv.DictReader(f)
  assert reader.fieldnames==fields,'Review CSV columns changed; refusing to alter it.'
  for r in reader:
   key=(r['run_id'],int(r['query_index']))
   assert key not in existing,'Duplicate review row; refusing to alter it.'
   existing[key]=r
new_rows=[]
for r in all_review:
 if r['host_label']=='[pending]':continue
 key=(r['run_id'],r['query_index'])
 if key in existing:
  assert all(str(r[k])==existing[key][k] for k in r),'Recorded question/label changed; refusing to alter review.'
 else:new_rows.append(r)
if new_rows:
 with review_path.open('a',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields)
  if needs_header:w.writeheader()
  w.writerows(new_rows)
print(json.dumps(summary,ensure_ascii=False,indent=2))
