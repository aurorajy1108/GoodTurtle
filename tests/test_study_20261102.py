import argparse
import json
import tempfile
import unittest
from pathlib import Path
from scripts.study_20261102 import groups, SETS, OWNERS
from turtle_loop.experiments import make_plan, planned_games


class StudyPlanTests(unittest.TestCase):
    def test_directions_relation_labels_and_counts(self):
        g=groups(list(SETS))['groups'];self.assertEqual(len(g),17)
        self.assertTrue(all(e['anchor']==e['directed_pairs'][0][1] and e['analysis_role']=='primary' for e in g))
        exploratory=groups(list(SETS),'bidirectional')['groups']
        self.assertEqual(len(exploratory),24)
        self.assertEqual(sum(e['analysis_role']=='exploratory' for e in exploratory),7)
        for e in g:
            spec=SETS[e['set_id']];a,b=e['directed_pairs'][0]
            self.assertIn(int(b[2:]),[spec['anchor']]+spec['positive'])
            if e['relation']!='positive':self.assertEqual(b,e['anchor'])
        self.assertEqual({tuple(e['directed_pairs'][0]) for e in groups([1])['groups']},
            {('TS015','TS013'),('TS016','TS013'),('TS014','TS013'),('TS028','TS013')})
        self.assertEqual(set(OWNERS),{'TS038','TS002','TS014','TS022','TS042'})

    def test_planner_never_expands_forbidden_reverse_pairs(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder,'groups.json');p.write_text(json.dumps(groups(list(SETS))))
            args=argparse.Namespace(command='continual',groups=str(p),group='all',pair=None,controls='answer_only',
              control_source=None,source_feedback='answer',memory='transcript',repeat=3,seed=1)
            bank={f'TS{n:03d}':{} for n in range(1,51)}
            blocks=make_plan(args,bank)
            self.assertEqual(len(blocks),51)
            self.assertEqual(planned_games(blocks,'continual'),168)
            self.assertEqual(planned_games(blocks,'continual','per-repeat'),204)
            self.assertTrue(all(set(b['conditions'])=={'direct','transcript','answer_only'} for b in blocks))
            self.assertFalse(any(b['source']=='TS013' and b['target']=='TS014' for b in blocks))
            d=groups([1]);d['groups'][0]['directed_pairs']=[['TS015','TS015']];p.write_text(json.dumps(d))
            with self.assertRaises(ValueError):make_plan(args,bank)
