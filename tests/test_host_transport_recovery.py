"""Offline tests: a transport interruption must not regenerate a paid player action."""
import copy
import json
import ssl
import tempfile
import unittest
import urllib.error
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from turtle_loop.engine import Recorder, load_prompts, play, saved_host_transport_recovery
from turtle_loop.providers import Client
from test_loop import PUZZLE, evaluated


class Response:
    def __init__(self, text, rid):
        self.data = {'id': rid, 'model': 'fixture', 'choices': [
            {'message': {'content': text}, 'finish_reason': 'stop'}]}

    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self): return json.dumps(self.data).encode()


@patch.dict('os.environ', {'DEEPSEEK_API_KEY': 'fixture'})
class HostTransportRecoveryTests(unittest.TestCase):
    def interrupted(self, root):
        config = {'max_questions': 3, 'session_mode': 'persistent', **{
            r: {'provider': 'deepseek', 'model': 'fixture', 'max_retries': 0}
            for r in ('host', 'player', 'grader')}}
        prompts = load_prompts()
        rec = Recorder(root/'game', PUZZLE, config, prompts, echo=False)
        clients = {r: Client(config[r], r, rec.audit) for r in ('host', 'player', 'grader')}
        requests = {r: [] for r in clients}
        def serve(role):
            def answer(req, **kwargs):
                requests[role].append(json.loads(req.data))
                n = len(requests[role])
                if role == 'host' and n == 2:
                    raise urllib.error.URLError(ssl.SSLError(1, 'fixture TLS failure'))
                text = json.dumps({'type': 'question', 'text': f'Question {n}?'}) if role == 'player' else 'yes'
                return Response(text, f'{role}-{n}')
            return answer
        with ExitStack() as stack:
            for role, client in clients.items():
                stack.enter_context(patch.object(client.opener, 'open', side_effect=serve(role)))
            result = play(PUZZLE, config, rec, clients, prompts)
        self.assertEqual(result['status'], 'error')
        self.assertEqual((result['submissions'], result['pending_feedback']), (2, 1))
        rec.calls = [json.loads(line) for line in (rec.folder/'api_calls.jsonl').read_text().splitlines()]
        return config, prompts, rec, result, requests

    def test_exact_request_replayed_before_next_player_and_failed_cost_retained(self):
        with tempfile.TemporaryDirectory() as tmp:
            config, prompts, rec, result, original = self.interrupted(Path(tmp))
            with self.assertRaisesRegex(ValueError, 'Persistent interrupted'):
                Recorder.restore(rec.folder, PUZZLE, config, prompts, echo=False)
            recovery = saved_host_transport_recovery(result, rec.calls, rec.turns, config)
            self.assertTrue(recovery['possible_duplicate_remote_charge'])
            marker = rec.folder/'host_transport_recovery.json'
            marker.write_text(json.dumps(recovery))
            restored = Recorder.restore(rec.folder, PUZZLE, config, prompts, echo=False)
            clients = {r: Client(config[r], r, restored.audit) for r in ('host', 'player', 'grader')}
            order, retried = [], []
            def serve(role):
                def answer(req, **kwargs):
                    body = json.loads(req.data); order.append(role)
                    if role == 'host':
                        retried.append(body)
                        return Response('no', 'host-2-retry')
                    if role == 'player':
                        # Both earlier actions are preserved in this same role session.
                        self.assertEqual(len(body['messages']), 6)
                        return Response(json.dumps({'type': 'final', 'text': 'submitted explanation'}), 'player-3')
                    return Response(evaluated(), 'grader-1')
                return answer
            with ExitStack() as stack:
                for role, client in clients.items():
                    stack.enter_context(patch.object(client.opener, 'open', side_effect=serve(role)))
                final = play(PUZZLE, config, restored, clients, prompts)
            self.assertEqual(order, ['host', 'player', 'grader'])
            self.assertEqual(retried[0], original['host'][-1])
            self.assertEqual((final['submissions'], final['counted_questions']), (3, 2))
            self.assertTrue(final['success'])
            self.assertEqual(sum(c['status'] == 'transport_error' for c in restored.calls), 1)
            self.assertFalse(marker.exists())

    def test_reject_observed_responses_tampered_chain_wrong_question_or_role(self):
        with tempfile.TemporaryDirectory() as tmp:
            config, _, rec, result, _ = self.interrupted(Path(tmp))
            self.assertIsNotNone(saved_host_transport_recovery(result, rec.calls, rec.turns, config))
            for change in ('observed', 'previous_id', 'message', 'question', 'wrong_role', 'prior_failure'):
                calls, turns = copy.deepcopy(rec.calls), copy.deepcopy(rec.turns)
                if change == 'observed': calls[-1]['text'] = 'no'
                elif change == 'previous_id': calls[-1]['previous_response_id'] = 'wrong'
                elif change == 'message': calls[-1]['request']['messages'][1]['content'] = '{}'
                elif change == 'question': turns[-1]['text'] = 'different?'
                elif change == 'wrong_role': calls[-1]['role'] = 'player'
                else: calls[0]['status'] = 'transport_error'
                self.assertIsNone(saved_host_transport_recovery(result, calls, turns, config), change)

    def test_reject_tampered_opt_in_and_request_before_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            config, prompts, rec, result, _ = self.interrupted(Path(tmp))
            marker = rec.folder/'host_transport_recovery.json'
            marker.write_text('{}')
            with self.assertRaisesRegex(ValueError, 'does not match'):
                Recorder.restore(rec.folder, PUZZLE, config, prompts, echo=False)
            client = Client(config['host'], 'host', lambda call: None)
            client.begin_game(tmp, lambda *a, **k: None)
            client.expected_recovery_request = {'tampered': True}
            try:
                with patch.object(client.opener, 'open') as opened:
                    with self.assertRaisesRegex(ValueError, 'differs from the saved'):
                        client.complete('host', '{}')
                    opened.assert_not_called()
            finally:
                client.close_game()
