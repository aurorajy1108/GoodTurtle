import copy
import json
import tempfile
import unittest
import hashlib
from pathlib import Path

from turtle_loop.host_context import (host_payload, grader_story_context, context_policy,
                                      build_story_context, RUNTIME_VERSION)
from turtle_loop.engine import Recorder, load_prompts
from test_loop import PUZZLE


class RuntimeContextTests(unittest.TestCase):
    def test_ts013_system_causation_correction_is_bound_and_retrieved(self):
        root=Path(__file__).resolve().parents[1]
        puzzles=json.loads((root/'data/annotations/turtle50_v4/private.json').read_text())['puzzles']
        puzzle=next(p for p in puzzles if p['id']=='TS013')
        review=json.loads((root/'data/host_reference/reviews/ts013_20261108_causal_fix.json').read_text())
        context=build_story_context(puzzle)
        self.assertEqual(context['binding_version'],review['active_version'])
        self.assertIn('An action or mistake in an academic course-selection/enrolment system did not cause the courses to disappear.',context['explicit_negatives'])
        audit=[]
        payload=host_payload(context,[{'type':'question','text':e['question'],'feedback':e['answer']}
                             for e in review['public_history']],review['question'],{'host_examples_limit':1},audit.append)
        precedent=payload['active_puzzle']['host_examples'][0]
        self.assertEqual(precedent['question'],review['question'])
        self.assertEqual(precedent['answer'],'no')
        self.assertEqual(precedent['public_history'],review['public_history'])
        self.assertEqual(audit[0]['selected'][0]['case_id'],review['active_case_id'])
        self.assertNotIn('original_answer',json.dumps(payload))
        self.assertNotIn('source_file',json.dumps(payload))

    def setUp(self):
        self.context = {'puzzle_id': 'FIXTURE', 'canonical_solution': 'The eraser covers the refill hole.',
                        'canonical_facts': ['It is a mechanical pencil.'],
                        'completion_requirements': ['Remove eraser to refill lead.'],
                        'explicit_negatives': ['The tip was not exposed by gravity.'],
                        'label_boundaries': ['Do not confuse refill access with tip extension.'],
                        'review_status': 'SECRET_METADATA',
                        'host_examples': [
                            {'case_id': 'E1', 'question': 'Was the eraser removed to refill lead?', 'answer': 'yes',
                             'rationale': 'SECRET_RATIONALE', 'provenance': 'SECRET_SOURCE'},
                            {'case_id': 'E2', 'question': 'Did that expose the writing tip?', 'answer': 'no',
                             'public_history': [{'question': 'Did she remove the eraser?', 'answer': 'yes',
                                                 'notes': 'SECRET_HISTORY_REVIEW'}]},
                            {'case_id': 'E3', 'question': 'Was the station at the seaside?', 'answer': 'irrelevant'}]}

    def test_exact_match_precedes_similar_opposite_label_and_strips_metadata(self):
        self.context['host_examples'].insert(0, {'case_id': 'NEG',
            'question': 'Was the eraser not removed to refill lead?', 'answer': 'no'})
        original = copy.deepcopy(self.context)
        audit = []
        payload = host_payload(self.context, [], 'Was the eraser removed to refill lead?',
                               {'host_examples_limit': 1}, audit.append)
        self.assertEqual(payload['active_puzzle']['host_examples'],
                         [{'question': 'Was the eraser removed to refill lead?', 'answer': 'yes'}])
        self.assertEqual(audit[0]['selected'][0]['case_id'], 'E1')
        self.assertNotIn('SECRET_', json.dumps(payload))
        self.assertEqual(original, self.context)

    def test_example_history_and_current_history_remain_separate_and_complete(self):
        history = [{'type': 'question', 'text': 'Did he open the box?', 'feedback': 'no'}] * 100
        payload = host_payload(self.context, history, 'Did that expose the writing tip?',
                               {'host_examples_limit': 1})
        self.assertEqual(payload['visible_history'], history)
        precedent = payload['active_puzzle']['host_examples'][0]
        self.assertEqual(precedent['public_history'], [{'question': 'Did she remove the eraser?', 'answer': 'yes'}])
        self.assertNotIn('SECRET_', json.dumps(payload))

    def test_whole_examples_only_no_truncation_and_no_unrelated_fillers(self):
        audit = []
        payload = host_payload(self.context, [], 'Did that expose the writing tip?',
                               {'host_examples_max_chars': 10}, audit.append)
        self.assertEqual(payload['active_puzzle']['host_examples'], [])
        self.assertIn('E2', audit[0]['skipped_oversize'])
        self.assertEqual(host_payload(self.context, [], 'xyzzy quux')['active_puzzle']['host_examples'], [])

    def test_grader_keeps_story_constraints_but_uses_its_own_selection(self):
        context = grader_story_context(self.context, 'Removed the eraser to refill lead.',
                                       {'grader_examples_limit': 1})
        for key in ('canonical_solution', 'canonical_facts', 'completion_requirements',
                    'explicit_negatives', 'label_boundaries'):
            self.assertEqual(context[key], self.context[key])
        self.assertEqual(len(context['host_examples']), 1)
        self.assertNotIn('SECRET_', json.dumps(context))

    def test_policy_rejects_silent_misconfiguration(self):
        for value in ({'typo': 1}, {'host_examples_limit': -1}, {'grader_examples_limit': True},
                      {'host_examples_max_chars': '6000'}, []):
            with self.assertRaises(ValueError):
                context_policy(value)
        p = host_payload(self.context, [], 'eraser', {'host_examples_limit': 0})
        self.assertEqual(p['active_puzzle']['host_examples'], [])

    def test_all_dataset_contexts_preserve_story_and_retrieve_exact_examples(self):
        root = Path(__file__).resolve().parents[1]
        puzzles = json.loads((root/'data/annotations/turtle50_v4/private.json').read_text())['puzzles']
        for puzzle in puzzles:
            context = build_story_context(puzzle)
            for example in context['host_examples']:
                # Large budget verifies ranking, not the deliberately bounded default.
                payload = host_payload(context, example.get('public_history', []), example['question'],
                                       {'host_examples_max_chars': 50000})['active_puzzle']
                self.assertEqual(payload['canonical_solution'], context['canonical_solution'])
                self.assertTrue(any(e['question'] == example['question'] for e in payload['host_examples']),
                                (puzzle['id'], example['case_id']))

    def test_resume_rejects_mixing_old_host_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = {'max_questions': 3}; prompts = load_prompts()
            rec = Recorder(Path(tmp)/'game', PUZZLE, config, prompts, echo=False)
            result = rec.report('interrupted', 'fixture')
            self.assertEqual(result['evaluation_versions']['runtime_context_version'], RUNTIME_VERSION)
            del result['evaluation_versions']['runtime_context_version']
            (rec.folder/'result.json').write_text(json.dumps(result))
            with self.assertRaisesRegex(ValueError, 'Runtime context policy changed'):
                Recorder.restore(rec.folder, PUZZLE, config, prompts)

    def test_resume_launcher_preserves_frozen_code_and_rejects_unsupported_snapshots(self):
        from scripts.resume_study import prepare
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root/'old'; snap = source/'runtime_snapshot'
            (snap/'turtle_loop').mkdir(parents=True)
            engine = snap/'turtle_loop/engine.py'; experiments = snap/'turtle_loop/experiments.py'
            engine.write_text('def restore(): pass\n# OLD FROZEN POLICY\n')
            experiments.write_text('# --resume\n')
            (source/'status.json').write_text(json.dumps({'status': 'interrupted'}))
            (source/'study_plan.json').write_text(json.dumps({'jobs': [{'name': 'team',
                'argv': ['python', str(snap/'scripts/experiment.py'), '--out', str(source/'team'), '--resume']}]}))
            def hashes():
                (source/'snapshot_hashes.json').write_text(json.dumps({str(p.relative_to(snap)):
                    hashlib.sha256(p.read_bytes()).hexdigest() for p in (engine, experiments)}))
            hashes()
            record = prepare(source, root/'new')
            self.assertEqual(record['controller_overlay'], {})
            self.assertEqual((root/'new/runtime_snapshot/turtle_loop/engine.py').read_bytes(), engine.read_bytes())
            self.assertEqual(record['argv'].count('--resume'), 1)
            engine.write_text('# no restore support\n'); hashes()
            with self.assertRaisesRegex(ValueError, 'predates resume support'):
                prepare(source, root/'rejected')
            self.assertFalse((root/'rejected').exists())
