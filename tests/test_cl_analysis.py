import json
from pathlib import Path
import tempfile
import unittest

from scripts.analyze_cl_results import analyze


class CLAnalysisTests(unittest.TestCase):
    def test_incomplete_conditions_do_not_enter_paired_means_or_become_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            batch=Path(tmp)/'continual';batch.mkdir()
            blocks=[{'block':f'G_r{i}','source':'A','target':'B','repeat':i,
                     'conditions':['direct','answer_only','session']} for i in range(1,5)]
            (batch/'plan.json').write_text(json.dumps({'blocks':blocks}))
            rows=[]
            for i in (1,2,3):
                for c in ('direct','answer_only','session'):
                    if i==3 and c=='session':continue
                    name=f'G_r{i}_{c}'
                    score={1:{'direct':.2,'answer_only':.5,'session':.6},
                           2:{'direct':.4,'answer_only':.7,'session':.2},
                           3:{'direct':.9,'answer_only':.8}}[i][c]
                    rows.append({'run_dir':name,'source':'A','target':'B','repeat':i,'condition':c,
                        'status':'running' if i==3 and c=='answer_only' else 'completed',
                        'final_partial_score':score,'submissions':100,'success':False})
            (batch/'experiment_runs.json').write_text(json.dumps(rows))
            result=analyze(Path(tmp))
            self.assertEqual(result['planned_target_games'],12)
            self.assertEqual(result['completed_target_games'],7)
            self.assertEqual(result['global_balanced_repeats'],[1,2])
            self.assertAlmostEqual(result['by_source'][0]['scores']['direct']['mean'],.3)
            self.assertAlmostEqual(result['by_source'][0]['contrasts_to_direct']['session']['mean'],.1)
            self.assertEqual(sum(r['status']=='planned' for r in result['runs']),4)

    def test_duplicate_rollout_cannot_be_counted_twice(self):
        with tempfile.TemporaryDirectory() as tmp:
            batch=Path(tmp)/'continual';batch.mkdir()
            (batch/'plan.json').write_text(json.dumps({'blocks':[]}))
            row={'run_dir':'duplicate','condition':'direct'}
            (batch/'experiment_runs.json').write_text(json.dumps([row,row]))
            with self.assertRaisesRegex(ValueError,'Duplicate rollout'):analyze(tmp)
