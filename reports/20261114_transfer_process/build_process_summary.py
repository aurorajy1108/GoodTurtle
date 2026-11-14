"""Offline process evidence from already reviewed, frozen trajectories.

No keyword classifier, new model call, or source-score modification is used.
The food-sense milestone comes from the preceding question-level AI review.
"""
import csv
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def dump(p, x):
    p.write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n')


def events(folder):
    return [json.loads(l) for l in (folder/'trajectory.jsonl').read_text().splitlines() if l.strip()]


def csv_write(path, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, list(rows[0])); w.writeheader(); w.writerows(rows)


def main():
    formal = read(ROOT/'reports/20261114_all_versions/formal_inventory.json')
    previous = {r['game_id']:r for r in read(ROOT/'reports/20261114_joint_trajectory_review/local_cl/game_summaries.json')}
    a_by_puzzle = {r['puzzle']:r for r in formal if r['suite']=='Set1_unified' and r['role']=='source'}
    rows, first10 = [], []
    for r in formal:
        if r['suite']!='Set1_unified' or r['role']!='target':
            continue
        folder = ROOT/r['path']; es = events(folder)
        subs = {e['index']:e for e in es if e.get('event')=='submission'}
        labs = {e['submission']:e['label'] for e in es if e.get('event') in ('host_feedback','evaluation')}
        game = r['id'].split('::',1)[1]
        prev = previous[game]; milestone = prev['first_supported_core_breakthrough']
        result = read(folder/'result.json')
        grades = {c['id']:c['credit'] for c in result['latest_grade']['checkpoints']}
        a = a_by_puzzle[r['source']]
        row = {'game_id':game, 'fixed_A':r['source'], 'condition':r['condition'],
            'prior_A_provided':r['condition'] in ('answer_only','session'),
            'repeat':int(game.split('_r')[1][:2]), 'A_solved':a['success'], 'A_final_score':a['score'],
            'first_supported_food_sense':milestone, 'food_sense_by_submission10':milestone is not None and milestone<=10,
            'food_sense_observed':milestone is not None, 'final_score':result['final_partial_score'],
            'complete':result['success'], 'submissions':result['submissions'], 'final_attempts':result['final_attempts'],
            'final_C1_credit':grades['C1'], 'final_C2_credit':grades['C2'], 'final_C3_credit':grades['C3'],
            'trajectory':r['path']+'/trajectory.html',
            'milestone_review_basis':'previous question-level AI semantic review; food-sense recognition, not complete causal solution; not human gold'}
        if milestone is not None:
            row['milestone_question']=subs[milestone]['text']
            row['milestone_label']=labs[milestone]
        else:
            row['milestone_question']=None;row['milestone_label']=None
        rows.append(row)
        for i in range(1,11):
            first10.append({'game_id':game,'fixed_A':r['source'],'condition':r['condition'],
                            'submission':i,'type':subs[i]['type'],'question':subs[i]['text'],'actual_label':labs[i]})
    assert len(rows)==36 and len(first10)==360
    grouped = defaultdict(list)
    for r in rows:grouped[(r['fixed_A'],r['condition'])].append(r)
    summary = []
    for (a,c), group in sorted(grouped.items()):
        observed = [r['first_supported_food_sense'] for r in group if r['food_sense_observed']]
        summary.append({'fixed_A':a,'condition':c,'n':len(group),
           'milestone_positions':[r['first_supported_food_sense'] for r in group],
           'food_sense_by10':sum(r['food_sense_by_submission10'] for r in group),
           'food_sense_observed':len(observed),
           'observed_only_median':statistics.median(observed) if observed else None,
           'observed_only_timing_sample_sd':statistics.stdev(observed) if len(observed)>1 else None,
           'final_score_mean':statistics.mean(r['final_score'] for r in group),
           'final_score_sample_sd':statistics.stdev(r['final_score'] for r in group),
           'complete_count':sum(r['complete'] for r in group),
           'final_attempts_total':sum(r['final_attempts'] for r in group)})
    dump(OUT/'set1_game_metrics.json',rows);csv_write(OUT/'set1_game_metrics.csv',rows)
    dump(OUT/'set1_condition_metrics.json',summary);csv_write(OUT/'set1_condition_metrics.csv',summary)
    csv_write(OUT/'set1_first10_verbatim.csv',first10)

    def card(end, indices, claim):
        r=next(r for r in formal if r['id'].endswith(end));es=events(ROOT/r['path'])
        subs={e['index']:e for e in es if e.get('event')=='submission'}
        labs={e['submission']:e.get('label') for e in es if e.get('event') in ('host_feedback','evaluation')}
        return {'game_id':r['id'],'trajectory':r['path']+'/trajectory.html','claim_scope':claim,
          'original_final_score':r['score'], 'human_confirmed':False,
          'selected_submissions':[{'submission':i,'type':subs[i]['type'],'text':subs[i]['text'],'label':labs.get(i)} for i in indices]}
    cards=[
      card('S1_TS015_TS013_TS015_TS013_r01_session',[1,2,3,4,6,8,100],
           'Early semantic premise check; does not distinguish lexical priming from learning a general method.'),
      card('S1_TS015_TS013_TS015_TS013_r01_answer_only',[3,24,25,41,54,76,86,87,91,92,99,100],
           'At least six selected rejections of consumed-all/meal-finished explanation, followed by the same causal explanation in FINAL; selected episode, not a population rate.'),
      card('S1_TS015_TS013_TS015_TS013_r02_session',[7,8,12,37,63,74,100],
           'Some local information acquisition, but 19 FINALs and incomplete integration; no access to hidden beliefs.'),
      card('S1_TS015_TS013_TS015_TS013_r04_session',[2,3,6,8,9,10,100],
           'Host-induced false premise must be separated from solver failure to adapt to correct feedback.'),
      card('games/TS034_TS033_session_r02',[30,31,32,34,37,48,66,90,96,97,98,100],
           'OR narrowing and failure to recheck police premise; earlier mugging is an A-specific detail presupposed in B, not established by B.'),
      card('S1_TS015_TS013_TS015_TS013_r04_direct',[38,94,95,96,97,98,99,100],
           'No-A counterexample: a rejected consumed-all explanation also persists in direct. This failure pattern is not specific to transfer.'),
    ]
    police = next(r for r in formal if r['id'].endswith('games/TS034_TS033_session_r02'))
    es=events(ROOT/police['path']);labs={e['submission']:e.get('label') for e in es if e.get('event') in ('host_feedback','evaluation')}
    assert all(labs[i]=='no' for i in range(31,97))
    cards[-2]['verified_consecutive_no']={'first':31,'last':96,'count':66,'interpretation':'Each question rejects its full compound proposition, not logically every shared premise; the solver does not perform a clean parent-premise check.'}
    dump(OUT/'evidence_cards.json',cards)
    dump(OUT/'validation.json',{'games':36,'fixed_sources':3,'repeats_per_source_condition':4,
        'verbatim_early_submissions':360,'selected_case_cards':len(cards),
        'original_scores_changed':False,'new_model_calls':0,'human_confirmed':False,
        'label_based_progress_proxy':False,'unreached_milestones':None,
        'milestone_definition':'first story-supported meal-course interpretation, from prior semantic review; not first mention and not full solution',
        'final_C3_credit_counts':dict(Counter(r['final_C3_credit'] for r in rows)),
        'selection_policy':'All 36 Set1 B games for descriptive timing. Cases selected retrospectively; no event-frequency or general strategy-learning inference.'})
    print('Verified 36 Set1 games, 360 original early submissions, 6 evidence cards; no API calls.')


if __name__=='__main__':
    main()
