import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.auto_continue import run, resolve_source


class AutoContinueTests(unittest.TestCase):
    def test_stopped_supervisor_selects_latest_existing_checkpoint_not_failed_prepare(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'supervisor';root.mkdir()
            good=root/'continuation_01';self.stopped(good)
            status={'status':'requires_attention','attempts':[{'out':str(good)},{'out':str(root/'continuation_02')}]}
            (root/'status.json').write_text(json.dumps(status))
            self.assertEqual(resolve_source(root),good.resolve())
            status['status']='running';(root/'status.json').write_text(json.dumps(status))
            with self.assertRaises(ValueError):resolve_source(root)

    def stopped(self,path,identity='r61',submissions=60):
        path.mkdir(parents=True)
        (path/'status.json').write_text(json.dumps({'status':'stopped_on_error'}))
        (path/'study_plan.json').write_text(json.dumps({'jobs':[{'name':'continual'}]}))
        batch=path/'continual';batch.mkdir()
        (batch/'experiment_runs.json').write_text(json.dumps([
            {'run_dir':'source','status':'completed'}, {'run_dir':'target','status':'error'}]))
        game=batch/'target';game.mkdir()
        (game/'result.json').write_text(json.dumps({'status':'error','stop_reason':'ProtocolError',
            'pending_feedback':0,'submissions':submissions}))
        (game/'api_calls.jsonl').write_text(json.dumps({'role':'player','status':'ok','finish_reason':'stop',
            'response_id':identity,'text':'bad output '+identity})+'\n')

    def test_new_format_failure_continues_and_latest_cost_is_not_summed_twice(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'source';out=Path(tmp)/'auto';self.stopped(source)
            calls=[]
            def resume(argv):
                calls.append(argv);dest=Path(argv[argv.index('--out')+1])
                if len(calls)==1:self.stopped(dest,'r75',74)
                else:dest.mkdir()
                (dest/'cost_summary.json').write_text(json.dumps({'total':{'calls':100+len(calls)}}))
                return 1 if len(calls)==1 else 0
            with patch('scripts.auto_continue.resume_main',side_effect=resume):
                self.assertEqual(run(source,out,3,'run'),0)
            self.assertEqual(len(calls),2)
            self.assertIn('--auto-player-format',calls[0])
            self.assertEqual(calls[1][calls[1].index('--from-study')+1],str((out/'continuation_01').resolve()))
            self.assertEqual(json.loads((out/'cost_summary.json').read_text())['total']['calls'],102)
            self.assertEqual(json.loads((out/'status.json').read_text())['status'],'completed')

    def test_same_saved_reply_is_never_repaired_over_and_over(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'source';out=Path(tmp)/'auto';self.stopped(source)
            def resume(argv):
                self.stopped(Path(argv[argv.index('--out')+1]));return 1
            with patch('scripts.auto_continue.resume_main',side_effect=resume) as called:
                self.assertEqual(run(source,out,3,'run'),1)
            self.assertEqual(called.call_count,1)
            state=json.loads((out/'status.json').read_text())
            self.assertEqual(state['status'],'requires_attention')
            self.assertIn('Same failed reply',state['error'])

    def test_continuation_limit_bounds_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'source';out=Path(tmp)/'auto';self.stopped(source)
            def resume(argv):self.stopped(Path(argv[argv.index('--out')+1]),'r62',61);return 1
            with patch('scripts.auto_continue.resume_main',side_effect=resume) as called:
                self.assertEqual(run(source,out,1,'run'),1)
            self.assertEqual(called.call_count,1)
            self.assertEqual(json.loads((out/'status.json').read_text())['status'],'recovery_limit_reached')
