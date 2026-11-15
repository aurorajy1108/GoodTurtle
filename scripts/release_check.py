#!/usr/bin/env python3
"""Offline release checks; no API calls and no rewriting of research records."""
import json
import re
from pathlib import Path
try:
    from .results_catalog import validate
except ImportError:
    from results_catalog import validate

ROOT = Path(__file__).resolve().parents[1]

def check(root=ROOT):
    root = Path(root)
    remote_path=root/'results/remote.json'
    remote=json.loads(remote_path.read_text()) if remote_path.exists() else None
    if remote and (not remote.get('download_verified') or not re.fullmatch(r'[a-f0-9]{40}',remote.get('revision',''))):
        raise ValueError('Remote experiment release is not verified/pinned')
    lightweight=bool(remote and not (root/'results/catalog.json').exists())
    audit = json.loads((root/'docs/release/html_inventory.json').read_text())
    for item in audit:
        path = root/item['path']
        if item['decision'] == 'keep':
            if not path.is_file():
                raise ValueError('Runtime HTML missing: '+item['path'])
        else:
            if path.exists() or (not lightweight and not (root/item['replacement']).is_file()):
                raise ValueError('HTML cleanup/replacement failed: '+item['path'])
    actual = {str(p.relative_to(root)) for p in root.rglob('*.html') if '.git' not in p.parts}
    expected = {i['path'] for i in audit if i['decision'] == 'keep'}
    if actual != expected:
        raise ValueError('Unexpected HTML files: '+str(sorted(actual ^ expected)))
    for name in ('.env.local', '.env', '.DS_Store'):
        if (root/name).exists():
            raise ValueError('Local-only file in release tree: '+name)
    validation={'remote_release_verified':True,'games':remote['counts']['games'],'submissions':remote['counts']['turns'],'local_full_archive':False} if lightweight else validate(root)
    return {**validation, 'html_inspected':len(audit),
            'generated_html_removed':sum(i['decision']!='keep' for i in audit),
            'runtime_html_retained':len(expected)}

if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
