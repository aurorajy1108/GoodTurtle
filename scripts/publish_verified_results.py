#!/usr/bin/env python3
"""Offline audit and portable export of completed CL/MAS results; never call APIs."""
import argparse
import csv
import gzip
import hashlib
import html
import json
import math
from pathlib import Path
import shutil
import statistics
import sys
from datetime import datetime, timezone, timedelta

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.analyze_cl_results import analyze,write_report
from turtle_loop.costs import cost_summary,merge_summaries
from turtle_loop.sessions import GameSession,completed_host_replay_records
from turtle_loop.transport_recovery import replay_records


def read(path):return json.loads(Path(path).read_text())
def lines(path):return [json.loads(l) for l in Path(path).read_text().splitlines()]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
def dump(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def require(condition,message):
    if not condition:raise ValueError(message)


def audit_game(folder):
    """Check counters, completed grades, role-message lineage and actual costs."""
    r=read(folder/'result.json');events=lines(folder/'trajectory.jsonl');calls=lines(folder/'api_calls.jsonl')
    config=read(folder/'config.json');puzzle=read(folder/'puzzle_private.json');turns=[]
    require(r['status']=='completed' and not r.get('error') and not r.get('simulation'),'Not a completed real game')
    warnings=[]
    for e in events:
        if e['event']=='submission':
            require(e['index']==len(turns)+1,'Submission order/duplicate')
            turns.append(dict(e))
        elif e['event'] in ('evaluation','host_feedback'):
            require(1<=e['submission']<=len(turns),'Feedback without submission')
            turn=turns[e['submission']-1]
            require('label' not in turn,'Duplicate feedback')
            require(e['label'] in ('yes','no','yes and no','irrelevant'),'Invalid public label')
            require((turn['type']=='final')==(e['event']=='evaluation'),'Wrong feedback type')
            turn['label']=e['label']
            if e['event']=='evaluation':
                turn['grade']=e
                require((e['partial_score']==1)==e['complete'],'Full score and completion disagree')
                by_id={x['id']:x for x in e['checkpoints']}
                require(len(by_id)==len(puzzle['rubric']) and set(by_id)=={x['id'] for x in puzzle['rubric']},'Rubric IDs differ')
                score=sum(x['weight']*by_id[x['id']]['credit'] for x in puzzle['rubric'])
                require(e['partial_score'] is not None and math.isclose(score,e['partial_score'],abs_tol=1e-10),'Weighted score mismatch')
    require(turns and all('label' in t for t in turns),'Unanswered submission')
    require(len(turns)==r['submissions']<=config['max_questions']<=100,'Quota/submission mismatch')
    finals=[t for t in turns if t['type']=='final'];questions=sum(t['type']=='question' for t in turns)
    rejected=sum(not t['grade']['complete'] for t in finals)
    require(finals and (len(turns)<config['max_questions'] or turns[-1]['type']=='final'),'Missing mandatory final')
    require(questions==r['host_questions'] and len(finals)==r['final_attempts'] and rejected==r['rejected_finals'],'Action counts mismatch')
    require(r['counted_questions']==questions+rejected and r['pending_feedback']==0,'Counted questions/pending mismatch')
    require(r['success']==any(t['grade']['complete'] for t in finals),'Success mismatch')
    require(r['final_partial_score']==finals[-1]['grade']['partial_score'],'Final score mismatch')
    require((r['latest_grade']['complete'],r['latest_grade']['partial_score'])==
            (finals[-1]['grade']['complete'],finals[-1]['grade']['partial_score']),'Latest grade mismatch')
    normalized=replay_records(completed_host_replay_records(calls,events),events)
    for role in ('player','partner','host','grader'):
        session=GameSession(role,folder,lambda *a,**k:None)
        try:session.restore_chat(normalized)
        finally:session.close()
    computed=cost_summary([c['accounting'] for c in calls])
    require(computed==read(folder/'cost_summary.json')==r['costs'],'Raw-call cost accounting mismatch')
    require(computed['total']['calls']==len(calls),'API attempt count mismatch')
    if computed['total']['unknown_cost_calls']:warnings.append('Some failed calls have unknown usage/cost; totals are not an actual bill.')
    if (folder/'shared_dialogue.jsonl').exists():
        shared=lines(folder/'shared_dialogue.jsonl')
        public=[e for e in shared if e['speaker'] in ('A','B') and e['type'] in ('question','final')]
        feedback=[e for e in shared if e['speaker']=='Host']
        require(len(public)==len(feedback)==len(turns),'MAS public/Host turn count mismatch')
        require([e['message_index'] for e in shared]==list(range(1,len(shared)+1)),'MAS message order mismatch')
        for t,a,b in zip(turns,public,feedback):
            require(a['text']==t['text'] and a['type']==t['type'] and a['external_turn']==t['index'],'MAS action mismatch')
            require(b['text']==t['label'] and b['submission']==t['index'] and b['in_reply_to']==a['speaker'],'MAS Host response mismatch')
    if (folder/'solver_compute.json').exists():
        budget=read(folder/'solver_compute.json')
        require(budget['generations']<=budget['generation_cap'] and budget['output_tokens']<=budget['output_token_cap'],'Solver caps exceeded')
        if r['submissions']==100 and r['stop_reason']=='solver_budget_exhausted':
            warnings.append('Historical stop_reason uses solver_budget_exhausted at the 100-submission limit; inspect remaining budgets. Original result retained.')
    return {'scope':'structural/counters/score arithmetic/session lineage/cost accounting; no human semantic certification',
            'status':'passed','human_semantic_review':'pending','submissions':len(turns),'api_attempts':len(calls),
            'warnings':warnings,'source_api_calls_sha256':sha(folder/'api_calls.jsonl')},calls


COPY_FILES=('result.json','trajectory.jsonl','trajectory.md','trajectory.html','review_template.csv',
            'config.json','prompts.json','puzzle_private.json','runtime_context_policy.json','pricing_snapshot.json',
            'token_costs.csv','cost_summary.json','shared_dialogue.jsonl','shared_dialogue.html','dialogue_metrics.json',
            'dialogue_policy.json','collaboration.jsonl','self_review.html','solver_compute.json','transport_read_window.json')


def export_game(folder,dest,audit,calls):
    dest.mkdir(parents=True)
    manifest={};presentation_changes=[]
    for name in COPY_FILES:
        f=folder/name
        if f.exists():shutil.copy2(f,dest/name);manifest[name]=sha(f)
    if (dest/'self_review.html').exists() and not (dest/'shared_dialogue.html').exists():
        page=dest/'self_review.html'
        page.write_text(page.read_text().replace(' · <a href="shared_dialogue.html">MAS public dialogue</a>',''))
        presentation_changes.append('Removed an invalid MAS-dialogue hyperlink from the exported solo review page. Original local page and all results retained.')
    # Preserve response text and accounting for every attempt, including errors.
    # Huge repeated request histories stay local; their exact hashes are retained.
    with gzip.open(dest/'api_audit.jsonl.gz','wt',encoding='utf-8',compresslevel=6) as stream:
        for c in calls:
            compact={k:v for k,v in c.items() if k not in ('request','inherited_session')}
            compact['request_sha256']=digest(c['request'])
            compact['request_body_omitted_from_release']=True
            if 'inherited_session' in c:compact['inherited_session_sha256']=digest(c['inherited_session'])
            stream.write(json.dumps(compact,ensure_ascii=False,allow_nan=False)+'\n')
    audit={**audit,'source_files_sha256':manifest,'published_files_sha256':{n:sha(dest/n) for n in manifest},
           'presentation_changes':presentation_changes,'api_audit_sha256':sha(dest/'api_audit.jsonl.gz')}
    dump(dest/'verification.json',audit)


def csv_write(path,rows):
    with Path(path).open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def publish(cl,mas,out):
    cl,mas,out=map(lambda p:Path(p).resolve(),(cl,mas,out))
    require(not out.exists(),'Use a new output directory')
    clrows=read(cl/'continual/experiment_runs.json');masplan=read(mas/'plan.json')
    require(len(clrows)==39 and len({x['run_dir'] for x in clrows})==39,'Expected 39 unique CL games')
    require(len(masplan['jobs'])==8 and len({x['run_dir'] for x in masplan['jobs']})==8,'Expected eight unique MAS games')
    # Audit everything before writing a release, so partial exports cannot look final.
    accepted=[];excluded=[]
    for suite,root,items in [('cl',cl/'continual',clrows),('mas',mas,masplan['jobs'])]:
        for meta in items:
            folder=root/meta['run_dir'];result=read(folder/'result.json')
            require(folder.parent==root,'Unsafe run directory')
            if result['status']!='completed':
                excluded.append({'suite':suite,'run_dir':meta['run_dir'],'status':result['status'],
                    'submissions':result['submissions'],'reason':result.get('error'),
                    'result_sha256':sha(folder/'result.json'),'api_calls_sha256':sha(folder/'api_calls.jsonl'),
                    'included_in_outcome_statistics':False})
                continue
            audit,calls=audit_game(folder)
            accepted.append((suite,meta,folder,result,audit,calls))
    report=analyze(cl)
    require(report['completed_source_games']==3 and report['completed_target_games']==36 and
            report['global_balanced_repeats']==[1,2,3,4],'CL design not fully balanced')
    require(all(len(row['source_context_hashes'])==1 for row in report['by_source']),
            'A prefix changed between B repetitions')
    # Verify that all twelve B session continuations reveal A and reset the quota.
    for suite,meta,folder,result,audit,calls in accepted:
        if suite=='cl' and meta['condition']=='session':
            continuation=read(folder/'player_continuation.json');boundary=continuation['boundary']
            source=read(cl/'continual'/meta['source_run_dir']/'puzzle_private.json')
            require(boundary['completed_puzzle_full_answer']==source['answer'] and boundary['new_submission_budget']==100,
                    'Source answer disclosure or fresh B quota missing')
    out.mkdir(parents=True)
    write_report(report,out/'cl_analysis')
    readme=out/'cl_analysis/analysis.md'
    readme.write_text(readme.read_text().replace('# CL Set1 interim analysis','# CL Set1 completed four-repeat analysis',1))
    runrows=[];costs=[]
    for suite,meta,folder,r,audit,calls in accepted:
        export_game(folder,out/suite/folder.name,audit,calls);costs.append(r['costs'])
        row={'suite':suite,'run_dir':folder.name,'condition':meta['condition'],'repeat':meta['repeat'],
             'source':meta.get('source',''),'target':meta.get('target','TS038'),
             'status':r['status'],'success':r['success'],'score':r['final_partial_score'],
             'submissions':r['submissions'],'counted_questions':r['counted_questions'],
             'host_questions':r['host_questions'],'rejected_finals':r['rejected_finals'],
             'raw_stop_reason':r['stop_reason'],'human_semantic_review':'pending',
             'known_estimated_cost_usd':r['costs']['total']['known_estimated_cost_usd'],
             'unknown_cost_calls':r['costs']['total']['unknown_cost_calls'],
             'trajectory':f'{suite}/{folder.name}/trajectory.html'}
        runrows.append(row)
    dump(out/'runs.json',runrows);csv_write(out/'runs.csv',runrows);dump(out/'excluded.json',excluded)
    dump(out/'included_games_cost_summary.json',merge_summaries(costs))
    mas_summary=[]
    for condition in masplan['conditions']:
        rows=[r for r in runrows if r['suite']=='mas' and r['condition']==condition]
        scores=[r['score'] for r in rows]
        mas_summary.append({'condition':condition,'completed':len(rows),'planned':2,
            'successes':sum(r['success'] for r in rows),'score_mean':statistics.mean(scores) if scores else None,
            'score_sample_variance':statistics.variance(scores) if len(scores)>1 else None,
            'submissions':[r['submissions'] for r in rows],'scores':scores})
    dump(out/'mas_summary.json',mas_summary)
    protocol=out/'protocol';protocol.mkdir()
    for prefix,root,names in [('cl',cl,['study_plan.json','snapshot_hashes.json','resume_manifest.json']),
                              ('cl_batch',cl/'continual',['plan.json','summary.json']),
                              ('mas',mas,['plan.json','snapshot_hashes.json','recovery_manifest.json'])]:
        for name in names:
            if (root/name).exists():shutil.copy2(root/name,protocol/(prefix+'_'+name))
    manifest={'created_hong_kong':datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),
        'cl_source_archive':str(cl.relative_to(ROOT)),'mas_source_archive':str(mas.relative_to(ROOT)),
        'included_games':len(accepted),'cl_completed':39,'mas_completed':len(accepted)-39,'excluded':excluded,
        'scope':'Structural verification only. Host/Grader semantics remain pending human review.',
        'raw_api_policy':'Complete original API logs and repeated request bodies stay in local source archives. api_audit.jsonl.gz retains every response, usage, error and exact request SHA256, not reconstructable request bodies.',
        'cost_scope':'Included completed games only; excludes incomplete MAS cost and Host gate cost. Failed attempts within completed games are included. Unknown costs remain unknown. Do not add recovery copies.',
        'inputs_policy':'Per-game frozen config, prompts, puzzle rubric and grading requirements are included; protocol snapshots are fingerprinted, not bundled.'}
    dump(out/'manifest.json',manifest)
    cltable='\n'.join(f"| {row['source']} | "+' | '.join(f"{100*row['scores'][c]['mean']:.2f}%" for c in
                     ('direct','answer_only','session'))+' |' for row in report['by_source'])
    mastable='\n'.join(f"| {row['condition']} | {row['completed']}/2 | {row['successes']} | {100*row['score_mean']:.2f}% |"
                      for row in mas_summary if row['completed'])
    (out/'README.md').write_text(f'''# 2026-11-13 已完成结果与审核入口

本批 CL 已完成39/39局：3个固定A前题、36个B实验（3类前题×3个条件×4次重复）。MAS计算预算对照已完成{manifest['mas_completed']}/8局。只取每批最后一个权威归档，续跑副本不算额外重复。

**核验范围：** 提交顺序、反馈唯一性、100次额度和强制交卷、分数加权与complete一致性、持久会话链、MAS公开聊天、计算上限和API费用逐项通过离线检查。所有模型Host判断和Grader语义评分仍为**待人工审核**；这份发布不声称人工已经逐条认定正确。

直接打开[index.html](index.html)浏览全部{manifest['included_games']}局HTML轨迹；[runs.csv](runs.csv)和[runs.json](runs.json)提供逐局结果。每局的`verification.json`列出核验范围、原文件及发布文件哈希、已知元数据问题；`review_template.csv`供后续人工复核。`self_review.html`可查看私有自查，MAS另有`shared_dialogue.html`。

## CL Set1：固定B=TS013，重复4次

| 前题A | 直接做B | 仅给A完整答案 | 保留A会话再做B |
| --- | ---: | ---: | ---: |
{cltable}

36局B均未达到完整解答标准，均使用100次提交额度。因此当前不能用“平均问题数相同”判断效率相同；这是到达预算上限的观测，不是成功所需问题数。上述百分比是最终partial score均值，不是成功率。三种relation是预设假说，n=4且每个A只有一份固定前缀，不作普遍迁移结论。

A即使未被Player完全解出，也在B前揭晓完整答案；所有session条件均核验这一揭晓与B的新100次额度。详见[完整CL分析](cl_analysis/analysis.md)及逐次分数向量。

## MAS TS038：共同计算预算上限

| 条件 | 完成局数 | 成功局数 | 已完成局partial score均值 |
| --- | ---: | ---: | ---: |
{mastable}

各局上限均为225次solver生成、77,696输出token及100次外部提交；这表示可用预算上限一致，实际输入、输出、缓存及费用并不相等。普通solo、solo自查、MAS均有2次结果；MAS自查仅1次完成，不能把它与其他完整条件当成平衡2×2结果作结论。样本很小，不足以证明哪种架构普遍更好。

未完成的`TS038_r01_mas_review`停在第79次外部提交后，下一轮A的review输出`finish_reason=length`，用完该次2048输出token；未生成第80次公开动作。它仍是基础设施/生成中断，不是失败样本或0分，排除记录见[excluded.json](excluded.json)。原断点保存在本地，可另行修复续跑；本次没有重采样这段已观察到的截断文本。

## 文件和费用边界

- 每局保留原始问答轨迹、评分、配置、提示词、汤面汤底及评分点；原始结果JSON不修改。旧solo/MAS的`stop_reason`可能把100次外部上限称为solver预算耗尽，`verification.json`已标注，解释时结合实际预算余量。
- `api_audit.jsonl.gz`保留每次调用的完整返回正文、用量、错误和请求哈希；重复的完整HTTP请求历史留在本地原归档，未上传约693MB的原始API日志。精简audit不能还原完整请求body；源日志哈希见每局核验文件。
- `included_games_cost_summary.json`只汇总这{manifest['included_games']}个完成局，包括其中失败尝试；不包括未完成MAS局和单独Host门禁。未知usage/费用继续保留unknown，已知部分是标准API等价估计，不是实际账单。不要重复叠加旧恢复目录。
- `protocol/`含原计划及冻结代码指纹，逐局文件含实际冻结输入；本发布未复制整个运行时快照。运行新实验请使用仓库运行指南，不能将结果目录直接当成续跑目录。
- `.env.local`、API key、其他个人工作文件及未完成局的部分成绩未发布。

## 如何重建这份发布

在有完整本地原归档的机器上执行（无API调用）：

```bash
python3.11 scripts/publish_verified_results.py \\
  --cl-study LATEST_CL_STUDY \\
  --mas-run LATEST_MAS_2X2_RUN \\
  --out results/NEW_RELEASE_DIRECTORY
```

`--cl-study`为含`continual/`的最后一个单批次study；`--mas-run`为含`plan.json`的最后一个四组对照根目录；`--out`必须为尚不存在的新目录。脚本先完整核验再导出，不调用模型、不改源归档、不会覆盖已有发布。
''')
    blocks=''.join('<tr>'+''.join('<td>'+html.escape(str(r[k]))+'</td>' for k in
        ('suite','condition','repeat','source','score','submissions','success'))+
        f'<td><a href="{r["trajectory"]}">Trajectory</a></td></tr>' for r in runrows)
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>GoodTurtle verified results</title>'
        '<style>body{font:16px system-ui;max-width:1200px;margin:30px auto}td,th{padding:6px;border:1px solid #ddd}table{border-collapse:collapse}</style>'
        f'<h1>GoodTurtle completed results</h1><p>CL 39/39; MAS {manifest["mas_completed"]}/8. Structural checks passed; human semantic review pending.</p>'
        '<p><a href="README.md">Interpretation and limits</a> · <a href="runs.csv">Results CSV</a> · <a href="excluded.json">Excluded unfinished run</a></p>'
        '<table><tr><th>Suite</th><th>Condition</th><th>Repeat</th><th>Source A</th><th>Score</th><th>Submissions</th><th>Solved</th><th>View</th></tr>'+blocks+'</table>')
    return manifest,report,mas_summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cl-study',required=True,help='Latest authoritative stopped/completed single CL study')
    p.add_argument('--mas-run',required=True,help='Latest authoritative 2x2 compute pilot root')
    p.add_argument('--out',required=True,help='New portable release directory, outside runs/api')
    a=p.parse_args();manifest,_,_=publish(a.cl_study,a.mas_run,a.out)
    print(json.dumps(manifest,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
