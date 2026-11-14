"""Offline update from canonical records; retain raw online grades and cohort boundaries.

No API calls, semantic keyword scoring, or retrospective replacement of grades.
The previous 168-file snapshot is left intact. Recovery copies are not repeats.
"""
import csv
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/tables/20261114_latest_update'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def dump(name, data):
    (OUT/name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')


def write_csv(name, rows):
    with (OUT/name).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def aggregate(rows, keys):
    groups = defaultdict(list)
    for row in rows:
        if row['role'] == 'target' and row['primary']:
            groups[tuple(row[k] for k in keys)].append(row)
    out = []
    for key, group in sorted(groups.items(), key=lambda x: str(x[0])):
        accepted = [r for r in group if r['status'] == 'completed' and r['score'] is not None]
        scores = [r['score'] for r in accepted]
        out.append(dict(zip(keys, key), n_archived=len(group), n_accepted=len(accepted),
                        n_technical=len(group)-len(accepted),
                        scores=json.dumps(scores),
                        mean=statistics.mean(scores) if scores else None,
                        sample_sd=statistics.stdev(scores) if len(scores)>1 else None,
                        minimum=min(scores) if scores else None,
                        maximum=max(scores) if scores else None,
                        solved=sum(bool(r['success']) for r in accepted),
                        submissions_mean=statistics.mean(r['submissions'] for r in accepted) if accepted else None,
                        final_attempts_mean=statistics.mean(r['final_attempts'] for r in accepted) if accepted else None))
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    catalog = read(ROOT/'results/catalog.json')
    previous = read(ROOT/'results/tables/20261114_all_versions/formal_inventory.json')
    old_ids = {r['id'] for r in previous if not r.get('duplicate_of')}
    notes = read(ROOT/'results/reviews/20261114/latest_update_notes.json')
    reviewed_targets = {r['id'] for r in notes}
    inventory, first10, finals, anomalies, duplicates = [], [], [], [], defaultdict(list)
    labels = Counter()
    for r in catalog:
        folder = ROOT/r['path']
        es = [json.loads(line) for line in (folder/'trajectory.jsonl').read_text().splitlines() if line.strip()]
        result = read(folder/'result.json')
        subs = [e for e in es if e['event'] == 'submission']
        feedback = {e['submission']:e['label'] for e in es if e['event'] in ('host_feedback','evaluation')}
        assert [e['index'] for e in subs] == list(range(1, len(subs)+1)), r['id']
        assert len(subs) == r['submissions'] == result['submissions'], r['id']
        assert (r['score'], r['success'], r['status']) == (result.get('final_partial_score'), result.get('success'), result['status'])
        observed = [(e.get('timestamp'), e['index'], e['type'], e['text']) for e in subs]
        observation_hash = hashlib.sha256(json.dumps(observed, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        duplicates[observation_hash].append(r['id'])
        versions = result.get('evaluation_versions') or {}
        costs = result.get('costs') or {}
        total = costs.get('total') or {}
        tokens = total.get('tokens') or {}
        row = {k:r.get(k) for k in ['id','suite','puzzle','source','condition','role','status','success','score','submissions','path']}
        row.update(primary=r.get('primary', True), new_since_previous_analysis=r['id'] not in old_ids,
                   final_attempts=sum(e['type']=='final' for e in subs),
                   host_questions=sum(e['type']=='question' for e in subs),
                   stop_reason=result.get('stop_reason'),
                   grading_protocol=versions.get('grading_protocol') or r.get('grading_protocol'),
                   host_version=versions.get('host_binding_version') or r.get('host_version'),
                   story_sha256=versions.get('story_sha256'), grading_sha256=versions.get('grading_sha256'),
                   prompts_sha256=versions.get('prompts_sha256'), controller_sha256=versions.get('controller_sha256'),
                   host_context_sha256=versions.get('host_context_sha256'),
                   timed_submissions_sha256=observation_hash,
                   trajectory_sha256=hashlib.sha256((folder/'trajectory.jsonl').read_bytes()).hexdigest(),
                   input_tokens=tokens.get('input_tokens'), cached_input_tokens=tokens.get('cached_input_tokens'),
                   output_tokens=tokens.get('output_tokens'), estimated_usd=total.get('estimated_cost_usd'),
                   actual_billed_usd=total.get('actual_billed_cost_usd'), unknown_cost_calls=total.get('unknown_cost_calls'))
        inventory.append(row)
        for e in es:
            if e['event']=='host_feedback':
                labels[e.get('label')] += 1
            if e['event']=='evaluation' and e.get('partial_score')==1 and not e.get('complete'):
                anomalies.append({'game_id':r['id'], 'submission':e.get('submission'),
                                  'kind':'legacy_full_score_without_completion', 'protocol':row['grading_protocol']})
        if row['new_since_previous_analysis']:
            for e in subs[:10]:
                first10.append({'id':r['id'], 'role':r['role'], 'source':r.get('source'), 'condition':r['condition'],
                                'submission':e['index'], 'type':e['type'], 'text':e['text'],
                                'label':feedback.get(e['index']), 'trajectory':r['trajectory']})
            finals.append({'id':r['id'], 'status':r['status'], 'raw_online_score':r['score'],
                           'raw_online_success':r['success'], 'final':result.get('latest_final'),
                           'grade':result.get('latest_grade'), 'trajectory':r['trajectory'],
                           'semantic_review_scope':('Target final and first ten read by assistant; selected key questions inspected. No exhaustive new question-level Host certification.' if r['id'] in reviewed_targets else 'Export only; reading or semantic certification is not implied by this script.')})
    repeated = [v for v in duplicates.values() if len(v)>1]
    assert not repeated, repeated
    assert set(labels) <= {'yes','no','yes and no','irrelevant'}, labels
    write_csv('inventory.csv', inventory)
    dump('inventory.json', inventory)
    write_csv('by_condition.csv', aggregate(inventory, ['suite','puzzle','condition']))
    write_csv('by_source_condition.csv', aggregate(inventory, ['suite','puzzle','source','condition']))
    write_csv('new_first10_verbatim.csv', first10)
    dump('new_final_submissions.json', finals)
    dump('legacy_score_completion_mismatches.json', anomalies)
    new = [r for r in inventory if r['new_since_previous_analysis']]
    indexed = {r['id']:r for r in inventory}
    for note in notes:
        assert note['raw_online_score'] == indexed[note['id']]['score']
        assert note['raw_online_success'] == indexed[note['id']]['success']
    write_csv('new_target_qualitative_notes.csv', notes)
    cl = [r for r in inventory if r['role']=='target' and r['primary'] and r['puzzle'] in ('TS013','TS034','TS022')
          and r['condition'] in ('baseline','direct','answer_only','session')]
    dump('validation.json', {'games':len(inventory), 'completed':sum(r['status']=='completed' for r in inventory),
         'technical_errors':sum(r['status']=='error' for r in inventory), 'submissions':sum(r['submissions'] for r in inventory),
         'new_since_previous_analysis':len(new), 'new_targets':sum(r['role']=='target' for r in new),
         'new_sources':sum(r['role']=='source' for r in new),
         'new_by_cohort':dict(Counter(r['suite'] for r in new)),
         'new_submissions':sum(r['submissions'] for r in new), 'new_first10_rows':len(first10),
         'duplicate_timed_submission_observations':repeated,
         'cl_primary_targets':len(cl), 'cl_accepted':sum(r['status']=='completed' for r in cl),
         'cl_solved':sum(bool(r['success']) for r in cl), 'host_feedback_labels':dict(labels),
         'legacy_full_score_incomplete_evaluations':len(anomalies),
         'legacy_full_score_incomplete_games':len({r['game_id'] for r in anomalies}),
         'model_calls':0, 'online_grades_modified':False,
         'qualitatively_reviewed_new_targets':len(reviewed_targets),
         'new_targets_without_qualitative_notes':[r['id'] for r in new if r['role']=='target' and r['id'] not in reviewed_targets],
         'semantic_scope':'Exact reviewed targets are recorded in results/reviews/20261114/latest_update_notes.json: final, first ten and selected key questions, not exhaustive question-level review. Mechanical validation covers all games. This script cannot certify semantic reading of later additions.',
         'analysis_policy':'Separate protocols, sources and cohorts; no selective mixing of offline grades, no source/appendix/technical-error outcome imputation.'})
    print(json.dumps(read(OUT/'validation.json'), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
