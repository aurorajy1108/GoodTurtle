import json
import unittest
from pathlib import Path
from turtle_loop.dataset import load_dataset
from turtle_loop.host_context import build_story_context,host_payload

ROOT=Path(__file__).resolve().parents[1]


class CrossingGuardTests(unittest.TestCase):
    def test_original_references_preserved_and_direction_guard_reaches_runtime(self):
        old=json.loads((ROOT/'data/host_packs/archive/20261111_before_ts015_crossing/TS015.json').read_text())
        new=json.loads((ROOT/'data/host_packs/active/TS015.json').read_text())
        self.assertEqual(new['solution'],old['solution'])
        self.assertEqual(new['host_examples'][:len(old['host_examples'])],old['host_examples'])
        added=new['host_examples'][len(old['host_examples']):]
        self.assertEqual(len(added),5)
        self.assertTrue(all(e['provenance']['human_confirmed'] is False for e in added))
        puzzle=next(p for p in load_dataset(ROOT/'data/annotations/turtle50_v4/private.json')['puzzles'] if p['id']=='TS015')
        ctx=build_story_context(puzzle)
        mixed=next(e for e in added if e['answer']=='yes and no')
        runtime=host_payload(ctx,[],mixed['question'])
        self.assertTrue(any(e['answer']=='yes and no' and e['question']==mixed['question'] for e in runtime['active_puzzle']['host_examples']))
        self.assertTrue(any('CROSS' in b for b in runtime['active_puzzle']['label_boundaries']))
