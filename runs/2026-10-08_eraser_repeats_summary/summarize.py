"""Compute repeat statistics from saved results, not model-generated estimates."""
import csv,hashlib,json,statistics
from pathlib import Path
HERE=Path(__file__).resolve().parent
R=HERE.parent
IDS=['2026-10-08_eraser_03','2026-10-08_eraser_04']
results=[json.loads((R/i/'result.json').read_text()) for i in IDS]
configs=[json.loads((R/i/'config.json').read_text()) for i in IDS]
for f in ['host_context.txt','solver_task.txt','puzzle_private.json','shared_examples.json','grader_rubric.json']:
 assert (R/IDS[0]/f).read_bytes()==(R/IDS[1]/f).read_bytes(),f
for c in configs:assert c['status']=='completed'
def stats(values):
 return dict(n=len(values),values=values,mean=statistics.mean(values),population_variance=statistics.pvariance(values) if values else None,sample_variance=statistics.variance(values) if len(values)>1 else None)
assert all(x['complete_solution'] for x in results)
q=stats([x['host_queries'] for x in results]);a=stats([x['final_attempts'] for x in results]);s=stats([x['total_submissions'] for x in results])
prior=json.loads((R/'2026-10-08_eraser_02_continued/result.json').read_text())
combined=stats([prior['host_queries']]+q['values'])
summary=dict(primary_runs=IDS,successes=sum(x['complete_solution'] for x in results),primary_question_count=q,final_attempt_count=a,total_submission_count=s,definitions=dict(question_count='All host queries until the correct final submission, including repeats; excludes final-answer attempts.',population_variance='sum((x - mean)^2) / n',sample_variance='sum((x - mean)^2) / (n - 1)'),secondary_prior_inclusive=dict(question_count=combined,note='Descriptive only: earlier 14-question run was resumed after a mid-game protocol change and is not pooled into the primary same-protocol estimate.'),limitations=['Only two new repetitions; variance estimate is unstable.','Host semantic labels and controller grading still require human review.','Agent contexts are separate but sampling seed and exact checkpoint are not exposed; statistical independence is not established.','Do not attribute differences solely to solver; host wording decisions can vary.'])
(HERE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
with (HERE/'runs.csv').open('w',newline='') as f:
 cols=['run_id','complete_solution','host_queries','final_attempts','total_submissions','primary_analysis'];w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
 for i,x in zip(IDS,results):w.writerow(dict(run_id=i,primary_analysis=True,**{k:x[k] for k in cols[1:-1]}))
 w.writerow(dict(run_id='2026-10-08_eraser_02_continued',primary_analysis=False,**{k:prior[k] for k in cols[1:-1]}))
lines=['# 橡皮题：两次新增重复的均值与方差','',
'同一配置下新开两局：GPT-6 Sol（reasoning high）解题，GPT-6.1 Sol 主持；52 条共享示例、20 条专属示例，v0.4 三标签。开局就告知交卷错误继续，问题和交卷共同占用 50 次提交预算。','',
'| 运行 | 解出 | 提问数 | 交卷次数 | 总提交数 |','| --- | --- | --- | --- |']
for i,x in zip(IDS,results):lines.append(f"| [{i}](../{i}/trajectory.md) | 是 | {x['host_queries']} | {x['final_attempts']} | {x['total_submissions']} |")
lines+=['','## 本次两局统计','',
'提问数只数提交给 host 的问题，包含重复问题，不包含向 grader 的交卷尝试。两局均最终解出，没有对失败进行丢弃或按成功筛选。','',
'| 指标 | mean | 总体方差（除以 n） | 样本方差（除以 n−1） |','| --- | --- | --- | --- |',
f"| 提问数 {q['values']} | {q['mean']} | {q['population_variance']} | {q['sample_variance']} |",
f"| 交卷次数 {a['values']} | {a['mean']} | {a['population_variance']} | {a['sample_variance']} |",
f"| 总提交数 {s['values']} | {s['mean']} | {s['population_variance']} | {s['sample_variance']} |",'',
'提问数计算：mean = (15 + 25) / 2 = 20；平方离差和 = (15−20)² + (25−20)² = 50；总体方差 = 50 / 2 = 25，样本方差 = 50 / 1 = 50。方差单位是“问²”。','',
'## 加上此前 14 问结果的参考统计','',
f"若只做描述性汇总，{combined['values']} 的 mean = {combined['mean']}，总体方差 = {combined['population_variance']:.6f}，样本方差 = {combined['sample_variance']}。",'',
'此前那一局是在错误交卷结束后恢复，并中途调整停止/计数规则。因此主结果只用这次从开局规则一致的两局；旧 50 问失败局和第二局 3 问暂停记录也不混入主统计。','',
'## 输入一致性与审核限制','',
'- 已逐字节确认两局 host_context、solver_task、题目资料、共享示例、grader rubric 完全相同。',
'- 每局都新建 solver/host 子 agent，fork_turns=none；solver 不获知上一局轨迹，且被指令禁止工具。',
'- 采样 seed、精确 checkpoint 和 token 用量未提供，因此只能说会话独立，不能证明统计独立性。',
'- Grader 为根控制器按同一冻结 rubric 判断，不是另一个盲评模型；人工复核栏保留为空。',
'- 第二局 Q10 obtain lead、Q18 prevent lead falling out、Q23 advance lead 等标签有需要人工核对的措辞边界；见各局 audit_notes.md。问数方差同时包含 host 与 solver 交互的影响。',
'- 仅两局，样本方差很不稳定，不应据此声称模型稳定性或题目难度已经确定。',
'- 两局目录分别保存 trajectory.jsonl、trajectory.md、human_review.csv、final_attempt_review.csv 和冻结配置。','']
(HERE/'summary.md').write_text('\n'.join(lines))
# Include audit notes added after the run without changing its frozen inputs.
for i in IDS:
 p=R/i
 (p/'manifest.json').write_text(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(p.iterdir()) if f.is_file() and f.name!='manifest.json'},indent=2)+'\n')
print(json.dumps(summary,indent=2))
