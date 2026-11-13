"""Guard behavior at the intersection of main and the unified experiment branch."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from turtle_loop.engine import Recorder, ProtocolError, load_prompts, play
from turtle_loop.providers import Client, APIError
from test_loop import PUZZLE, evaluated
from test_sessions import Response


@patch.dict('os.environ', {'DEEPSEEK_API_KEY':'fixture'})
class MainIntegrationTests(unittest.TestCase):
    def test_invalid_json_keeps_response_fingerprint_without_recording_raw_body(self):
        calls=[]
        client=Client({'provider':'deepseek','model':'fixture'},'host',calls.append)
        response=Response({})
        raw=b'private invalid provider response'
        with patch.object(client.opener,'open',return_value=response) as opened, \
             patch.object(response,'read',return_value=raw), self.assertRaises(APIError):
            client.complete('system','{}')
        self.assertEqual(opened.call_count,1)
        self.assertEqual(calls[-1]['status'],'invalid_response')
        self.assertEqual(calls[-1]['response_bytes'],len(raw))
        self.assertEqual(calls[-1]['response_sha256'],hashlib.sha256(raw).hexdigest())
        self.assertNotIn(raw.decode(),str(calls))

    def test_explicit_reprompt_authorization_survives_other_recovery_markers(self):
        with tempfile.TemporaryDirectory() as tmp:
            config={'max_questions':3,'session_mode':'persistent',**{
                r:{'provider':'deepseek','model':r} for r in ('host','player','grader')}}
            prompts=load_prompts();counts={r:0 for r in ('host','player','grader')};requests=[]
            def api(req,**kwargs):
                body=json.loads(req.data);role=body['model'];counts[role]+=1;requests.append((role,body))
                text=('QUESTION\nOne question?' if counts['player']==1 else
                      'Only untyped thoughts.' if counts['player']==2 else
                      'FINAL\nsubmitted explanation') if role=='player' else 'no' if role=='host' else evaluated()
                return Response({'id':f'{role}-{counts[role]}','choices':[
                    {'message':{'content':text},'finish_reason':'stop'}]})
            def clients(rec):return {r:Client(config[r],r,rec.audit) for r in ('host','player','grader')}
            with patch('urllib.request.OpenerDirector.open',side_effect=api):
                rec=Recorder(Path(tmp)/'game',PUZZLE,config,prompts,echo=False)
                with patch('turtle_loop.player_format.is_untyped_prose',return_value=False), \
                     patch('turtle_loop.player_format.repair',side_effect=ProtocolError('Archived parser stopped')):
                    result=play(PUZZLE,config,rec,clients(rec),prompts)
                self.assertEqual(result['submissions'],1)
                raw='Only untyped thoughts.'
                marker={'response_id':'player-2','raw_sha256':hashlib.sha256(raw.encode()).hexdigest(),
                        'preserved_submissions':1,'authorization':'user_requested_reprompt','action_type':'final'}
                (rec.folder/'player_format_reprompt.json').write_text(json.dumps(marker))
                restored=Recorder.restore(rec.folder,PUZZLE,config,prompts,echo=False)
                self.assertEqual(restored.retry_player_format,'final')
                self.assertEqual(len(restored.turns),1)
                result=play(PUZZLE,config,restored,clients(restored),prompts)
                self.assertTrue(result['success'])
                self.assertEqual(result['submissions'],2)
                self.assertEqual(counts,{'host':1,'player':3,'grader':1})
                messages=next(b['messages'] for r,b in reversed(requests) if r=='player')
                self.assertIn(raw,[m['content'] for m in messages])
                events=[json.loads(line) for line in (rec.folder/'trajectory.jsonl').read_text().splitlines()]
                event=next(e for e in events if e['event']=='player_format_reprompt')
                self.assertFalse(event['counts_as_submission'])
                self.assertEqual(event['raw_sha256'],marker['raw_sha256'])
