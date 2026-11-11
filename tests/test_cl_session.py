"""Cross-puzzle message lineage, independent quotas and no private-context leaks."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from turtle_loop.providers import Client
from turtle_loop.sessions import GameSession, restore_context
from turtle_loop.engine import Recorder, ProtocolError, load_prompts, play
from turtle_loop.experiments import main
from test_loop import PUZZLE, evaluated
from test_sessions import Response


def response(provider, n, text):
    if provider=='openai':
        return Response({'id':f'r{n}','status':'completed','output':[
            {'type':'message','content':[{'type':'output_text','text':text}]}]})
    if provider=='anthropic':
        return Response({'id':f'r{n}','stop_reason':'end_turn','content':[{'type':'text','text':text}]})
    return Response({'id':f'r{n}','choices':[{'message':{'content':text},'finish_reason':'stop'}],
                     'usage':{'prompt_tokens':10,'completion_tokens':2}})


@patch.dict('os.environ',{'DEEPSEEK_API_KEY':'fixture','OPENAI_API_KEY':'fixture','ANTHROPIC_API_KEY':'fixture'})
class CLSessionTests(unittest.TestCase):
    def test_prefix_fork_restore_and_role_messages_across_providers(self):
        for provider in ('deepseek','openai','openai_chat','openai_compatible','anthropic'):
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as tmp:
                profile={'provider':provider,'model':'fixture'}
                if provider=='openai_compatible':profile.update(base_url='https://example.invalid/v1',api_key_env='OPENAI_API_KEY')
                source=[];target=[];requests=[];clients=[]
                def api(req,**kw):
                    requests.append(json.loads(req.data))
                    return response(provider,len(requests),'{"type":"question","text":"Original action?"}')
                def client(calls):
                    c=Client(profile,'player',calls.append);clients.append(c);return c
                with patch('urllib.request.OpenerDirector.open',side_effect=api):
                    try:
                        a=client(source);a.begin_game(tmp,lambda *a,**k:None)
                        payload={'opening':'A','visible_history':[],'turn_control':'A turn 1'}
                        a.complete('same player system',json.dumps(payload))
                        a.complete('same player system',json.dumps({**payload,'turn_control':'A turn 2'}))
                        a.close_game()
                        boundary={'completed_puzzle_full_answer':'FULL A ANSWER','new_submission_budget':100}
                        b=client(target);b.inherit_game(tmp,lambda *a,**k:None,source,boundary)
                        next_payload={'opening':'B','visible_history':[],'turn_control':'Used question-equivalents: 0'}
                        b.complete('same player system',json.dumps(next_payload))
                        first=target[0]
                        self.assertEqual(first['session_turn'],3)
                        self.assertEqual(first['previous_response_id'],source[-1]['response_id'])
                        self.assertEqual(first['inherited_session']['messages'],next(iter(a.session.lanes.values()))['messages'])
                        if provider=='openai':
                            self.assertEqual(first['request']['previous_response_id'],source[-1]['response_id'])
                            self.assertEqual(len(first['request']['input']),1)
                        else:
                            offset=0 if provider=='anthropic' else 1
                            self.assertEqual(first['request']['messages'][offset:-1],first['inherited_session']['messages'])
                        lane=next(iter(b.session.lanes.values()))
                        self.assertEqual(lane['previous']['puzzle_boundary'],boundary)
                        self.assertEqual(lane['previous']['visible_history'],[])
                        b.complete('same player system',json.dumps({**next_payload,'turn_control':'B turn 2'}))
                        self.assertNotIn('inherited_session',target[1])
                        restored=GameSession('player',tmp,lambda *a,**k:None)
                        try:
                            restored.restore_chat(target)
                            self.assertEqual(restored.freeze_prefix()['messages'],b.session.freeze_prefix()['messages'])
                            self.assertEqual(restored.freeze_prefix()['turn'],4)
                        finally:restored.close()
                        # A second B starts from exactly A, never from the earlier B.
                        c=client([]);c.inherit_game(tmp,lambda *a,**k:None,source,boundary)
                        self.assertEqual(c.session.freeze_prefix(),a.session.freeze_prefix())
                        with self.assertRaisesRegex(ValueError,'system prompt changed'):
                            c.complete('changed prompt',json.dumps(next_payload))
                        broken=copy.deepcopy(target);broken[0]['inherited_session']['messages'][0]['content']='{}'
                        guard=GameSession('player',tmp,lambda *a,**k:None)
                        try:
                            with self.assertRaises(ValueError):guard.restore_chat(broken)
                        finally:guard.close()
                    finally:
                        for c in clients:c.close_game()

    def test_source_exhausting_100_does_not_reduce_B_quota_or_leak_to_host(self):
        with tempfile.TemporaryDirectory() as tmp:
            prompts=load_prompts();calls=[];logical={};phase=['A'];seen_b=[]
            config={'max_questions':100,'session_mode':'persistent'}
            source_puzzle={**copy.deepcopy(PUZZLE),'id':'A','opening':'A opening','answer':'FULL_A_SECRET'}
            target_puzzle={**copy.deepcopy(PUZZLE),'id':'B','opening':'B opening','answer':'FULL_B_SECRET'}
            def api(req,**kw):
                body=json.loads(req.data);role=body['model'];key=(role,phase[0])
                logical[key]=restore_context(logical.get(key),body['messages'][-1]['content'])
                payload=logical[key]
                if role=='player':
                    if phase[0]=='B':seen_b.append(copy.deepcopy(payload))
                    text=json.dumps({'type':'final' if 'mandatory last turn' in payload['turn_control']
                        or (phase[0]=='B' and len(seen_b)==2) else 'question','text':'submitted explanation'})
                    if phase[0]=='B':self.assertNotIn('FULL_B_SECRET',str(body))
                elif role=='host':
                    if phase[0]=='B':self.assertNotIn('FULL_A_SECRET',str(body))
                    text='no'
                else:
                    if phase[0]=='B':self.assertNotIn('FULL_A_SECRET',str(body))
                    text=evaluated((0,0)) if phase[0]=='A' else evaluated()
                calls.append(body);return response('deepseek',len(calls),text)
            def clients(rec):return {r:Client({'provider':'deepseek','model':r},r,rec.audit) for r in ('host','player','grader')}
            with patch('urllib.request.OpenerDirector.open',side_effect=api):
                a=Recorder(Path(tmp)/'A',source_puzzle,config,prompts,echo=False)
                result_a=play(source_puzzle,config,a,clients(a),prompts)
                self.assertEqual(result_a['counted_questions'],100)
                self.assertEqual(result_a['stop_reason'],'budget_exhausted')
                phase[0]='B'
                # Mock backend reconstructs the continued context from the frozen prefix.
                source_calls=[c for c in a.calls if c['role']=='player']
                last=None
                for msg in source_calls[-1]['request']['messages']:
                    if msg['role']=='user':last=restore_context(last,msg['content'])
                logical[('player','B')]=last
                b=Recorder(Path(tmp)/'B',target_puzzle,config,prompts,echo=False)
                result_b=play(target_puzzle,config,b,clients(b),prompts,player_continuation={
                    'calls':source_calls,'boundary':{'completed_puzzle_full_answer':'FULL_A_SECRET','new_submission_budget':100}})
                self.assertTrue(result_b['success'])
                self.assertEqual(result_b['submissions'],2)
                self.assertIn('Used question-equivalents: 0.',seen_b[0]['turn_control'])
                self.assertNotIn('mandatory last turn',seen_b[0]['turn_control'])
                self.assertEqual(seen_b[0]['visible_history'],[])
                self.assertEqual([c['role'] for c in b.calls],['player','host','player','grader'])
                self.assertEqual(b.calls[0]['session_turn'],101)
                self.assertNotIn('prior_experience',seen_b[0])

    def test_full_pipeline_controls_and_fixed_source_branches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);puzzles=[{**copy.deepcopy(PUZZLE),'id':p,'opening':p+' opening','answer':p+' SECRET'} for p in ('A','B')]
            (root/'data.json').write_text(json.dumps({'schema_version':1,'puzzles':puzzles}))
            (root/'groups.json').write_text(json.dumps({'groups':[{'id':'G','puzzles':['A','B'],'relation':'positive','directed_pairs':[['A','B']]}]}))
            config={'session_mode':'persistent','max_questions':2,**{r:{'provider':'deepseek','model':r} for r in ('host','player','grader')}}
            (root/'config.json').write_text(json.dumps(config));requests=[]
            def api(req,**kw):
                body=json.loads(req.data);requests.append(body)
                text='{"type":"final","text":"submitted explanation"}' if body['model']=='player' else evaluated()
                return response('deepseek',len(requests),text)
            with patch('urllib.request.OpenerDirector.open',side_effect=api):
                code=main(['continual','--dataset',str(root/'data.json'),'--config',str(root/'config.json'),
                    '--groups',str(root/'groups.json'),'--group','G','--repeat','2','--controls','answer_only','--quiet','--out',str(root/'out')])
            self.assertEqual(code,0)
            rows=json.loads((root/'out/experiment_runs.json').read_text())
            self.assertEqual(len(rows),7)
            self.assertEqual(sum(r['condition']=='source' for r in rows),1)
            systems={req['messages'][0]['content'] for req in requests if req['model']=='player'}
            self.assertEqual(len(systems),1)
            prefixes=[]
            for row in rows:
                folder=root/'out'/row['run_dir']
                records=[json.loads(l) for l in (folder/'api_calls.jsonl').read_text().splitlines()]
                player=next(c for c in records if c['role']=='player')
                if row['condition']=='session':
                    prefixes.append(player['inherited_session'])
                    self.assertFalse((folder/'prior_experience.json').exists())
                    self.assertIn('A SECRET',str(player['request']))
                elif row['condition']=='direct':self.assertNotIn('A SECRET',str(player['request']))
                for c in records:
                    if c['role']=='grader' and row['condition']!='source':self.assertNotIn('A SECRET',str(c['request']))
            self.assertEqual(prefixes[0],prefixes[1])
            comparisons=json.loads((root/'out/control_contrasts.json').read_text())
            self.assertEqual(len(comparisons),2)
            self.assertTrue(all(c['treatment']=='session' for c in comparisons))

    def test_format_resume_preserves_inherited_prefix_and_never_regenerates_pending_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            prompts=load_prompts();counter=[0];player_calls=[0];broken=[True]
            config={'max_questions':3,'session_mode':'persistent',
                **{r:{'provider':'deepseek','model':r} for r in ('host','player','grader')}}
            source=[]
            def api(req,**kw):
                body=json.loads(req.data);counter[0]+=1
                if body['model']=='player':
                    player_calls[0]+=1
                    # First call solves A; second call is B's saved malformed envelope.
                    text=('QUESTION\nB question?' if player_calls[0]==2 else 'FINAL\nsubmitted explanation')
                    if player_calls[0]==2:text='</think>'+text
                else:text='no' if body['model']=='host' else evaluated()
                return response('deepseek',counter[0],text)
            with patch('urllib.request.OpenerDirector.open',side_effect=api):
                a=Client(config['player'],'player',source.append);a.begin_game(tmp,lambda *a,**k:None)
                a.complete(prompts['player'],json.dumps({'opening':'A','visible_history':[],'turn_control':'first','action_protocol':'prefix-v1'}))
                a.close_game()
                rec=Recorder(Path(tmp)/'B',PUZZLE,config,prompts,echo=False)
                def clients(rec):return {r:Client(config[r],r,rec.audit) for r in ('host','player','grader')}
                continuation={'calls':source,'boundary':{'completed_puzzle_full_answer':'A full answer','new_submission_budget':3}}
                with patch('turtle_loop.player_format.repair',side_effect=ProtocolError('simulated old parser stopping')):
                    stopped=play(PUZZLE,config,rec,clients(rec),prompts,player_continuation=continuation)
                self.assertEqual(stopped['status'],'error')
                self.assertEqual(stopped['submissions'],0)
                self.assertEqual(player_calls[0],2)
                restored=Recorder.restore(rec.folder,PUZZLE,config,prompts,echo=False)
                resumed=play(PUZZLE,config,restored,clients(restored),prompts,player_continuation=continuation)
                self.assertTrue(resumed['success'])
                self.assertEqual(resumed['submissions'],2)
                self.assertEqual(player_calls[0],3)  # A, saved B question, one new B final.
                b_players=[c for c in restored.calls if c['role']=='player']
                self.assertEqual([c['session_turn'] for c in b_players],[2,3])
                self.assertEqual(b_players[1]['request']['messages'][1:3],source[0]['request']['messages'][1:]+[
                    {'role':'assistant','content':source[0]['text']}])
                self.assertEqual(restored.turns[0]['text'],'B question?')


if __name__=='__main__':unittest.main()
