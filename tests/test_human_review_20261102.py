import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from turtle_loop.host_context import build_story_context
from turtle_loop.experiments import experience
from scripts.apply_human_review_20261102 import ROOT, DEST, AUTO


class HumanReviewTests(unittest.TestCase):
    def test_exact_annotations_and_delegation_loaded(self):
        m=json.loads((DEST/'manifest.json').read_text())
        bank={p['id']:p for p in json.loads((ROOT/'data/annotations/turtle50_v4/private.json').read_text())['puzzles']}
        self.assertEqual(hashlib.sha256((ROOT/m['source_workbook']).read_bytes()).hexdigest(),m['source_sha256'])
        self.assertEqual(set(AUTO),set(m['delegated_cases']))
        self.assertEqual(len(AUTO),34)
        for c in m['changes']:
            self.assertIn(c['example'],build_story_context(bank[c['puzzle_id']])['host_examples'])
        by={c['audit_case']:c['example'] for c in m['changes']}
        self.assertEqual(by['INBOX_TS042_016']['answer'],'yes and no')
        self.assertEqual(by['INBOX_TS042_018']['answer'],'no')
        self.assertTrue(by['INBOX_TS042_018']['provenance']['human_confirmed'])
        self.assertFalse(by['RUN_TS031_082']['provenance']['human_confirmed'])
        self.assertEqual(by['INBOX_TS002_076']['answer'],'no')
        self.assertEqual(by['RUN_TS035_068']['answer'],by['RUN_TS035_070']['answer'])
        self.assertNotIn('INBOX_TS022_002',by)  # deferred despite a label cell
        self.assertNotIn('INBOX_TS019_005',by)  # sibling note isn't a new label

    def test_reveal_uses_completed_source_narrative_without_private_extras(self):
        with tempfile.TemporaryDirectory() as folder:
            p={'id':'SRC','opening':'SOURCE','answer':'SHORT'}
            Path(folder,'host_context.json').write_text(json.dumps({'puzzle_id':'SRC','canonical_solution':'FULL HUMAN CLARIFICATION','host_examples':'SECRET EXAMPLES','rubric':'SECRET RUBRIC'}))
            rec=SimpleNamespace(folder=Path(folder),turns=[{'type':'final','text':'guess','label':'no','grade':'SECRET'}])
            value=experience(p,rec,{'stop_reason':'budget_exhausted'},'answer')
            self.assertEqual(value['revealed_source_answer'],'FULL HUMAN CLARIFICATION')
            self.assertNotIn('SECRET',str(value))
            self.assertNotIn('revealed_source_answer',experience(p,rec,{'stop_reason':'budget_exhausted'},'none'))
            with self.assertRaises(ValueError):experience({**p,'id':'TARGET'},rec,{'stop_reason':'solved'},'answer')
