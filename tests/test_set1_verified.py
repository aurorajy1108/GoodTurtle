import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.run_set1_verified import prepare, execute
from scripts.check_host import main as check_host
from turtle_loop.costs import cost_summary
from turtle_loop.providers import Reply

ROOT=Path(__file__).resolve().parents[1]


class Set1VerifiedTests(unittest.TestCase):
    def test_host_changes_preserve_original_human_labels_and_record_ai_provenance(self):
        added=[]
        for pid in ('TS013','TS014'):
            before=json.loads((ROOT/f'data/host_packs/archive/20261110_before_v11/{pid}.json').read_text())
            after=json.loads((ROOT/f'data/host_packs/active/{pid}.json').read_text())
            self.assertEqual(after['host_examples'][:len(before['host_examples'])],before['host_examples'])
            self.assertEqual(after['solution'],before['solution'])
            added.extend(after['host_examples'][len(before['host_examples']):])
        self.assertEqual(len(added),26)
        self.assertTrue(all(e['provenance']['human_confirmed'] is False for e in added))

    def test_frozen_plan_has_only_three_sources_and_fresh_target_conditions(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'run'
            manifest=prepare(out,ROOT/'configs/loop.deepseek.json',
                             ROOT/'data/annotations/turtle50_v4/private.json',20261102)
            self.assertEqual(manifest['planned_games'],12)
            self.assertEqual(manifest['repeat'],1)
            self.assertEqual(manifest['planned_host_checks'],20)
            self.assertFalse(manifest['old_trajectories_reused'])
            self.assertEqual(manifest['source_puzzles'],['TS015','TS014','TS028'])
            plan=json.loads((out/'study/study_plan.json').read_text())
            self.assertTrue(all(b['target']=='TS013' for b in plan['blocks']['continual']))
            self.assertTrue(all(set(b['conditions'])=={'direct','session','answer_only'}
                                for b in plan['blocks']['continual']))
            self.assertEqual(plan['config']['player']['extra_body']['thinking']['type'],'disabled')

    def test_failed_host_gate_prevents_paid_cl_and_retains_costs(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'run'
            manifest=prepare(out,ROOT/'configs/loop.deepseek.json',
                             ROOT/'data/annotations/turtle50_v4/private.json',1)
            class Child:
                pid=123
                def wait(self):return 1
            def popen(argv,**kwargs):
                gate=out/'host_gate';gate.mkdir()
                (gate/'cost_summary.json').write_text(json.dumps(cost_summary([])))
                return Child()
            with patch('scripts.run_set1_verified.subprocess.Popen',side_effect=popen) as started:
                self.assertEqual(execute(out,manifest),1)
            self.assertEqual(started.call_count,1)
            self.assertEqual(json.loads((out/'status.json').read_text())['status'],'stopped_on_host_gate')
            self.assertTrue((out/'cost_summary.json').exists())
            self.assertFalse((out/'study/continual').exists())

    def test_passed_gate_runs_exactly_one_cl_job_and_counts_completed_games(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'run'
            manifest=prepare(out,ROOT/'configs/loop.deepseek.json',
                             ROOT/'data/annotations/turtle50_v4/private.json',1)
            class Child:
                pid=123
                def wait(self):return 0
            def popen(argv,**kwargs):
                if '--cases' in argv:
                    gate=out/'host_gate';gate.mkdir()
                    (gate/'summary.json').write_text(json.dumps({'completed_calls':20,'passed':20,'errors':0}))
                    (gate/'cost_summary.json').write_text(json.dumps(cost_summary([])))
                else:
                    folder=out/'study/continual';folder.mkdir()
                    rows=[{'run_dir':f'fixture_{i}','status':'completed','costs':cost_summary([])} for i in range(12)]
                    (folder/'experiment_runs.json').write_text(json.dumps(rows))
                return Child()
            with patch('scripts.run_set1_verified.subprocess.Popen',side_effect=popen) as started:
                self.assertEqual(execute(out,manifest),0)
            self.assertEqual(started.call_count,2)
            state=json.loads((out/'status.json').read_text())
            self.assertTrue(state['host_gate_passed'])
            self.assertEqual(state['completed_games'],12)
            self.assertEqual(state['status'],'completed')

    def test_mutated_snapshot_rejected_before_any_model_process(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'run'
            manifest=prepare(out,ROOT/'configs/loop.deepseek.json',
                             ROOT/'data/annotations/turtle50_v4/private.json',1)
            (out/'study/runtime_snapshot/prompts/loop_host_v1.txt').write_text('modified')
            with patch('scripts.run_set1_verified.subprocess.Popen') as started:
                with self.assertRaisesRegex(ValueError,'Frozen input changed'):
                    execute(out,manifest)
                started.assert_not_called()

    def test_diagnostic_uses_persistent_host_only_hides_expected_and_records_tokens(self):
        calls=[];clients=[]
        class Host:
            def __init__(self,profile,role,audit):
                self.audit=audit;clients.append(self);self.opened=False;self.closed=False
            def begin_game(self,*args):self.opened=True
            def close_game(self):self.closed=True
            def complete(self,system,user):
                payload=json.loads(user);calls.append(copy.deepcopy(payload))
                self.audit({'role':'host','provider':'deepseek','model_requested':'fixture',
                            'model_returned':'fixture','status':'ok',
                            'usage':{'prompt_tokens':100,'completion_tokens':1,'total_tokens':101}})
                return Reply('yes',{})
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);cases=root/'cases.json'
            cases.write_text(json.dumps([{'id':'fixture','puzzle_id':'TS013',
                                        'question':'Are the courses meal dishes?','expected':'yes'}]))
            with patch('scripts.check_host.Client',Host):
                self.assertEqual(check_host(['--dataset',str(ROOT/'data/annotations/turtle50_v4/private.json'),
                    '--config',str(ROOT/'configs/loop.deepseek.json'),'--cases',str(cases),
                    '--out',str(root/'gate')]),0)
            self.assertTrue(clients[0].opened and clients[0].closed)
            self.assertEqual(set(calls[0]),{'active_puzzle','visible_history','current_question'})
            self.assertNotIn('expected',calls[0])
            costs=json.loads((root/'gate/cost_summary.json').read_text())['total']
            self.assertEqual(costs['tokens']['total_tokens'],101)
            self.assertIsNone(costs['estimated_cost_usd'])
            self.assertEqual(costs['unknown_cost_calls'],1)
