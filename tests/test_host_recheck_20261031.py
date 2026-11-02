import hashlib
import json
import unittest
from scripts.recheck_host_31_40 import ROOT, MANIFEST, issues, decisions, human_rows, HUMAN_SCOPE, PROTOCOL_CLOSED
from turtle_loop.host_context import build_story_context


class HostRecheckTests(unittest.TestCase):
    def test_all_target_flags_have_an_explicit_resolution_or_human_question(self):
        rows=issues();done,pending=decisions()
        target={r['case_id'] for r in rows if 'TS031'<=r['puzzle_id']<='TS040'}
        self.assertEqual(len(target),87)
        self.assertEqual(set(done)|set(pending),target)
        self.assertFalse(set(done)&set(pending))
        self.assertEqual(len(done),53)
        self.assertEqual(len(pending),34)
        for d in pending.values():self.assertTrue(d['human_question'])

    def test_only_requested_unresolved_cases_are_in_the_checklist(self):
        rows=issues();done,pending=decisions();groups=human_rows(rows,pending,done)
        actual=[r['case_id'] for g in groups for r in g['cases']]
        self.assertEqual(len(actual),len(set(actual)))
        self.assertEqual(set(actual),{r['case_id'] for r in rows if r['puzzle_id'] in HUMAN_SCOPE}-set(done)-PROTOCOL_CLOSED)
        self.assertEqual(len(HUMAN_SCOPE),22)
        self.assertTrue(all(g['puzzle_id'] in HUMAN_SCOPE for g in groups))
        self.assertFalse({'NEW042','NEW043','NEW044'}&set(actual))  # TS037 outside requested scope

    def test_runtime_uses_reviewed_labels_without_rewriting_sources(self):
        manifest=json.loads(MANIFEST.read_text())
        bank={p['id']:p for p in json.loads((ROOT/'data/annotations/turtle50_v4/private.json').read_text())['puzzles']}
        for p,h in manifest['source_sha256'].items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),h)
        self.assertEqual(len(manifest['changes']),47)
        for c in manifest['changes']:
            self.assertIn(c['example'],build_story_context(bank[c['puzzle_id']])['host_examples'])
            self.assertFalse(c['example']['provenance']['human_confirmed'])
        by={c['source_case']:c['example'] for c in manifest['changes']}
        self.assertEqual(by['NEW003']['answer'],'no')
        self.assertEqual(by['NEW011']['answer'],'irrelevant')
        self.assertEqual(by['NEW031']['provenance']['original_answer'],'mo')
        self.assertEqual(by['RUN_TS038_080']['answer'],'irrelevant')
        self.assertEqual(len(by['RUN_TS038_080']['public_history']),6)
        for pid in ['TS036','TS040']:
            self.assertEqual(manifest['context_sha256_before'][pid],manifest['context_sha256_after'][pid])
