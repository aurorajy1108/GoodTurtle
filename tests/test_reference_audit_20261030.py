"""Verify source preservation, explicit supersession and actual active loading."""
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from scripts.audit_host_references_20261030 import collect, apply_decisions, ROOT, REVIEW
from turtle_loop.host_context import build_story_context


class ReferenceAuditTests(unittest.TestCase):
    def test_frozen_sources_and_original_contexts_are_reproducible(self):
        audit=json.loads((REVIEW/'activation.json').read_text())
        for path, sha in audit['source_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),sha,path)
        bank=json.loads((ROOT/'data/annotations/turtle50_v4/private.json').read_text())['puzzles']
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'configs').mkdir();(root/'data/host_packs/active').mkdir(parents=True)
            shutil.copyfile(REVIEW/'baseline/bindings.json',root/'configs/host_bindings.json')
            for p in (REVIEW/'baseline').glob('TS*.json'):shutil.copyfile(p,root/'data/host_packs/active'/p.name)
            for puzzle in bank:
                self.assertEqual(build_story_context(puzzle,root)['context_sha256'],audit['context_sha256_before'][puzzle['id']])

    def test_visible_source_actions_are_not_dropped_or_promoted_as_human(self):
        rows,sources=collect();rows=apply_decisions(rows)
        self.assertEqual(len(rows),1098)
        self.assertEqual(sum(r['origin']=='model_generated' for r in rows),300)
        self.assertEqual(sum(r['origin']=='model_generated' and r['action_type']=='final' for r in rows),22)
        self.assertEqual(len(sources),20)
        for r in rows:self.assertFalse(r['human_confirmed'])
        by={r['case_id']:r for r in rows}
        self.assertEqual(by['INBOX_TS007_006']['proposed_label'],'yes')
        self.assertEqual(by['INBOX_TS017_041']['proposed_label'],'yes')
        self.assertEqual(by['INBOX_TS002_076']['proposed_label'],'no')
        self.assertEqual(by['INBOX_TS014_081']['decision'],'unanswered')
        self.assertEqual(by['INBOX_TS043_019']['observed'],'/quit')
        self.assertEqual(by['RUN_TS035_070']['observed'],'no')
        self.assertEqual(by['RUN_TS038_086']['decision'],'reviewed_no_issue_found')

    def test_adjudicated_references_reach_active_host_with_provenance(self):
        audit=json.loads((REVIEW/'activation.json').read_text())
        bank={p['id']:p for p in json.loads((ROOT/'data/annotations/turtle50_v4/private.json').read_text())['puzzles']}
        self.assertEqual(len(audit['changes']),103)
        for change in audit['changes']:
            context=build_story_context(bank[change['puzzle_id']])
            self.assertIn(change['example'],context['host_examples'])
            self.assertEqual(context['verification_policy'],'independent_then_adjudicate_v1')
            e=change['example'];self.assertFalse(e['provenance']['human_confirmed'])
            self.assertEqual(e['public_history'],[])  # no copied hundred-turn context per example
            if change['action'].startswith('add_'):
                self.assertEqual(e['provenance']['source_kind'],'model_generated')
                self.assertEqual(e['provenance']['answer_origin'],'ai_source_based_adjudication')
        live=build_story_context(bank['TS033'])
        case=next(e for e in live['host_examples'] if e['case_id']=='SHARE_6adf3775_120')
        self.assertEqual(case['answer'],'no');self.assertEqual(case['provenance']['original_answer'],'yes')


if __name__=='__main__':unittest.main()
