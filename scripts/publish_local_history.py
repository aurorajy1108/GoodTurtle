#!/usr/bin/env python3
"""Offline portable archive of observed local histories, not a performance filter.

Preserves failed and superseded snapshots. Exact question/feedback aliases share
one trajectory directory; all alias provenance is retained. Never calls models.
Repeated HTTP request bodies are replaced by hashes in compressed API audits.
"""
import argparse
import csv
import gzip
import hashlib
import html
import json
import shutil
from collections import Counter, defaultdict
from pathlib import Path


def read(p):
    return json.loads(p.read_text())


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True).encode()).hexdigest()


def dump(p, x):
    p.write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n')


COPY_NAMES = (
    'result.json', 'trajectory.jsonl', 'trajectory.md', 'trajectory.html',
    'config.json', 'partner_config.json', 'prompts.json', 'puzzle_private.json',
    'host_context.json', 'runtime_context_policy.json', 'pricing_snapshot.json',
    'cost_summary.json', 'token_costs.csv', 'human_review.csv', 'review_template.csv',
    'shared_dialogue.jsonl', 'shared_dialogue.html', 'dialogue_metrics.json',
    'dialogue_policy.json', 'collaboration.jsonl', 'self_review.html',
    'solver_compute.json', 'transport_read_window.json', 'actor_retry_authorization.json',
    'transfer_input.json', 'transfer_metadata.json', 'source_binding.json',
    'prior_experience.json', 'player_continuation.json', 'source_answer_reveal.json',
    'first_turn_billing_call.json',
)


def api_export(source, target):
    raw = source / 'api_calls.jsonl'
    if not raw.exists():
        return None
    count = 0
    with raw.open() as inp, gzip.open(target / 'api_audit.jsonl.gz', 'wt', compresslevel=6) as out:
        for line in inp:
            if not line.strip():
                continue
            c = json.loads(line)
            compact = {k: v for k, v in c.items() if k not in ('request', 'inherited_session')}
            for k in ('request', 'inherited_session'):
                if k in c:
                    compact[k + '_sha256'] = digest(c[k])
            compact['repeated_request_bodies_omitted'] = True
            out.write(json.dumps(compact, ensure_ascii=False) + '\n')
            count += 1
    return {'source_raw_sha256': sha(raw), 'source_raw_bytes': raw.stat().st_size,
            'published_sha256': sha(target / 'api_audit.jsonl.gz'), 'attempts': count}


def ensure_trajectory_html(folder):
    if (folder/'trajectory.html').exists():
        return {}
    events = [json.loads(l) for l in (folder/'trajectory.jsonl').read_text().splitlines() if l.strip()]
    labels = {e['submission']:e for e in events if e.get('event') in ('host_feedback','evaluation')}
    cards = []
    for e in events:
        if e.get('event')!='submission':
            continue
        feedback = labels.get(e['index'], {})
        cards.append('<article><h2>'+html.escape(str(e['index'])+' '+e['type'])+'</h2><pre>'+html.escape(e['text'])+'</pre><p>Host/Grader: '+html.escape(str(feedback.get('label','pending')))+' </p><details><summary>Original feedback</summary><pre>'+html.escape(json.dumps(feedback,ensure_ascii=False,indent=2))+'</pre></details></article>')
    (folder/'trajectory.html').write_text('<!doctype html><meta charset="utf-8"><title>Archived trajectory</title><style>body{font:15px/1.65 system-ui;max-width:1100px;margin:30px auto}article{border-bottom:1px solid #ccc;padding:16px}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style><h1>Archived trajectory</h1><p>Derived presentation of original JSONL; original questions, feedback and scores retained. No semantic certification.</p>'+''.join(cards))
    return {'trajectory.html':sha(folder/'trajectory.html')}


def publish(source_root, out):
    if out.exists():
        raise ValueError('Use a new output directory')
    groups, inventory = defaultdict(list), []
    for f in sorted((source_root / 'runs/api').rglob('result.json')):
        r = read(f)
        entry = {'source': str(f.parent.relative_to(source_root)), 'status_as_recorded': r.get('status'),
                 'simulation': r.get('simulation'), 'submissions': r.get('submissions'),
                 'result_sha256': sha(f)}
        inventory.append(entry)
        traj = f.parent / 'trajectory.jsonl'
        if r.get('simulation') or not r.get('submissions') or not traj.exists():
            entry['archive_scope'] = 'inventory_only_zero_submission_or_simulated'
            continue
        events = [json.loads(l) for l in traj.read_text().splitlines() if l.strip()]
        subs = [e for e in events if e.get('event') == 'submission']
        feedback = [e for e in events if e.get('event') in ('host_feedback', 'evaluation')]
        if not subs:
            continue
        sig = digest([subs, feedback])
        entry.update(signature=sig, event_count=len(events), trajectory_sha256=sha(traj),
                     first_submission=subs[0].get('timestamp'), first_text=subs[0].get('text'),
                     archive_scope='observed_history')
        groups[sig].append(entry)
    out.mkdir(parents=True)
    rows = []
    for sig, aliases in sorted(groups.items()):
        a = max(aliases, key=lambda x: (x['status_as_recorded'] == 'completed', x['event_count'], x['source']))
        src = source_root / a['source']
        dest = out / 'histories' / sig[:16]
        dest.mkdir(parents=True)
        copied = {}
        for name in COPY_NAMES:
            f = src / name
            if f.exists():
                shutil.copy2(f, dest / name)
                copied[name] = sha(f)
                assert sha(dest / name) == copied[name]
        api = api_export(src, dest)
        r = read(src / 'result.json')
        p = read(src / 'puzzle_private.json') if (src / 'puzzle_private.json').exists() else {}
        config = read(src / 'config.json') if (src / 'config.json').exists() else {}
        mode = config.get('mode', '')
        row = {'history_id': sig[:16], 'source': a['source'], 'alias_count': len(aliases),
               'puzzle': p.get('id'), 'status': r.get('status'), 'submissions': r.get('submissions'),
               'success': r.get('success'), 'score': r.get('final_partial_score'),
               'first_submission': a['first_submission'],
               'rollout_family': digest([a['first_submission'], a['first_text']])[:16],
               'scripted_demo': 'scripted' in mode.lower(), 'human_semantic_review': 'not_certified',
               'trajectory': 'histories/' + sig[:16] + '/trajectory.html'}
        dump(dest / 'archive_verification.json', {'scope': 'archive integrity only, not semantic correctness or independent-trial certification',
             'original_files_sha256': copied, 'api_audit': api, 'aliases': aliases,
             'derived_presentation_files_sha256':ensure_trajectory_html(dest),
             'note': 'Recovery prefixes and divergent continuations may share a rollout_family; not independent repetitions. Status running is historical, not a live-process claim.'})
        rows.append(row)
    dump(out / 'all_local_inventory.json', inventory)
    dump(out / 'histories.json', rows)
    with (out / 'histories.csv').open('w', encoding='utf-8-sig', newline='') as fp:
        w = csv.DictWriter(fp, list(rows[0])); w.writeheader(); w.writerows(rows)
    dump(out / 'manifest.json', {'inventory_entries': len(inventory), 'observed_history_archives': len(rows),
         'status_counts': dict(Counter(r['status'] for r in rows)), 'rollout_families': len({r['rollout_family'] for r in rows}),
         'source_root': str(source_root), 'raw_requests_policy': 'Original repeated HTTP requests remain local. Every response/error/usage in selected archives is included with exact request hashes.',
         'statistics_policy': 'Historical archive, NOT an analysis sample. Do not sum recovery snapshots, shared prefixes, demos, versions, or aliases as independent experiments.'})
    links = ''.join(f'<tr><td>{html.escape(str(r["puzzle"]))}</td><td>{html.escape(r["source"])}</td><td>{r["status"]}</td><td>{r["submissions"]}</td><td>{r["score"]}</td><td><a href="{r["trajectory"]}">trajectory</a></td></tr>' for r in rows)
    (out / 'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Local experiment history</title><style>body{font:14px/1.6 system-ui;margin:30px}td{padding:8px;border-bottom:1px solid #ccc;overflow-wrap:anywhere}table{width:100%}</style><h1>Local observed experiment histories</h1><p>Integrity archive; includes incomplete/superseded/demo histories. These are not independent repetitions. See manifest and joint analysis.</p><table><tr><th>Puzzle</th><th>Source</th><th>Status as recorded</th><th>Submissions</th><th>Final score</th><th>Read</th></tr>' + links + '</table>')
    print(json.dumps({'histories': len(rows), 'inventory': len(inventory), 'out': str(out)}), flush=True)


def retain_snapshot_evidence(source_root, out):
    """Keep every recorded result and distinct API attempt log, including aliases.

    This is archival provenance only, never extra performance observations.
    """
    inventory = read(out / 'all_local_inventory.json')
    api_by_hash = {}
    for f in (out / 'histories').glob('*/archive_verification.json'):
        meta = read(f).get('api_audit')
        if meta:
            api_by_hash[meta['source_raw_sha256']] = str((f.parent / 'api_audit.jsonl.gz').relative_to(out))
    snapshot_root = out / 'snapshots'
    snapshot_root.mkdir(exist_ok=True)
    for row in inventory:
        src = source_root / row['source']
        ident = hashlib.sha256(row['source'].encode()).hexdigest()[:16]
        dest = snapshot_root / ident
        dest.mkdir(exist_ok=True)
        for name in ('result.json', 'cost_summary.json'):
            if (src / name).exists():
                shutil.copy2(src / name, dest / name)
        row['result_snapshot'] = str((dest / 'result.json').relative_to(out))
        raw = src / 'api_calls.jsonl'
        if raw.exists():
            signature = sha(raw)
            if signature not in api_by_hash:
                api_export(src, dest)
                api_by_hash[signature] = str((dest / 'api_audit.jsonl.gz').relative_to(out))
            row['source_api_calls_sha256'] = signature
            row['api_audit'] = api_by_hash[signature]
        dump(dest / 'snapshot_provenance.json', row)
    dump(out / 'all_local_inventory.json', inventory)
    manifest = read(out / 'manifest.json')
    manifest.update(result_snapshots=len(inventory), distinct_api_archives=len(api_by_hash),
                    snapshot_policy='All result snapshots, including simulation, zero-turn errors, superseded checkpoints, and aliases, are retained separately; none is an additional independent trial.')
    dump(out / 'manifest.json', manifest)
    print(json.dumps({'retained_result_snapshots': len(inventory), 'distinct_api_archives': len(api_by_hash)}), flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-root', required=True, type=Path)
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args()
    publish(args.source_root.resolve(), args.out.resolve())
    retain_snapshot_evidence(args.source_root.resolve(), args.out.resolve())
