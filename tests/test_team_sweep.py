"""Offline integration checks for frozen, nested multi-condition sweeps."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts import team_sweep
from scripts.render_trajectories import collect


class SweepTests(unittest.TestCase):
    def test_snapshot_dry_run_uses_its_own_package_and_records_every_condition(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            puzzle = {'id': 'AUDIT_FIXTURE', 'opening': 'Why did A pick up an umbrella?',
                      'answer': 'To retrieve a bag from a high shelf.',
                      'rubric': [{'id': 'C1', 'weight': 1, 'criterion': 'Reach the bag.'}]}
            dataset = root / 'dataset.json'
            dataset.write_text(json.dumps({'schema_version': 1, 'puzzles': [puzzle]}))
            config = root / 'config.json'
            config.write_text(json.dumps({'max_questions': 3,
                'host': {'provider': 'openai', 'model': 'offline-fixture'},
                'player': {'provider': 'openai', 'model': 'offline-fixture'}}))
            out = root / 'sweep'
            partner = root / 'partner.json'
            partner.write_text(json.dumps({'provider': 'deepseek', 'model': 'offline-partner'}))
            code = team_sweep.main(['--dataset', str(dataset), '--config', str(config),
                '--partner-config', str(partner),
                '--puzzles', 'AUDIT_FIXTURE', '--strategies', 'solo,independent',
                '--repeat', '2', '--workers', '1', '--poll-seconds', '1',
                '--dry-run', '--out', str(out)])
            self.assertEqual(code, 0)
            progress = json.loads((out / 'progress.json').read_text())
            self.assertEqual(progress['planned_games'], 4)
            self.assertEqual(progress['recorded_games'], 4)
            self.assertEqual({r['status'] for r in progress['statuses']}, {'dry_run'})
            self.assertEqual(len(collect(out)), 4)
            self.assertFalse(list(out.rglob('api_calls.jsonl')))
            snapshot = (out / 'runtime_snapshot').resolve()
            self.assertTrue((snapshot / 'turtle_loop/engine.py').exists())
            plan = json.loads((out / 'batches/AUDIT_FIXTURE/plan.json').read_text())
            self.assertEqual(Path(plan['arguments']['dataset']), snapshot / 'data/dataset.json')
            self.assertEqual(Path(plan['arguments']['config']), snapshot / 'configs/run.json')
            self.assertEqual(Path(plan['arguments']['partner_config']), snapshot / 'configs/partner.json')
            self.assertEqual(plan['partner']['model'], 'offline-partner')
            self.assertTrue((out / 'trajectories.html').exists())

    def test_completed_subset_must_not_pass_full_sweep_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'snapshot_hashes.json').write_text('{}')
            (root / 'sweep.json').write_text(json.dumps({'planned_games': 2,
                'repeat': 1, 'strategies': ['solo', 'independent'],
                'jobs': [{'puzzle_id': 'FIXTURE'}], 'dry_run': False}))
            batch = root / 'batches/FIXTURE'
            game = batch / 'FIXTURE_r01_solo'
            game.mkdir(parents=True)
            (batch / 'plan.json').write_text(json.dumps({'blocks': [{
                'block': 'FIXTURE_r01', 'target': 'FIXTURE', 'repeat': 1,
                'conditions': ['solo', 'independent']}]}))
            (game / 'result.json').write_text(json.dumps({'status': 'completed',
                'counted_questions': 1, 'host_questions': 1, 'rejected_finals': 0,
                'submissions': 2, 'pending_feedback': 0}))
            team_sweep.validate_finished(root)
            self.assertFalse(json.loads((root / 'validation.json').read_text())['passed'])

    def test_nested_renderer_excludes_snapshot_copies(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in ('batches/FIXTURE/game', 'runtime_snapshot/copied_game'):
                folder = root / relative
                folder.mkdir(parents=True)
                (folder / 'trajectory.jsonl').write_text('{"event":"start"}\n')
                (folder / 'puzzle_private.json').write_text('{"id":"FIXTURE"}')
            self.assertEqual([g['name'] for g in collect(root)], ['batches/FIXTURE/game'])


if __name__ == '__main__':
    unittest.main()
