"""Render the resumed game, retaining every rejected final-answer attempt."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
root=Path(__file__).resolve().parent
events=[json.loads(l) for l in (root/'trajectory.jsonl').read_text().splitlines()]
questions={};answers={};attempts=[];grades={};submissions=[]
for e in events:
 if e['event']=='solver':
  v=json.loads(e['raw']);assert v['type']=='question';questions[e['query_index']]=(e,v);submissions.append(e['submission_index'])
 elif e['event']=='host':
  assert e['raw'] in {'yes','no','yes and no'};assert e['query_index'] not in answers;answers[e['query_index']]=e['raw']
 elif e['event']=='solver_final_attempt':
  v=json.loads(e['raw']);assert v['type']=='final';attempts.append((e,v));submissions.append(e['submission_index'])
 elif e['event']=='grader':
  assert e['attempt_index'] not in grades;grades[e['attempt_index']]=e
assert sorted(questions)==sorted(answers)==list(range(1,15))
assert submissions==list(range(1,18))
assert [e['attempt_index'] for e,v in attempts]==[1,2,3]
assert [grades[i]['verdict'] for i in (1,2,3)]==['no','no','yes']
assert grades[3]['complete'] and len(submissions)<=50
c=json.loads((root/'config.json').read_text());c.update(status='completed',finished_at_utc='2026-10-08T07:56:58Z',finished_at_description='controller observation after accepting final attempt 3',host_queries=14,final_attempts=3,total_submissions=17,stop_reason='correct_final_answer')
c['continuation_templates']['solver']='Host response to query {n}: {label}\nSubmission slots used: {s}/50. Continue under the updated protocol. Return only your next question JSON or final explanation JSON.'
(root/'config.json').write_text(json.dumps(c,indent=2)+'\n')
counts=dict(Counter(answers.values()))
result=dict(complete_solution=True,host_queries=14,final_attempts=3,rejected_final_attempts=2,total_submissions=17,max_submissions=50,first_correct_final_after_query=14,first_correct_final_submission=17,stop_reason='correct_final_answer',final_explanation=attempts[-1][1]['text'],host_label_counts=counts,host_format_compliance=1.0,host_accuracy=None,human_review_status='pending',assessment_by='Root controller using recorded rubric; not an independent blinded grader',parent_run='2026-10-08_eraser_02',additional_host_queries_since_resume=11,additional_final_attempts_since_resume=2,additional_submissions_since_resume=13,comparison_note='Same solver/host contexts as run 02; mid-game rejection feedback and budget change, not an independent fresh run.')
(root/'result.json').write_text(json.dumps(result,indent=2)+'\n')
if not (root/'human_review.csv').exists():
 with (root/'human_review.csv').open('w',newline='') as f:
  cols=['query_index','submission_index','question','host_label','reviewer_label','acceptable','issue_type','notes'];w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
  for i,(e,v) in questions.items():w.writerow(dict(query_index=i,submission_index=e['submission_index'],question=v['text'],host_label=answers[i]))
if not (root/'final_attempt_review.csv').exists():
 with (root/'final_attempt_review.csv').open('w',newline='') as f:
  cols=['attempt_index','after_query','submission_index','explanation','grader_verdict','human_verdict','notes'];w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
  for e,v in attempts:w.writerow(dict(attempt_index=e['attempt_index'],after_query=e['after_query'],submission_index=e['submission_index'],explanation=v['text'],grader_verdict=grades[e['attempt_index']]['verdict']))
lines=['# 橡皮题第二局续跑：完整轨迹','',
'**结果：第 14 个问题后，第 3 次交卷正确。共 14 问 + 3 次交卷 = 17 次提交，前两次交卷错误。**','',
'继续使用 GPT-6 Sol（reasoning high）与 GPT-6.1 Sol host 的原会话。Host 输入保持 v0.4、52 条共享示例、20 条专属示例及扩展汤底；没有中途修正 host 回答。','',
'这不是新开的独立试验：原第二局已在 3 问后错误交卷并暂停。按用户要求恢复上下文，向 solver 反馈 no 后继续；问题和交卷各计 1 次，总预算 50。旧 3 问和第一次交卷计入本报告。原报告保持冻结。','',
'Host 问题反馈始终来自 host；最终答案由控制器按 grader_rubric.json 判定，只向 solver 返回 yes/no，不说明缺失要素。控制器不是独立盲评模型，最终判定待人工确认。','',
'## 原题与本次 Host 汤底','',json.loads((root/'puzzle_private.json').read_text())['opening'],'',
'**Host 汤底：** '+json.loads((root/'puzzle_private.json').read_text())['solution'],'',
'## 完整时间顺序','', '| 提交序号 | 类型 | Solver 原文 | 反馈 |','| --- | --- | --- | --- |']
for e in events:
 if e['event']=='solver':
  v=json.loads(e['raw']);lines.append(f"| {e['submission_index']} | 问题 {e['query_index']} | {v['text']} | {answers[e['query_index']]} |")
 elif e['event']=='solver_final_attempt':
  v=json.loads(e['raw']);lines.append(f"| {e['submission_index']} | 交卷 {e['attempt_index']} | {v['text']} | grader: {grades[e['attempt_index']]['verdict']} |")
lines+=['','## 最终正确解释（原文）','', '> '+attempts[-1][1]['text'],'',
'## 审核与限制','',f'- Host 标签分布：`{json.dumps(counts)}`。14 条格式均合规，语义准确率未经过人工审核。',
'- human_review.csv：全部 14 个问题的空白人工标注栏；final_attempt_review.csv：三次交卷及控制器 verdict，另留人工审核栏。',
'- trajectory.jsonl：原始可见输出、交卷和 grader 事件；continuation_task.txt：恢复时发给 solver 的完整规则与反馈。部分反馈通过 config.json 中模板记录。',
'- 此次恢复新增 11 问和 2 次交卷；总数 14 问包含原来那 3 问。',
'- 第一次交卷后才明确引入错误交卷继续与总提交预算；不能把本局当成从开局就使用该协议的独立样本。',
'- 相对第一局，汤底、示例、host 协议及终止规则均发生变化，不能将改进归因于单一因素。',
'- 子 agent 的模型参数沿用原配置；精确 checkpoint、token 用量未提供。上下文隔离依赖不读文件/工具的指令，非 OS 级沙箱。日志为可见问答，不包含私有思维链。','']
(root/'trajectory.md').write_text('\n'.join(lines))
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.iterdir()) if p.is_file() and p.name!='manifest.json'}
(root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(result,indent=2))
