import json
from pathlib import Path
import ssl
import tempfile
import unittest
import urllib.error
import shutil
import subprocess
import sys
from unittest.mock import patch

from scripts.matched_self_review import solo_base_prompts
from turtle_loop.budgeted_agents import SolverBudget,BudgetedAgent,phase_prompt
from turtle_loop.dialogue import FreeDialoguePlayer,dialogue_settings
from turtle_loop.engine import Recorder,load_prompts,play
from turtle_loop.providers import Client,PreSendTLSFailure
from turtle_loop.sessions import restore_context
from turtle_loop.transport_recovery import saved_transport_recovery
from test_loop import PUZZLE,evaluated
from test_sessions import Response


@patch.dict('os.environ',{'DEEPSEEK_API_KEY':'fixture'})
class BudgetedAgentsTests(unittest.TestCase):
    def test_frozen_worker_cold_start_needs_no_parent_supervisor_module(self):
        repo=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            shutil.copytree(repo/'turtle_loop',root/'turtle_loop',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
            (root/'scripts').mkdir()
            for name in ('compute_matched_agents.py','matched_self_review.py'):
                shutil.copy2(repo/'scripts'/name,root/'scripts'/name)
            result=subprocess.run([sys.executable,str(root/'scripts/compute_matched_agents.py'),'--help'],
                                  cwd=root,capture_output=True,text=True,timeout=15)
            self.assertEqual(result.returncode,0,result.stderr)

    def config(self):
        return {'max_questions':4,'session_mode':'persistent',**{r:{'provider':'deepseek','model':r,
                'max_output_tokens':8192,'max_retries':0,'extra_body':{'thinking':{'type':'disabled'}}}
                for r in ('player','host','grader')}}

    def clients(self,config,rec,budget,mas,review):
        ledger=SolverBudget(rec,budget,review)
        a=BudgetedAgent(config['player'],'player',ledger,'A')
        player=a
        if mas:
            b=BudgetedAgent({**config['player'],'model':'partner'},'partner',ledger,'B')
            player=FreeDialoguePlayer(a,b,rec,dialogue_settings(type('Args',(),{})()))
        return ledger,{'player':player,**{r:Client(config[r],r,rec.audit) for r in ('host','grader')}}

    def api(self,mas=False,discuss=False,reject=False,fail=False):
        self.previous={};self.seen=[];self.failed=False
        def request(req,**kw):
            body=json.loads(req.data);role=body['model']
            payload=restore_context(self.previous.get(role),body['messages'][-1]['content'])
            self.seen.append((role,body,payload))
            phase=payload.get('solver_phase',{})
            if fail and role==('partner' if mas else 'player') and phase.get('slot')==2 and phase.get('phase')=='action' and not self.failed:
                self.failed=True
                raise urllib.error.URLError(PreSendTLSFailure(ssl.SSLError('handshake failure')))
            self.previous[role]=payload
            if role=='host':text='no'
            elif role=='grader':text=evaluated((0,0) if reject else (1,1))
            elif phase['phase']!='action':text='PRIVATE_'+phase['actor']+'_NOTE. This is tentative, not Host evidence.'
            elif phase['force_final']:text='FINAL\nsubmitted explanation'
            elif discuss and not payload['shared_dialogue']:text='DISCUSS NEXT=B\nCheck the identity.'
            else:text=('QUESTION NEXT='+('B' if role=='player' else 'A') if mas else 'QUESTION')+'\nOne atomic question?'
            return Response({'id':f'{role}-{len(self.seen)}','choices':[{'message':{'content':text},'finish_reason':'stop'}],
                             'usage':{'prompt_tokens':50,'completion_tokens':10,'total_tokens':60}})
        return request

    def test_solo_prompt_uses_solo_base_without_positive_mas_role_instructions(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'team/TS038_r01_solo';path.mkdir(parents=True)
            (path/'prompts.json').write_text(json.dumps({'player':'You solve alone.','host':'H','grader':'G'}))
            clean=solo_base_prompts(tmp,{'player':'SHARED DIALOGUE PROTOCOL','host':'H','grader':'G'})
            self.assertEqual(clean['player'],'You solve alone.')
            self.assertEqual(clean['host'],'H')
            self.assertNotIn('other solver',phase_prompt(False))
            self.assertIn('only Player',phase_prompt(False))

    def test_four_conditions_keep_independent_lanes_and_one_combined_budget(self):
        config,prompts=self.config(),load_prompts()
        budget={'generation_cap':6,'output_token_cap':12000,'submission_cap':4}
        for mas in (False,True):
            for review in (False,True):
                with self.subTest(mas=mas,review=review),tempfile.TemporaryDirectory() as tmp,patch('urllib.request.OpenerDirector.open',side_effect=self.api(mas)):
                    rec=Recorder(Path(tmp)/'game',PUZZLE,config,prompts,echo=False)
                    ledger,clients=self.clients(config,rec,budget,mas,review)
                    result=play(PUZZLE,config,rec,clients,prompts)
                    self.assertTrue(result['success']);self.assertEqual(result['submissions'],4)
                    self.assertEqual(ledger.status()['generations'],6 if review else 4)
                    actor_calls=[c for c in rec.calls if c['role'] in ('player','partner')]
                    self.assertEqual(len({c['game_session_id'] for c in actor_calls}),2 if mas else 1)
                    for role in ('player','partner') if mas else ('player',):
                        own=[c for c in actor_calls if c['role']==role]
                        self.assertEqual(len({c['session_lane_id'] for c in own}),1)
                        for c in own:
                            self.assertNotIn('SECRET_',json.dumps(c['request']))
                            other='B' if role=='player' else 'A'
                            self.assertNotIn('PRIVATE_'+other+'_NOTE',json.dumps(c['request']))
                            self.assertLessEqual(c['request']['max_tokens'],2048)
                    if mas:
                        transcript=(rec.folder/'shared_dialogue.jsonl').read_text()
                        self.assertNotIn('PRIVATE_',transcript)

    def test_mas_discussion_and_reviews_cannot_escape_shared_generation_cap(self):
        config,prompts=self.config(),load_prompts()
        budget={'generation_cap':4,'output_token_cap':12000,'submission_cap':4}
        with tempfile.TemporaryDirectory() as tmp,patch('urllib.request.OpenerDirector.open',side_effect=self.api(True,True,True)):
            rec=Recorder(Path(tmp)/'game',PUZZLE,config,prompts,echo=False)
            ledger,clients=self.clients(config,rec,budget,True,True)
            result=play(PUZZLE,config,rec,clients,prompts)
            self.assertFalse(result['success']);self.assertEqual(result['submissions'],3)
            self.assertEqual(result['stop_reason'],'solver_budget_exhausted')
            self.assertEqual(ledger.status()['generations'],4)
            self.assertTrue(result['forced_final'])

    def test_solo_transport_resume_reuses_paid_review_and_exact_request(self):
        config,prompts=self.config(),load_prompts()
        budget={'generation_cap':6,'output_token_cap':12000,'submission_cap':4}
        with tempfile.TemporaryDirectory() as tmp,patch('urllib.request.OpenerDirector.open',side_effect=self.api(fail=True)):
            folder=Path(tmp)/'game';rec=Recorder(folder,PUZZLE,config,prompts,echo=False)
            ledger,clients=self.clients(config,rec,budget,False,True)
            result=play(PUZZLE,config,rec,clients,prompts)
            self.assertEqual(result['status'],'error')
            raw=[json.loads(s) for s in (folder/'api_calls.jsonl').read_text().splitlines()]
            proof=saved_transport_recovery(result,raw,rec.turns,config,folder)
            self.assertIsNotNone(proof)
            (folder/'transport_recovery.json').write_text(json.dumps(proof))
            before=len(self.seen);restored=Recorder.restore(folder,PUZZLE,config,prompts,echo=False)
            ledger,clients=self.clients(config,restored,budget,False,True)
            result=play(PUZZLE,config,restored,clients,prompts)
            self.assertTrue(result['success'])
            self.assertEqual(self.seen[before][1],self.seen[before-1][1])
            self.assertEqual(ledger.status()['generations'],6)

    def test_mas_transport_resume_keeps_private_review_and_shared_chat(self):
        config,prompts=self.config(),load_prompts()
        budget={'generation_cap':6,'output_token_cap':12000,'submission_cap':4}
        with tempfile.TemporaryDirectory() as tmp,patch('urllib.request.OpenerDirector.open',side_effect=self.api(mas=True,fail=True)):
            folder=Path(tmp)/'game';rec=Recorder(folder,PUZZLE,config,prompts,echo=False)
            ledger,clients=self.clients(config,rec,budget,True,True)
            result=play(PUZZLE,config,rec,clients,prompts)
            self.assertEqual(result['status'],'error')
            raw=[json.loads(s) for s in (folder/'api_calls.jsonl').read_text().splitlines()]
            proof=saved_transport_recovery(result,raw,rec.turns,config,folder)
            self.assertIsNotNone(proof)
            self.assertEqual(proof['dialogue']['actor'],'B')
            (folder/'transport_recovery.json').write_text(json.dumps(proof))
            before=len(self.seen);restored=Recorder.restore(folder,PUZZLE,config,prompts,echo=False)
            ledger,clients=self.clients(config,restored,budget,True,True)
            result=play(PUZZLE,config,restored,clients,prompts)
            self.assertTrue(result['success'])
            self.assertEqual(self.seen[before][1],self.seen[before-1][1])
            self.assertEqual(ledger.status()['generations'],6)
            self.assertEqual(sum(c.get('reflection_phase')=='review' and c.get('reflection_slot')==2
                                 for c in restored.calls),1)


if __name__=='__main__':unittest.main()
