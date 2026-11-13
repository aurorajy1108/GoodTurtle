#!/usr/bin/env python3
"""Summarize one authoritative CL archive without counting recovery copies twice."""
import argparse
import csv
from datetime import datetime,timezone,timedelta
import json
from pathlib import Path
import statistics

ROOT=Path(__file__).resolve().parents[1]
CONDITIONS=('direct','answer_only','session')


def stats(values):
    return {'n':len(values),'mean':statistics.mean(values) if values else None,
            'sample_sd':statistics.stdev(values) if len(values)>1 else None,
            'sample_variance':statistics.variance(values) if len(values)>1 else None}


def analyze(study):
    study=Path(study).resolve();batch=study/'continual'
    plan=json.loads((batch/'plan.json').read_text())
    indexed={}
    for row in json.loads((batch/'experiment_runs.json').read_text()):
        if row['run_dir'] in indexed:raise ValueError('Duplicate rollout '+row['run_dir'])
        result_path=batch/row['run_dir']/'result.json'
        result=json.loads(result_path.read_text()) if result_path.exists() else {}
        indexed[row['run_dir']]={**row,**result}
    source_rows=[r for r in indexed.values() if r['condition'] in ('source','control_source')]
    expected=[]
    for block in plan['blocks']:
        for condition in block['conditions']:
            if condition not in CONDITIONS:raise ValueError('This analysis expects direct/answer_only/session')
            name=block['block']+'_'+condition
            expected.append(indexed.get(name,{'run_dir':name,'source':block['source'],'target':block['target'],
                'repeat':block['repeat'],'condition':condition,'status':'planned','success':None,
                'final_partial_score':None,'submissions':0}))
    lookup={(r['source'],r['repeat'],r['condition']):r for r in expected}
    sources=sorted({r['source'] for r in expected})
    repeats=sorted({r['repeat'] for r in expected})
    complete=lambda r:r['status']=='completed' and r.get('final_partial_score') is not None
    global_balanced=[i for i in repeats if all(complete(lookup[(a,i,c)]) for a in sources for c in CONDITIONS)]
    comparisons=[]
    for source in sources:
        balanced=[i for i in repeats if all(complete(lookup[(source,i,c)]) for c in CONDITIONS)]
        local={c:stats([lookup[(source,i,c)]['final_partial_score'] for i in balanced]) for c in CONDITIONS}
        contrasts={c:stats([lookup[(source,i,c)]['final_partial_score']-
                           lookup[(source,i,'direct')]['final_partial_score'] for i in balanced])
                   for c in ('answer_only','session')}
        comparisons.append({'source':source,'complete_paired_repeats':balanced,'scores':local,'contrasts_to_direct':contrasts,
            'score_vectors':{c:[lookup[(source,i,c)]['final_partial_score'] for i in balanced] for c in CONDITIONS},
            'source_context_hashes':sorted({r['source_context_sha256'] for r in expected
                                           if r['source']==source and r.get('source_context_sha256')})})
    pooled={c:stats([lookup[(a,i,c)]['final_partial_score'] for a in sources for i in global_balanced]) for c in CONDITIONS}
    done=[r for r in expected if r['status']=='completed']
    return {'as_of_hong_kong':datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),
        'study':str(study.relative_to(ROOT)) if study.is_relative_to(ROOT) else study.name,
        'planned_source_games':len(sources),'completed_source_games':sum(r['status']=='completed' for r in source_rows),
        'planned_target_games':len(expected),'completed_target_games':len(done),
        'target_successes':sum(r.get('success') is True for r in done),
        'all_completed_targets_hit_100':bool(done) and all(r['submissions']==100 for r in done),
        'global_balanced_repeats':global_balanced,'balanced_pooled_scores':pooled,'by_source':comparisons,
        'runs':[{k:r.get(k) for k in ('run_dir','source','target','repeat','condition','status','success','submissions',
                  'host_questions','rejected_finals','final_partial_score','stop_reason')} for r in expected],
        'limitations':['Only completed games enter outcome means; missing/running scores are never filled with zero.',
            'Per-source comparisons use the same completed repeat IDs for all three conditions.',
            'Pooled comparisons use only repeat IDs completed across every source and condition.',
            'One fixed A prefix per source; B repetitions are conditional on it, not independent A experiences.',
            'Model grades are descriptive outcomes, not human-verified successes. No Host judgments are changed.',
            'Historical and new repetitions used recorded parser/controller overlays; preserve that cohort distinction.']}


def write_report(report,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    with (out/'runs.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(report['runs'][0]));writer.writeheader();writer.writerows(report['runs'])
    fmt=lambda x:'—' if x is None else f'{100*x:.2f}%'
    deltafmt=lambda x:'—' if x is None else f'{100*x:+.2f} pp'
    lines=['# CL Set1 interim analysis','',f"As of Hong Kong: {report['as_of_hong_kong']}",'',
        f"Source games: {report['completed_source_games']}/{report['planned_source_games']}; target games: "
        f"{report['completed_target_games']}/{report['planned_target_games']}; target successes: {report['target_successes']}.",'',
        'Only the latest archive is counted. Recovery copies are not extra repetitions. All scores below are provisional model judgments.','',
        '| A | Matched completed repeats | Direct B | Answer only | A session → B | Session − direct |',
        '| --- | --- | ---: | ---: | ---: | ---: |']
    for row in report['by_source']:
        lines.append('| '+' | '.join([row['source'],','.join(map(str,row['complete_paired_repeats'])),
            *(fmt(row['scores'][c]['mean']) for c in CONDITIONS),deltafmt(row['contrasts_to_direct']['session']['mean'])])+' |')
    lines+=['','Scores use identical repeat IDs within each row. Rows with different numbers of completed repeats are not a balanced cross-relation comparison.','',
        '## Balanced comparison across all three source relations','',
        'Completed repeat IDs: '+','.join(map(str,report['global_balanced_repeats']))+'.','',
        '| Condition | n | Mean score | Sample SD |','| --- | ---: | ---: | ---: |']
    for c,v in report['balanced_pooled_scores'].items():lines.append(f"| {c} | {v['n']} | {fmt(v['mean'])} | {fmt(v['sample_sd'])} |")
    lines+=['','## Interpretation','',
        'TS015 is the prespecified positive source, TS014 negative, and TS028 neutral; relation types are hypotheses. '
        'The target is always TS013. The source answer is revealed before B even when A was not solved.','',
        ('On the balanced completed repeats, answer_only minus session mean score is '+
         deltafmt(report['balanced_pooled_scores']['answer_only']['mean']-report['balanced_pooled_scores']['session']['mean'])+
         '.' if report['balanced_pooled_scores']['session']['mean'] is not None else
         'No balanced cross-source repeat is complete yet.'),
        'This contrasts canonical answer exposure with answer plus dialogue/history length; it does not isolate the effect of context length alone.','',
        'The completed four-repeat TS014 row, when available, describes performance conditional on one academic-story prefix. '
        'Inspect its repeat vectors rather than inferring a universal negative-transfer effect from a mean.','',
        'If every completed B reaches 100 submissions without solving, the observed count is budget consumption, not time to a successful solution. '
        'Partial scores, checkpoint coverage and trajectories remain informative; question-count means alone cannot rank efficiency.','',
        '## Limits','',*['- '+s for s in report['limitations']],'',
        'See runs.csv for all planned/completed/running cases, and summary.json for score vectors and paired differences.']
    (out/'analysis.md').write_text('\n'.join(lines)+'\n')


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--study',required=True,help='One latest authoritative study with continual/; never pass multiple recovery copies')
    p.add_argument('--out',required=True,help='Summary-only report directory')
    a=p.parse_args(argv);r=analyze(a.study);write_report(r,a.out)
    print(json.dumps({k:r[k] for k in ('completed_source_games','completed_target_games','planned_target_games',
                                     'target_successes','global_balanced_repeats')}))


if __name__=='__main__':main()
