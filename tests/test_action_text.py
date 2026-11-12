import json
import tempfile
import unittest
from pathlib import Path
from turtle_loop.action_text import parse_prefix_action
from turtle_loop.engine import parse_action, ProtocolError
from turtle_loop.codex_client import output_contract
from turtle_loop.dialogue_contract import valid_dialogue_action
from turtle_loop.engine import Recorder, load_prompts, play
from test_loop import PUZZLE, FakeClient, evaluated

class PrefixTests(unittest.TestCase):
    def test_unique_inline_action_and_preamble_recover_verbatim_without_model(self):
        from turtle_loop.engine import parse_player_json
        from turtle_loop.player_format import is_untyped_prose, verbatim_proof
        for raw in ('QUESTION Is this written?',
                    'Thoughts remain hypothetical.\nQUESTION Is this written?',
                    'Thoughts.\nFINAL: Keep this exact explanation.\nAnd this qualifier.'):
            action, meta = parse_player_json(raw)
            self.assertEqual(action['text'], raw[meta['text_span'][0]:meta['text_span'][1]])
            self.assertTrue(verbatim_proof(raw, action))
            self.assertFalse(is_untyped_prose(raw))
        action, _ = parse_player_json('Notes.\nQUESTION NEXT=B Is this written?')
        self.assertEqual(action, {'type': 'question', 'text': 'Is this written?', 'next_speaker': 'B'})
        for raw in ('QUESTION First?\nFINAL Second.', 'Notes.\nQUESTION First?\nQUESTION Second.'):
            with self.assertRaises(ProtocolError):
                parse_action(raw)

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

    def test_dialogue_contract_lists_literal_headers_not_a_copyable_placeholder(self):
        from turtle_loop.dialogue_contract import dialogue_contract_text
        text=dialogue_contract_text(['question','discuss'])
        self.assertNotIn('ACTION NEXT=',text)
        for header in ('QUESTION NEXT=A','QUESTION NEXT=B','DISCUSS NEXT=A','DISCUSS NEXT=B'):
            self.assertIn(header,text)
            self.assertTrue(valid_dialogue_action(parse_prefix_action(header+'\nBody'),['question','discuss']))

    def test_archived_json_and_codex_text_contract(self):
        self.assertEqual(parse_action('{"type":"question","text":"Q?"}')['text'],'Q?')
        self.assertEqual(output_contract(json.dumps({'action_protocol':'prefix-v1','opening':'Q','turn_control':'next'})),(None,None,''))

    def test_mandatory_final_control_matches_new_or_frozen_legacy_prompt(self):
        for prefix in (True,False):
            with self.subTest(prefix=prefix), tempfile.TemporaryDirectory() as tmp:
                prompts=load_prompts()
                if not prefix:prompts['player']='Legacy prompt: return one JSON action.'
                def action(n,payload):
                    self.assertIn('mandatory last turn',payload['turn_control'])
                    if prefix:
                        self.assertEqual(payload['action_protocol'],'prefix-v1')
                        self.assertIn('Return FINAL followed by a newline',payload['turn_control'])
                        self.assertNotIn('type=final',payload['turn_control'])
                        return 'FINAL\nsubmitted explanation'
                    self.assertNotIn('action_protocol',payload)
                    self.assertIn('Return type=final',payload['turn_control'])
                    return '{"type":"final","text":"submitted explanation"}'
                rec=Recorder(Path(tmp)/'game',PUZZLE,{'max_questions':1},prompts,echo=False)
                result=play(PUZZLE,{'max_questions':1},rec,{'player':FakeClient(action),
                    'host':FakeClient(lambda *args:self.fail('Final sent to Host')),
                    'grader':FakeClient(lambda *args:evaluated())},prompts)
                self.assertTrue(result['success'])
                self.assertEqual(result['submissions'],1)

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

    def test_unique_preamble_recovery_and_exact_proof(self):
        from turtle_loop.engine import parse_player_json
        from turtle_loop.player_format import local_repair, load_policy, verbatim_proof
        body='Is "course" a meal?\nKeep this qualifier: before dinner.'
        raw='Some unwanted explanation.\nQUESTION\n'+body
        action,meta=parse_player_json(raw)
        self.assertEqual(action,{'type':'question','text':body})
        self.assertEqual(meta['discarded_prefix_chars'],raw.index('QUESTION'))
        self.assertEqual(local_repair(raw,False,load_policy())[0],action)
        self.assertTrue(verbatim_proof(raw,action))
        self.assertFalse(verbatim_proof(raw,{'type':'question','text':'Is "course" a meal?'}))
        self.assertFalse(verbatim_proof(raw,{'type':'final','text':body}))
        with self.assertRaises(ProtocolError):parse_action(raw,True)
        mas,_=parse_player_json('Explanation.\nDISCUSS NEXT=B\nCheck the timeline.')
        self.assertTrue(valid_dialogue_action(mas,['discuss']))

    def test_ambiguous_prefixes_never_call_formatter(self):
        from turtle_loop.player_format import repair, load_policy, verbatim_proof
        from unittest.mock import patch
        for raw in ('Preamble\nQUESTION\nQ?\nFINAL\nAnswer',
                    'Preamble\nQUESTION\n',
                    '{"type":"final","text":"Guess"}\nQUESTION\nQ?',
                    'Preamble\n```text\nQUESTION\nQ?\n```'):
            with self.subTest(raw=raw), patch('turtle_loop.providers.Client') as formatter:
                with self.assertRaises(ProtocolError):
                    repair(raw,False,load_policy(),lambda c:None,lambda *a,**k:None)
                formatter.assert_not_called()
                self.assertFalse(verbatim_proof(raw,{'type':'question','text':'Q?'}))

    def test_game_audits_preamble_without_extra_player_call(self):
        import tempfile
        from pathlib import Path
        from turtle_loop.engine import Recorder, load_prompts, play
        from test_loop import FakeClient, PUZZLE, evaluated
        with tempfile.TemporaryDirectory() as tmp:
            prompts=load_prompts();config={'max_questions':2}
            rec=Recorder(Path(tmp)/'game',PUZZLE,config,prompts,echo=False)
            player=FakeClient(lambda i,p:'Unwanted preface.\nQUESTION\nIs this relevant?' if i==1 else 'FINAL\nComplete explanation')
            clients={'player':player,'host':FakeClient(lambda i,p:'no'),
                     'grader':FakeClient(lambda i,p:evaluated())}
            result=play(PUZZLE,config,rec,clients,prompts)
            self.assertTrue(result['success'])
            self.assertEqual(len(player.inputs),2)
            self.assertEqual(rec.turns[0]['text'],'Is this relevant?')
            events=[json.loads(line) for line in (rec.folder/'trajectory.jsonl').read_text().splitlines()]
            self.assertTrue(any(e.get('method')=='unique_prefix_action' for e in events))
