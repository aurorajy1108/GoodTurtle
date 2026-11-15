import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

from turtle_loop.sessions import delta, GameSession, LEGACY_SESSION_INSTRUCTIONS, restore_context
from turtle_loop.providers import Client, Reply, APIError
from turtle_loop.engine import Recorder, load_prompts, play
from turtle_loop.experiments import TeamPlayer
from test_loop import PUZZLE, FakeClient, evaluated


class Response:
    def __init__(self, data): self.data = data
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self): return json.dumps(self.data).encode()


class SessionTests(unittest.TestCase):
    def test_reference_cache_transmits_each_body_once_and_preserves_active_scope(self):
        events=[]
        session=GameSession('host','.',lambda *a,**k:events.append((a,k)))
        examples=[{'question':'Question '+str(i)+'?', 'answer':'yes',
                   'public_history':[{'question':'Before?','answer':'no'}]} for i in range(3)]
        initial={'active_puzzle':{'canonical_solution':'secret', 'host_examples':examples[:2]},
                 'visible_history':[], 'current_question':'Q1?'}
        try:
            lane,payload,_,wire,_=session.prepare('host',json.dumps(initial))
            self.assertNotIn('host_examples',payload['active_puzzle'])
            self.assertEqual(len(payload['active_puzzle']['reference_library']),2)
            session.accept(lane,payload,wire,Reply('yes',{},response_id='r1'))
            second=copy.deepcopy(initial);second['active_puzzle']['host_examples']=[examples[1],examples[2]]
            second['current_question']='Q2?'
            _,new_payload,_,new_wire,_=session.prepare('host',json.dumps(second))
            self.assertNotIn(examples[0]['question'],new_wire)
            self.assertNotIn(examples[1]['question'],new_wire)
            self.assertIn(examples[2]['question'],new_wire)
            self.assertEqual(restore_context(payload,new_wire),new_payload)
            story=new_payload['active_puzzle']
            self.assertEqual([story['reference_library'][i] for i in story['active_example_ids']],examples[1:])
            self.assertEqual(story['canonical_solution'],'secret')
            # Returning to an earlier selection sends IDs, not its example text.
            session.accept(lane,new_payload,new_wire,Reply('no',{},response_id='r2'))
            _,last,_,last_wire,_=session.prepare('host',json.dumps(initial))
            self.assertNotIn('Question 0?',last_wire)
            self.assertNotIn('Question 1?',last_wire)
            self.assertEqual(restore_context(new_payload,last_wire),last)
        finally:session.close()

    def test_restored_legacy_prompt_is_preserved_verbatim(self):
        with tempfile.TemporaryDirectory() as tmp:
            old=GameSession('player',tmp,lambda *a,**k:None)
            with patch('turtle_loop.sessions.SESSION_INSTRUCTIONS',LEGACY_SESSION_INSTRUCTIONS):
                lane,payload,system,wire,meta=old.prepare('original player prompt',json.dumps({'opening':'story','visible_history':[]}))
            call={**meta,'role':'player','provider':'deepseek','status':'ok',
                  'request':{'messages':[{'role':'system','content':system},{'role':'user','content':wire}]},
                  'text':'{"type":"question","text":"Q?"}','response_id':'response-1'}
            old.close()
            restored=GameSession('player',tmp,lambda *a,**k:None)
            try:
                restored.restore_chat([call])
                _,_,new_system,_,new_meta=restored.prepare('original player prompt',
                    json.dumps({'opening':'story','visible_history':[{'text':'Q?','feedback':'no'}]}))
                self.assertEqual(new_system,system)
                self.assertEqual(new_meta['session_turn'],2)
                self.assertEqual(new_meta['session_lane_id'],meta['session_lane_id'])
            finally:restored.close()

    def test_delta_losslessly_reconstructs_sync_reorder_and_removed_fields(self):
        before = {'opening': 'story', 'prior_experience': {'answer': 'A'},
                  'visible_history': [{'text':'q1'}, {'text':'q3'}], 'temp': True}
        after = {'opening': 'story', 'prior_experience': {'answer': 'A'},
                 'visible_history': [{'text':'q1'}, {'text':'q2'}, {'text':'q3'}]}
        update = delta(before, after)['context_update']
        self.assertIn('visible_history', update['set'])
        self.assertNotIn('prior_experience', update['set'])
        reconstructed = copy.deepcopy(before)
        for key in update['remove']: reconstructed.pop(key)
        reconstructed.update(update['set'])
        self.assertEqual(reconstructed, after)
        next_value = {**after, 'visible_history': after['visible_history'] + [{'text':'q4'}]}
        self.assertEqual(delta(after, next_value)['context_update']['append_visible_history'], [{'text':'q4'}])

    @patch('turtle_loop.codex_client.shutil.which', return_value='/bin/codex')
    def test_codex_resumes_exact_role_thread_schema_and_never_last(self, _):
        records, commands, inputs = [], [], []
        def run(args, **kwargs):
            commands.append(args); inputs.append(json.loads(kwargs['input']))
            self.assertEqual(json.loads(Path(args[args.index('--output-schema')+1]).read_text())['properties']['label']['enum'],
                             ['yes','no','yes and no','irrelevant'])
            events = [{'type':'thread.started','thread_id':'fixture-thread'},
                      {'type':'item.completed','item':{'type':'agent_message','text':'{"label":"yes"}'}},
                      {'type':'turn.completed','usage':{'input_tokens':50*len(commands),'output_tokens':len(commands)}}]
            return subprocess.CompletedProcess(args,0,'\n'.join(map(json.dumps, events)), '')
        client = Client({'provider':'codex_cli','model':'fixture'},'host',records.append)
        with tempfile.TemporaryDirectory() as tmp, patch('turtle_loop.codex_client.subprocess.run',side_effect=run):
            client.begin_game(tmp, lambda *a, **k: None)
            first = {'active_puzzle': {'canonical_solution':'secret'}, 'visible_history':[], 'current_question':'q1'}
            self.assertEqual(client.complete('host',json.dumps(first)).text,'yes')
            second = {**first, 'visible_history':[{'text':'q1','feedback':'yes'}], 'current_question':'q2'}
            client.complete('host',json.dumps(second))
            self.assertNotIn('resume',commands[0]); self.assertNotIn('--ephemeral',commands[0])
            self.assertEqual(commands[1][-3:],['resume','fixture-thread','-'])
            self.assertNotIn('--last',commands[1]); self.assertIn('shell_tool',commands[1])
            self.assertNotIn('active_puzzle',inputs[1]['context_update']['set'])
            self.assertEqual(records[1]['previous_response_id'],'fixture-thread')
            self.assertEqual(records[1]['raw_usage']['input_tokens'],100)
            self.assertEqual(records[1]['usage']['input_tokens'],50)
            self.assertEqual(records[1]['usage']['output_tokens'],1)
            client.close_game()
            with self.assertRaises(ValueError): client.complete('host',json.dumps(second))

    @patch.dict('os.environ', {'OPENAI_API_KEY':'fixture','DEEPSEEK_API_KEY':'fixture','ANTHROPIC_API_KEY':'fixture'})
    def test_provider_modes_and_exact_context_deltas(self):
        for provider in ('openai', 'deepseek', 'anthropic'):
            records, requests = [], []
            client = Client({'provider':provider,'model':'fixture'},'player',records.append)
            def request(req, **kwargs):
                requests.append(json.loads(req.data)); i=len(requests)
                if provider == 'openai':
                    return Response({'id':f'resp{i}', 'status':'completed', 'output':[{'type':'message','content':[{'type':'output_text','text':'answer'}]}]})
                if provider == 'anthropic':
                    return Response({'id':f'resp{i}', 'stop_reason':'end_turn','content':[{'type':'text','text':'answer'}]})
                return Response({'id':f'resp{i}', 'choices':[{'message':{'content':'answer'},'finish_reason':'stop'}]})
            with tempfile.TemporaryDirectory() as tmp, patch.object(client.opener,'open',side_effect=request):
                client.begin_game(tmp,lambda *a,**k:None)
                payload={'opening':'B','prior_experience':{'answer':'A'},'visible_history':[],'turn_control':'first'}
                client.complete('player',json.dumps(payload))
                client.complete('player',json.dumps({**payload,'turn_control':'second'}))
                if provider == 'openai':
                    self.assertTrue(requests[0]['store'])
                    self.assertEqual(requests[1]['previous_response_id'],'resp1')
                    self.assertEqual(len(requests[1]['input']),1)
                    self.assertIn('SESSION PROTOCOL',requests[1]['instructions'])
                    text=requests[1]['input'][-1]['content']
                else:
                    messages=requests[1]['messages']
                    self.assertEqual([m['role'] for m in messages][-3:],['user','assistant','user'])
                    text=messages[-1]['content']
                self.assertNotIn('prior_experience',json.loads(text)['context_update']['set'])
                self.assertEqual(records[1]['session_turn'],2)
                client.close_game()

    @patch.dict('os.environ', {'OPENAI_API_KEY':'fixture'})
    def test_ambiguous_transport_failure_is_not_retried_or_reopened(self):
        client=Client({'provider':'openai','model':'fixture','max_retries':3},'host',lambda r:None)
        with tempfile.TemporaryDirectory() as tmp, patch.object(client.opener,'open',side_effect=URLError('timeout')) as mocked:
            client.begin_game(tmp,lambda *a,**k:None)
            with self.assertRaises(APIError): client.complete('host','{}')
            self.assertEqual(mocked.call_count,1)
            with self.assertRaisesRegex(ValueError,'Session failed'): client.complete('host','{}')
            client.close_game()

    def test_private_selection_lane_never_enters_independent_proposal_lane(self):
        with tempfile.TemporaryDirectory() as tmp:
            state=GameSession('player',tmp,lambda *a,**k:None)
            proposal,payload,_,wire,_=state.prepare('proposal',json.dumps({'opening':'B'}))
            state.accept(proposal,payload,wire,Reply('my draft',{},'draft-thread'))
            selection,payload,_,wire,_=state.prepare('selector',json.dumps({'teammate':'SECRET_PROPOSAL'}))
            state.accept(selection,payload,wire,Reply('chosen',{},'select-thread'))
            again,_,_,_,_=state.prepare('proposal',json.dumps({'opening':'B','feedback':'no'}))
            self.assertIs(again,proposal)
            self.assertNotIn('SECRET_PROPOSAL',json.dumps(again['messages']))
            self.assertNotEqual(proposal['id'],selection['id'])
            state.close()

    def test_role_lifecycle_and_fresh_b_game(self):
        class FakeSessionClient(FakeClient):
            def begin_game(self, folder, event): self.state=GameSession('fixture',folder,event)
            def close_game(self): self.state.close()
        identifiers=[]
        with tempfile.TemporaryDirectory() as tmp:
            for n in range(2):
                config={'max_questions':2,'session_mode':'persistent'}; prompts=load_prompts()
                rec=Recorder(Path(tmp)/str(n),PUZZLE,config,prompts,echo=False)
                clients={'player':FakeSessionClient(lambda i,p:json.dumps({'type':'final','text':'guess'})),
                         'host':FakeSessionClient(lambda i,p:'yes'), 'grader':FakeSessionClient(lambda i,p:evaluated())}
                play(PUZZLE,config,rec,clients,prompts)
                identifiers.extend(c.state.id for c in clients.values())
                self.assertTrue(all(c.state.closed for c in clients.values()))
            self.assertEqual(len(identifiers),len(set(identifiers)))

    def test_grader_current_submission_always_replaces_previous(self):
        with tempfile.TemporaryDirectory() as tmp:
            state=GameSession('grader',tmp,lambda *a,**k:None)
            payload={'story_context':{'canonical_solution':'secret'},'rubric':[], 'submitted_explanation':'old answer'}
            lane,p,_,wire,_=state.prepare('grade',json.dumps(payload))
            state.accept(lane,p,wire,Reply('grade',{},'grading-thread'))
            _,_,system,wire,_=state.prepare('grade',json.dumps({**payload,'submitted_explanation':'new answer'}))
            self.assertEqual(json.loads(wire)['context_update']['set'], {'submitted_explanation':'new answer'})
            self.assertIn('Never carry a prior submitted',system)
            state.close()

    def test_shared_buffer_sessions_never_receive_unpublished_partner_feedback(self):
        class SessionSpy:
            def __init__(self, role, folder):
                self.state=GameSession(role,folder,lambda *a,**k:None)
                self.sent=[]
            def complete(self, system, user):
                lane,payload,_,wire,_=self.state.prepare(system,user)
                self.sent.append(wire)
                reply=Reply(json.dumps({'type':'question','text':'next'}),{},'thread')
                self.state.accept(lane,payload,wire,reply)
                return reply
        with tempfile.TemporaryDirectory() as tmp:
            rec=Recorder(Path(tmp)/'game',PUZZLE,{'max_questions':6},load_prompts(),echo=False)
            a,b=SessionSpy('player',tmp),SessionSpy('partner',tmp)
            team=TeamPlayer(a,b,'shared_buffer',rec,4)
            history=[]
            for i in range(5):
                team.complete('player',json.dumps({'opening':'B','visible_history':history,'turn_control':'normal'}))
                if i < 4:
                    sender = a if i % 2 == 0 else b
                    other = 'B_PRIVATE' if i % 2 == 0 else 'A_PRIVATE'
                    self.assertNotIn(other, '\n'.join(sender.sent))
                history.append({'type':'question','text':f'Q{i}',
                                'feedback':'A_PRIVATE' if i%2==0 else 'B_PRIVATE'})
            self.assertIn('B_PRIVATE',a.sent[-1])
            self.assertNotEqual(a.state.id,b.state.id)
            a.state.close(); b.state.close()

    def test_nested_delta_does_not_resend_canonical_story_when_references_change(self):
        before={'active_puzzle':{'canonical_solution':'STORY','host_examples':[{'question':'q1','answer':'yes'}]}}
        after={'active_puzzle':{'canonical_solution':'STORY','host_examples':[{'question':'q2','answer':'no'}]}}
        update=delta(before,after)
        self.assertNotIn('STORY',json.dumps(update))
        self.assertEqual(update['context_update']['update_objects']['active_puzzle']['set'],
                         {'host_examples':[{'question':'q2','answer':'no'}]})
