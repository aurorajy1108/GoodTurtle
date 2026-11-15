#!/usr/bin/env python3
"""Prepare a portable HF experiment dataset without changing original records."""
import argparse
import gzip
import hashlib
import json
import re
import subprocess
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPO = 'COMP1110-20261A-Group50/GoodTurtle-experiments'

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()

def lines(path):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def write_rows(path, rows):
    with path.open('w', encoding='utf-8') as f:
        for row in rows: f.write(json.dumps(row, ensure_ascii=False)+'\n')

def prepare(root, out, repo_id=DEFAULT_REPO):
    try:
        from .results_catalog import validate
    except ImportError:
        from results_catalog import validate
    root, out = Path(root).resolve(), Path(out).resolve()
    validation = validate(root)
    if out.exists(): raise ValueError('Choose a new export directory')
    out.mkdir(parents=True)
    data = out/'data'; data.mkdir()
    catalog = json.loads((root/'results/catalog.json').read_text())
    games, turns, messages = [], [], []
    for row in catalog:
        folder = root/row['path']
        result = json.loads((folder/'result.json').read_text())
        game = {k:row.get(k) for k in ['id','suite','puzzle','source','condition','role','primary','status','success','score','submissions','host_version','grading_protocol','annotation_version','duplicate_of']}
        total = result.get('costs', {}).get('total', {})
        game.update(path=row['path'],final_attempts=result.get('final_attempts'),
                    models_json=json.dumps(row.get('models', {})),
                    usage_json=json.dumps(result.get('usage', {})),
                    cost_usd=total.get('estimated_cost_usd'),
                    known_cost_usd=total.get('known_estimated_cost_usd'))
        games.append(game)
        events = lines(folder/'trajectory.jsonl')
        feedback = {e.get('submission'):e for e in events if e.get('event') in ('host_feedback','evaluation')}
        for event in events:
            if event.get('event') != 'submission': continue
            reply = feedback.get(event['index'], {})
            turns.append(dict(game_id=row['id'],index=event['index'],timestamp=event.get('timestamp'),
                              type=event['type'],text=event['text'],feedback=reply.get('label'),
                              feedback_json=json.dumps(reply, ensure_ascii=False),forced=event.get('forced',False)))
        shared = folder/'shared_dialogue.jsonl'
        if shared.exists():
            for i, event in enumerate(lines(shared)):
                messages.append(dict(game_id=row['id'],kind='shared',source_index=i,
                    timestamp=event.get('timestamp'),speaker=event.get('speaker'),type=event.get('type'),
                    external_turn=event.get('external_turn',event.get('submission')),text=event.get('text',''),
                    metadata_json=json.dumps(event,ensure_ascii=False)))
        audit = folder/'api_audit.jsonl.gz'
        if audit.exists():
            for i, event in enumerate(lines(audit)):
                phase = event.get('reflection_phase',event.get('self_review_phase'))
                if phase not in ('draft','review') or event.get('status')!='ok' or not event.get('text'): continue
                messages.append(dict(game_id=row['id'],kind='private_reflection',source_index=i,
                    timestamp=event.get('timestamp'),speaker=event.get('reflection_actor',event.get('role')),type=phase,
                    external_turn=event.get('reflection_slot',event.get('self_review_slot')),text=event['text'],
                    metadata_json=json.dumps({k:v for k,v in event.items() if k!='text'},ensure_ascii=False)))
    for name, values in [('games',games),('turns',turns),('messages',messages)]: write_rows(data/(name+'.jsonl'),values)
    files = sorted(p for p in (root/'results').rglob('*') if p.is_file())
    secret = re.compile(rb'(?:hf_[A-Za-z0-9]{25,}|sk-[A-Za-z0-9_-]{25,})')
    for f in files:
        if secret.search(f.read_bytes()): raise ValueError('Potential credential found in '+str(f.relative_to(root)))
    manifest = {str(p.relative_to(root)): {'bytes':p.stat().st_size,'sha256':digest(p)} for p in files}
    (out/'archive_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    with tarfile.open(out/'results.tar.gz','w:gz') as tar:
        for f in files: tar.add(f,arcname=str(f.relative_to(root)),recursive=False)
    try:
        top=subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=root,text=True,stderr=subprocess.DEVNULL).strip()
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True,stderr=subprocess.DEVNULL).strip() if Path(top).resolve()==root else None
    except (OSError,subprocess.CalledProcessError): commit=None
    info={'repo_id':repo_id,'source_code_commit':commit,'counts':{'games':len(games),'turns':len(turns),'messages':len(messages)},
          'original_validation':validation,'archive_file':'results.tar.gz','archive_sha256':digest(out/'results.tar.gz'),
          'manifest_file':'archive_manifest.json','source_dataset':'COMP1110-20261A-Group50/GoodTurtle'}
    (out/'release.json').write_text(json.dumps(info,indent=2)+'\n')
    card='''---
language:
- en
task_categories:
- question-answering
tags:
- turtle-soup
- lateral-thinking
- multi-agent
- in-context-learning
pretty_name: GoodTurtle Experiments
configs:
- config_name: games
  data_files:
  - split: records
    path: data/games.jsonl
- config_name: turns
  data_files:
  - split: records
    path: data/turns.jsonl
- config_name: messages
  data_files:
  - split: records
    path: data/messages.jsonl
---
# GoodTurtle experiment records

Experiment evidence accompanying [GoodTurtle](https://github.com/aurorajy1108/GoodTurtle).
Puzzle collection: [GoodTurtle dataset](https://huggingface.co/datasets/COMP1110-20261A-Group50/GoodTurtle).

## Contents

- `games`: one row per canonical archived game, with condition, outcome, model and usage information.
- `turns`: original questions and submitted explanations with recorded public feedback.
- `messages`: shared agent messages and private draft/review notes, explicitly distinguished.
- `results.tar.gz`: full published text/JSON records, frozen settings, review records and analysis tables.
- `archive_manifest.json`: inventory for checking the complete downloaded archive.
- `release.json`: counts, source code version and archive information.

Use `game_id` to join the tables. The records split includes source games and technical interruptions;
filter role, status and condition explicitly for statistical comparisons. Recovery copies are not additional trials.

## Provenance and interpretation

Original questions, host replies, scores, source labels and completion decisions are unchanged.
Model-generated gameplay and private reflection remain model-generated records, distinct from human reference annotations.
Historical cohorts retain their original model, host and grading versions. Revised report labels for Set 2
are documented in the code repository; original labels are not retroactively rewritten here.

English is the primary language. Original messages and dated review notes may retain other languages.
This archive contains model judgments and research annotations; it is not a human-gold benchmark of every reply.
Potentially violent fictional stories appear in the source puzzles and gameplay.

## Reproduce and cite

Download a fixed dataset revision and use the code repository's `scripts/fetch_results.py` to restore
and verify the complete archive before running analysis. See the repository's CITATION.cff for author metadata.
Underlying puzzle stories retain their source ownership; this dataset does not assign a new license to them.
'''
    (out/'README.md').write_text(card)
    return info

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',default=str(ROOT));p.add_argument('--out',required=True);p.add_argument('--repo-id',default=DEFAULT_REPO)
    a=p.parse_args();print(json.dumps(prepare(a.root,a.out,a.repo_id),indent=2))

if __name__=='__main__': main()
