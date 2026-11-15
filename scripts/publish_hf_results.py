#!/usr/bin/env python3
"""Publish a prepared experiment bundle, then verify a pinned remote download."""
import argparse
import json
import os
from pathlib import Path
from export_hf_results import digest, DEFAULT_REPO
from fetch_results import restore_archive

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--folder',required=True,help='New bundle made by export_hf_results.py')
    p.add_argument('--repo-id',default=DEFAULT_REPO)
    p.add_argument('--verification-dir',required=True,help='New local directory for the downloaded verification copy')
    p.add_argument('--receipt',required=True,help='New receipt file written only after verification')
    a=p.parse_args()
    folder=Path(a.folder).resolve();verification=Path(a.verification_dir).resolve();receipt=Path(a.receipt)
    if verification.exists() or receipt.exists():raise ValueError('Verification directory and receipt must be new')
    info=json.loads((folder/'release.json').read_text())
    if info['repo_id']!=a.repo_id:raise ValueError('Prepared repository differs from upload destination')
    if digest(folder/'results.tar.gz')!=info['archive_sha256']:raise ValueError('Prepared archive changed')
    from huggingface_hub import HfApi, snapshot_download
    token=(os.environ.get('HF_TOKEN') or '').strip() or None
    if 'HF_TOKEN' in os.environ and token is None:
        raise SystemExit('HF_TOKEN is set but empty. Fill it with a project-write token before publishing.')
    api=HfApi(token=token)
    api.create_repo(a.repo_id,repo_type='dataset',exist_ok=True,private=False)
    commit=api.upload_folder(repo_id=a.repo_id,repo_type='dataset',folder_path=folder,
        commit_message='Publish GoodTurtle experiment records and frozen evidence')
    revision=commit.oid
    snapshot_download(a.repo_id,repo_type='dataset',revision=revision,token=token,
        allow_patterns=['release.json','archive_manifest.json','results.tar.gz'],local_dir=verification/'download')
    downloaded=verification/'download'
    if digest(downloaded/'results.tar.gz')!=info['archive_sha256']:raise ValueError('Remote archive differs from prepared release')
    checked=restore_archive(downloaded/'results.tar.gz',downloaded/'archive_manifest.json',verification/'restored')
    result={'repo_id':a.repo_id,'repo_type':'dataset','revision':revision,'archive_file':'results.tar.gz',
        'archive_sha256':info['archive_sha256'],'source_dataset':info['source_dataset'],
        'counts':info['counts'],'download_verified':True,'verification':checked}
    receipt.parent.mkdir(parents=True,exist_ok=True);receipt.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
