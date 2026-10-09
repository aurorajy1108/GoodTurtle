import csv,hashlib,json,shutil,sys
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path('/Users/aurorasun/Desktop/COMP1110/GP/GoodTurtle')
R=ROOT/'runs'
def now():return datetime.now(timezone.utc).isoformat()
def dump(path,v):path.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def events(run):return [json.loads(s) for s in (run/'trajectory.jsonl').read_text().splitlines()]
cmd=sys.argv[1]
if cmd=='init':
 old=R/'2026-10-08_eraser_02_continued'
 for idx in ('03','04'):
  p=R/f'2026-10-08_eraser_{idx}';p.mkdir(exist_ok=False)
  for name in ['host_context.txt','host_messages_template.json','puzzle_private.json','shared_examples.json','grader_rubric.json']:
   shutil.copyfile(old/name,p/name)
  task='''You are the answer-blind SOLVER in one English Turtle Soup game. Do not use ANY tools, file access, web access, other agents, or outside assistance. Do not inspect the workspace. You receive only the opening below; the host knows the hidden solution. You have a budget of 50 submissions. Each question and each final-answer attempt consumes one submission. An incorrect final answer receives only a no verdict and does NOT end the game: continue until a correct final explanation or budget exhaustion. The host returns exactly yes, no, or yes and no. yes/no mean supported/contradicted by the intended hidden story, including ordinary implications and rejection of a wrong explanatory mechanism. yes and no means mixed correctness OR an unspecified detail, material ambiguity, or a question that cannot be answered as a binary claim; it does not guarantee that any part is correct. Ask atomic yes/no questions. You may submit an explanation whenever ready, including before asking questions. Do not request approval or send commentary. Each turn output only one JSON object, either {"type":"question","text":"your single question"} or {"type":"final","text":"your final explanation"}. Do not include private reasoning or alternatives. After a question or final attempt, wait for the relayed host label or grader verdict before taking another turn. Your final response for each turn is the JSON object; the controller will resume you with feedback. Use English throughout.

OPENING:
'''+json.loads((p/'puzzle_private.json').read_text())['opening']+'\n\nBegin now.'
  (p/'solver_task.txt').write_text(task+'\n');(p/'trajectory.jsonl').touch()
  c=dict(run_id=p.name,status='ready',created_at_utc=now(),local_timezone='Asia/Hong_Kong',solver_model_requested='gpt-6-sol',solver_reasoning_effort_requested='high',host_model_requested='gpt-6.1-sol',host_reasoning_effort='inherited runtime default; not explicitly overridden',backend='Codex collaboration subagents, not standalone API',max_submissions=50,budget_rule='Each question and each final attempt counts once, specified from the start',termination_rule='Correct final answer or budget exhaustion; wrong finals continue',host_protocol='v0.4',shared_examples=52,target_examples=20,host_prompt_sha256=hashlib.sha256((p/'host_context.txt').read_bytes()).hexdigest(),solver_prompt_sha256=hashlib.sha256((p/'solver_task.txt').read_bytes()).hexdigest(),grader='Root controller using frozen rubric; not an independent blinded grader',exact_checkpoint=None,sampling_parameters=None,usage_tokens=None,isolation='fork_turns=none; solver instructed not to use tools; not OS-level sandbox',host_prompt_delivery='Agent reads frozen text during initialization; higher runtime instructions remain',host_pack_review_status='pending_human_review',continuation_templates={'host':'Player question (query {q}):\n{text}','solver':'Host response to query {q}: {label}\nSubmission slots used: {s}/50. Continue under the same protocol. Return only your next question JSON or final explanation JSON.','rejected_final':'Final-answer verdict: no.\nSubmission slots used: {s}/50. The game continues. Return only your next question JSON or another final explanation JSON. No tools; no hints are supplied.'})
  dump(p/'config.json',c)
 print('Created two frozen run directories with identical solver/host prompts.')
elif cmd=='append':
 p=R/f'2026-10-08_eraser_{sys.argv[2]}';new=json.load(sys.stdin)
 c=json.loads((p/'config.json').read_text())
 if c['status']=='ready':c['status']='running';c['started_at_utc']=now();dump(p/'config.json',c)
 with (p/'trajectory.jsonl').open('a') as f:
  for e in new:e['recorded_at_utc']=now();f.write(json.dumps(e,ensure_ascii=False)+'\n')
 print(f'Recorded {len(new)} events for {p.name}')
elif cmd=='finalize':
 p=R/f'2026-10-08_eraser_{sys.argv[2]}';es=events(p);qs={};hs={};attempts=[];gs={};subs=[]
 for e in es:
  if e['event']=='solver':
   v=json.loads(e['raw']);assert v['type']=='question';qs[e['query_index']]=(e,v);subs.append(e['submission_index'])
  elif e['event']=='host':assert e['raw'] in ['yes','no','yes and no'];hs[e['query_index']]=e['raw']
  elif e['event']=='solver_final_attempt':
   v=json.loads(e['raw']);assert v['type']=='final';attempts.append((e,v));subs.append(e['submission_index'])
  elif e['event']=='grader':gs[e['attempt_index']]=e
 assert sorted(qs)==sorted(hs)==list(range(1,len(qs)+1))
 assert subs==list(range(1,len(subs)+1)) and len(subs)<=50
 assert len(attempts)==len(gs)
 success=bool(attempts and gs[attempts[-1][0]['attempt_index']]['complete'])
 assert success or len(subs)==50
 c=json.loads((p/'config.json').read_text());c.update(status='completed',finished_at_utc=now(),solver_agent='/root/eraser'+sys.argv[2]+'_solver',host_agent='/root/eraser'+sys.argv[2]+'_host',host_queries=len(qs),final_attempts=len(attempts),total_submissions=len(subs),stop_reason='correct_final_answer' if success else 'budget_exhausted');dump(p/'config.json',c)
 result=dict(complete_solution=success,host_queries=len(qs),final_attempts=len(attempts),rejected_final_attempts=sum(not g['complete'] for g in gs.values()),total_submissions=len(subs),first_correct_final_after_query=len(qs) if success else None,first_correct_final_submission=len(subs) if success else None,stop_reason=c['stop_reason'],final_explanation=attempts[-1][1]['text'] if attempts else None,host_label_counts=dict(Counter(hs.values())),host_accuracy=None,host_format_compliance=1.0,human_review_status='pending',assessment_by=c['grader']);dump(p/'result.json',result)
 for fname,cols,rows in [('human_review.csv',['query_index','submission_index','question','host_label','reviewer_label','acceptable','issue_type','notes'],[dict(query_index=i,submission_index=e['submission_index'],question=v['text'],host_label=hs[i]) for i,(e,v) in qs.items()]),('final_attempt_review.csv',['attempt_index','after_query','submission_index','explanation','grader_verdict','human_verdict','notes'],[dict(attempt_index=e['attempt_index'],after_query=e['after_query'],submission_index=e['submission_index'],explanation=v['text'],grader_verdict=gs[e['attempt_index']]['verdict']) for e,v in attempts])]:
  if not (p/fname).exists():
   with (p/fname).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
 lines=[f'# {p.name} — complete trajectory','',f"结果：{'完整解出' if success else '预算内未解出'}。{len(qs)} 个问题，{len(attempts)} 次交卷，共 {len(subs)} 次提交。",'',
 'Solver: GPT-6 Sol, reasoning high. Host: GPT-6.1 Sol, inherited runtime effort. 新独立上下文，从开局告知错误交卷继续；总预算 50 次提交。', '',
 'Host 使用固定 v0.4 三标签、52 条共享和 20 条专属示例及扩展汤底。专属示例仍待人工审核。所有原始反馈未纠正；grader 由根控制器按冻结 rubric 执行，仅返回 yes/no，不透露缺失要素。', '',
 '## 汤面与 host 汤底','',json.loads((p/'puzzle_private.json').read_text())['opening'],'','**Host solution:** '+json.loads((p/'puzzle_private.json').read_text())['solution'],'',
 '## 逐轮可见交互','','| 提交 | 类型 | Solver 原文 | 反馈 |','| --- | --- | --- | --- |']
 for e in es:
  if e['event']=='solver':v=json.loads(e['raw']);lines.append(f"| {e['submission_index']} | 问题 {e['query_index']} | {v['text']} | {hs[e['query_index']]} |")
  elif e['event']=='solver_final_attempt':v=json.loads(e['raw']);lines.append(f"| {e['submission_index']} | 交卷 {e['attempt_index']} | {v['text']} | grader: {gs[e['attempt_index']]['verdict']} |")
 lines+=['','## 审核说明','', 'human_review.csv 保存问题及空白人工标注栏；final_attempt_review.csv 保存交卷和空白复核栏。trajectory.jsonl 保存原始输出与判分事件。','',
 '通过指定模型子 agent 实际运行，非独立 API benchmark；精确 checkpoint、token 用量和采样参数未提供。fork_turns=none；solver 被禁止工具，属于指令级隔离而非 OS 沙箱。Host 只获准初始化读取冻结上下文。日志不含私有思维链。','']
 (p/'trajectory.md').write_text('\n'.join(lines));dump(p/'manifest.json',{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(p.iterdir()) if f.is_file() and f.name!='manifest.json'})
 print(json.dumps(result,indent=2))
