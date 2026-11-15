#!/usr/bin/env python3
"""Download a pinned experiment release and safely restore its original records."""
import argparse
import hashlib
import json
import re
import shutil
import tarfile
import tempfile
import urllib.request
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
PROTECTED = {'results/README.md','results/summary.csv','results/summary.json','results/remote.json'}

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def restore_archive(archive, manifest, root):
    root=Path(root).resolve(); inventory=json.loads(Path(manifest).read_text())
    with tempfile.TemporaryDirectory(prefix='goodturtle-restore-') as tmp:
        stage=Path(tmp);seen=set()
        with tarfile.open(archive,'r:gz') as tar:
            for member in tar:
                name=member.name;path=PurePosixPath(name)
                if (not member.isfile() or path.is_absolute() or '..' in path.parts
                        or not path.parts or path.parts[0]!='results'
                        or name not in inventory or name in seen):
                    raise ValueError('Unsafe or unexpected archive member: '+name)
                seen.add(name);target=stage/name;target.parent.mkdir(parents=True,exist_ok=True)
                if member.size!=inventory[name]['bytes']:raise ValueError('Archive size mismatch: '+name)
                with tar.extractfile(member) as src,target.open('wb') as dst:shutil.copyfileobj(src,dst)
                if digest(target)!=inventory[name]['sha256']:raise ValueError('Archive content mismatch: '+name)
        if seen!=set(inventory):raise ValueError('Archive is missing files')
        try:
            from .results_catalog import validate
        except ImportError:
            from results_catalog import validate
        checked=validate(stage)
        # Preflight every destination before writing any record.
        for name in inventory:
            target=root/name
            if not target.resolve().is_relative_to(root):raise ValueError('Destination escapes repository')
            if name not in PROTECTED and target.exists() and digest(target)!=inventory[name]['sha256']:
                raise ValueError('Refusing to overwrite a different local file: '+name)
        copied=0
        for name in inventory:
            if name in PROTECTED:continue
            target=root/name
            if not target.exists():
                target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(stage/name,target);copied+=1
    return {**checked,'restored_files':copied,'complete_download_verified':True}

def download(url,path):
    with urllib.request.urlopen(url,timeout=180) as src,path.open('wb') as dst:shutil.copyfileobj(src,dst)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',default=str(ROOT),help='Repository root receiving results/ (default: this checkout)')
    p.add_argument('--source',help='Local exported bundle directory for offline verification/restore')
    p.add_argument('--manifest',default=str(ROOT/'results/remote.json'),help='Pinned remote release descriptor')
    a=p.parse_args()
    if a.source:
        source=Path(a.source);info=json.loads((source/'release.json').read_text())
        if digest(source/'results.tar.gz')!=info['archive_sha256']:raise ValueError('Archive download differs from release')
        print(json.dumps(restore_archive(source/'results.tar.gz',source/'archive_manifest.json',a.root),indent=2));return
    descriptor=Path(a.manifest)
    if not descriptor.exists():raise SystemExit('No published remote descriptor yet. Use --source for a prepared local bundle.')
    info=json.loads(descriptor.read_text());repo=info['repo_id'];revision=info['revision']
    if not re.fullmatch(r'[\w.-]+/[\w.-]+',repo) or not re.fullmatch(r'[a-f0-9]{40}',revision):raise ValueError('Use a fixed valid HF dataset revision')
    with tempfile.TemporaryDirectory(prefix='goodturtle-download-') as tmp:
        source=Path(tmp);base=f'https://huggingface.co/datasets/{repo}/resolve/{revision}/'
        for name in ['results.tar.gz','archive_manifest.json']:download(base+name,source/name)
        if digest(source/'results.tar.gz')!=info['archive_sha256']:raise ValueError('Archive download differs from pinned release')
        print(json.dumps(restore_archive(source/'results.tar.gz',source/'archive_manifest.json',a.root),indent=2))

if __name__=='__main__':main()
