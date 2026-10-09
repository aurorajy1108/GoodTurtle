"""Rebuild reports from visible model outputs; no inference or network calls."""
import csv, hashlib, json, statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent
RUNS=HERE.parent

def dump(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def csvwrite(p,cols,rows):
    # Human annotations are never overwritten on report regeneration.
    if p.exists(): return
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
def stats(v):
    return dict(n=len(v),values=v,mean=statistics.mean(v) if v else None,population_variance=statistics.pvariance(v) if v else None,sample_variance=statistics.variance(v) if len(v)>1 else None)
results=[]
for i in range(1,4):
    p=RUNS/f'2026-10-08_pillow_{i:02d}'
    es=[json.loads(x) for x in (p/'trajectory.jsonl').read_text().splitlines()]
    qs=[e for e in es if e['event']=='solver']
    hs=[e for e in es if e['event']=='host']
    fs=[e for e in es if e['event']=='solver_final_attempt']
    gs=[e for e in es if e['event']=='grader']
    subs=[e['submission_index'] for e in es if e['event'] in ('solver','solver_final_attempt')]
    assert subs==list(range(1,len(subs)+1)) and len(subs)<=50
    assert [e['query_index'] for e in qs]==[e['query_index'] for e in hs]==list(range(1,len(qs)+1))
    assert [e['attempt_index'] for e in fs]==[e['attempt_index'] for e in gs]==list(range(1,len(fs)+1))
    assert all(e['raw'] in ('yes','no','yes and no') for e in hs)
    assert all(json.loads(e['raw'])['type']=='question' for e in qs)
    assert all(json.loads(e['raw'])['type']=='final' for e in fs)
    assert all(e['verdict']==('yes' if e['complete'] else 'no') for e in gs)
    assert all(e['complete']==all(e['coverage_private'].values()) for e in gs)
    solved=bool(gs and gs[-1]['complete']);assert solved or len(subs)==50
    c=json.loads((p/'config.json').read_text())
    assert c['host_prompt_sha256']==sha(p/'host_context.txt')
    assert c['solver_prompt_sha256']==sha(p/'solver_task.txt')
    c.update(status='completed',finished_at_utc=es[-1]['recorded_at_utc'],solver_agent=f'/root/pillow{i:02d}_solver',host_agent=f'/root/pillow{i:02d}_host',host_queries=len(qs),final_attempts=len(fs),total_submissions=len(subs),stop_reason='correct_final_answer' if solved else 'budget_exhausted',timestamp_note='Event times are controller recording times, not inference start/end timestamps.',continuation_templates={'host':'Player question (query {q}):\n{text}','solver':'Host response to query {q}: {label}\nSubmission slots used: {s}/50. Continue under the same protocol. Return only your next question JSON or final explanation JSON.','rejected_final':'Final-answer verdict: no.\nSubmission slots used: {s}/50. The game continues. Return only your next question JSON or another final explanation JSON. No tools; no hints are supplied.'})
    dump(p/'config.json',c)
    task=f'''You are the HOST for a controlled Turtle Soup trial. First read ONLY {p/'host_context.txt'} using a read-only tool. It contains the frozen v0.4 host instructions, shared protocol demonstrations, ACTIVE_PUZZLE and TARGET_DEMONSTRATIONS for this game. Do not read any other file or access web/agents. After initialization, use no further tools. Follow the loaded host protocol. Each follow-up contains the next player question. Retain previous public questions and your answers as dialogue, but do not treat guesses as canonical facts. Output exactly one lowercase label yes, no, or yes and no in your final response for each question, without explanations or commentary. You are not the grader. Do not solve on behalf of the player or provide hints.

First player question (query 1):
'''+json.loads(qs[0]['raw'])['text']
    (p/'host_task.txt').write_text(task+'\n')
    r=dict(run_id=p.name,complete_solution=solved,host_queries=len(qs),final_attempts=len(fs),rejected_final_attempts=sum(not g['complete'] for g in gs),total_submissions=len(subs),first_correct_final_after_query=len(qs) if solved else None,first_correct_final_submission=len(subs) if solved else None,stop_reason=c['stop_reason'],final_explanation=json.loads(fs[-1]['raw'])['text'] if fs else None,host_label_counts=dict(Counter(e['raw'] for e in hs)),host_format_compliance=1.0,host_accuracy=None,human_review_status='pending',assessment_by='Controller using frozen six-element full-narrative rubric; not independent blinded grader')
    dump(p/'result.json',r);results.append(r)
    labels={e['query_index']:e['raw'] for e in hs};grades={e['attempt_index']:e['verdict'] for e in gs}
    csvwrite(p/'human_review.csv',['query_index','submission_index','question','host_label','reviewer_label','acceptable','issue_type','notes'],[dict(query_index=e['query_index'],submission_index=e['submission_index'],question=json.loads(e['raw'])['text'],host_label=labels[e['query_index']]) for e in qs])
    csvwrite(p/'final_attempt_review.csv',['attempt_index','after_query','submission_index','explanation','grader_verdict','human_verdict','notes'],[dict(attempt_index=e['attempt_index'],after_query=e['after_query'],submission_index=e['submission_index'],explanation=json.loads(e['raw'])['text'],grader_verdict=grades[e['attempt_index']]) for e in fs])
    lines=[f'# {p.name} — 逐轮轨迹','',f'结果：完整解出={solved}；问题 {len(qs)}，交卷 {len(fs)}，总提交 {len(subs)}。','', 'Solver: GPT-6 Sol, reasoning high。Host: GPT-6.1 Sol，effort 未覆盖。三次使用相同冻结资料：v0.4、52 条共享示例、80 条专属示例。专属示例仍待人工审核。','', '完整叙事、严格 hand/arm；错误交卷只给 no 后继续，预算含提问与交卷。不提供缺失要素。','', '## 汤面','',json.loads((p/'puzzle_private.json').read_text())['opening'],'','## 可见交互','','| 提交 | 类型 | Solver 原文 | 原始反馈 |','| --- | --- | --- | --- |']
    for e in es:
        if e['event'] not in ('solver','solver_final_attempt'):continue
        text=json.loads(e['raw'])['text'].replace('|','\\|').replace('\n','<br>')
        if e['event']=='solver':kind=f"问题 {e['query_index']}";feedback=labels[e['query_index']]
        else:kind=f"交卷 {e['attempt_index']}";feedback='grader: '+grades[e['attempt_index']]
        lines.append(f"| {e['submission_index']} | {kind} | {text} | {feedback} |")
    lines+=['','## 审核与限制','','`human_review.csv` 保留空白人工标注栏；`final_attempt_review.csv` 保留交卷复核栏；`trajectory.jsonl` 保存模型可见输出及控制器私有评分（不含模型私有思维链）。原始 host 标签未事后更改。','','使用 Codex collaboration 子 agent，非独立 API benchmark。fork_turns=none，solver 仅获汤面及协议，工具隔离由指令实现；host 初始化读取冻结资料。精确 checkpoint、采样参数、token 用量不可得。详见 config.json。','','跨局疑点见 [audit_notes.md](../2026-10-08_pillow_repeats_summary/audit_notes.md)。没有正确交卷，不能估计成功解出所需提问数。','']
    (p/'trajectory.md').write_text('\n'.join(lines))
summary=dict(puzzle_id='USER_PILLOW_001',runs=results,successes=sum(r['complete_solution'] for r in results),trials=len(results),observed_question_count=stats([r['host_queries'] for r in results]),observed_total_submissions=stats([r['total_submissions'] for r in results]),questions_to_success=stats([r['host_queries'] for r in results if r['complete_solution']]),interpretation='Observed counts are budget-limited consumption, not questions-to-success. All failed under strict rubric and 50 total submissions. Host semantics unvalidated; failures cannot establish intrinsic puzzle difficulty.')
dump(HERE/'summary.json',summary)
# This table is machine-generated, never a human annotation file.
with (HERE/'runs.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['run_id','host_queries','final_attempts','total_submissions','complete_solution','stop_reason']);w.writeheader();w.writerows({k:r[k] for k in w.fieldnames} for r in results)
for i in range(1,4):
    p=RUNS/f'2026-10-08_pillow_{i:02d}'
    dump(p/'manifest.json',{f.name:sha(f) for f in sorted(p.iterdir()) if f.is_file() and f.name!='manifest.json'})
for name in ['host_context.txt','host_messages_template.json','solver_task.txt','puzzle_private.json','shared_examples.json','grader_rubric.json']:
    assert len({sha(RUNS/f'2026-10-08_pillow_{i:02d}'/name) for i in range(1,4)})==1,name
print(json.dumps({k:v for k,v in summary.items() if k!='runs'},indent=2))
