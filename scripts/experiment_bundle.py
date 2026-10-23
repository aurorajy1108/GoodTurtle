#!/usr/bin/env python3
"""Export/verify local private inputs for coworkers; never uploads data or credentials."""
import argparse
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from turtle_loop.dataset import load_dataset
from turtle_loop.host_context import build_story_context


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def export(dataset, output, root=ROOT):
    root, output = Path(root), Path(output)
    data = load_dataset(dataset)
    bindings_path = root / 'configs/host_bindings.json'
    bindings = json.loads(bindings_path.read_text())
    members = {'data/annotations/turtle50_v2/private.json':
               (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode()}
    for puzzle in data['puzzles']:
        build_story_context(puzzle, root)
        for key in ('overlay_pack', 'legacy_pack'):
            name = bindings.get(puzzle['id'], {}).get(key)
            if name:
                source = (root / name).resolve()
                if not source.is_relative_to((root / 'data/host_packs').resolve()):
                    raise ValueError('Pack outside data/host_packs')
                members[str(source.relative_to(root.resolve()))] = source.read_bytes()
    manifest = {'format': 1, 'puzzle_ids': [p['id'] for p in data['puzzles']],
                'dataset': 'data/annotations/turtle50_v2/private.json',
                'required_bindings_sha256': digest(bindings_path.read_bytes()),
                'files': {name: digest(blob) for name, blob in members.items()},
                'privacy': 'Private puzzle answers and AI-reviewed rubrics. Share separately; not a Git release.',
                'credentials_included': False}
    # Only explicit dataset/pack members; never include .env, login files, configs or runs.
    with ZipFile(output, 'x', compression=ZIP_DEFLATED) as archive:
        for name, blob in members.items():
            archive.writestr(name, blob)
        archive.writestr('data/experiment_bundle_manifest.json', json.dumps(manifest, indent=2) + '\n')
    return {'archive': str(output), 'sha256': digest(output.read_bytes()),
            'puzzles': len(data['puzzles']), 'files': len(members)}


def verify(archive, root=ROOT):
    with ZipFile(archive) as bundle:
        names = bundle.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Duplicate archive members')
        for name in names:
            path = PurePosixPath(name)
            if path.is_absolute() or '..' in path.parts or not name.startswith('data/') or '\\' in name:
                raise ValueError('Invalid bundle member path')
        manifest = json.loads(bundle.read('data/experiment_bundle_manifest.json'))
        if manifest.get('format') != 1:
            raise ValueError('Unsupported bundle format')
        if set(names) != set(manifest['files']) | {'data/experiment_bundle_manifest.json'}:
            raise ValueError('Unlisted or missing bundle files')
        for name, expected in manifest['files'].items():
            if digest(bundle.read(name)) != expected:
                raise ValueError('Hash mismatch: ' + name)
        if digest((Path(root) / 'configs/host_bindings.json').read_bytes()) != manifest['required_bindings_sha256']:
            raise ValueError('Code host bindings differ from bundle; use the matching code revision')
    return {'verified': True, 'puzzles': len(manifest['puzzle_ids']), 'dataset': manifest['dataset']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    create = sub.add_parser('export', help='Create a NEW local ZIP of private dataset + required host packs')
    create.add_argument('--dataset', required=True, help='Private dataset JSON or labeled XLSX')
    create.add_argument('--out', required=True, help='New ZIP path; parent directory must exist')
    check = sub.add_parser('verify', help='Verify hashes, member paths and matching repository host bindings')
    check.add_argument('--archive', required=True, help='ZIP from export; verification does not extract or call models')
    args = parser.parse_args()
    result = export(args.dataset, args.out) if args.command == 'export' else verify(args.archive)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
