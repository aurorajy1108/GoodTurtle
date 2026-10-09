"""Build unlimited-run artifacts from recorded visible events, without inference calls."""
import csv, hashlib, json
from collections import Counter
from pathlib import Path
import sys
p=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent
def dump(name,value): (p/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def csvwrite(name,cols,rows):
    if (p/name).exists(): return
    with (p/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
es=[json.loads(x) for x in (p/'trajectory.jsonl').read_text().splitlines()]
c=json.loads((p/'config.json').read_text())
paused=c.get('status')=='paused_by_user'
qs=[e for e in es if e['event']=='solver']; hs=[e for e in es if e['event']=='host']
fs=[e for e in es if e['event']=='solver_final_attempt']; gs=[e for e in es if e['event']=='grader']
subs=[e['submission_index'] for e in es if e['event'] in ('solver','solver_final_attempt')]
assert subs==list(range(1,len(subs)+1))
assert [e['query_index'] for e in qs]==list(range(1,len(qs)+1))
assert [e['query_index'] for e in hs]==list(range(1,len(hs)+1))
assert len(hs)==len(qs) or (paused and len(qs)-len(hs)==1)
assert [e['attempt_index'] for e in fs]==[e['attempt_index'] for e in gs]==list(range(1,len(fs)+1))
assert all(e['raw'] in ('yes','no','yes and no') for e in hs)
assert all(e['complete']==all(e['coverage_private'].values()) for e in gs)
solved=bool(gs and gs[-1]['complete'])
rejected=sum(not g['complete'] for g in gs)
counted=len(qs)+rejected
c.update(status='completed' if solved else ('paused_by_user' if paused else 'running'),host_queries=len(qs),host_answers=len(hs),final_attempts=len(fs),rejected_final_attempts=rejected,question_count_including_incorrect_finals=counted,total_submissions=len(subs),stop_reason='correct_final_answer' if solved else ('user_requested_pause' if paused else None))
if solved:c['finished_at_utc']=es[-1]['recorded_at_utc']
dump('config.json',c)
r=dict(run_id=p.name,complete_solution=solved,host_queries=len(qs),final_attempts=len(fs),rejected_final_attempts=sum(not g['complete'] for g in gs),total_submissions=len(subs),first_correct_final_after_query=len(qs) if solved else None,first_correct_final_submission=len(subs) if solved else None,stop_reason=c['stop_reason'],final_explanation=json.loads(fs[-1]['raw'])['text'] if fs else None,host_label_counts=dict(Counter(e['raw'] for e in hs)),host_format_compliance=1.0,host_accuracy=None,human_review_status='pending',assessment_by='Controller using frozen six-element full-narrative rubric; not independent blinded grader')
r.update(status=c['status'],question_count_including_incorrect_finals=counted,host_answers_received=len(hs),pending_host_answers=len(qs)-len(hs),counting_rule='ordinary questions + rejected finals; pending saved question counted once',latest_final_coverage=gs[-1]['coverage_private'] if gs else None,core_hand_headrest_and_security_recovered=bool(gs and gs[-1]['coverage_private']['R5'] and gs[-1]['coverage_private']['R6']))
dump('result.json',r)
labels={e['query_index']:e['raw'] for e in hs};grades={e['attempt_index']:e['verdict'] for e in gs}
csvwrite('human_review.csv',['query_index','submission_index','question','host_label','reviewer_label','acceptable','issue_type','notes'],[dict(query_index=e['query_index'],submission_index=e['submission_index'],question=json.loads(e['raw'])['text'],host_label=labels.get(e['query_index'],'[pending]')) for e in qs])
csvwrite('final_attempt_review.csv',['attempt_index','after_query','submission_index','explanation','grader_verdict','human_verdict','notes'],[dict(attempt_index=e['attempt_index'],after_query=e['after_query'],submission_index=e['submission_index'],explanation=json.loads(e['raw'])['text'],grader_verdict=grades[e['attempt_index']]) for e in fs])
lines=[f'# {p.name}', '',f'Complete solution: {solved}. Questions: {len(qs)}. Final attempts: {len(fs)}. Total submissions: {len(subs)}.', '', 'Unlimited questions and final attempts. Incorrect or incomplete finals receive no and the game continues. Frozen v0.4 host, 52 shared examples and 80 target examples; target labels await human review.', '', 'Solver: gpt-6-sol, high. Host: gpt-6.1-sol, reasoning effort not explicitly overridden. Fresh fork_turns=none agents. Solver tool prohibition is instruction based. Exact checkpoint, sampling parameters and token use unavailable.', '', '## Opening', '', json.loads((p/'puzzle_private.json').read_text())['opening'], '', '## Visible trajectory', '', '| Submission | Type | Solver output | Feedback |','| --- | --- | --- | --- |']
lines[2]=f"Status: {c['status']}. Complete solution: {solved}. Ordinary questions: {len(qs)}. Incorrect finals: {rejected}. Counted questions: {counted}. Pending host answers: {len(qs)-len(hs)}."
for e in es:
    if e['event'] not in ('solver','solver_final_attempt'):continue
    text=json.loads(e['raw'])['text'].replace('|','\\|').replace('\n','<br>')
    kind=f"Question {e['query_index']}" if e['event']=='solver' else f"Final {e['attempt_index']}"
    feedback=labels.get(e['query_index'],'[pending: paused before host relay]') if e['event']=='solver' else 'grader: '+grades[e['attempt_index']]
    lines.append(f"| {e['submission_index']} | {kind} | {text} | {feedback} |")
lines+=['','Human annotation columns are blank pending review. Raw host labels are preserved. Private rubric coverage is controller assessment; no private model reasoning is recorded. Exact startup and continuation instructions are saved separately.','']
(p/'trajectory.md').write_text('\n'.join(lines))
dump('manifest.json',{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(p.iterdir()) if f.is_file() and f.name!='manifest.json'})
print(json.dumps(r,ensure_ascii=False))
