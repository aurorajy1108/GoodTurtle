"""Isolation, budget, ordering and failure behaviour of v7 experiment controls."""
import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from turtle_loop.experiments import main, make_plan
from turtle_loop.providers import Client, APIError
from test_loop import PUZZLE, FakeClient, evaluated


class ControlDesignTests(unittest.TestCase):
    def run_controls(self, root, fail_direct=False, budget=100):
        puzzles=[]
        for pid in ('A','B','C'):
            puzzle=copy.deepcopy(PUZZLE)
            puzzle.update(id='V7_'+pid,opening='OPEN_'+pid,answer='PRIVATE_'+pid)
            puzzles.append(puzzle)
        data=root/'data.json';data.write_text(json.dumps({'schema_version':1,'puzzles':puzzles}))
        config=root/'config.json';config.write_text(json.dumps({'max_questions':budget,
            'host':{'provider':'openai','model':'fixture'},'player':{'provider':'openai','model':'fixture'}}))
        groups=root/'groups.json';groups.write_text(json.dumps({'groups':[{'id':'G','puzzles':['V7_A','V7_B'],'relation':'negative'}]}))
        sessions=[];private_payloads=[]
        def factory(profile,role,audit):
            session=[]
            if role=='player':sessions.append(session)
            def reply(i,payload):
                if role=='player':
                    session.append(payload)
                    if fail_direct and payload['opening']=='OPEN_B' and 'prior_experience' not in payload:
                        raise APIError('synthetic transport failure')
                    return json.dumps({'type':'final' if i in (1,budget) else 'question','text':f'{payload["opening"]} action {i}'})
                private_payloads.append((role,payload))
                return 'no' if role=='host' else evaluated((0,0))
            return FakeClient(reply)
        out=root/'out'
        with patch('turtle_loop.cli.validate_profile'),patch('turtle_loop.experiments.Client',side_effect=factory):
            code=main(['continual','--dataset',str(data),'--config',str(config),'--groups',str(groups),
                '--group','G','--pair','V7_A:V7_B','--repeat','1','--controls','answer_only,unrelated',
                '--control-source','V7_C','--quiet','--out',str(out)])
        return code,out,sessions,private_payloads

    def test_all_controls_fresh_100_budget_and_no_target_or_grade_leak(self):
        with tempfile.TemporaryDirectory() as tmp:
            code,out,sessions,private_payloads=self.run_controls(Path(tmp))
            self.assertEqual(code,0)
            self.assertEqual(len(sessions),6)  # two sources and four B conditions
            for session in sessions:
                self.assertEqual(len(session),100)
                self.assertIn('Used question-equivalents: 0.',session[0]['turn_control'])
                self.assertEqual(session[0]['visible_history'],[])
                self.assertIn('mandatory last turn',session[-1]['turn_control'])
                self.assertNotIn('PRIVATE_B',json.dumps(session))
                self.assertNotIn('SECRET_RUBRIC',json.dumps(session))
            targets=[s for s in sessions if s[0]['opening']=='OPEN_B']
            self.assertEqual(len(targets),4)
            related=[s for s in targets if s[0].get('prior_experience',{}).get('revealed_source_answer')=='PRIVATE_A']
            self.assertEqual(sorted(len(s[0]['prior_experience'].get('history',[])) for s in related),[0,100])
            unrelated=[s for s in targets if s[0].get('prior_experience',{}).get('revealed_source_answer')=='PRIVATE_C']
            self.assertEqual(len(unrelated),1)
            self.assertNotIn('PRIVATE_A',json.dumps(unrelated))
            direct=[s for s in targets if 'prior_experience' not in s[0]]
            self.assertEqual(len(direct),1)
            self.assertNotIn('PRIVATE_A',json.dumps(direct));self.assertNotIn('PRIVATE_C',json.dumps(direct))
            for role,payload in private_payloads:
                if (payload.get('active_puzzle',{}).get('opening') or payload.get('opening'))=='OPEN_B':
                    self.assertNotIn('PRIVATE_A',json.dumps(payload));self.assertNotIn('PRIVATE_C',json.dumps(payload))
            target_prompts=[json.loads(f.read_text())['player'] for f in out.glob('*/prompts.json')
                            if not f.parent.name.endswith('_source')]
            self.assertEqual(len(set(target_prompts)),1)
            summary=json.loads((out/'condition_summary.json').read_text())
            self.assertEqual(len(summary),4);self.assertNotIn('G/control_source',summary)
            for f in out.glob('*/result.json'):
                result=json.loads(f.read_text())
                self.assertEqual((result['counted_questions'],result['submissions'],result['rejected_finals']),(100,100,2))
            self.assertTrue(all(x['valid_pair'] for x in json.loads((out/'control_contrasts.json').read_text())))

    def test_failed_baseline_does_not_stop_other_conditions_or_become_zero_score(self):
        with tempfile.TemporaryDirectory() as tmp:
            code,out,sessions,_=self.run_controls(Path(tmp),fail_direct=True,budget=2)
            self.assertEqual(code,1)  # failure stays visible even though scheduling continues
            rows=json.loads((out/'experiment_runs.json').read_text())
            self.assertEqual(sum(r['status']=='completed' for r in rows),5)
            self.assertEqual(sum(r['status']=='error' for r in rows),1)
            self.assertTrue(all(not x['valid_pair'] and x['score_gain'] is None
                for x in json.loads((out/'contrasts.json').read_text())))

    def test_balanced_controls_and_invalid_source_rejected(self):
        from argparse import Namespace
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'groups.json';path.write_text(json.dumps({'groups':[{'id':'G','puzzles':['A','B'],'relation':'negative'}]}))
            args=Namespace(command='continual',groups=str(path),group='G',pair='A:B',repeat=4,
                memory='transcript',seed=4,controls='answer_only,unrelated',control_source='C',source_feedback='answer')
            plan=sorted(make_plan(args,{'A':{},'B':{},'C':{}}),key=lambda x:x['repeat'])
            for position in range(4):self.assertEqual(len({b['conditions'][position] for b in plan}),4)
            args.control_source='B'
            with self.assertRaises(ValueError):make_plan(args,{'A':{},'B':{},'C':{}})


class CapacityRetryTests(unittest.TestCase):
    @patch('turtle_loop.codex_client.shutil.which',return_value='/bin/codex')
    @patch('turtle_loop.providers.time.sleep')
    def test_capacity_retries_identical_request_without_model_fallback(self, sleep, _):
        profile={'provider':'codex_cli','model':'gpt-6.1-sol','max_retries':2}
        failure=subprocess.CompletedProcess([],1,json.dumps({'type':'error','message':'Selected model is at capacity.'}),'')
        success=subprocess.CompletedProcess([],0,'\n'.join([json.dumps({'type':'item.completed','item':{'type':'agent_message','text':'{"text":"yes"}'}}),json.dumps({'type':'turn.completed','usage':{}})]),'')
        records=[]
        with patch('turtle_loop.codex_client.subprocess.run',side_effect=[failure,failure,success]) as run:
            reply=Client(profile,'host',records.append).complete('SYSTEM','INPUT')
        self.assertEqual(reply.text,'yes');self.assertEqual(run.call_count,3)
        self.assertEqual([r['attempt'] for r in records],[1,2,3])
        self.assertTrue(all(r['model_requested']=='gpt-6.1-sol' and r['request']['user']=='INPUT' for r in records))

    @patch('turtle_loop.codex_client.shutil.which',return_value='/bin/codex')
    @patch('turtle_loop.providers.time.sleep')
    def test_capacity_retry_exhaustion_is_bounded(self, sleep, _):
        failure=subprocess.CompletedProcess([],1,json.dumps({'type':'error','message':'Selected model is at capacity.'}),'')
        with patch('turtle_loop.codex_client.subprocess.run',return_value=failure) as run:
            with self.assertRaises(APIError):Client({'provider':'codex_cli','model':'gpt-6.1-sol','max_retries':1},'host',lambda x:None).complete('S','U')
        self.assertEqual(run.call_count,2)

    @patch('turtle_loop.codex_client.shutil.which',return_value='/bin/codex')
    def test_partial_or_invalid_generation_never_resampled(self, _):
        output='\n'.join([json.dumps({'type':'item.completed','item':{'type':'agent_message','text':'not json'}}),json.dumps({'type':'error','message':'at capacity'})])
        with patch('turtle_loop.codex_client.subprocess.run',return_value=subprocess.CompletedProcess([],1,output,'')) as run:
            with self.assertRaises(APIError):Client({'provider':'codex_cli','model':'gpt-6.1-sol'},'host',lambda x:None).complete('S','U')
        self.assertEqual(run.call_count,1)

    @patch('turtle_loop.codex_client.shutil.which',return_value='/bin/codex')
    def test_reasoning_started_before_capacity_failure_is_not_retried(self, _):
        output='\n'.join([json.dumps({'type':'item.started','item':{'type':'reasoning'}}),
                          json.dumps({'type':'error','message':'at capacity'})])
        with patch('turtle_loop.codex_client.subprocess.run',return_value=subprocess.CompletedProcess([],1,output,'')) as run:
            with self.assertRaises(APIError):Client({'provider':'codex_cli','model':'gpt-6.1-sol'},'host',lambda x:None).complete('S','U')
        self.assertEqual(run.call_count,1)
