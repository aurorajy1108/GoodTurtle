import json
import tempfile
import unittest
from pathlib import Path

from scripts.watch_progress import collect, read_events
from scripts.serve_progress import artifact_path


class ProgressDashboardTests(unittest.TestCase):
    def test_formal_b_slot_shows_global_repeats_before_results_are_written(self):
        with tempfile.TemporaryDirectory() as directory:
            batch = Path(directory)/'tasks/mas-ts038-b/team'
            game = batch/'TS038_r01_solo'
            game.mkdir(parents=True)
            (batch.parent/'assignment.json').write_text(json.dumps({
                'preset':'full','runner':'april','repeat':2,'repeat_offset':2}))
            (batch/'plan.json').write_text(json.dumps({'kind':'team','blocks':[
                {'block':f'TS038_r{n:02d}','target':'TS038','repeat':n,
                 'conditions':['solo','free_dialogue']} for n in (1,2)]}))
            (game/'trajectory.jsonl').write_text('{"event":"start","puzzle_id":"TS038"}\n')
            rows = collect([(batch,'/runs/0')])['games']
            self.assertEqual(len(rows),4)
            self.assertEqual({(r['condition'],r['global_repeat']) for r in rows},
                             {('solo',3),('free_dialogue',3),('solo',4),('free_dialogue',4)})
            self.assertEqual(rows[0]['global_repeat'],3)
            self.assertTrue(all(r['runner']=='april' and r['preset']=='full' for r in rows))

    def test_team_plan_keeps_unstarted_baseline_and_public_agent_activity(self):
        with tempfile.TemporaryDirectory() as directory:
            batch = Path(directory)/'smoke/team'
            game = batch/'TS038_r01_free_dialogue'
            game.mkdir(parents=True)
            (batch/'plan.json').write_text(json.dumps({'kind':'team', 'blocks':[
                {'block':'TS038_r01','target':'TS038','conditions':['free_dialogue','solo']}]}))
            (batch.parent/'status.json').write_text('{"status":"stopped_on_error"}')
            (game/'trajectory.jsonl').write_text('{"event":"start","puzzle_id":"TS038"}\n')
            (game/'result.json').write_text('{"status":"error"}')
            (game/'shared_dialogue.jsonl').write_text(json.dumps({
                'speaker':'A','type':'discuss','text':'Public hypothesis','effective_next_speaker':'B',
                'private':'MUST_NOT_LEAK'})+'\n')
            rows = collect([(batch,'/runs/0')])['games']
            self.assertEqual(len(rows), 2)
            active, baseline = rows
            self.assertEqual(active['condition'], 'free_dialogue')
            self.assertEqual(active['actor_messages'], {'A':1,'B':0})
            self.assertEqual((active['current_actor'],active['internal_messages']), ('B',1))
            self.assertNotIn('MUST_NOT_LEAK',json.dumps(active))
            self.assertEqual((baseline['puzzle_id'],baseline['condition'],baseline['status']),
                             ('TS038','solo','not_started'))
            self.assertTrue(baseline['blocked'])
            self.assertIsNone(baseline['score'])

    def test_local_server_only_serves_artifacts_inside_its_selected_batch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            batch = root/'team'
            batch.mkdir()
            (batch/'result.json').write_text('{}')
            (root/'.env').write_text('PRIVATE')
            (batch/'escape.json').symlink_to(root/'.env')
            mounts = [(batch,'/runs/0')]
            self.assertEqual(artifact_path(mounts,'/runs/0/result.json'),(batch/'result.json').resolve())
            for path in ('/.env','/runs/0/../.env','/runs/0/%2e%2e/.env',
                         '/runs/0/escape.json','/runs/4/result.json'):
                self.assertIsNone(artifact_path(mounts,path))

    def test_live_events_update_without_a_new_result_and_zero_score_is_real(self):
        with tempfile.TemporaryDirectory() as directory:
            batch = Path(directory)/'batch/web/run'
            game = batch/'TS034_r01'
            game.mkdir(parents=True)
            (game/'config.json').write_text(json.dumps({'max_questions': 100}))
            (game/'result.json').write_text(json.dumps({'status': 'running', 'submissions': 0}))
            path = game/'trajectory.jsonl'
            events = [{'event': 'start', 'puzzle_id': 'TS034', 'budget': 100},
                      {'event': 'submission', 'index': 1, 'type': 'question', 'text': '<script>unsafe</script>'}]
            path.write_text(''.join(json.dumps(e)+'\n' for e in events))
            first = collect([(batch, '/retry')])['games'][0]
            self.assertEqual(first['submissions'], 1)
            self.assertEqual(first['pending_feedback'], 1)
            self.assertIsNone(first['score'])
            with path.open('a') as stream:
                for event in [{'event': 'host_feedback', 'submission': 1, 'label': 'no'},
                              {'event': 'submission', 'index': 2, 'type': 'final', 'text': 'Answer'},
                              {'event': 'evaluation', 'submission': 2, 'partial_score': 0, 'label': 'no'}]:
                    stream.write(json.dumps(event)+'\n')
                stream.write('{"event":')
            second = collect([(batch, '/retry')])['games'][0]
            self.assertEqual(second['submissions'], 2)
            self.assertEqual(second['pending_feedback'], 0)
            self.assertEqual(second['score'], 0)
            self.assertEqual(second['scores'], [{'submission': 2, 'score': 0}])
            self.assertEqual(second['links']['result'], '/retry/TS034_r01/result.json')
            self.assertEqual(second['turns'][0]['text'], '<script>unsafe</script>')

    def test_empty_provider_response_error_and_usage_are_visible_without_raw_request(self):
        with tempfile.TemporaryDirectory() as directory:
            batch = Path(directory)/'batch/web/run'
            game = batch/'TS034_r01'
            game.mkdir(parents=True)
            (game/'trajectory.jsonl').write_text('{"event":"start","puzzle_id":"TS034"}\n')
            (game/'result.json').write_text(json.dumps({'status': 'error', 'error': 'invalid response'}))
            call = {'role': 'player', 'status': 'ok', 'text': '  \n',
                    'request': {'private': 'PRIVATE_REQUEST'}, 'usage': {'total_tokens': 1125}}
            (game/'api_calls.jsonl').write_text(json.dumps(call)+'\n')
            data = collect([(batch, '/run')])['games'][0]
            self.assertIn('空白文本', data['error'])
            self.assertIsNone(data['score'])
            self.assertIsNone(data['cost_usd'])
            self.assertEqual(data['total_tokens'], 1125)
            self.assertEqual(data['successful_calls'], 1)
            self.assertNotIn('PRIVATE_REQUEST', json.dumps(data))

    def test_no_started_game_or_missing_log(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(collect([(Path(directory), '/run')])['games'], [])
            self.assertEqual(read_events(Path(directory)/'missing'), [])

    def test_study_games_report_their_actual_condition_and_source(self):
        with tempfile.TemporaryDirectory() as directory:
            batch = Path(directory)/'round/continual'
            game = batch/'S2_TS033_TS034_r01_session'
            game.mkdir(parents=True)
            (game/'trajectory.jsonl').write_text('{"event":"start","puzzle_id":"TS034"}\n')
            (batch/'experiment_runs.json').write_text(json.dumps([{
                'run_dir':game.name,'condition':'session','source':'TS033'}]))
            row = collect([(batch,'/round')])['games'][0]
            self.assertEqual((row['puzzle_id'],row['condition'],row['source_puzzle']),
                             ('TS034','session','TS033'))
            self.assertEqual(row['batch'],'round')
