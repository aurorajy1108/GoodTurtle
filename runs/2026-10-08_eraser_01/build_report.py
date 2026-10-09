"""Render saved visible experiment messages; does not call models."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parent
events = [json.loads(s) for s in (root/'trajectory.jsonl').read_text().splitlines()]
assert len(events) == 101
turns = []
for i in range(50):
    s, h = events[2*i:2*i+2]
    assert s['event'] == 'solver' and h['event'] == 'host'
    assert s['query_index'] == h['query_index'] == i+1
    q = json.loads(s['raw'])
    assert q['type'] == 'question'
    assert h['raw'] in {'YES','NO','UNKNOWN','CLARIFY'}
    turns.append({'query_index': i+1, 'question': q['text'], 'host_label': h['raw']})
final = json.loads(events[-1]['raw'])
assert final['type'] == 'final'
counts = dict(Counter(t['host_label'] for t in turns))
config = json.loads((root/'config.json').read_text())
config.update(status='completed',finished_at_utc='2026-10-08T02:10:00Z',finished_at_precision='approximate to minute',solver_agent='/root/eraser_solver',host_agent='/root/eraser_host',host_queries=50,stop_reason='query_budget_exhausted',continuation_templates={'host':'Player question (query {n}):\n{question}','solver':'Host response to query {n}: {label}\nContinue under the same protocol. Return only your next question JSON or final explanation JSON.','solver_after_50':'Host response to query 50: UNKNOWN\nThe 50-question budget is now exhausted. Submit your final explanation as {"type":"final","text":"your final explanation"}. No more questions. Do not use tools.'})
(root/'config.json').write_text(json.dumps(config,indent=2)+'\n')
result=dict(host_queries=50,final_explanation=final['text'],complete_solution=False,first_complete_query=None,assessment_by='Root controller after game; not an independent blinded grader; pending human review',assessment_basis='The final explanation omits both the mechanical pencil and loading lead, the entire supplied answer mechanism.',host_label_counts=counts,host_format_compliance=1.0,host_accuracy=None,host_human_review='pending',notes='No intermediate explanations were elicited. No successful final answer was observed; question text does not mention the target mechanism. This is one run, not a model-level success-rate estimate.')
(root/'result.json').write_text(json.dumps(result,indent=2)+'\n')
with (root/'human_review.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['query_index','question','host_label','reviewer_label','acceptable','issue_type','notes'])
    w.writeheader()
    for turn in turns:
        w.writerow(turn)
lines=['# Eraser puzzle — trajectory', '',
'日期：2026-10-08（Asia/Hong_Kong）。一次独立试跑，50 次 host 查询后强制提交最终答案。', '',
'**结果：未完整解出。** 最终答案没有给出 mechanical pencil / loading lead；这是控制器的事后判断，待人工审核。', '',
'## 配置与边界', '',
'- Solver：`gpt-6-sol`，`reasoning_effort=high`；host：`gpt-6.1-sol`，effort 沿用运行时默认，未显式覆盖。',
'- 通过 Codex 子 agent 实际调用上述模型；不是独立 API harness，精确 checkpoint、温度、token 用量未由此接口提供。',
'- 两个 agent 都用 `fork_turns=none` 创建。solver 初始任务只含规则和汤面，没有汤底；每轮只转发 host 标签。',
'- Solver 被明确禁止使用工具；host 仅获准初始化时读取冻结的 `host_context.txt`。这是指令级隔离，不是文件系统级安全隔离，也没有独立完整工具遥测。',
'- Host 使用现有 system prompt 的文本 + 示例库前 8 条（全部来自 D01）。文本通过子 agent 初始化任务加载，并非独立 API system role 的强制注入；上层 Codex 运行时指令仍存在。',
'- 汤底保留用户原文，没有预先补充“移除笔尾橡皮才能装铅芯”等操作细节。未中途改 prompt、纠正标签、给提示或重跑择优。',
'- 保存的是全部可见问题、标签、最终答案和调度模板，不包含模型私有思维链。逐轮时间与 token 未采集。', '',
'## 用户提供的题目', '',
json.loads((root/'puzzle_private.json').read_text())['opening'], '',
'**用户提供的汤底：** Because A needed to put lead into a mechanical pencil.', '',
'## 全部问答（原文）', '',
'| # | Solver question | Host |', '| --- | --- | --- |']
for t in turns:
    lines.append(f"| {t['query_index']} | {t['question'].replace('|', chr(92)+'|')} | {t['host_label']} |")
lines += ['', '## 最终答案（原文）', '', '> '+final['text'], '',
'## 汇总', '',f'- Host 标签分布：`{json.dumps(counts)}`。',
'- 50/50 回答符合四标签格式；格式合规不能证明语义正确或鲁棒。',
'- 人工审核表：`human_review.csv`。reviewer_label、acceptable、issue_type、notes 均留空，可先独立标注。',
'- 原始逐轮可见消息：`trajectory.jsonl`；冻结 host 输入：`host_context.txt`；solver 初始任务：`solver_task.txt`。',
'- AI 事后审核建议另见 `audit_notes.md`，没有写入原始轨迹，也没有传给 solver。', '']
(root/'trajectory.md').write_text('\n'.join(lines))
manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.iterdir()) if p.is_file() and p.name != 'manifest.json'}
(root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(result,indent=2))
print('Verified 50 ordered question/label pairs + 1 final answer; generated report and blank human review CSV.')
