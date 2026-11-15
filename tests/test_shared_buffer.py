import json
import tempfile
import unittest
from pathlib import Path
from turtle_loop.experiments import TeamPlayer
from turtle_loop.engine import Recorder, load_prompts
from test_loop import FakeClient, PUZZLE

class SharedBufferTests(unittest.TestCase):
    def test_private_then_sync_and_forced_final(self):
        with tempfile.TemporaryDirectory() as tmp:
            rec=Recorder(Path(tmp)/'game',PUZZLE,{'max_questions':6},load_prompts(),echo=False)
            a=FakeClient(lambda i,p:json.dumps({'type':'question','text':'A'}))
            b=FakeClient(lambda i,p:json.dumps({'type':'question','text':'B'}))
            team=TeamPlayer(a,b,'shared_buffer',rec,4)
            history=[]
            for i in range(6):
                control='This is the mandatory last turn.' if i==5 else 'ordinary'
                team.complete('player',json.dumps({'opening':'PUBLIC','visible_history':history,'turn_control':control}))
                history.append({'type':'question','text':f'Q{i+1}','feedback':'no'})
            payloads=[json.loads(x[1]) for x in b.inputs]
            self.assertEqual(payloads[0]['visible_history'],[])
            self.assertEqual(payloads[0]['unpublished_questions'],[{'submission':1,'text':'Q1'}])
            self.assertNotIn('feedback',str(payloads[0]['unpublished_questions']))
            self.assertEqual(payloads[2]['unpublished_questions'],[])
            self.assertEqual([x['text'] for x in payloads[1]['visible_history']],['Q2'])
            self.assertEqual(len(payloads[2]['visible_history']),5)
            ap=[json.loads(x[1]) for x in a.inputs]
            self.assertEqual([x['text'] for x in ap[1]['visible_history']],['Q1'])
            self.assertEqual(len(ap[2]['shared_buffer']['entries']),4)
            self.assertNotEqual(ap[0]['exploration_role'],payloads[0]['exploration_role'])
            self.assertNotIn('SECRET',json.dumps(ap)+json.dumps(payloads))
            self.assertEqual(len(a.inputs)+len(b.inputs),6)

    def test_superseded_renderer_does_not_report_running(self):
        from scripts.render_trajectories import collect
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);game=root/'game';game.mkdir()
            (game/'trajectory.jsonl').write_text('{"event":"start"}\n')
            (game/'result.json').write_text('{"status":"running","success":null}')
            (game/'superseded.json').write_text('{"reason":"handoff"}')
            self.assertEqual(collect(root)[0]['result']['status'],'superseded')
            self.assertEqual(json.loads((game/'result.json').read_text())['status'],'running')

    def test_invalid_interval(self):
        with self.assertRaises(ValueError):TeamPlayer(None,None,'shared_buffer',None,0)
