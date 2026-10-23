#!/usr/bin/env python3
"""Describe actual completed trial results without treating dry runs/errors as scores."""
import argparse
import csv
import html
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path


def stats(values):
    return {'n':len(values),'mean':statistics.mean(values) if values else None,
            'population_variance':statistics.pvariance(values) if values else None,
            'sample_variance':statistics.variance(values) if len(values)>1 else None}


def summarize(root):
    groups={};rows=[];planned=0;profiles=[]
    amendment_path=root/'scope_amendment.json'
    amendment=json.loads(amendment_path.read_text()) if amendment_path.exists() else None
    for group in ('positive','negative','team'):
        plan_path=root/group/'plan.json'
        if plan_path.exists():
            plan=json.loads(plan_path.read_text())
            planned+=sum(len(b['conditions'])+(plan['kind']=='continual') for b in plan['blocks'])
            profiles.append(plan['config']['player'])
        path=root/group/'experiment_runs.json'
        if not path.exists():
            continue
        current=json.loads(path.read_text())
        # Batch rows refresh between games; per-game results refresh every turn.
        current=[{**x,**json.loads((root/group/x['run_dir']/'result.json').read_text())}
                 if (root/group/x['run_dir']/'result.json').exists() else x for x in current]
        rows.extend({'experiment':group,**x} for x in current)
        for condition in sorted({x['condition'] for x in current}):
            selected=[x for x in current if x['condition']==condition]
            done=[x for x in selected if x['status']=='completed']
            solved=[x for x in done if x['success']]
            groups[group+'/'+condition]={'recorded':len(selected),'completed':len(done),'solved':len(solved),
                'question_counts':[x['counted_questions'] for x in done],
                'questions_completed':stats([x['counted_questions'] for x in done]),
                'questions_solved':stats([x['counted_questions'] for x in solved]),
                'scores':stats([x['final_partial_score'] for x in done if x['final_partial_score'] is not None])}
    output={'generated_at':datetime.now(timezone.utc).isoformat(),'player_profiles':profiles,
            'model_returned_verification':'CLI does not report server model identity; request is pinned.',
            'planned_games':planned,'recorded_games':len(rows),'not_started_games':planned-len(rows),
            'completed_games':sum(x['status']=='completed' for x in rows),
            'running_games':sum(x['status']=='running' for x in rows),
            'scope_amendment':amendment,
            'conditions':groups,'runs':rows,
            'interpretation':'Small exploratory pilot only. Source games excluded from B effects. Failed games are not successful solution times. Shared account and parallel batches confound wall-clock comparisons.'}
    (root/'pilot_summary.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    score_rows=[]
    for row in rows:
        trajectory=root/row['experiment']/row['run_dir']/'trajectory.jsonl'
        if not trajectory.exists():
            continue
        contents=trajectory.read_text()
        lines_in=contents.splitlines()
        for index,line in enumerate(lines_in):
            try:
                event=json.loads(line)
            except json.JSONDecodeError:
                if index==len(lines_in)-1 and not contents.endswith('\n'):
                    continue  # A live writer may be finishing its last event.
                raise
            if event.get('event')!='evaluation':
                continue
            score_rows.append({'experiment':row['experiment'],'run_dir':row['run_dir'],
                'condition':row['condition'],'puzzle_id':row['puzzle_id'],
                'submission':event['submission'],
                'counted_questions':event['submission']-int(event['complete']),
                'partial_score':event['partial_score'],'complete':event['complete'],
                'public_label':event['label'],'completion_note':event.get('completion_note','')})
    with (root/'submission_scores.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=['experiment','run_dir','condition','puzzle_id',
            'submission','counted_questions','partial_score','complete','public_label','completion_note'])
        writer.writeheader();writer.writerows(score_rows)
    lines=['# Experiment pilot','','Snapshot: '+output['generated_at'],
        '', 'Player profiles: '+json.dumps(profiles,ensure_ascii=False),
        '',f"Completed games: {output['completed_games']} / {planned}; running: {output['running_games']}; not started: {output['not_started_games']}. No simulation scores included.",'',
        '| Experiment / condition | Completed | Solved | Question counts | Mean | Population variance | Mean partial score |',
        '| --- | ---: | ---: | --- | ---: | ---: | ---: |']
    if amendment:
        lines[1:1]=['',f"Scope amended to {amendment['selected_pilot_games']} selected pilot games; original {planned}-game plan retained. See scope_amendment.json and control_events.jsonl. A controller-issued SIGINT may leave a next-game interrupted record; it is retained and excluded from comparisons.",'']
    def fmt(x): return '—' if x is None else f'{x:.4g}'
    for name,g in groups.items():
        lines.append(f"| {name} | {g['completed']} | {g['solved']} | {g['question_counts']} | {fmt(g['questions_completed']['mean'])} | {fmt(g['questions_completed']['population_variance'])} | {fmt(g['scores']['mean'])} |")
    lines+=['','Question count = ordinary questions + incorrect/incomplete finals. Successful final submissions are separate. Means above include budget-exhausted completed games; use questions_solved for successful solving efficiency.','',
            '## Incomplete games','',
            '| Run | Status | Questions so far | Final attempts | Stop reason / error |',
            '| --- | --- | ---: | ---: | --- |']
    for x in rows:
        if x['status']!='completed':
            reason=str(x.get('error') or x.get('stop_reason') or '—').replace('|','/').replace('\n',' ')
            lines.append(f"| {x['experiment']} / {x['run_dir']} | {x['status']} | {x['counted_questions']} | {x.get('final_attempts',0)} | {reason} |")
    lines+=['','Incomplete consumption is not a successful solving time and is excluded from the completed-game means.','', '## Paired contrasts','']
    for group in ('positive','negative','team'):
        path=root/group/'contrasts.json'
        if path.exists():
            lines += ['### '+group,'','```json',json.dumps(json.loads(path.read_text()),ensure_ascii=False,indent=2),'```','']
    lines+=['## Trajectories','','Each game preserves trajectory.html, trajectory.md, trajectory.jsonl, api_calls.jsonl and human_review.csv. Team discussions additionally preserve collaboration.html/.md/.jsonl.',
            '', '[All graded submissions and their question counts](submission_scores.csv). These are observed submitted-answer scores; they do not estimate knowledge between submissions.','']
    lines += [f"- [{x['experiment']} / {x['run_dir']} — {x['status']}]({x['experiment']}/{x['run_dir']}/trajectory.html)" for x in rows]
    lines+=['','## Limits','','Few repeats do not establish significance. With one observation, sample variance cannot be estimated; population variance zero is a mathematical consequence, not evidence of stable performance. Both solver and judge use the same requested model; human review is pending. See audit_notes.md for observed host/grader inconsistencies. Codex CLI reports missing local metadata for Luna; requests remain pinned, but its event stream does not independently echo the server model. Tool use invalidates a response. No hidden reasoning or credentials are included.','',output['interpretation']]
    (root/'summary.md').write_text('\n'.join(lines)+'\n')
    def selected(row):
        if not amendment:
            return True
        choice=amendment['selected'].get(row['experiment'],{})
        return row['block']==choice.get('block') and row['condition'] in choice.get('conditions',[])
    def table(items):
        rendered=[]
        for row in items:
            base=row['experiment']+'/'+row['run_dir']
            links=f'<a href="{html.escape(base,quote=True)}/trajectory.html">Trajectory</a>'
            if (root/base/'collaboration.html').exists():
                links+=f' · <a href="{html.escape(base,quote=True)}/collaboration.html">Discussion</a>'
            success='—' if row['success'] is None else ('yes' if row['success'] else 'no')
            cells=[row['experiment'],row['condition'],row['puzzle_id'],row['status'],
                   str(row['counted_questions']),fmt(row['final_partial_score']),success]
            rendered.append('<tr>'+''.join('<td>'+html.escape(x)+'</td>' for x in cells)+'<td>'+links+'</td></tr>')
        return '<table><thead><tr><th>Experiment</th><th>Condition</th><th>Puzzle</th><th>Status</th><th>Questions</th><th>Score</th><th>Full story solved</th><th>Records</th></tr></thead><tbody>'+''.join(rendered)+'</tbody></table>'
    chosen=[row for row in rows if selected(row)]
    excluded=[row for row in rows if not selected(row)]
    page=['<!doctype html><meta charset="utf-8"><title>Turtle Soup pilot</title>',
          '<style>body{font:16px system-ui;max-width:1200px;margin:40px auto;padding:0 20px;color-scheme:light dark}table{border-collapse:collapse;width:100%;margin:24px 0}th,td{border:1px solid #8886;padding:9px;text-align:left}th{background:#8882}p{line-height:1.6}small{opacity:.7}</style>',
          '<h1>Turtle Soup pilot</h1>',
          '<p>模型判分，待人工审核。Score 1.0 不等于完整叙事通过；失败交卷计入 Questions，成功交卷单列。单次对照不能估计样本方差或建立因果结论。</p>',
          '<p><a href="summary.md">统计汇总</a> · <a href="audit_notes.md">审核疑点</a> · <a href="submission_scores.csv">全部交卷分数</a> · <a href="scope_amendment.json">试跑范围</a></p>',
          '<small>Snapshot: '+html.escape(output['generated_at'])+'</small>',
          f"<p>Selected completed: {sum(row['status']=='completed' for row in chosen)} / {amendment['selected_pilot_games'] if amendment else planned}. Original plan: {planned} games.</p>",
          table(chosen)]
    if excluded:
        page+=['<h2>保留的范围外启动记录</h2><p>这些记录不纳入选定对照；控制器在首组对照完成后停止了后续重复。</p>',table(excluded)]
    (root/'index.html').write_text('\n'.join(page)+'\n')
    print('Completed',output['completed_games'],'/',planned,';',len(rows),'games recorded')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory',type=Path)
    summarize(p.parse_args().directory)
