import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from turtle_loop.player_format import load_policy, local_repair, repair, verbatim_proof
from turtle_loop.engine import ProtocolError, Recorder, play, load_prompts
from turtle_loop.providers import Reply
from test_loop import PUZZLE, FakeClient, evaluated


class PlayerFormatTests(unittest.TestCase):
    def setUp(self):self.policy=load_policy()

    def test_terminal_marker_and_fixed_last_candidate_do_not_use_quality(self):
        first=json.dumps({'type':'question','text':'A plausible question?'})
        last=json.dumps({'type':'question','text':'An unhelpful question?'})
        raw=first+'\n<解答过程>draft thoughts<｜end▁of▁thinking｜>'+last
        action,meta=local_repair(raw,False,self.policy)
        self.assertEqual(action['text'],'An unhelpful question?')
        self.assertEqual(meta['method'],'terminal_action_envelope')
        action,meta=local_repair(first+'\n'+last,False,self.policy)
        self.assertEqual(action['text'],'An unhelpful question?')
        self.assertEqual((meta['candidate_count'],meta['selected_index']),(2,1))
        self.assertIsNone(local_repair(first+'\n'+last,False,{**self.policy,'multiple_actions':'reject'}))
        self.assertIsNone(local_repair('</think>'+last+'{"type":',False,self.policy))
        body='Did he say "course"?\nWas it C:\\notes?'
        framed='```text\r\nQUESTION\r\n'+body+'\r\n```'
        recovered,meta=local_repair(framed,False,self.policy)
        self.assertEqual(recovered,{'type':'question','text':body})
        self.assertEqual(meta['method'],'terminal_action_envelope')

    def test_identical_duplicate_fields_preserve_final_and_conflicts_are_rejected(self):
        raw='{"type":"final","text":"The full explanation.","type":"final"}'
        action,meta=local_repair(raw,False,self.policy)
        self.assertEqual(action,{'type':'final','text':'The full explanation.'})
        self.assertEqual(meta['removed_duplicate_keys'],['type'])
        self.assertIsNone(local_repair(raw.replace('"type":"final"}', '"type":"question"}'),False,self.policy))
        self.assertIsNone(local_repair('{"type":"final","text":"First explanation.","text":"Different explanation."}',False,self.policy))
        self.assertIsNone(local_repair('{"type":"final","text":"Same.","text":"Same.","extra":"guess"}',False,self.policy))

    def test_codex_verbatim_guard_rejects_rewriting_qualifiers_and_extra_keys(self):
        raw="{'type':'question','text':'Did all the members contribute?'}"
        self.assertTrue(verbatim_proof(raw,{'type':'question','text':'Did all the members contribute?'}))
        for bad in ['Did the members contribute?','members contribute?','A different question?']:
            self.assertFalse(verbatim_proof(raw,{'type':'question','text':bad}))
        self.assertFalse(verbatim_proof(raw,{'type':'final','text':'Did all the members contribute?'}))
        self.assertFalse(verbatim_proof(raw[:-1]+",'other_question':'Q2?'}",{'type':'question','text':'Did all the members contribute?'}))
        self.assertTrue(verbatim_proof("{'type':'question','text':'Was the classmate\\'s work missing?'}",
                                      {'type':'question','text':"Was the classmate's work missing?"}))

    def test_predicted_feedback_is_discarded_and_real_host_still_answers(self):
        raw='{"type":"question","text":"Did A leave early?","feedback":"no"}'
        with patch('turtle_loop.providers.Client') as formatter:
            action,details=repair(raw,False,self.policy,lambda *a:None,lambda *a,**k:None)
            formatter.assert_not_called()
        self.assertEqual(action,{'type':'question','text':'Did A leave early?'})
        self.assertEqual(details['removed_fields'],['feedback'])
        self.assertIsNone(local_repair(raw.replace('"no"','"maybe"'),False,self.policy))
        self.assertIsNone(local_repair(raw[:-1]+',"secret":"ignore me"}',False,self.policy))
        class Player(FakeClient):
            def complete(self,system,user):
                reply=super().complete(system,user);reply.finish_reason='stop';return reply
        with tempfile.TemporaryDirectory() as tmp:
            rec=Recorder(Path(tmp)/'game',PUZZLE,{'max_questions':3},load_prompts(),echo=False)
            player=Player(lambda n,p:raw if n==1 else '{"type":"final","text":"submitted explanation"}')
            host=FakeClient(lambda n,p:'yes')
            result=play(PUZZLE,{'max_questions':3},rec,
                {'player':player,'host':host,'grader':FakeClient(lambda n,p:evaluated())},load_prompts())
            self.assertTrue(result['success'])
            self.assertEqual(len(host.inputs),1)
            self.assertEqual(rec.turns[0]['label'],'yes')
            self.assertEqual(json.loads(player.inputs[1][1])['visible_history'][0]['feedback'],'yes')

    def test_codex_sees_only_raw_transport_and_all_usage_is_audited(self):
        raw="{'type':'question','text':'Did all the members contribute?'}"
        seen=[];calls=[];events=[]
        class Formatter:
            def __init__(self,profile,role,audit):
                self.audit=audit
                self.profile=profile
                self.role=role
            def complete(self,system,user):
                payload=json.loads(user);seen.append(payload)
                self.audit({'role':self.role,'provider':'codex_cli','status':'ok'})
                return Reply(json.dumps({'type':'question','text':'Did all the members contribute?'}),{},response_id='format-response')
        with patch('turtle_loop.providers.Client',Formatter):
            action,meta=repair(raw,False,self.policy,calls.append,lambda *a,**k:events.append((a,k)),'player-response')
        self.assertEqual(action['text'],'Did all the members contribute?')
        self.assertEqual(meta['method'],'codex_verbatim_format')
        self.assertEqual(seen[0]['raw_output'],raw)
        self.assertEqual(set(seen[0]),{'opening','turn_control','raw_output','format_repair'})
        self.assertEqual(calls[0]['format_source_response_id'],'player-response')
        self.assertTrue(events)

    def test_repair_budget_and_mandatory_final_never_trigger_unbounded_model_calls(self):
        with patch('turtle_loop.providers.Client') as client:
            with self.assertRaises(ProtocolError):
                repair("bad JSON",False,self.policy,lambda *a:None,lambda *a,**k:None,codex_calls=3)
            with self.assertRaises(ProtocolError):
                repair('<think>draft</think>{"type":"question","text":"Q?"}',True,
                       self.policy,lambda *a:None,lambda *a,**k:None)
            client.assert_not_called()

    def test_loop_repairs_without_stopping_reasking_or_charging_question_quota(self):
        class Player(FakeClient):
            def complete(self,system,user):
                result=super().complete(system,user);result.finish_reason='stop';return result
        with tempfile.TemporaryDirectory() as tmp:
            config={'max_questions':3};prompts=load_prompts()
            rec=Recorder(Path(tmp)/'game',copy.deepcopy(PUZZLE),config,prompts,echo=False)
            player=Player(lambda n,p:'{"type":"question","text":"Draft?"}</think>{"type":"question","text":"Actual?"}'
                          if n==1 else '{"type":"final","text":"submitted explanation"}')
            host=FakeClient(lambda n,p:'no')
            grader=FakeClient(lambda n,p:evaluated())
            result=play(PUZZLE,config,rec,{'player':player,'host':host,'grader':grader},prompts)
            self.assertTrue(result['success'])
            self.assertEqual((result['submissions'],result['counted_questions']),(2,1))
            self.assertEqual(len(player.inputs),2)
            self.assertEqual(json.loads(host.inputs[0][1])['current_question'],'Actual?')
            self.assertEqual(len(host.inputs),1)
            events=[json.loads(x) for x in (rec.folder/'trajectory.jsonl').read_text().splitlines()]
            self.assertEqual(len([e for e in events if e['event']=='player_format_recovery']),1)
