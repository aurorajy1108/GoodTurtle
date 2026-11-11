"""Offline fixtures only: never invoke a model or run a dataset experiment."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from turtle_loop.experiments import main
from turtle_loop.providers import APIError
from test_loop import PUZZLE, FakeClient, evaluated


class FixedSourceTests(unittest.TestCase):
    def run_fixture(self, root, policy='fixed', source_error=False, source_unsolved=False):
        puzzles=[]
        for pid in ('FIXTURE_A','FIXTURE_B','FIXTURE_C'):
            puzzle=copy.deepcopy(PUZZLE)
            puzzle.update(id=pid,opening='PUBLIC_'+pid,answer='PRIVATE_'+pid)
            puzzles.append(puzzle)
        (root/'data.json').write_text(json.dumps({'schema_version':1,'puzzles':puzzles}))
        (root/'config.json').write_text(json.dumps({'max_questions':100,
            'host':{'provider':'openai','model':'fixture'},'player':{'provider':'openai','model':'fixture'}}))
        (root/'groups.json').write_text(json.dumps({'groups':[
            {'id':'G'+p,'puzzles':['FIXTURE_A',p],'directed_pairs':[['FIXTURE_A',p]],
             'relation':'positive','analysis_role':'primary'} for p in ('FIXTURE_B','FIXTURE_C')]}))
        seen=[]
        def factory(profile,role,audit):
            def answer(i,payload):
                if role=='player':
                    seen.append(copy.deepcopy(payload))
                    if source_error and payload['opening']=='PUBLIC_FIXTURE_A':
                        raise APIError('fixture failure')
                    return json.dumps({'type':'final','text':'PUBLIC_GUESS'})
                if source_unsolved and role=='grader' and payload['opening']=='PUBLIC_FIXTURE_A':
                    # A exhausts the full 100; B must receive a fresh quota.
                    return evaluated((0,0))
                return evaluated()
            return FakeClient(answer)
        out=root/'out'
        argv=['continual','--dataset',str(root/'data.json'),'--config',str(root/'config.json'),
              '--groups',str(root/'groups.json'),'--group','all','--memory','transcript','--repeat','3',
              '--controls','answer_only','--on-error','continue','--out',str(out),'--quiet']
        if policy is not None:argv+=['--source-policy',policy]
        with patch('turtle_loop.cli.validate_profile'), patch('turtle_loop.experiments.Client',side_effect=factory):
            code=main(argv)
        return code,seen,out

    def test_default_freezes_a_across_repeats_and_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            code,seen,out=self.run_fixture(Path(tmp),policy=None)
            self.assertEqual(code,0)
            self.assertEqual(sum(x['opening']=='PUBLIC_FIXTURE_A' for x in seen),1)
            targets=[x for x in seen if x['opening']!='PUBLIC_FIXTURE_A']
            self.assertEqual(len(targets),18)
            self.assertTrue(all('Used question-equivalents: 0.' in x['turn_control'] for x in targets))
            self.assertTrue(all('Total limit: 100 submissions' in x['turn_control'] for x in targets))
            self.assertTrue(all(not x['visible_history'] for x in targets))
            histories=[x['prior_experience'] for x in targets if 'history' in x.get('prior_experience',{})]
            self.assertEqual(len(histories),6)
            self.assertTrue(all(x==histories[0] for x in histories))
            self.assertEqual(histories[0]['revealed_source_answer'],'PRIVATE_FIXTURE_A')
            self.assertEqual(sum('prior_experience' not in x for x in targets),6)
            self.assertNotIn('PRIVATE_FIXTURE_B',json.dumps(seen))
            self.assertNotIn('PRIVATE_FIXTURE_C',json.dumps(seen))
            self.assertNotIn('SECRET_',json.dumps(seen))
            reuse=json.loads((out/'source_reuse.json').read_text()).values()
            self.assertEqual(len({x['source_run_dir'] for x in reuse}),1)
            self.assertEqual(len({x['source_context_sha256'] for x in reuse}),1)
            rows=json.loads((out/'experiment_runs.json').read_text())
            self.assertEqual(len(rows),19)  # Costs count the A game once, not six times.
            contrasts=json.loads((out/'contrasts.json').read_text())
            self.assertTrue(all(x['source_success'] and x['valid_pair'] for x in contrasts))

    def test_explicit_per_repeat_regenerates_a(self):
        with tempfile.TemporaryDirectory() as tmp:
            code,seen,out=self.run_fixture(Path(tmp),policy='per-repeat')
            self.assertEqual(code,0)
            self.assertEqual(sum(x['opening']=='PUBLIC_FIXTURE_A' for x in seen),6)
            self.assertEqual(len(json.loads((out/'experiment_runs.json').read_text())),24)

    def test_failed_fixed_a_is_not_retried_or_replaced(self):
        with tempfile.TemporaryDirectory() as tmp:
            code,seen,out=self.run_fixture(Path(tmp),source_error=True)
            self.assertEqual(code,1)
            self.assertEqual(len(seen),1)
            self.assertEqual(len(list(out.glob('*_skipped.json'))),6)

    def test_unsolved_a_is_kept_and_revealed_without_spending_b_quota(self):
        with tempfile.TemporaryDirectory() as tmp:
            code,seen,out=self.run_fixture(Path(tmp),source_unsolved=True)
            self.assertEqual(code,0)
            self.assertEqual(sum(x['opening']=='PUBLIC_FIXTURE_A' for x in seen),100)
            targets=[x for x in seen if x['opening']!='PUBLIC_FIXTURE_A']
            self.assertTrue(all('Used question-equivalents: 0.' in x['turn_control'] for x in targets))
            histories=[x['prior_experience'] for x in targets if 'history' in x.get('prior_experience',{})]
            self.assertTrue(all(len(x['history'])==100 for x in histories))
            self.assertTrue(all(x['revealed_source_answer']=='PRIVATE_FIXTURE_A' for x in histories))
            rows=json.loads((out/'experiment_runs.json').read_text())
            sources=[r for r in rows if r['condition']=='source']
            self.assertEqual(len(sources),1)
            self.assertFalse(sources[0]['success'])
            self.assertEqual(sources[0]['counted_questions'],100)
