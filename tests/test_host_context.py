import copy
import json
import tempfile
import unittest
from pathlib import Path
from turtle_loop.engine import Recorder, load_prompts, play
from turtle_loop.host_context import build_story_context, story_fingerprint
from test_loop import PUZZLE, FakeClient, evaluated


class HostContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'configs').mkdir()
        (self.root/'data/host_packs').mkdir(parents=True)
        self.puzzle = copy.deepcopy(PUZZLE)
        self.puzzle['completion_requirements'] = ['PRIVATE_COMPLETION_SENTINEL']
        self.pack = {'solution': 'PRIVATE_CANONICAL_SENTINEL', 'canonical_facts': ['PRIVATE_FACT'],
                     'host_examples': [{'case_id': 'E1', 'question': 'What colour?', 'answer': 'yes and no'}]}
        (self.root/'data/host_packs/legacy.json').write_text(json.dumps(self.pack))
        self.binding = {'legacy_pack': 'data/host_packs/legacy.json', 'version': 'test',
                        'story_sha256': story_fingerprint(self.puzzle),
                        'label_overrides': {'E1': {'answer': 'irrelevant', 'rationale': 'Incidental'}}}
        self.write_binding()

    def write_binding(self):
        (self.root/'configs/host_bindings.json').write_text(json.dumps({'FIXTURE': self.binding}))

    def test_bound_examples_and_wrong_story_rejected(self):
        story = build_story_context(self.puzzle, self.root)
        self.assertEqual(story['host_examples'][0]['answer'], 'irrelevant')
        self.assertEqual(story['canonical_solution'], 'PRIVATE_CANONICAL_SENTINEL')
        for field in ('opening', 'answer'):
            changed = {**self.puzzle, field: 'other story'}
            with self.assertRaisesRegex(ValueError, 'does not match'):
                build_story_context(changed, self.root)

    def test_missing_pack_or_escaping_path_fails(self):
        self.binding['legacy_pack'] = 'data/host_packs/missing.json'
        self.write_binding()
        with self.assertRaises(FileNotFoundError):
            build_story_context(self.puzzle, self.root)
        self.binding['legacy_pack'] = '../outside.json'
        self.write_binding()
        with self.assertRaisesRegex(ValueError, 'inside'):
            build_story_context(self.puzzle, self.root)

    def test_reviewed_overlay_replaces_legacy_labels(self):
        overlay = {'version': 'review-v3', 'replace_host_examples': True,
                   'review_status': 'ai_review_pending_human',
                   'host_examples': [{'case_id': 'NEW', 'question': 'New question?', 'answer': 'no'}]}
        (self.root/'data/host_packs/overlay.json').write_text(json.dumps(overlay))
        self.binding['overlay_pack'] = 'data/host_packs/overlay.json'
        self.write_binding()
        story = build_story_context(self.puzzle, self.root)
        self.assertEqual([x['case_id'] for x in story['host_examples']], ['NEW'])
        self.assertEqual(story['canonical_solution'], 'PRIVATE_CANONICAL_SENTINEL')
        self.assertEqual(story['review_status'], 'ai_review_pending_human')

    def test_shared_snapshot_private_from_player(self):
        from unittest.mock import patch
        story = build_story_context(self.puzzle, self.root)
        prompts = load_prompts()
        rec = Recorder(self.root/'run', self.puzzle, {'max_questions': 2}, prompts, echo=False)
        clients = {'player': FakeClient(lambda i,p: json.dumps({'type':'question' if i==1 else 'final','text':'Guess'})),
                   'host': FakeClient(lambda i,p: 'no'), 'grader': FakeClient(lambda i,p: evaluated())}
        with patch('turtle_loop.engine.build_story_context', return_value=story):
            result = play(self.puzzle, {'max_questions': 2}, rec, clients, prompts)
        self.assertTrue(result['success'])
        host = json.loads(clients['host'].inputs[0][1])['active_puzzle']
        grader = json.loads(clients['grader'].inputs[0][1])['story_context']
        self.assertEqual(host, grader)
        self.assertEqual(host, json.loads((rec.folder/'host_context.json').read_text()))
        public = json.dumps(clients['player'].inputs)
        for marker in ('PRIVATE_', 'SECRET_', 'canonical_facts', 'host_examples'):
            self.assertNotIn(marker, public)
