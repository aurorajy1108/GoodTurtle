"""Verify the audited historical examples actually reach the bound host context."""
import hashlib
import json
import unittest
from pathlib import Path
from turtle_loop.dataset import load_dataset
from turtle_loop.host_context import build_story_context, story_fingerprint, grading_fingerprint

ROOT=Path(__file__).resolve().parents[1]


class HistoryQAMergeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit=json.loads((ROOT/'docs/reviews/history_qa_merge_20261026.json').read_text())
        cls.bank={p['id']:p for p in load_dataset(ROOT/cls.audit['dataset'])['puzzles']}
        cls.bindings=json.loads((ROOT/'configs/host_bindings.json').read_text())

    def test_every_supplied_case_is_accounted_for_without_rewriting_source(self):
        expected_sources={str(p.relative_to(ROOT)) for p in (ROOT/'data/host_packs').glob('LOOP_TS*_history_v1.json')}
        self.assertEqual(expected_sources,{p['source_pack'] for p in self.audit['puzzles']})
        counts={'accepted':0,'rewritten':0,'withheld':0}
        for group in self.audit['puzzles']:
            raw=(ROOT/group['source_pack']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),group['source_sha256'])
            sources={e['case_id']:e for e in json.loads(raw)['host_examples']}
            self.assertEqual(len(sources),len(group['decisions']))
            self.assertEqual(set(sources),{e['source_case_id'] for e in group['decisions']})
            for entry in group['decisions']:
                self.assertEqual(sources[entry['source_case_id']],entry['original'])
                counts[entry['decision']]+=1
        self.assertEqual(counts,self.audit['summary'])
        self.assertEqual(sum(counts.values()),89)
        self.assertFalse(self.audit['human_confirmed'])

    def test_bound_host_contains_only_adjudicated_history_and_preserves_core(self):
        for group in self.audit['puzzles']:
            with self.subTest(puzzle=group['puzzle_id']):
                puzzle=self.bank[group['puzzle_id']]
                self.assertEqual(story_fingerprint(puzzle),group['story_sha256'])
                self.assertEqual(grading_fingerprint(puzzle),group['grading_sha256'])
                base_path=ROOT/group['base_binding']['overlay_pack']
                self.assertEqual(hashlib.sha256(base_path.read_bytes()).hexdigest(),group['base_sha256'])
                base=json.loads(base_path.read_text())
                merged=json.loads((ROOT/group['merged_pack']).read_text())
                self.assertEqual(self.bindings[puzzle['id']]['overlay_pack'],group['merged_pack'])
                for field in ('solution','canonical_facts','explicit_negatives','unknown_details','irrelevant_details','event_order','knowledge_states','verification_policy'):
                    self.assertEqual(merged.get(field),base.get(field),field)
                active=build_story_context(puzzle)
                actual={e['case_id']:e for e in active['host_examples']}
                self.assertEqual(len(actual),len(active['host_examples']))
                for old in base['host_examples']:self.assertEqual(actual[old['case_id']],old)
                history={k for k in actual if k.startswith('HIST_')}
                reviewed={e['merged_case_id'] for e in group['decisions'] if e['decision']!='withheld'}
                self.assertEqual(history,reviewed)
                for entry in group['decisions']:
                    if entry['decision']=='withheld':
                        self.assertNotIn(entry['source_case_id'],actual)
                        continue
                    current=actual[entry['merged_case_id']]
                    self.assertEqual(current,entry['merged'])
                    self.assertFalse(current['provenance']['human_confirmed'])
                    self.assertEqual(current['answer'],entry['original']['answer'])
                    self.assertEqual(current.get('public_history',[]),entry['original'].get('public_history',[]))
                    self.assertEqual(current['provenance']['source_case'],entry['original']['provenance']['source_case'])
                    if entry['decision']=='rewritten':
                        self.assertNotEqual(current['question'],entry['original']['question'])
                        self.assertEqual(current['provenance']['question_origin'],'ai_rewrite_of_user_supplied_question')
                    else:self.assertEqual(current['question'],entry['original']['question'])
                self.assertEqual(len(actual),group['final_examples'])

    def test_regression_cases_match_live_examples_and_exclude_held_paternity_claim(self):
        cases=json.loads((ROOT/'tests/fixtures/history_qa_merged_v1.json').read_text())
        self.assertEqual(len(cases),88)
        for case in cases:
            examples={e['case_id']:e for e in build_story_context(self.bank[case['puzzle_id']])['host_examples']}
            self.assertEqual(case['question'],examples[case['id']]['question'])
            self.assertEqual(case['expected'],examples[case['id']]['answer'])
        self.assertNotIn('HIST_TS006_010',{c['id'] for c in cases})
        self.assertEqual(len(self.bank),50)
        for puzzle in self.bank.values():build_story_context(puzzle)
