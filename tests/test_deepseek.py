"""Exercise every role through the HTTP adapter without using a paid API."""
import copy
import io
import http.client
import json
import os
import tempfile
import unittest
from argparse import Namespace
from contextlib import ExitStack, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from scripts.study_20261102 import main as study_main
from scripts.smoke_sessions import main as smoke_main
from turtle_loop.cli import configuration
from turtle_loop.dialogue import FreeDialoguePlayer, dialogue_settings
from turtle_loop.engine import Recorder, load_prompts, play
from turtle_loop.providers import Client
from turtle_loop.providers import APIError
from test_loop import PUZZLE, evaluated

ROOT = Path(__file__).resolve().parents[1]


class Response:
    def __init__(self, data): self.data = data
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self): return json.dumps(self.data).encode()


class DeepSeekTests(unittest.TestCase):
    @patch.dict(os.environ, {'DEEPSEEK_API_KEY':'fixture'})
    def test_json_action_mode_preserves_plain_text_review_and_summary_calls(self):
        requests=[]
        def respond(req,**kwargs):
            body=json.loads(req.data);requests.append(body)
            return Response({'id':str(len(requests)),'model':body['model'],
                'choices':[{'message':{'content':'{}'},'finish_reason':'stop'}]})
        profile={'provider':'deepseek','model':'deepseek-flash'}
        with patch('urllib.request.OpenerDirector.open',side_effect=respond):
            player=Client(profile,'player',lambda *a:None)
            player.complete('Return JSON action.',json.dumps({'opening':'story','turn_control':'normal'}))
            player.complete('Review in plain text.',json.dumps({'public_context':{'opening':'story','turn_control':'normal'},'proposed_action':{'type':'question','text':'Q?'}}))
            Client(profile,'memory',lambda *a:None).complete('Summarize.',json.dumps({'opening':'story','history':[]}))
        self.assertEqual(requests[0]['response_format'],{'type':'json_object'})
        self.assertNotIn('response_format',requests[1])
        self.assertNotIn('response_format',requests[2])

    @patch.dict(os.environ, {'DEEPSEEK_API_KEY':'fixture-secret-key'})
    def test_incomplete_http_read_is_logged_and_stops_persistent_game(self):
        config=configuration(Namespace(config=str(ROOT/'configs/loop.deepseek.json'),dry_run=False))
        records=[]
        client=Client(config['player'],'player',records.append)
        with tempfile.TemporaryDirectory() as folder:
            client.begin_game(folder,lambda *a,**k:None)
            response=Response({})
            with patch.object(client.opener,'open',return_value=response) as opened, \
                 patch.object(response,'read',side_effect=http.client.IncompleteRead(b'partial-sensitive-body')):
                with self.assertRaises(APIError):
                    client.complete('system',json.dumps({'opening':'story','turn_control':'normal'}))
                self.assertEqual(opened.call_count,1)
            self.assertTrue(client.session.failed)
            self.assertEqual(records[-1]['status'],'transport_error')
            self.assertEqual(records[-1]['error_type'],'IncompleteRead')
            self.assertNotIn('partial-sensitive-body',str(records))
            client.close_game()

    @patch.dict(os.environ, {'DEEPSEEK_MODEL':'deepseek-flash', 'DEEPSEEK_API_KEY':'fixture-secret-key'})
    def test_all_role_http_calls_persistent_sessions_and_shared_dialogue(self):
        for team in (False, True):
            with self.subTest(team=team), tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
                config=configuration(Namespace(config=str(ROOT/'configs/loop.deepseek.json'), dry_run=False))
                config['max_questions']=4
                prompts=load_prompts()
                rec=Recorder(Path(folder)/'game', copy.deepcopy(PUZZLE), config, prompts, echo=False)
                clients={role:Client(config[role],role,rec.audit) for role in ('host','player','grader')}
                if team:
                    partner=Client(copy.deepcopy(config['player']),'partner',rec.audit)
                    clients['partner_fixture']=partner
                requests={role:[] for role in ('host','player','grader','partner')}

                def callback(role):
                    def respond(req, **kwargs):
                        body=json.loads(req.data)
                        requests[role].append(body)
                        i=len(requests[role])
                        self.assertEqual(req.full_url,'https://api.deepseek.com/chat/completions')
                        self.assertEqual(req.get_header('Authorization'),'Bearer fixture-secret-key')
                        self.assertEqual(body['model'], 'deepseek-v4-pro' if role in ('host','grader') else 'deepseek-flash')
                        self.assertEqual(body['thinking'],{'type':'enabled' if role in ('host','grader') else 'disabled'})
                        self.assertNotIn('tools',body)
                        self.assertNotIn('previous_response_id',body)
                        if role=='host':
                            text='no'
                            self.assertEqual(body['reasoning_effort'],'high')
                            self.assertNotIn('response_format',body)
                        elif role=='grader':
                            self.assertEqual(body['response_format'],{'type':'json_object'})
                            text=evaluated((.5,0)) if i==1 else evaluated()
                        else:
                            self.assertNotIn('reasoning_effort',body)
                            # Neither earlier private scores nor story facts enter either solver session.
                            self.assertNotIn('SECRET_',json.dumps(body))
                            self.assertNotIn('completion_note',json.dumps(body))
                            self.assertEqual(body['response_format'],{'type':'json_object'})
                            if team:
                                if role=='player':
                                    kind,text,next_actor=('discuss','Check the identity','B') if i==1 else ('final','Explanation','B')
                                else:
                                    kind,text,next_actor='question','Is identity relevant?','A'
                                text=json.dumps(dict(type=kind,text=text,next_speaker=next_actor))
                            else:
                                text=json.dumps(dict(type='question' if i%2 else 'final',text='Attempt'))
                        return Response(dict(id=f'{role}-{i}',model=body['model'],
                            choices=[dict(message={'content':text,'reasoning_content':'PRIVATE_REASONING_SENTINEL'},finish_reason='stop')],
                            usage=dict(prompt_tokens=100,completion_tokens=25,prompt_cache_hit_tokens=20,
                                       prompt_cache_miss_tokens=80,completion_tokens_details={'reasoning_tokens':10})))
                    return respond

                for role, client in clients.items():
                    stack.enter_context(patch.object(client.opener,'open',side_effect=callback('partner' if role=='partner_fixture' else role)))
                if team:
                    partner=clients.pop('partner_fixture')
                    clients['player']=FreeDialoguePlayer(clients['player'],partner,rec,dialogue_settings(Namespace()))
                result=play(copy.deepcopy(PUZZLE),config,rec,clients,prompts)
                self.assertTrue(result['success'])
                self.assertEqual((result['submissions'],result['counted_questions'],result['rejected_finals']),(4,3,1))
                self.assertEqual(len(requests['host']),2)
                self.assertEqual(len(requests['grader']),2)
                self.assertEqual([m['role'] for m in requests['host'][1]['messages']],['system','user','assistant','user'])
                host_update=json.loads(requests['host'][1]['messages'][-1]['content'])['context_update']
                self.assertIn('append_visible_history',host_update)
                self.assertTrue(all((getattr(c,'leader',c)).session.closed for c in clients.values()))
                logs=(rec.folder/'api_calls.jsonl').read_text()
                self.assertNotIn('fixture-secret-key',logs)
                self.assertNotIn('PRIVATE_REASONING_SENTINEL',logs)
                calls=[json.loads(x) for x in logs.splitlines()]
                self.assertEqual({x['provider'] for x in calls},{'deepseek'})
                first={x['role']:x['game_session_id'] for x in calls}
                self.assertEqual(len(set(first.values())),4 if team else 3)
                if team:
                    self.assertEqual(result['dialogue_metrics']['internal_messages'],1)
                    update=json.loads(requests['player'][1]['messages'][-1]['content'])['context_update']
                    self.assertEqual(update['append_shared_dialogue'][-1]['speaker'],'Host')
                costs=json.loads((rec.folder/'cost_summary.json').read_text())
                self.assertIn('total',costs)

    @patch.dict(os.environ, {'DEEPSEEK_MODEL':'deepseek-flash'})
    def test_study_set1_and_team_dry_run_use_deepseek_for_every_role(self):
        with tempfile.TemporaryDirectory() as folder, redirect_stdout(io.StringIO()):
            out=Path(folder)/'study'
            code=study_main(['--config',str(ROOT/'configs/loop.deepseek.json'),
                '--dataset',str(ROOT/'data/annotations/turtle50_v4/private.json'),
                '--suite','all','--sets','1','--team-puzzles','TS038',
                '--source-puzzles','TS015,TS014,TS028',
                '--strategies','solo,free_dialogue','--repeat','1','--mode','dry-run','--out',str(out)])
            self.assertEqual(code,0)
            plan=json.loads((out/'study_plan.json').read_text())
            self.assertEqual(plan['planned_games'],{'continual':12,'team':2})
            self.assertEqual({b['source'] for b in plan['blocks']['continual']},{'TS015','TS014','TS028'})
            self.assertTrue(all(b['target']=='TS013' for b in plan['blocks']['continual']))
            for role in ('host','player','grader'):
                self.assertEqual(plan['config'][role]['provider'],'deepseek')
                self.assertEqual(plan['config'][role]['model'], 'deepseek-v4-pro' if role in ('host','grader') else 'deepseek-flash')
                self.assertEqual(plan['config'][role]['api_key_env'],'DEEPSEEK_API_KEY')
            partner=json.loads((out/'team/TS038_r01_free_dialogue/partner_config.json').read_text())
            self.assertEqual(partner['provider'],'deepseek')
            self.assertEqual(partner['model'],'deepseek-flash')
            self.assertFalse(list(out.rglob('api_calls.jsonl')))

    @patch.dict(os.environ, {'DEEPSEEK_MODEL':'deepseek-flash', 'DEEPSEEK_API_KEY':'fixture-secret-key'})
    def test_smoke_resolves_model_and_supports_json_grader_profile(self):
        bodies=[]
        def respond(req, **kwargs):
            body=json.loads(req.data); bodies.append(body)
            self.assertEqual(body['model'], 'deepseek-flash' if len(bodies) in (3,4) else 'deepseek-v4-pro')
            code=json.loads(body['messages'][1]['content'])['code']
            return Response(dict(id=f'smoke-{len(bodies)}',model=body['model'],
                choices=[dict(message={'content':json.dumps({'code':code})},finish_reason='stop')],
                usage=dict(prompt_tokens=20,completion_tokens=5,prompt_cache_hit_tokens=0)))
        with tempfile.TemporaryDirectory() as folder, redirect_stdout(io.StringIO()), \
                patch('urllib.request.OpenerDirector.open',side_effect=respond):
            out=Path(folder)/'smoke'
            self.assertEqual(smoke_main(['--config',str(ROOT/'configs/loop.deepseek.json'), '--run','--out',str(out)]),0)
            self.assertEqual(len(bodies),6)
            self.assertTrue(json.loads((out/'result.json').read_text())['passed'])
            self.assertEqual(bodies[-1]['response_format'],{'type':'json_object'})


if __name__ == '__main__':
    unittest.main()
