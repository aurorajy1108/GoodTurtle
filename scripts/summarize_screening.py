#!/usr/bin/env python3
"""Summarize six sourced screening runs without changing raw trials or review labels."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BATCH=ROOT/'runs/2026-10-09_nonenglish_screening'

def main():
    source=ROOT/'data/research/nonenglish_candidates_2026-10-09.json'
    if source.exists():
        bank=json.loads(source.read_text())
    else:
        # The published data directory contains only eraser and pillow;
        # historical screening metadata remains in its frozen run inputs.
        bank=[]
        for path in sorted(BATCH.glob('JP[0-9][0-9][0-9]/puzzle_private.json')):
            repeat=path.parent.with_name(path.parent.name+'_r2')/'puzzle_private.json'
            bank.append(json.loads((repeat if repeat.exists() else path).read_text()))
    rows=[]
    combined=[]
    visible=["# 六题可见轨迹（持续更新）", "", "只含提问、host 标签和交卷，不含模型私有思维链。", ""]
    invalidated=[]
    for p in bank:
      selected=p['puzzle_id']+'_r2' if p['puzzle_id'] in ('JP001','JP004') else p['puzzle_id']
      for r in sorted(BATCH.glob(p['puzzle_id']+'*')):
        if not r.is_dir() or not (r/'config.json').exists():continue
        events=[json.loads(s) for s in (r/'trajectory.jsonl').read_text().splitlines() if s.strip()]
        visible += [f"## {r.name}", '', p['opening'], '']
        for e in events:
            combined.append(dict(e,puzzle_id=p['puzzle_id'],run_id=r.name))
            if e.get('event')=='host':
                visible += [f"Q{e['question_number']}: {e['text']}", f"Host: `{e['host_answer']}`", '']
            elif e.get('event')=='solver_final_attempt':
                visible += [f"Final {e['final_attempt_number']}: {e['text']}", f"Verdict: {'yes' if e['accepted'] else 'no'}", '']
            elif e.get('type')=='pending_question_not_sent_to_host':
                visible += [f"Unanswered submission {e['submission_number']}: {e['text']}", 'Not relayed after invalidation; excluded from host-question count.', '']
        c=json.loads((r/'config.json').read_text())
        result=json.loads((r/'result.json').read_text()) if (r/'result.json').exists() else {}
        execution=json.loads((r/'execution_metadata.json').read_text()) if (r/'execution_metadata.json').exists() else {}
        row=dict(puzzle_id=p['puzzle_id'],run_id=r.name,source_title=p['source_title'],source_url=p['source_url'],status=result.get('status',execution.get('status',c.get('status'))),questions=result.get('host_queries',result.get('question_count',sum(e.get('event')=='solver' for e in events))),final_attempts=result.get('final_attempts',sum(e.get('event')=='solver_final_attempt' for e in events)),complete_solution=result.get('complete_solution'),retained=result.get('retained',result.get('retain',False)),host_review_status=result.get('host_review_status','pending'),result=result)
        (rows if r.name==selected else invalidated).append(row)
    (BATCH/'all_trajectories.md').write_text('\n'.join(visible)+'\n')
    (BATCH/'all_trajectories.jsonl').write_text(''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in combined))
    (BATCH/'summary.json').write_text(json.dumps({'threshold':'>30 host questions before first complete final','valid_trials_per_puzzle':1,'max_questions':None,'rows':rows,'invalidated_runs':invalidated},ensure_ascii=False,indent=2)+'\n')
    cols=['puzzle_id','run_id','source_title','source_url','status','questions','final_attempts','complete_solution','retained','host_review_status']
    with (BATCH/'runs.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows({k:v[k] for k in cols} for v in rows)
    lines=['# 六道日语来源题：单次难度筛选','','以完整因果叙事为成功条件；必须首次完整解出前提问 **31 次或更多**，并且没有影响结果的重大 host 错答/泄漏，才列为暂定保留。一次试跑不足以证明稳定难度。人工审核尚未完成。','','Solver GPT-6 Sol (high)；host GPT-6.1 Sol；v0.5.1；每题独立上下文；无次数上限；错误交卷继续。问题与交卷分别计数。','','| ID | 日语来源 | 状态 | 提问数 | 交卷数 | 完整解出 | 暂定保留 |','| --- | --- | --- | ---: | ---: | --- | --- |']
    for v in rows:
        lines.append(f"| [{v['puzzle_id']}]({v['run_id']}/trajectory.md) | [{v['source_title']}]({v['source_url']}) | {v['status']} | {v['questions']} | {v['final_attempts']} | {v['complete_solution']} | {v['retained']} |")
    if invalidated:
        lines += ['','无效局单独保留，不作为失败或难度成绩：']
        for v in invalidated:lines.append(f"- [{v['run_id']}]({v['run_id']}/trajectory.md)：{v['questions']} 问，{v['status']}。修复 host 资料后换全新 solver 重跑；评分条件与 solver 提示不变。")
    lines += ['','[全部可见问答（持续更新）](all_trajectories.md) · [来源提取审核](source_audit.md)', '', '[候选英文汤面、汤底与来源说明](../../docs/nonenglish_candidates.md) · [Host 通用规则与验证](../../docs/host_v05.md)','','所有候选保留 provenance、冻结输入、问答和交卷记录；未入选题不删除。只有已完成局的结果可以用于筛选。正在运行的局不计失败，未解出不等于难题。']
    (BATCH/'summary.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
