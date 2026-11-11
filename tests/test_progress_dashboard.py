import json
import tempfile
import unittest
from pathlib import Path

from scripts.watch_progress import collect, read_events


class ProgressDashboardTests(unittest.TestCase):
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
