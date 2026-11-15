import copy
import json
import tempfile
import unittest
from argparse import Namespace
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch
from turtle_loop.action_text import recover_prefix_action
from turtle_loop.dialogue import FreeDialoguePlayer,dialogue_settings,dialogue_system_prompt
from turtle_loop.dialogue_recovery import saved_dialogue_action_recovery
from turtle_loop.engine import Recorder,ProtocolError,load_prompts,play,parse_player_json
from turtle_loop.providers import Client
from test_loop import PUZZLE,evaluated
from test_sessions import Response


class DialogueRecoveryTests(unittest.TestCase):
    def test_wrapper_requires_explicit_type_and_consistent_handoff(self):
        action,meta=recover_prefix_action('ACTION NEXT=B\nFINAL\nKeep all words and "quotes".')
        self.assertEqual(action,{'type':'final','text':'Keep all words and "quotes".','next_speaker':'B'})
        self.assertEqual(meta['method'],'explicit_placeholder_wrapper')
        self.assertIsNone(recover_prefix_action('ACTION NEXT=B\nSome untyped prose.'))
        with self.assertRaises(ValueError):recover_prefix_action('ACTION NEXT=B\nFINAL NEXT=A\nAnswer')

    @patch.dict('os.environ',{'DEEPSEEK_API_KEY':'fixture'})
    def test_resume_restores_both_agents_and_grades_saved_final_without_another_solver_call(self):
        with tempfile.TemporaryDirectory() as tmp,ExitStack() as stack:
            config={'max_questions':3,'session_mode':'persistent',**{
                r:{'provider':'deepseek','model':r,'max_retries':0} for r in ('host','player','grader')}}
            prompts=load_prompts();prompts['player']=dialogue_system_prompt()
            rec=Recorder(Path(tmp)/'game',PUZZLE,config,prompts,echo=False)
            counts={r:0 for r in ('host','player','grader','partner')}
            def response(req,**kwargs):
                body=json.loads(req.data);role=body['model'];counts[role]+=1
                text={'player':'QUESTION NEXT=B\nQuestion?', 'partner':'ACTION NEXT=B\nFINAL\nsubmitted explanation',
                      'host':'yes','grader':evaluated()}[role]
                return Response({'id':f'{role}-{counts[role]}','choices':[{'message':{'content':text},'finish_reason':'stop'}]})
            stack.enter_context(patch('urllib.request.OpenerDirector.open',side_effect=response))
            settings=dialogue_settings(Namespace())
            def clients(rec):
                c={r:Client(config[r],r,rec.audit) for r in ('host','player','grader')}
                c['player']=FreeDialoguePlayer(c['player'],Client(config['player']|{'model':'partner'},'partner',rec.audit),rec,settings)
                return c
            def old_parser(raw):
                if raw.startswith('ACTION '):raise ProtocolError('Old placeholder failure')
                return parse_player_json(raw)
            with patch('turtle_loop.dialogue.parse_player_json',side_effect=old_parser):
                stopped=play(PUZZLE,config,rec,clients(rec),prompts)
            self.assertEqual(stopped['status'],'error')
            self.assertEqual(stopped['submissions'],1)
            saved_calls=[json.loads(s) for s in (rec.folder/'api_calls.jsonl').read_text().splitlines()]
            checkpoint=saved_dialogue_action_recovery(stopped,saved_calls,rec.turns,config,rec.folder)
            self.assertIsNotNone(checkpoint)
            marker=rec.folder/'dialogue_action_recovery.json';marker.write_text(json.dumps(checkpoint))
            restored=Recorder.restore(rec.folder,PUZZLE,config,prompts,echo=False)
            before=dict(counts)
            result=play(PUZZLE,config,restored,clients(restored),prompts)
            self.assertTrue(result['success']);self.assertEqual(result['submissions'],2)
            self.assertEqual(result['counted_questions'],1)
            self.assertEqual(counts['player'],before['player'])
            self.assertEqual(counts['partner'],before['partner'])
            self.assertEqual(counts['host'],before['host'])
            self.assertEqual(counts['grader'],before['grader']+1)
            self.assertEqual(restored.turns[-1]['text'],'submitted explanation')
            self.assertFalse(marker.exists())
            # A later batch resume must be able to skip this completed game.
            completed=Recorder.restore(rec.folder,PUZZLE,config,prompts,echo=False)
            self.assertEqual(len(completed.turns),2)
            events=[json.loads(s) for s in (rec.folder/'trajectory.jsonl').read_text().splitlines()]
            self.assertEqual(sum(e['event']=='dialogue_saved_action_recovered' for e in events),1)
