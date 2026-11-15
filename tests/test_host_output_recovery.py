import copy
import http.client
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from turtle_loop.host import normalize_host_label
from turtle_loop.host_output_recovery import saved_host_output_recovery
from turtle_loop.engine import Recorder,load_prompts,play
from turtle_loop.providers import APIError,Client
from turtle_loop.sessions import GameSession,restore_context
from turtle_loop.transport_recovery import saved_transport_recovery
from test_loop import PUZZLE,evaluated
from test_sessions import Response
import test_budgeted_agents as budget_fixtures


@patch.dict('os.environ',{'DEEPSEEK_API_KEY':'fixture'})
class HostOutputRecoveryTests(unittest.TestCase):
    config=budget_fixtures.BudgetedAgentsTests.config

    def response(self,text,rid):
        return Response({'id':rid,'choices':[{'message':{'content':text},'finish_reason':'stop'}],
                         'usage':{'prompt_tokens':50,'completion_tokens':10,'total_tokens':60}})

    def marker(self,rec,result,config):
        calls=[json.loads(s) for s in (rec.folder/'api_calls.jsonl').read_text().splitlines()]
        proof=saved_host_output_recovery(result,calls,rec.turns,config,rec.folder)
        self.assertIsNotNone(proof)
        (rec.folder/'host_output_recovery.json').write_text(json.dumps(proof))
        return proof

    def test_label_envelopes_normalize_only_one_unambiguous_meaning(self):
        for raw,label in [(' exactly no.no','no'),('NO.','no'),('Answer: YES','yes'),
                          ('"irrelevant"','irrelevant'),('yes & no','yes and no'),
                          ('yes&no','yes and no'),('YES AND NO. yes and no','yes and no')]:
            self.assertEqual(normalize_host_label(raw),label,raw)
        for raw in ('','yes/no','no. yes','no, because it is dangerous','not no','probably yes','yes and no; no'):
            self.assertIsNone(normalize_host_label(raw),raw)

    def test_live_empty_host_retries_same_request_without_new_player_action(self):
        config=self.config();config['host']['max_retries']=2
        prompts=load_prompts();seen=[];counts={'player':0,'host':0,'grader':0}
        def api(req,**kw):
            body=json.loads(req.data);role=body['model'];counts[role]+=1;seen.append((role,body))
            text=('QUESTION\nOne question?' if counts[role]==1 else 'FINAL\nsubmitted explanation') if role=='player' else (
                '' if counts[role]==1 else 'exactly no.no') if role=='host' else evaluated()
            return self.response(text,f'{role}-{counts[role]}')
        with tempfile.TemporaryDirectory() as tmp,patch('urllib.request.OpenerDirector.open',side_effect=api):
            rec=Recorder(Path(tmp)/'game',PUZZLE,config,prompts,echo=False)
            result=play(PUZZLE,config,rec,{r:Client(config[r],r,rec.audit) for r in counts},prompts)
            self.assertTrue(result['success']);self.assertEqual(result['submissions'],2)
            self.assertEqual(counts['host'],2);self.assertEqual(counts['player'],2)
            host=[body for role,body in seen if role=='host'];self.assertEqual(host[0],host[1])
            self.assertEqual(rec.turns[0]['label'],'no')
            self.assertEqual(result['usage']['host']['provider_reported_usage']['completion_tokens'],20)
            session=GameSession('host',tmp,lambda *a,**kw:None)
            try:session.restore_chat(rec.calls);self.assertEqual(session.freeze_prefix()['turn'],1)
            finally:session.close()

    def test_three_empty_replies_exhaust_one_question_budget_and_do_not_loop(self):
        config=self.config();config['host']['max_retries']=2;prompts=load_prompts();n=[0]
        def api(req,**kw):
            role=json.loads(req.data)['model'];n[0]+=role=='host'
            return self.response('QUESTION\nOne question?' if role=='player' else '',str(n[0]))
        with tempfile.TemporaryDirectory() as tmp,patch('urllib.request.OpenerDirector.open',side_effect=api):
            rec=Recorder(Path(tmp)/'game',PUZZLE,config,prompts,echo=False)
            result=play(PUZZLE,config,rec,{r:Client(config[r],r,rec.audit) for r in ('player','host','grader')},prompts)
            self.assertEqual(result['status'],'error');self.assertEqual(result['submissions'],1);self.assertEqual(n[0],3)
            raw=[json.loads(s) for s in (rec.folder/'api_calls.jsonl').read_text().splitlines()]
            self.assertIsNone(saved_host_output_recovery(result,raw,rec.turns,config,rec.folder))

    def test_saved_repeated_label_is_recovered_without_reasking_host_or_player(self):
        config=self.config();prompts=load_prompts();counts={'player':0,'host':0,'grader':0}
        def api(req,**kw):
            role=json.loads(req.data)['model'];counts[role]+=1
            text=('QUESTION\nOne question?' if counts[role]==1 else 'FINAL\nsubmitted explanation') if role=='player' else ' exactly no.no' if role=='host' else evaluated()
            return self.response(text,f'{role}-{counts[role]}')
        def old_host(client,system,payload,*args,**kwargs):
            client.complete(system,json.dumps(payload,ensure_ascii=False))
            raise APIError('Host returned an invalid label; raw response remains in API audit')
        with tempfile.TemporaryDirectory() as tmp,patch('urllib.request.OpenerDirector.open',side_effect=api):
            folder=Path(tmp)/'game';rec=Recorder(folder,PUZZLE,config,prompts,echo=False)
            clients=lambda record:{r:Client(config[r],r,record.audit) for r in counts}
            with patch('turtle_loop.engine.answer_question',side_effect=old_host):
                stopped=play(PUZZLE,config,rec,clients(rec),prompts)
            proof=self.marker(rec,stopped,config);self.assertEqual(proof['mode'],'normalize')
            restored=Recorder.restore(folder,PUZZLE,config,prompts,echo=False)
            result=play(PUZZLE,config,restored,clients(restored),prompts)
            self.assertTrue(result['success']);self.assertEqual(counts,{'player':2,'host':1,'grader':1})
            self.assertEqual(restored.turns[0]['label'],'no')
            self.assertEqual(next(c for c in restored.calls if c['role']=='host')['text'],' exactly no.no')

    def test_saved_empty_mas_host_replays_only_host_and_keeps_private_reviews(self):
        helper=budget_fixtures.BudgetedAgentsTests();config=self.config();prompts=load_prompts()
        budget={'generation_cap':6,'output_token_cap':12000,'submission_cap':4}
        base=helper.api(mas=True);host_count=[0]
        def api(req,**kw):
            response=base(req,**kw)
            if json.loads(req.data)['model']=='host':
                host_count[0]+=1
                if host_count[0]==2:response.data['choices'][0]['message']['content']=''
            return response
        with tempfile.TemporaryDirectory() as tmp,patch('urllib.request.OpenerDirector.open',side_effect=api):
            folder=Path(tmp)/'game';rec=Recorder(folder,PUZZLE,config,prompts,echo=False)
            ledger,clients=helper.clients(config,rec,budget,True,True)
            stopped=play(PUZZLE,config,rec,clients,prompts)
            self.assertEqual(stopped['status'],'error');self.assertEqual(stopped['submissions'],2)
            proof=self.marker(rec,stopped,config);self.assertEqual(proof['mode'],'retry_empty')
            before=len(helper.seen);restored=Recorder.restore(folder,PUZZLE,config,prompts,echo=False)
            ledger,clients=helper.clients(config,restored,budget,True,True)
            result=play(PUZZLE,config,restored,clients,prompts)
            self.assertTrue(result['success']);self.assertEqual(result['submissions'],4)
            self.assertEqual(helper.seen[before][0],'host')
            self.assertEqual(helper.seen[before][1],helper.seen[before-1][1])
            self.assertEqual(ledger.status()['generations'],6)
            self.assertEqual(host_count[0],4)
            self.assertEqual(sum(c.get('reflection_phase')=='review' and c.get('reflection_slot')==2 for c in restored.calls),1)
            for role in ('player','partner','host','grader'):
                session=GameSession(role,tmp,lambda *a,**kw:None)
                try:session.restore_chat(restored.calls)
                finally:session.close()

    def test_conflicting_visible_labels_are_not_retried_or_guessed(self):
        config=self.config();config['host']['max_retries']=2;prompts=load_prompts();n=[0]
        def api(req,**kw):
            role=json.loads(req.data)['model'];n[0]+=role=='host'
            return self.response('QUESTION\nOne question?' if role=='player' else 'yes/no',str(n[0]))
        with tempfile.TemporaryDirectory() as tmp,patch('urllib.request.OpenerDirector.open',side_effect=api):
            rec=Recorder(Path(tmp)/'game',PUZZLE,config,prompts,echo=False)
            result=play(PUZZLE,config,rec,{r:Client(config[r],r,rec.audit) for r in ('player','host','grader')},prompts)
            self.assertEqual(result['status'],'error');self.assertEqual(n[0],1)
            raw=[json.loads(s) for s in (rec.folder/'api_calls.jsonl').read_text().splitlines()]
            self.assertIsNone(saved_host_output_recovery(result,raw,rec.turns,config,rec.folder))

    def test_mas_read_recovery_after_empty_recovery_keeps_review_ledger(self):
        helper=budget_fixtures.BudgetedAgentsTests();config=self.config();prompts=load_prompts()
        budget={'generation_cap':6,'output_token_cap':12000,'submission_cap':4}
        base=helper.api(mas=True);n=[0]
        class BrokenRead(Response):
            def read(self):raise http.client.IncompleteRead(b'partial')
        def api(req,**kw):
            response=base(req,**kw)
            if json.loads(req.data)['model']=='host':
                n[0]+=1
                if n[0]==2:response.data['choices'][0]['message']['content']=''
                if n[0]==4:return BrokenRead({})
            return response
        with tempfile.TemporaryDirectory() as tmp,patch('urllib.request.OpenerDirector.open',side_effect=api):
            rec=Recorder(Path(tmp)/'game',PUZZLE,config,prompts,echo=False)
            ledger,clients=helper.clients(config,rec,budget,True,True)
            stopped=play(PUZZLE,config,rec,clients,prompts);self.marker(rec,stopped,config)
            rec=Recorder.restore(rec.folder,PUZZLE,config,prompts,echo=False)
            ledger,clients=helper.clients(config,rec,budget,True,True)
            stopped=play(PUZZLE,config,rec,clients,prompts)
            self.assertEqual(stopped['submissions'],3);self.assertEqual(stopped['status'],'error')
            raw=[json.loads(s) for s in (rec.folder/'api_calls.jsonl').read_text().splitlines()]
            proof=saved_transport_recovery(stopped,raw,rec.turns,config,rec.folder)
            self.assertIsNotNone(proof);self.assertTrue(proof['possible_duplicate_remote_charge'])
            (rec.folder/'transport_recovery.json').write_text(json.dumps(proof))
            before=len(helper.seen);rec=Recorder.restore(rec.folder,PUZZLE,config,prompts,echo=False)
            ledger,clients=helper.clients(config,rec,budget,True,True)
            result=play(PUZZLE,config,rec,clients,prompts)
            self.assertTrue(result['success']);self.assertEqual(result['submissions'],4)
            self.assertEqual(helper.seen[before][:2],helper.seen[before-1][:2])
            self.assertEqual(ledger.status()['generations'],6)
            self.assertEqual(sum(c.get('reflection_phase')=='review' and c.get('reflection_slot')==2 for c in rec.calls),1)

    def test_empty_refusal_or_truncation_is_not_treated_as_retryable_blank(self):
        for kind in ('refusal','length'):
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as tmp:
                config=self.config();config['host']['max_retries']=2;prompts=load_prompts();n=[0]
                def api(req,**kw):
                    role=json.loads(req.data)['model']
                    if role=='player':return self.response('QUESTION\nOne question?','p1')
                    n[0]+=1;response=self.response('','h1')
                    if kind=='refusal':response.data['choices'][0]['message']['refusal']='Provider refused'
                    else:response.data['choices'][0]['finish_reason']='length'
                    return response
                with patch('urllib.request.OpenerDirector.open',side_effect=api):
                    rec=Recorder(Path(tmp)/'game',PUZZLE,config,prompts,echo=False)
                    result=play(PUZZLE,config,rec,{r:Client(config[r],r,rec.audit) for r in ('player','host','grader')},prompts)
                self.assertEqual(result['status'],'error');self.assertEqual(n[0],1)
                raw=[json.loads(s) for s in (rec.folder/'api_calls.jsonl').read_text().splitlines()]
                self.assertIsNone(saved_host_output_recovery(result,raw,rec.turns,config,rec.folder))

    def test_saved_empty_retry_budget_does_not_reset_across_restart(self):
        helper=budget_fixtures.BudgetedAgentsTests();config=self.config();config['host']['max_retries']=2
        prompts=load_prompts();budget={'generation_cap':6,'output_token_cap':12000,'submission_cap':4}
        base=helper.api(mas=True);n=[0]
        def api(req,**kw):
            response=base(req,**kw)
            if json.loads(req.data)['model']=='host':
                n[0]+=1
                if n[0]>=2:response.data['choices'][0]['message']['content']=''
            return response
        with tempfile.TemporaryDirectory() as tmp,patch('urllib.request.OpenerDirector.open',side_effect=api):
            folder=Path(tmp)/'game';rec=Recorder(folder,PUZZLE,config,prompts,echo=False)
            ledger,clients=helper.clients(config,rec,budget,True,True)
            # Simulate the archived version which did not retry empty replies.
            clients['host'].profile={**config['host'],'max_retries':0}
            stopped=play(PUZZLE,config,rec,clients,prompts)
            self.marker(rec,stopped,config)
            restored=Recorder.restore(folder,PUZZLE,config,prompts,echo=False)
            ledger,clients=helper.clients(config,restored,budget,True,True)
            result=play(PUZZLE,config,restored,clients,prompts)
            self.assertEqual(result['status'],'error')
            self.assertEqual(n[0],4)  # One earlier valid Host + three blank attempts.
            self.assertEqual(result['submissions'],2)
            raw=[json.loads(s) for s in (folder/'api_calls.jsonl').read_text().splitlines()]
            self.assertIsNone(saved_host_output_recovery(result,raw,restored.turns,config,folder))


if __name__=='__main__':unittest.main()
