import json
import unittest
from turtle_loop.action_text import parse_prefix_action
from turtle_loop.engine import parse_action, ProtocolError
from turtle_loop.codex_client import output_contract
from turtle_loop.dialogue_contract import valid_dialogue_action

class PrefixTests(unittest.TestCase):
    def test_punctuation_and_multiline_preserved(self):
        body='Is "A" using C:\\new?\nOr a literal \\?'
        self.assertEqual(parse_action('QUESTION\n'+body),{'type':'question','text':body})
        self.assertEqual(parse_action('FINAL\n'+body,True)['text'],body)
        self.assertEqual(parse_action('QUESTION\r\n'+body),{'type':'question','text':body})

    def test_no_silent_multiple_actions_or_forced_question(self):
        for raw in ('QUESTION\n', 'QUESTION\nQ?\nFINAL\nGuess', 'QUESTION\nQ?'):
            with self.assertRaises(ProtocolError):parse_action(raw,True)
        with self.assertRaises(ValueError):parse_prefix_action('PROSE\nGuess')

    def test_mas_handoff_and_allowed_actions(self):
        action=parse_prefix_action('DISCUSS NEXT=B\nCheck identity.')
        self.assertTrue(valid_dialogue_action(action,['discuss']))
        self.assertFalse(valid_dialogue_action(action,['final'],True))
        self.assertFalse(valid_dialogue_action(parse_prefix_action('QUESTION\nQ?'),['question']))
        self.assertTrue(valid_dialogue_action(parse_prefix_action('FINAL\nAnswer'),['final'],True))

    def test_archived_json_and_codex_text_contract(self):
        self.assertEqual(parse_action('{"type":"question","text":"Q?"}')['text'],'Q?')
        self.assertEqual(output_contract(json.dumps({'action_protocol':'prefix-v1','opening':'Q','turn_control':'next'})),(None,None,''))

    def test_prefix_proposals_work_in_all_team_modes(self):
        import tempfile
        from pathlib import Path
        from turtle_loop.engine import Recorder, load_prompts
        from turtle_loop.experiments import TeamPlayer
        from test_loop import FakeClient, PUZZLE
        for strategy in ('independent','discuss','solo_reflect','alternating','shared_buffer'):
            with self.subTest(strategy=strategy), tempfile.TemporaryDirectory() as tmp:
                rec=Recorder(Path(tmp)/'game',PUZZLE,{'max_questions':3},load_prompts(),echo=False)
                leader=FakeClient(lambda i,p:'QUESTION\nIs it a dinner?')
                partner=FakeClient(lambda i,p:'QUESTION\nIs it a dinner?')
                team=TeamPlayer(leader,partner,strategy,rec)
                reply=team.complete('system',json.dumps({'opening':'Puzzle','visible_history':[],
                                     'turn_control':'next','action_protocol':'prefix-v1'}))
                self.assertEqual(parse_action(reply.text)['text'],'Is it a dinner?')
