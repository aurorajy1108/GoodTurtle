"""Render recorded visible messages; never invokes a model or rewrites the run."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
root=Path(__file__).resolve().parent
events=[json.loads(line) for line in (root/'trajectory.jsonl').read_text().splitlines()]
assert events[-1]['event']=='solver_final'
assert (len(events)-1)%2==0
turns=[]
for i in range((len(events)-1)//2):
 s,h=events[2*i:2*i+2]
 assert s['event']=='solver' and h['event']=='host'
 assert s['query_index']==h['query_index']==i+1
 q=json.loads(s['raw']);assert q['type']=='question'
 assert h['raw'] in {'yes','no','yes and no'}
 turns.append(dict(query_index=i+1,question=q['text'],host_label=h['raw']))
final=json.loads(events[-1]['raw']);assert final['type']=='final'
assert events[-1]['after_query']==len(turns)
result=dict(host_queries=len(turns),max_host_queries=50,stop_reason='solver_submitted_final_early',complete_solution=False,first_complete_query=None,final_explanation=final['text'],assessment_by='Root controller after game; pending human confirmation, not independent blinded grading',assessment_basis='Final answer guesses lifting the whole pencil by its eraser end. It omits removing the eraser, exposing the refill opening and adding lead. This differs from the supplied intended solution.',host_label_counts=dict(Counter(t['host_label'] for t in turns)),host_format_compliance=1.0,host_accuracy=None,host_review_status='pending_human_review',usage_tokens=None)
(root/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
review=root/'human_review.csv'
if not review.exists():
 with review.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['query_index','question','host_label','reviewer_label','acceptable','issue_type','notes']);w.writeheader();w.writerows(turns)
lines=['# Eraser trial 02 — complete trajectory','',
'2026-10-08（Asia/Hong_Kong）。**3 次提问后自行提交错误答案**；允许最多 50 问，但没有用满预算。不是“3 问解出”。','',
'## 本次设置','',
'- Solver：`gpt-6-sol`，reasoning `high`。Host：`gpt-6.1-sol`，effort 沿用运行时默认，未显式覆盖。',
'- 使用全新的独立子 agent，均为 `fork_turns=none`；solver 初始任务只收到规则与原始汤面，不含题目答案或主持示例。',
'- Host 使用 v0.4 三标签规则、52 条共享示例、20 条该题专属示例及扩展汤底；专属标签仍是待人工确认的草稿。',
'- 初始化仅让 host 读取冻结的 host_context.txt；solver 禁止工具访问。属于指令级隔离，不是 OS 级隔离，也没有完整独立工具遥测。',
'- 实际通过指定模型子 agent 运行；不是独立 API benchmark。精确 checkpoint、温度、token 用量未提供；上层 Codex 指令仍存在。',
'- 所有问题和标签原样转发，无纠正、提示、重试择优；solver 交卷后停止。记录可见消息，不包含私有思维链。','',
'## 原始汤面','',json.loads((root/'puzzle_private.json').read_text())['opening'],'',
'## Host 持有的扩展汤底','',json.loads((root/'puzzle_private.json').read_text())['solution'],'',
'## 逐轮问答（原文）','','| # | Solver question | Host |','| --- | --- | --- |']
for t in turns:lines.append(f"| {t['query_index']} | {t['question']} | {t['host_label']} |")
lines+=['','## 最终答案（原文）','', '> '+final['text'],'',
'控制器事后判定：未解出。说到橡皮与铅笔相连不等于解释了取橡皮的必要性；最终猜测是拿起整支笔，缺少取下橡皮、露出补芯口和装铅芯。','',
'## 与旧局对照','','| 指标 | 旧局 01 | 本局 02 |','| --- | --- | --- |',
'| 实际提问数 | 50 | 3 |','| 结束原因 | 用满预算 | 自行提前交卷 |',
'| 完整解出 | 否 | 否 |','| Host 规则 | 四标签 v0.1 | 三标签 v0.4 |',
'| Host 示例 | 8 条共享 | 52 条共享 + 20 条专属 |',
'| 汤底 | 一句话 | 扩展说明、事实及明确排除 |','',
'这次不是单变量对比：host 规则、示例、汤底细节以及 solver 对标签的说明都变了；不能把问数减少解读为解题效率提升。新 host 对三个实际问题的回答与当前资料一致，但样本太少，不能据此判定其总体鲁棒性。','',
'人工审核用 human_review.csv（标注栏留空）；AI 审阅意见单独存于 audit_notes.md。配置、初始化任务和冻结输入均在本目录。','']
(root/'trajectory.md').write_text('\n'.join(lines))
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.iterdir()) if p.is_file() and p.name!='manifest.json'}
(root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(result,indent=2))
