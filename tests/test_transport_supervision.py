import copy
import http.client
import json
import ssl
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

from turtle_loop.engine import Recorder,load_prompts,play
from turtle_loop.providers import Client,PreSendTLSFailure
from turtle_loop.dialogue import FreeDialoguePlayer,dialogue_settings,dialogue_system_prompt
from turtle_loop.transport_recovery import saved_transport_recovery,replay_records
from scripts.supervise_campaign import desktop_notification,notify,choose_recovery
from test_loop import PUZZLE,evaluated
from test_sessions import Response


@patch.dict('os.environ',{'DEEPSEEK_API_KEY':'fixture'})
class TransportSupervisionTests(unittest.TestCase):
    def config(self):
        return {'max_questions':4,'session_mode':'persistent',**{r:{'provider':'deepseek','model':r,'max_retries':0} for r in ('player','host','grader')}}

    def response(self,text,rid):
        return Response({'id':rid,'choices':[{'message':{'content':text},'finish_reason':'stop'}]})

    def marker(self,rec,result,config):
        calls=[json.loads(l) for l in (rec.folder/'api_calls.jsonl').read_text().splitlines()]
        proof=saved_transport_recovery(result,calls,rec.turns,config,rec.folder)
        self.assertIsNotNone(proof)
        (rec.folder/'transport_recovery.json').write_text(json.dumps(proof))
        return proof

    def test_solo_presend_failure_retries_exact_body_without_repeating_paid_questions(self):
        config=self.config();prompts=load_prompts();counts={'player':0,'host':0,'grader':0};seen=[]
        def api(req,**kw):
            body=json.loads(req.data);r=body['model'];counts[r]+=1;seen.append((r,body))
            if r=='player' and counts[r]==2:raise urllib.error.URLError(PreSendTLSFailure(ssl.SSLError('handshake failure')))
            return self.response(('QUESTION\nA question?' if counts[r]==1 else 'FINAL\nsubmitted explanation') if r=='player' else 'no' if r=='host' else evaluated(),f'{r}-{counts[r]}')
        with tempfile.TemporaryDirectory() as tmp,patch('urllib.request.OpenerDirector.open',side_effect=api):
            rec=Recorder(Path(tmp)/'run',PUZZLE,config,prompts,echo=False)
            clients=lambda record:{r:Client(config[r],r,record.audit) for r in counts}
            stopped=play(PUZZLE,config,rec,clients(rec),prompts)
            self.assertEqual(stopped['submissions'],1);self.assertEqual(stopped['status'],'error')
            for mutation in ('observed','changed_request','http402'):
                calls=copy.deepcopy(rec.calls)
                if mutation=='observed':calls[-1]['text']='Observed output'
                elif mutation=='changed_request':calls[-1]['request']['messages'][-1]['content']='{}'
                else:calls[-1].update(status='http_error',http_status=402)
                self.assertIsNone(saved_transport_recovery(stopped,calls,rec.turns,config,rec.folder),mutation)
            proof=self.marker(rec,stopped,config);self.assertFalse(proof['possible_duplicate_remote_charge'])
            restored=Recorder.restore(rec.folder,PUZZLE,config,prompts,echo=False)
            before=len(seen);result=play(PUZZLE,config,restored,clients(restored),prompts)
            self.assertTrue(result['success']);self.assertEqual(result['submissions'],2)
            self.assertEqual(counts['host'],1);self.assertEqual(seen[before][1],seen[before-1][1])
            self.assertFalse((rec.folder/'transport_recovery.json').exists())
            # Completed replays normalize only the failed chat attempt, not its audit.
            events=[json.loads(l) for l in (rec.folder/'trajectory.jsonl').read_text().splitlines()]
            normal=replay_records(restored.calls,events)
            self.assertEqual(len(normal),len(restored.calls)-1)
            corrupt=copy.deepcopy(restored.calls);corrupt[proof['calls_count']]['request']['temperature']=0.1
            with self.assertRaises(ValueError):replay_records(corrupt,events)

    def test_mas_pending_host_restores_both_agents_buffer_handoff_and_quota(self):
        config=self.config();prompts={**load_prompts(),'player':dialogue_system_prompt()}
        settings=dialogue_settings(type('Args',(),{})());partner={'provider':'deepseek','model':'partner','max_retries':0}
        seen=[];counts={r:0 for r in ('player','partner','host','grader')}
        def api(req,**kw):
            body=json.loads(req.data);r=body['model'];counts[r]+=1;seen.append((r,body))
            if r=='host' and counts[r]==2:raise KeyboardInterrupt()
            text=('QUESTION NEXT=B\nFirst question?' if counts[r]==1 else 'FINAL NEXT=B\nsubmitted explanation') if r=='player' else 'QUESTION NEXT=A\nSecond question?' if r=='partner' else 'no' if r=='host' else evaluated()
            return self.response(text,f'{r}-{counts[r]}')
        with tempfile.TemporaryDirectory() as tmp,patch('urllib.request.OpenerDirector.open',side_effect=api):
            rec=Recorder(Path(tmp)/'run',PUZZLE,config,prompts,echo=False)
            def clients(record):
                cs={r:Client(config[r],r,record.audit) for r in ('player','host','grader')}
                cs['player']=FreeDialoguePlayer(cs['player'],Client(partner,'partner',record.audit),record,settings)
                return cs
            stopped=play(PUZZLE,config,rec,clients(rec),prompts)
            self.assertEqual(stopped['submissions'],2);self.assertEqual(stopped['pending_feedback'],1)
            proof=self.marker(rec,stopped,config);self.assertEqual(proof['dialogue']['actor'],'B');self.assertTrue(proof['possible_duplicate_remote_charge'])
            shared=(rec.folder/'shared_dialogue.jsonl').read_text();rows=shared.splitlines();bad=json.loads(rows[-1]);bad['text']='Different question';rows[-1]=json.dumps(bad)
            (rec.folder/'shared_dialogue.jsonl').write_text('\n'.join(rows)+'\n')
            self.assertIsNone(saved_transport_recovery(stopped,rec.calls,rec.turns,config,rec.folder))
            (rec.folder/'shared_dialogue.jsonl').write_text(shared)
            restored=Recorder.restore(rec.folder,PUZZLE,config,prompts,echo=False);cs=clients(restored)
            self.assertEqual(cs['player'].speaker,'A');self.assertEqual(cs['player'].pending['actor'],'B')
            before=len(seen);result=play(PUZZLE,config,restored,cs,prompts)
            self.assertTrue(result['success']);self.assertEqual(result['submissions'],3)
            self.assertEqual(seen[before],seen[before-1]);self.assertEqual(counts['partner'],1)
            transcript=[json.loads(l) for l in (rec.folder/'shared_dialogue.jsonl').read_text().splitlines()]
            self.assertEqual([e['submission'] for e in transcript if e['speaker']=='Host'],[1,2,3])

    def test_notification_logs_result_without_shell_interpolation(self):
        with tempfile.TemporaryDirectory() as tmp,patch('scripts.supervise_campaign.subprocess.run') as run:
            run.return_value.returncode=0
            result=notify(Path(tmp),'test','A literal $(command) and "quotes"')
            self.assertTrue(result['delivery']['command_succeeded'])
            argv=run.call_args.args[0];self.assertEqual(argv[-1],'A literal $(command) and "quotes"')
            self.assertNotIn('shell',run.call_args.kwargs)
            self.assertEqual(json.loads((Path(tmp)/'alerts.jsonl').read_text())['kind'],'test')

    def test_unanswered_grader_read_failure_preserves_submission_and_replays_exactly(self):
        config=self.config();prompts=load_prompts();seen=[];counts={'player':0,'host':0,'grader':0}
        class BrokenRead(Response):
            def read(self):raise http.client.IncompleteRead(b'partial wire bytes')
        def api(req,**kw):
            body=json.loads(req.data);role=body['model'];counts[role]+=1;seen.append((role,body))
            if role=='grader' and counts[role]==2:return BrokenRead({})
            return self.response('FINAL\nsubmitted explanation' if role=='player' else
                                 evaluated((1,0)) if counts[role]==1 else evaluated(),f'{role}-{counts[role]}')
        with tempfile.TemporaryDirectory() as tmp,patch('urllib.request.OpenerDirector.open',side_effect=api):
            rec=Recorder(Path(tmp)/'game',PUZZLE,config,prompts,echo=False)
            clients=lambda record:{r:Client(config[r],r,record.audit) for r in counts}
            stopped=play(PUZZLE,config,rec,clients(rec),prompts)
            self.assertEqual(stopped['submissions'],2);self.assertEqual(stopped['status'],'error')
            for mutation in ('observed','http_error','changed_request'):
                raw=copy.deepcopy(rec.calls)
                if mutation=='observed':raw[-1]['text']='received grade'
                elif mutation=='http_error':raw[-1].update(status='http_error',http_status=402)
                else:raw[-1]['request']['messages'][-1]['content']='{}'
                self.assertIsNone(saved_transport_recovery(stopped,raw,rec.turns,config,rec.folder))
            proof=self.marker(rec,stopped,config);self.assertTrue(proof['possible_duplicate_remote_charge'])
            before=len(seen);restored=Recorder.restore(rec.folder,PUZZLE,config,prompts,echo=False)
            result=play(PUZZLE,config,restored,clients(restored),prompts)
            self.assertTrue(result['success']);self.assertEqual(result['submissions'],2)
            self.assertEqual(counts['player'],2);self.assertEqual(seen[before],seen[before-1])

    def test_actor_read_failure_never_resamples_action(self):
        config=self.config();prompts=load_prompts();counts={'player':0,'host':0,'grader':0}
        class BrokenRead(Response):
            def read(self):raise http.client.IncompleteRead(b'partial')
        def api(req,**kw):
            role=json.loads(req.data)['model'];counts[role]+=1
            if role=='player' and counts[role]==2:return BrokenRead({})
            return self.response('QUESTION\nOne question?' if role=='player' else 'no',f'{role}-{counts[role]}')
        with tempfile.TemporaryDirectory() as tmp,patch('urllib.request.OpenerDirector.open',side_effect=api):
            rec=Recorder(Path(tmp)/'game',PUZZLE,config,prompts,echo=False)
            stopped=play(PUZZLE,config,rec,{r:Client(config[r],r,rec.audit) for r in counts},prompts)
            self.assertIsNone(saved_transport_recovery(stopped,rec.calls,rec.turns,config,rec.folder))

    def test_host_read_recovery_limit_survives_restarts(self):
        config=self.config();prompts=load_prompts();counts={'player':0,'host':0,'grader':0}
        class BrokenRead(Response):
            def read(self):raise http.client.IncompleteRead(b'partial')
        def api(req,**kw):
            role=json.loads(req.data)['model'];counts[role]+=1
            if role=='host' and counts[role]>1:return BrokenRead({})
            return self.response('QUESTION\nOne question?' if role=='player' else 'no',f'{role}-{counts[role]}')
        with tempfile.TemporaryDirectory() as tmp,patch('urllib.request.OpenerDirector.open',side_effect=api):
            rec=Recorder(Path(tmp)/'game',PUZZLE,config,prompts,echo=False)
            clients=lambda record:{r:Client(config[r],r,record.audit) for r in counts}
            stopped=play(PUZZLE,config,rec,clients(rec),prompts)
            for _ in range(2):
                self.marker(rec,stopped,config)
                rec=Recorder.restore(rec.folder,PUZZLE,config,prompts,echo=False)
                stopped=play(PUZZLE,config,rec,clients(rec),prompts)
            self.assertEqual(counts,{'player':2,'host':4,'grader':0})
            self.assertIsNone(saved_transport_recovery(stopped,rec.calls,rec.turns,config,rec.folder))

class SupervisorLifecycleTests(unittest.TestCase):
    def run_supervisor(self,stop_code=0,unknown=False,same_checkpoint=False):
        from argparse import Namespace
        from scripts.supervise_campaign import supervise
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);root=Path(temp.name).resolve()
        source=root/'campaign';source.mkdir();out=root/'supervision'
        (source/'campaign.json').write_text(json.dumps({'planned_games':2,'jobs':[
            {'id':'cl','folder':'tasks/cl','planned_games':1},
            {'id':'mas','folder':'tasks/mas','planned_games':1}]}))
        (source/'status.json').write_text(json.dumps({'status':'stopped_on_error','active':{}}))
        class Proc:
            pid=1000001
            def poll(self):return stop_code
        def rows(path,slot):
            return [{'status':'completed' if stop_code==0 and out in path.parents else 'error'}]
        def choose(path):
            if unknown:raise ValueError('HTTP 402 requires user action')
            return '--recover-transport',{'game':'game','preserved_submissions':58,
                'calls_sha256':'same' if same_checkpoint else str(path)}
        def report(path,state):
            (path/'status.json').write_text(json.dumps(state))
        args=Namespace(campaign=str(source),out=str(out),interval=1,cooldown=0,max_recoveries=2,stall_seconds=60,notify='none')
        with patch('scripts.supervise_campaign.choose_recovery',side_effect=choose),\
             patch('scripts.supervise_campaign.job_rows',side_effect=rows),\
             patch('scripts.supervise_campaign.report',side_effect=report),\
             patch('scripts.supervise_campaign.subprocess.Popen',return_value=Proc()) as start,\
             patch('scripts.supervise_campaign.time.sleep'):
            code=supervise(args)
        return code,json.loads((out/'status.json').read_text()),start.call_count

    def test_each_independent_slot_completes_without_restarting_other_slot(self):
        code,state,starts=self.run_supervisor()
        self.assertEqual(code,0);self.assertEqual(starts,2);self.assertEqual(state['status'],'completed')

    def test_unknown_errors_notify_without_any_paid_restart(self):
        code,state,starts=self.run_supervisor(unknown=True)
        self.assertEqual(code,1);self.assertEqual(starts,0)
        self.assertTrue(all(j['status']=='requires_attention' for j in state['jobs'].values()))

    def test_recurring_failures_have_a_per_slot_retry_limit(self):
        code,state,starts=self.run_supervisor(stop_code=1)
        self.assertEqual(code,1);self.assertEqual(starts,4)
        self.assertTrue(all(len(j['attempts'])==2 for j in state['jobs'].values()))

    def test_identical_failed_checkpoint_is_not_repaired_repeatedly(self):
        code,state,starts=self.run_supervisor(stop_code=1,same_checkpoint=True)
        self.assertEqual(code,1);self.assertEqual(starts,2)

    def test_user_interrupt_is_not_automatically_overridden(self):
        code,state,starts=self.run_supervisor(stop_code=130)
        self.assertEqual(code,1);self.assertEqual(starts,2)
        self.assertTrue(all(len(j['attempts'])==1 for j in state['jobs'].values()))

class PrefixCheckpointTests(unittest.TestCase):
    def test_only_append_time_metadata_may_differ(self):
        from turtle_loop.experiments import same_player_prefix
        saved={'boundary':{'new_submission_budget':100},'calls':[{'role':'player','text':'QUESTION\nQ?',
            'request':{'messages':[{'role':'assistant','content':'previous'}]}}]}
        current=copy.deepcopy(saved);current['calls'][0]['timestamp']='added on disk'
        self.assertTrue(same_player_prefix(saved,current))
        current['calls'][0]['request']['messages'][0]['content']='changed answer'
        self.assertFalse(same_player_prefix(saved,current))
        current=copy.deepcopy(saved);current['boundary']['new_submission_budget']=99
        self.assertFalse(same_player_prefix(saved,current))

@patch.dict('os.environ',{'DEEPSEEK_API_KEY':'fixture'})
class ActorCorrectionRecoveryTests(unittest.TestCase):
    config=TransportSupervisionTests.config
    response=TransportSupervisionTests.response
    marker=TransportSupervisionTests.marker
    def test_mas_cancelled_format_correction_replays_the_same_request_and_retry_number(self):
        config=self.config();prompts={**load_prompts(),'player':dialogue_system_prompt()}
        settings=dialogue_settings(type('Args',(),{})());partner={'provider':'deepseek','model':'partner','max_retries':0}
        seen=[];counts={r:0 for r in ('player','partner','host','grader')}
        def api(req,**kw):
            body=json.loads(req.data);r=body['model'];counts[r]+=1;seen.append((r,body))
            if r=='player' and counts[r]==3:raise KeyboardInterrupt()
            if r=='player':text='QUESTION NEXT=B\nFirst question?' if counts[r]==1 else 'An untyped proposed explanation.' if counts[r]==2 else 'FINAL NEXT=B\nsubmitted explanation'
            else:text='QUESTION NEXT=A\nSecond question?' if r=='partner' else 'no' if r=='host' else evaluated()
            return self.response(text,f'{r}-{counts[r]}')
        with tempfile.TemporaryDirectory() as tmp,patch('urllib.request.OpenerDirector.open',side_effect=api):
            rec=Recorder(Path(tmp)/'run',PUZZLE,config,prompts,echo=False)
            def clients(record):
                cs={r:Client(config[r],r,record.audit) for r in ('player','host','grader')}
                cs['player']=FreeDialoguePlayer(cs['player'],Client(partner,'partner',record.audit),record,settings);return cs
            stopped=play(PUZZLE,config,rec,clients(rec),prompts)
            self.assertEqual(stopped['submissions'],2);self.assertEqual(stopped['pending_feedback'],0)
            proof=self.marker(rec,stopped,config)
            self.assertEqual(proof['dialogue']['format_attempt'],1)
            restored=Recorder.restore(rec.folder,PUZZLE,config,prompts,echo=False);before=len(seen)
            result=play(PUZZLE,config,restored,clients(restored),prompts)
            self.assertTrue(result['success']);self.assertEqual(result['submissions'],3)
            self.assertEqual(seen[before],seen[before-1]);self.assertEqual(counts['host'],2)
