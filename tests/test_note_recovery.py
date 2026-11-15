import copy
import json
import os
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

from turtle_loop.engine import Recorder, ProtocolError, load_prompts, parse_action, play, saved_player_note_recovery, saved_player_json_recovery, saved_player_auto_recovery
from turtle_loop.providers import Client
from turtle_loop.sessions import GameSession, delta, restore_context
from turtle_loop.sessions import restorable_chat_records
from test_loop import PUZZLE, evaluated
from test_sessions import Response


class NoteRecoveryTests(unittest.TestCase):
    def test_escaped_closing_quote_repair_preserves_words_and_internal_escapes(self):
        question='Did A use "lead" with a slash \\ here?'
        valid=json.dumps({'type':'question','text':question})
        at=valid.rfind('"');raw=valid[:at]+'\\'+valid[at:]
        audit=[]
        self.assertEqual(parse_action(raw,audit=audit.append),{'type':'question','text':question})
        self.assertEqual(audit[0]['method'],'escaped_question_text_closing_quote')
        self.assertEqual(audit[0]['characters_removed'],1)
        for bad in [raw[:-1],raw+'{}',raw.replace('"question"','"final"'),
                    raw.replace('here?', 'here.'),raw[:-1]+',"extra":true}']:
            with self.assertRaises(ProtocolError):parse_action(bad)
        with self.assertRaises(ProtocolError):parse_action(raw,force_final=True)

    def test_pre_send_retry_requires_identical_request_and_completed_next_attempt(self):
        failed={'role':'host','provider':'deepseek','model_requested':'fixture','endpoint':'https://fixture',
                'game_session_id':'g','session_lane_id':'lane','session_turn':3,'previous_response_id':'r2',
                'request':{'messages':[{'role':'user','content':'Q?'}]},'attempt':1,
                'status':'transport_error','safe_pre_send_retry':True,
                'transport_category':'tls_handshake_eof','transport_phase':'open'}
        ok={**failed,'status':'ok','attempt':2,'text':'no','response_id':'r3'}
        self.assertEqual(restorable_chat_records([failed,ok]),[ok])
        for field,value in [('safe_pre_send_retry',False),('transport_phase','read'),
                            ('text','observed answer'),('transport_category','tls')]:
            with self.assertRaises(ValueError):restorable_chat_records([{**failed,field:value},ok])
        for field,value in [('request',{'different':True}),('session_turn',4),('attempt',3),('role','player')]:
            with self.assertRaises(ValueError):restorable_chat_records([failed,{**ok,field:value}])
        with self.assertRaises(ValueError):restorable_chat_records([failed])

    def test_only_nonsemantic_string_note_is_ignored(self):
        raw={'type':'question','text':'The same question?','text_note':'rephrase'}
        self.assertEqual(parse_action(json.dumps(raw)),{'type':'question','text':'The same question?'})
        for extra in ({'another_question':'Q2?'},{'text_note':{'question':'Q2?'}},{'answer':'guess'}):
            with self.assertRaises(ProtocolError):
                parse_action(json.dumps({'type':'question','text':'Q?',**extra}))
        with self.assertRaises(ProtocolError):parse_action(json.dumps(raw),force_final=True)

    def test_saved_deltas_reconstruct_nested_removal_and_both_histories(self):
        before={'opening':'story','visible_history':[{'text':'Q1'}], 'shared_dialogue':[],
                'selection':{'old':True,'keep':3}}
        after={'opening':'story','visible_history':[{'text':'Q1'},{'text':'Q2'}],
               'shared_dialogue':[{'speaker':'B','text':'idea'}], 'selection':{'keep':4}}
        self.assertEqual(restore_context(before,json.dumps(delta(before,after))),after)
        self.assertEqual(restore_context(None,json.dumps(before)),before)
        with self.assertRaises(ValueError):restore_context(None,json.dumps(delta(before,after)))

    def test_resume_preserves_messages_saved_action_budget_and_costs_without_resampling(self):
        self.resume_case('text_note')

    def test_missing_quote_resume_preserves_saved_question_and_does_not_resample(self):
        self.resume_case('question_quote')

    def test_unescaped_inner_quote_resume_does_not_regenerate_question(self):
        self.resume_case('inner_quotes')

    def test_escaped_closing_quote_resume_preserves_successful_pre_send_retries(self):
        self.resume_case('escaped_closing_quote')

    def test_terminal_action_resume_never_regenerates_saved_player_reply(self):
        self.resume_case('terminal_action')

    @patch.dict(os.environ, {'DEEPSEEK_API_KEY':'fixture'})
    def resume_case(self, mode):
        class StopAfterSavedReply(Client):
            def complete(self, system, user):
                reply=super().complete(system,user)
                if 'text_note' in reply.text or reply.text.endswith('?}') or 'Action "three"?' in reply.text or reply.text.endswith('\\"}') or '</think>' in reply.text:
                    raise ProtocolError('Player JSON must contain type=question|final and nonempty text')
                return reply

        counts=Counter(); requests=[]
        question3='Action 3?' if mode in ('question_quote','escaped_closing_quote','terminal_action') else 'Action "three"?' if mode=='inner_quotes' else 'Action 3'
        def respond(req, **kwargs):
            body=json.loads(req.data); role=body['model'].removeprefix('fixture-')
            counts[role]+=1; n=counts[role]; requests.append((role,body))
            if role=='player':
                value={'type':'final' if n==4 else 'question','text':question3 if n==3 else f'Action {n}'}
                if n==3 and mode=='text_note':value['text_note']='rephrase'
                text=json.dumps(value)
                if n==3 and mode=='question_quote':
                    at=text.rfind('"');text=text[:at]+text[at+1:]
                if n==3 and mode=='inner_quotes':text=text.replace('\\"three\\"','"three"')
                if n==3 and mode=='escaped_closing_quote':
                    at=text.rfind('"');text=text[:at]+'\\'+text[at:]
                if n==3 and mode=='terminal_action':
                    text='{"type":"question","text":"Draft question?"}<think>draft reasoning</think>'+text
            elif role=='host':text='no'
            else:text=evaluated()
            return Response({'id':f'{role}-{n}','model':body['model'],
                'choices':[{'message':{'content':text},'finish_reason':'stop'}],
                'usage':{'prompt_tokens':10,'completion_tokens':1,'prompt_cache_hit_tokens':0}})

        with tempfile.TemporaryDirectory() as tmp, patch('urllib.request.OpenerDirector.open',side_effect=respond):
            config={'max_questions':4,'session_mode':'persistent',
                    **{r:{'provider':'deepseek','model':'fixture-'+r} for r in ('player','host','grader')}}
            prompts=load_prompts()
            rec=Recorder(Path(tmp)/'game',PUZZLE,config,prompts,echo=False)
            clients={r:(StopAfterSavedReply if r=='player' else Client)(config[r],r,rec.audit) for r in ('player','host','grader')}
            result=play(PUZZLE,config,rec,clients,prompts)
            self.assertEqual((result['status'],result['counted_questions']),('error',2))
            self.assertEqual(counts,{'player':3,'host':2})
            old_player=next(c for c in rec.calls if c['role']=='player')
            old_host=next(c for c in rec.calls if c['role']=='host')
            if mode=='escaped_closing_quote':
                at=next(i for i,c in enumerate(rec.calls) if c['role']=='host')
                success=rec.calls[at]
                failure={**success,'status':'transport_error','safe_pre_send_retry':True,
                         'transport_category':'tls_handshake_eof','transport_phase':'open','attempt':1}
                for key in ('response_id','text','usage','model_returned','finish_reason'):failure.pop(key,None)
                from turtle_loop.costs import account_call
                failure['accounting']=account_call(failure,rec.pricing)
                success['attempt']=2
                rec.calls.insert(at,failure)
                (rec.folder/'api_calls.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in rec.calls))
            recover=saved_player_note_recovery if mode=='text_note' else saved_player_auto_recovery if mode=='terminal_action' else saved_player_json_recovery
            for changed in ('transport','unknown_metadata','broken_chain'):
                calls=copy.deepcopy(rec.calls)
                if changed=='transport':calls[-1]['status']='transport_error'
                elif changed=='unknown_metadata':calls[-1]['text']='{"type":"question","text":"Q","answer":"guess"}'
                else:calls[-1]['session_turn']=500
                self.assertIsNone(recover(result,calls,rec.turns,config),changed)
            if mode!='text_note':
                calls=copy.deepcopy(rec.calls);calls[-1]['finish_reason']='length'
                self.assertIsNone(recover(result,calls,rec.turns,config))
            self.assertIsNone(recover(result,rec.calls,rec.turns,
                              {**config,'player':{'provider':'openai','model':'fixture'}}))
            before=len(requests)
            restored=Recorder.restore(rec.folder,PUZZLE,config,prompts,echo=False)
            self.assertEqual(len(requests),before)  # Recovery itself is offline.
            self.assertEqual(restored.turns[-1]['index'],3)
            self.assertEqual(restored.turns[-1]['text'],question3)
            self.assertNotIn('label',restored.turns[-1])
            clients={r:Client(config[r],r,restored.audit) for r in ('player','host','grader')}
            completed=play(PUZZLE,config,restored,clients,prompts)
            self.assertTrue(completed['success'])
            self.assertEqual((completed['submissions'],completed['counted_questions']),(4,3))
            self.assertEqual(counts,{'player':4,'host':3,'grader':1})
            self.assertEqual(requests[before][0],'host')  # Submit saved Action 3 before any new player generation.
            new_player=next(c for c in restored.calls if c['role']=='player' and c['session_turn']==4)
            new_host=next(c for c in restored.calls if c['role']=='host' and c['session_turn']==3)
            self.assertEqual(new_player['game_session_id'],old_player['game_session_id'])
            self.assertEqual(new_player['session_lane_id'],old_player['session_lane_id'])
            self.assertEqual(new_host['session_lane_id'],old_host['session_lane_id'])
            messages=new_player['request']['messages']
            self.assertEqual(messages[-2]['content'],rec.calls[-1]['text'])  # Preserve the exact old assistant reply.
            self.assertIn('mandatory last turn',messages[-1]['content'])
            self.assertNotIn('text_note',json.dumps(new_host['request']))
            self.assertEqual(len(restored.calls),9 if mode=='escaped_closing_quote' else 8)
            self.assertEqual(completed['costs']['total']['tokens']['total_tokens'],88)
            events=[json.loads(x) for x in (rec.folder/'trajectory.jsonl').read_text().splitlines()]
            recovered=[e for e in events if e.get('event')=='submission' and e.get('recovered_from_response_id')]
            self.assertEqual(len(recovered),1)
            self.assertEqual(recovered[0]['index'],3)


if __name__=='__main__':unittest.main()
