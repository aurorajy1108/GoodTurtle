import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.compute_matched_agents import prepare,extend,CONDITIONS
from turtle_loop.engine import dump


class ComputeExtensionTests(unittest.TestCase):
    def completed_fixture(self,root):
        source=root/'source';plan=prepare(None,source)
        for spec in plan['jobs']:
            game=source/spec['run_dir'];game.mkdir()
            dump(game/'result.json',{'status':'completed','simulation':False,'success':False,
                 'submissions':100,'final_partial_score':0.5})
            for name in ('config.json','prompts.json','puzzle_private.json'):dump(game/name,{'fixture':spec['run_dir']})
            (game/'api_calls.jsonl').write_text('');(game/'trajectory.jsonl').write_text('')
        dump(source/'status.json',{'status':'completed','active':{}})
        return source,plan

    @patch('urllib.request.OpenerDirector.open',side_effect=AssertionError('Extension must not call API'))
    def test_append_only_two_repeats_preserves_old_results_and_frozen_role_inputs(self,api):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source,old=self.completed_fixture(root);out=root/'extended'
            inputs=(source/'runtime_snapshot/configs/compute_agents_inputs.json').read_bytes()
            plan=extend(source,out,4)
            self.assertEqual(plan['planned_games'],16);self.assertEqual(plan['new_repeat_ids'],[3,4])
            self.assertEqual((out/'runtime_snapshot/configs/compute_agents_inputs.json').read_bytes(),inputs)
            for c in CONDITIONS:self.assertEqual(sorted(s['repeat'] for s in plan['jobs'] if s['condition']==c),[1,2,3,4])
            for spec in old['jobs']:
                for name in ('result.json','api_calls.jsonl','trajectory.jsonl','config.json','prompts.json','puzzle_private.json'):
                    self.assertEqual((source/spec['run_dir']/name).read_bytes(),(out/spec['run_dir']/name).read_bytes())
            for spec in plan['jobs']:
                if spec['repeat']>2:self.assertFalse((out/spec['run_dir']).exists())
            status=json.loads((out/'status.json').read_text());self.assertEqual(status['completed_games'],8)
            performance=json.loads((out/'performance.json').read_text())
            self.assertTrue(all(c['expected']==4 and c['completed']==2 for c in performance['conditions']))

    def test_refuses_incomplete_simulated_or_nonadditional_extensions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source,old=self.completed_fixture(root)
            with self.assertRaises(ValueError):extend(source,root/'no_new_repeats',2)
            dump(source/'status.json',{'status':'running','active':{'job':123}})
            with self.assertRaises(ValueError):extend(source,root/'running',4)
            dump(source/'status.json',{'status':'completed','active':{}})
            dump(source/old['jobs'][0]['run_dir']/'result.json',{'status':'completed','simulation':True})
            with self.assertRaises(ValueError):extend(source,root/'simulated',4)
            self.assertFalse((root/'simulated').exists())
