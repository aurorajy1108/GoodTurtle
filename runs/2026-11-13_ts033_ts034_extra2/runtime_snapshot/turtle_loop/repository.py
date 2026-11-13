"""Resolve dated provenance paths after repository layout migrations.

Only audit/archive consumers use this helper. Runtime host bindings remain explicit:
missing or invalid active packs must fail rather than silently load an archive.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def resolve_historical_path(name, root=ROOT):
    root=Path(root).resolve()
    source=(root/name).resolve()
    if not source.is_relative_to(root):raise ValueError('Historical path must stay within repository')
    if source.exists():return source
    manifest=root/'configs/repository_layout.json'
    moves=json.loads(manifest.read_text()).get('moves',{}) if manifest.exists() else {}
    target=(root/moves.get(str(Path(name)),str(name))).resolve()
    if not target.is_relative_to(root):raise ValueError('Mapped path must stay within repository')
    return target
