import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from turtle_loop.engine import Recorder,ProtocolError,load_prompts,play
from turtle_loop.player_format import is_untyped_prose,saved_untyped_player_correction
from turtle_loop.providers import Client
from test_loop import PUZZLE,FakeClient,evaluated
from test_sessions import Response


class CompleteFake(FakeClient):
    def complete(self,system,user):
        reply=super().complete(system,user);reply.finish_reason='stop';reply.response_id='reply-'+str(len(self.inputs));return reply


class UntypedTests(unittest.TestCase):
    def test_only_untyped_non_json_prose_qualifies(self):
        self.assertTrue(is_untyped_prose('I should consider another theory.'))
        for text in ('QUESTION\nA question?','FINAL\nA story.', '{"type":"question","text":"Q?"}',
                     '{"unknown":"schema"}', 'Some preamble\nQUESTION\nQ?', '</think>QUESTION\nQ?',
                     '```text\nFINAL\nAn explanation.\n```', 'QUESTION: Q?', 'final: An answer.',
                     'QUESTION: Q?\nFINAL: An answer.'):
            self.assertFalse(is_untyped_prose(text))

    def test_correction_preserves_slot_and_has_two_call_limit(self):
        for succeed in (True,False):
            with self.subTest(succeed=succeed),tempfile.TemporaryDirectory() as tmp:
                def response(n,payload):
                    if n>1:
                        self.assertEqual(payload['format_correction']['same_submission_slot'],1)
                        self.assertEqual(payload['visible_history'],[])
                    return 'FINAL\nsubmitted explanation' if succeed and n==2 else 'Only analysis, no action yet.'
                player=CompleteFake(response);host=FakeClient(lambda *a:self.fail('No question should be sent'))
                rec=Recorder(Path(tmp)/'run',PUZZLE,{'max_questions':100},load_prompts(),echo=False)
                result=play(PUZZLE,{'max_questions':100},rec,{'player':player,'host':host,
                    'grader':FakeClient(lambda *a:evaluated())},load_prompts())
                self.assertEqual(len(player.inputs),2 if succeed else 3)
                self.assertEqual(result['submissions'],1 if succeed else 0)
                self.assertEqual(result['counted_questions'],0)
                self.assertEqual(result['success'],True if succeed else None)
                self.assertEqual(len(result['player_format_corrections']),1 if succeed else 2)

    @patch.dict('os.environ',{'DEEPSEEK_API_KEY':'fixture'})
    def test_saved_prose_resumes_original_messages_and_does_not_repeat_host_question(self):
        with tempfile.TemporaryDirectory() as tmp:
            config={'max_questions':3,'session_mode':'persistent',**{r:{'provider':'deepseek','model':r} for r in ('host','player','grader')}}
            prompts=load_prompts();counts={r:0 for r in ('host','player','grader')};requests=[]
            def api(req,**kw):
                body=json.loads(req.data);role=body['model'];counts[role]+=1;requests.append((role,body))
                text=('QUESTION\nOne question?' if counts['player']==1 else 'Only analysis without an action.' if counts['player']==2 else 'FINAL\nsubmitted explanation') if role=='player' else 'no' if role=='host' else evaluated()
                return Response({'id':f'{role}-{counts[role]}','choices':[{'message':{'content':text},'finish_reason':'stop'}]})
            def clients(rec):return {r:Client(config[r],r,rec.audit) for r in ('host','player','grader')}
            with patch('urllib.request.OpenerDirector.open',side_effect=api):
                rec=Recorder(Path(tmp)/'game',PUZZLE,config,prompts,echo=False)
                with patch('turtle_loop.player_format.is_untyped_prose',return_value=False),\
                     patch('turtle_loop.player_format.repair',side_effect=ProtocolError('Old parser stopped')):
                    stopped=play(PUZZLE,config,rec,clients(rec),prompts)
                self.assertEqual(stopped['submissions'],1)
                calls=[json.loads(s) for s in (rec.folder/'api_calls.jsonl').read_text().splitlines()]
                checkpoint=saved_untyped_player_correction(stopped,calls,rec.turns,config)
                self.assertIsNotNone(checkpoint)
                marker=rec.folder/'player_format_correction.json';marker.write_text(json.dumps(checkpoint))
                restored=Recorder.restore(rec.folder,PUZZLE,config,prompts,echo=False)
                before=len(requests);result=play(PUZZLE,config,restored,clients(restored),prompts)
                self.assertTrue(result['success']);self.assertEqual(result['submissions'],2)
                self.assertEqual(counts,{'host':1,'player':3,'grader':1})
                self.assertEqual(requests[before][0],'player')
                self.assertEqual(requests[before][1]['messages'][-2]['content'],checkpoint['raw'])
                self.assertFalse(marker.exists())
