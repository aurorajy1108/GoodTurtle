#!/usr/bin/env python3
"""Offline join of the reviewed cohorts and newly published T22/T42 results."""
import csv
import hashlib
import html
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/20261114_all_versions'


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def dump(p, x):
    p.write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n')


def stats(rows):
    done = [r for r in rows if r['status'] == 'completed']
    scores = [r['score'] for r in done]
    return {'n': len(done), 'incomplete': len(rows)-len(done),
            'successes': sum(bool(r['success']) for r in done),
            'mean_score': statistics.mean(scores) if scores else None,
            'sample_sd': statistics.stdev(scores) if len(scores) > 1 else None,
            'mean_submissions': statistics.mean(r['submissions'] for r in done) if done else None}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    old = read(ROOT / 'reports/20261114_joint_trajectory_review/global_inventory.json')['records']
    local_archive = ROOT / 'results/20261114_local_history'
    local = {r['source']: r for r in read(local_archive/'all_local_inventory.json')}
    specs = []
    old_local_prefix = '/Users/aurorasun/Desktop/COMP1110/GP/GoodTurtle/'
    for r in old:
        source = r['source_path']
        if source.startswith(old_local_prefix):
            provenance = local[source[len(old_local_prefix):]]
            folder = local_archive/'histories'/provenance['signature'][:16]
        else:
            parts = source.split('/tmp/joint_coworkers/', 1)[1].split('/', 1)
            folder = ROOT/parts[1]
        group = r['report_group']
        suite = {'local_cl': 'Set1_unified', 'local_mas': 'TS038_v14_2x2',
                 'coworkers': 'Set2_v17', 'coworker_other': 'April_TS038_v9'}.get(group)
        if group == 'coworker_legacy_set2':
            suite = 'Set2_legacy_round' + str(r['group_game_id'].split('::')[0].replace('round',''))
        if group == 'coworker_other' and 'extra2' in source:
            suite = 'Set2_extra2_v13'
        specs.append({'id': r['archive_id'], 'folder': folder, 'suite': suite,
             'source': r['design_block_source_puzzle_id'], 'condition': r['condition'],
             'role': 'source' if r['analysis_role']=='A_source' else 'target',
             'primary': r['analysis_role']!='A_source', 'native_cohort': r['cohort'],
             'semantic_review': 'question_by_question_AI_review_not_human_gold'})
    new = ROOT/'results/20261114_t22_t42_session_free_dialogue'
    for r in read(new/'manifest.json')['games']:
        specs.append({'id': 't22_t42::'+r['trajectory_dir'], 'folder': new/r['trajectory_dir'],
             'suite': 'T22_T42_20261114', 'source': r['predecessor_A'], 'condition': r['condition'],
             'role': 'source' if r['condition']=='source' else 'target',
             'primary': r['scope']=='main', 'native_cohort': r['scope'],
             'semantic_review': 'all_final_answers_and_selected_questions_reviewed_by_AI_not_full_turn_review'})
    rows, seen = [], {}
    for spec in specs:
        folder = spec.pop('folder')
        result = read(folder/'result.json');puzzle = read(folder/'puzzle_private.json')
        host = read(folder/'host_context.json') if (folder/'host_context.json').exists() else {}
        events = [json.loads(l) for l in (folder/'trajectory.jsonl').read_text().splitlines() if l.strip()]
        subs = [e for e in events if e.get('event')=='submission']
        labels = {e['submission']: e.get('label') for e in events if e.get('event') in ('host_feedback','evaluation')}
        observation = [[e.get('timestamp'),e['index'],e['type'],e['text'],labels.get(e['index'])] for e in subs]
        sig = hashlib.sha256(json.dumps(observation,sort_keys=True).encode()).hexdigest()
        config = read(folder/'config.json')
        row = {**spec, 'puzzle': puzzle['id'], 'status':result['status'],
          'success':result.get('success'), 'score':result.get('final_partial_score'),
          'best_score':result.get('best_partial_score'), 'submissions':len(subs),
          'path':str(folder.relative_to(ROOT)), 'host_version':host.get('binding_version'),
          'grading_protocol':puzzle.get('grading_protocol'), 'annotation_version':puzzle.get('annotation_version'),
          'observation_sha256':sig, 'duplicate_of':seen.get(sig),
          'models':{k:{field:config.get(k,{}).get(field) for field in ('provider','model','reasoning_effort','extra_body')}
                    for k in ('host','player','grader')}}
        seen.setdefault(sig,row['id'])
        assert len(subs)==result['submissions'], row['id']
        if spec['suite']=='T22_T42_20261114':
            assert result['status']=='completed'
            assert [e['index'] for e in subs]==list(range(1,len(subs)+1))
            for e in events:
                if e.get('event')=='evaluation':
                    by={c['id']:c['credit'] for c in e['checkpoints']}
                    total=sum(c['weight']*by[c['id']] for c in puzzle['rubric'])
                    assert math.isclose(total,e['partial_score'],abs_tol=1e-9)
                    assert (e['partial_score']==1)==e['complete']
        rows.append(row)
    groups = defaultdict(list)
    for r in rows:
        if not r['primary'] or r['duplicate_of']:
            continue
        source = r['source'] if r['condition'] in ('session','answer_only') else None
        groups[(r['suite'],r['puzzle'],r['condition'],source)].append(r)
    summaries = [{'suite':k[0],'puzzle':k[1],'condition':k[2],'source':k[3],**stats(v)} for k,v in groups.items()]
    unique = [r for r in rows if not r['duplicate_of']]
    dump(OUT/'formal_inventory.json', rows)
    dump(OUT/'condition_summary.json', summaries)
    totals = {'physical_archives':len(rows),'physical_submissions':sum(r['submissions'] for r in rows),
              'unique_observations':len(unique),'unique_submissions':sum(r['submissions'] for r in unique),
              'unique_statuses':dict(Counter(r['status'] for r in unique)),
              'semantic_review_scope_counts':dict(Counter(r['semantic_review'] for r in rows)),
              'policy':'All original scores retained. Primary tables exclude source games, duplicate archives, appendix early sessions and incomplete outcomes. Cross-version comparisons are descriptive, not adjusted causal effects.'}
    dump(OUT/'validation.json',totals)
    for name,data in [('formal_inventory.csv',rows),('condition_summary.csv',summaries)]:
        with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
            fields=[k for k in data[0] if k!='models'];w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(data)
    body=''.join('<tr>'+''.join('<td>'+html.escape(str(r.get(k)))+'</td>' for k in
                ('suite','puzzle','condition','source','n','successes','mean_score','sample_sd'))+'</tr>' for r in summaries)
    links=''.join('<tr><td>'+html.escape(r['id'])+'</td><td>'+html.escape(r['status'])+'</td><td>'+str(r['score'])+'</td><td><a href="../../'+r['path']+'/trajectory.html">trajectory</a></td></tr>' for r in rows)
    (OUT/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>All versions · GoodTurtle</title><style>body{font:14px/1.6 system-ui;margin:30px}td,th{padding:8px;border-bottom:1px solid #ddd;text-align:left}table{width:100%}</style><h1>GoodTurtle · All-version results · 2026-11-14</h1><p><a href="analysis.zh-CN.md">中文综合分析</a> · <a href="../20261114_joint_trajectory_review/index.html">上一批逐问AI审阅</a> · <a href="../../results/20261114_local_history/index.html">全部本机历史归档</a></p><p>原始评分保留；旧/新版分层展示。新T22/T42仅完成结构、末卷和选取问答审阅，未冒称逐问语义复核。中断、前题、早期附录不并入主比较。</p><h2>Condition results (0–1 scale)</h2><table><tr><th>Cohort</th><th>Puzzle</th><th>Condition</th><th>A</th><th>n</th><th>Solved</th><th>Mean</th><th>SD</th></tr>'+body+'</table><h2>Every formal archive</h2><table>'+links+'</table>')
    print(json.dumps(totals,ensure_ascii=False))


if __name__=='__main__':
    main()
