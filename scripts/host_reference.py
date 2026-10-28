#!/usr/bin/env python3
"""Create and validate human-reference upload folders. Never modifies active Host packs."""
import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from turtle_loop.repository import resolve_historical_path

ALLOWED_EXTENSIONS={'.md','.txt','.json','.jsonl','.csv'}


def puzzle_ids(root):
    return {p['id'] for p in json.loads((Path(root)/'data/annotations/turtle50_v4/private.json').read_text())['puzzles']}


def init_source(ids, source_id, source_url='', input_file=None, root=ROOT):
    root=Path(root).resolve();ids=list(ids)
    if not ids or len(ids)!=len(set(ids)) or set(ids)-puzzle_ids(root):raise ValueError('Provide unique existing puzzle IDs; use commas for a multi-puzzle source')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}',source_id):raise ValueError('source-id must be 1-80 letters/digits/underscore/hyphen, starting with a letter/digit')
    bucket=ids[0] if len(ids)==1 else 'multi'
    folder=root/'data/host_reference/inbox'/bucket/source_id
    if not folder.resolve().is_relative_to(root/'data/host_reference/inbox'):raise ValueError('Invalid upload destination')
    blob=None
    if input_file:
        inp=Path(input_file)
        if inp.suffix.lower() not in ALLOWED_EXTENSIONS:raise ValueError('Use conversation-only .md/.txt/.json/.jsonl/.csv; do not import an entire account ZIP')
        blob=inp.read_bytes()
        if not blob.strip():raise ValueError('Empty trajectory')
        filename='trajectory'+inp.suffix.lower()
    else:filename='trajectory.md'
    metadata={'schema_version':1,'source_id':source_id,'puzzle_ids':ids,'source_url':source_url,'uploaded_at':datetime.now(ZoneInfo('Asia/Hong_Kong')).isoformat(),
        'review_status':'pending','role_mapping':{'user':'human_host','assistant':'player'},'role_mapping_status':'confirm_before_review',
        'trajectory_file':filename,'submission_status':'uploaded' if blob is not None else 'template',
        'trajectory_sha256':hashlib.sha256(blob).hexdigest() if blob is not None else None,
        'notes':'Preserve original questions, feedback, corrections, missing replies and final submissions. Upload does not change runtime Host context.'}
    folder.mkdir(parents=True,exist_ok=False)
    try:
        (folder/'source.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
        if blob is not None:(folder/filename).write_bytes(blob)
        else:(folder/filename).write_text('# 待填写人工 trajectory\n\n请替换本文件为完整对话；保留角色、原文、纠正和未答问题。\n填写后将 source.json 的 submission_status 改为 uploaded。\n')
    except Exception:
        shutil.rmtree(folder);raise
    return folder


def validate_inbox(root=ROOT):
    root=Path(root).resolve();base=root/'data/host_reference/inbox';valid_ids=puzzle_ids(root);rows=[]
    for path in sorted(base.rglob('source.json')):
        row={'source':str(path.relative_to(root)),'status':'valid','errors':[],'warnings':[]}
        try:
            d=json.loads(path.read_text());ids=d.get('puzzle_ids',[])
            if path.is_symlink() or not path.resolve().is_relative_to(base):raise ValueError('Source metadata must remain inside inbox')
            if d.get('schema_version')!=1:raise ValueError('Unsupported schema version')
            if not isinstance(ids,list) or not ids or any(not isinstance(i,str) for i in ids) or len(set(ids))!=len(ids) or set(ids)-valid_ids:raise ValueError('Invalid puzzle_ids')
            expected_bucket=ids[0] if len(ids)==1 else 'multi'
            if path.parent.name!=d.get('source_id') or path.parent.parent!=base/expected_bucket:raise ValueError('Folder does not match source ID / puzzle IDs')
            if d.get('review_status')!='pending':raise ValueError('Inbox records must remain pending; reviewed decisions belong in reviews/')
            if d.get('role_mapping') not in ({'user':'human_host','assistant':'player'},{'user':'player','assistant':'human_host'}):raise ValueError('Explicitly map user/assistant to human_host/player')
            filename=d.get('trajectory_file','')
            if not isinstance(filename,str) or Path(filename).name!=filename or Path(filename).suffix not in ALLOWED_EXTENSIONS:raise ValueError('Invalid trajectory_file')
            payload=path.parent/filename
            if payload.is_symlink() or not payload.resolve().is_relative_to(path.parent.resolve()):raise ValueError('Trajectory must remain inside its upload folder')
            data=payload.read_bytes()
            if not data.strip():raise ValueError('Empty trajectory')
            if d.get('trajectory_sha256') and hashlib.sha256(data).hexdigest()!=d['trajectory_sha256']:raise ValueError('Trajectory changed since import; preserve original source and submit a new revision')
            if d.get('submission_status') not in ('template','uploaded'):raise ValueError('Invalid submission_status')
            if d.get('submission_status')=='template':row['status']='draft';row['warnings'].append('Template only: replace text and set submission_status=uploaded')
            if d.get('role_mapping_status')!='confirmed':row['warnings'].append('Role mapping needs confirmation before review')
        except (ValueError,KeyError,TypeError,OSError) as exc:row['status']='invalid';row['errors'].append(str(exc))
        rows.append(row)
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    init=sub.add_parser('init',help='Create a new pending upload; existing folders are never overwritten')
    init.add_argument('--puzzle',required=True,help='Existing ID, or comma-separated IDs for one multi-puzzle conversation')
    init.add_argument('--source-id',required=True,help='Unique source name, e.g. 20261028_chat01')
    init.add_argument('--source-url',default='',help='Optional share/source URL; stored only, never fetched')
    init.add_argument('--file',type=Path,help='Optional existing conversation text/JSON/CSV to copy verbatim; omitted creates a template')
    sub.add_parser('validate',help='Validate all inbox metadata, puzzle IDs, file integrity and pending status; does not grade labels')
    resolve=sub.add_parser('locate',help='Locate a path mentioned in an older audit record')
    resolve.add_argument('path',help='Old repository-relative file path')
    args=p.parse_args()
    try:
        if args.command=='init':print(init_source(args.puzzle.split(','),args.source_id,args.source_url,args.file))
        elif args.command=='validate':
            rows=validate_inbox();print(json.dumps({'sources':rows,'invalid':sum(r['status']=='invalid' for r in rows)},ensure_ascii=False,indent=2));return int(any(r['status']=='invalid' for r in rows))
        else:
            result=resolve_historical_path(args.path)
            if not result.exists():raise ValueError('Path not found in current layout or migration map')
            print(result)
    except (ValueError,OSError) as exc:p.error(str(exc))
    return 0

if __name__=='__main__':raise SystemExit(main())
