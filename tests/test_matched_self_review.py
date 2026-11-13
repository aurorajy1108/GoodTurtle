import json
from pathlib import Path
import ssl
import tempfile
import unittest
import urllib.error
from unittest.mock import patch

from turtle_loop.engine import Recorder, load_prompts, play, parse_action, ProtocolError
from turtle_loop.matched_self_review import (MatchedSelfReviewPlayer, extra_calls,
                                             solver_usage, submitted_review_actions,
                                             action_text, saved_action_recovery)
from turtle_loop.providers import Client, PreSendTLSFailure
from turtle_loop.sessions import restore_context
from turtle_loop.transport_recovery import saved_transport_recovery
from test_loop import PUZZLE, evaluated
from test_sessions import Response


@patch.dict('os.environ', {'DEEPSEEK_API_KEY': 'fixture'})
class MatchedSelfReviewTests(unittest.TestCase):
    def test_schedule_matches_both_reference_budgets_and_reserves_final(self):
        for cap in (139, 225):
            notes = [extra_calls(s, cap) for s in range(1, 101)]
            self.assertEqual(sum(notes)+100, cap)
            self.assertEqual(notes[-1], 0)
            self.assertLessEqual(max(notes), 2)

    def test_inline_normalization_preserves_question_and_rejects_ambiguous_actions(self):
        self.assertEqual(action_text('QUESTION Is this written?'), 'QUESTION\nIs this written?')
        self.assertEqual(action_text('FINAL A single explanation.', True), 'FINAL\nA single explanation.')
        for text in ['A question without a type?', 'QUESTION First?\nFINAL\nAnother action.', 'DISCUSS A thought']:
            with self.assertRaises(ProtocolError):
                action_text(text)

    def config(self):
        return {'max_questions': 4, 'session_mode': 'persistent', **{
            role: {'provider': 'deepseek', 'model': role, 'max_retries': 0,
                   'max_output_tokens': 8192, 'extra_body': {'thinking': {'type': 'disabled'}}}
            for role in ('player', 'host', 'grader')}}

    def clients(self, config, rec, budget):
        return {'player': MatchedSelfReviewPlayer(config['player'], rec, budget),
                **{r: Client(config[r], r, rec.audit) for r in ('host', 'grader')}}

    def api(self, fail=None, invalid=False, tokens=10, reject=False):
        self.seen, self.previous, self.failed = [], {}, False
        def request(req, **kw):
            body = json.loads(req.data)
            role = body['model']
            # Failure before accepting the request leaves the context unchanged.
            payload = restore_context(self.previous.get(role), body['messages'][-1]['content'])
            self.seen.append((role, body, payload))
            phase = payload.get('phase_control', {})
            if fail and role == 'player' and phase.get('submission_slot') == 2 and phase.get('phase') == 'action' and not self.failed:
                self.failed = True
                raise urllib.error.URLError(PreSendTLSFailure(ssl.SSLError('handshake failure')))
            self.previous[role] = payload
            if role == 'host':
                text = 'no'
            elif role == 'grader':
                text = evaluated((0, 0) if reject else (1, 1))
            elif phase['phase'] != 'action':
                text = 'Working notes: this remains a hypothesis; test an unsupported assumption.'
            elif invalid and not payload.get('format_correction') and phase['submission_slot'] == 1:
                text = 'Untyped proposed question?'
            else:
                text = 'FINAL\nsubmitted explanation' if phase['force_final'] else 'QUESTION\nOne atomic question?'
            return Response({'id': f'{role}-{len(self.seen)}', 'choices': [{'message': {'content': text}, 'finish_reason': 'stop'}],
                             'usage': {'prompt_tokens': 50, 'completion_tokens': tokens, 'total_tokens': 50+tokens}})
        return request

    def test_one_lane_private_data_isolation_and_actual_generations(self):
        config, prompts = self.config(), load_prompts()
        budget = {'generation_cap': 6, 'output_token_cap': 10000, 'submission_cap': 4}
        with tempfile.TemporaryDirectory() as tmp, patch('urllib.request.OpenerDirector.open', side_effect=self.api()):
            rec = Recorder(Path(tmp)/'game', PUZZLE, config, prompts, echo=False)
            result = play(PUZZLE, config, rec, self.clients(config, rec, budget), prompts)
            self.assertTrue(result['success'])
            self.assertEqual(result['submissions'], 4)
            actors = [c for c in rec.calls if c['role'] == 'player']
            self.assertEqual(len(actors), 6)
            self.assertEqual(len({c['game_session_id'] for c in actors}), 1)
            self.assertEqual(len({c['session_lane_id'] for c in actors}), 1)
            self.assertEqual(len(submitted_review_actions(rec.calls)), 4)
            self.assertEqual(solver_usage(rec.calls)['output_tokens'], 60)
            for c in actors:
                self.assertNotIn('SECRET_', json.dumps(c['request']))
                self.assertNotIn('response_format', c['request'])

    def test_early_budget_final_stops_even_if_wrong(self):
        config, prompts = self.config(), load_prompts()
        budget = {'generation_cap': 4, 'output_token_cap': 2000, 'submission_cap': 4}
        with tempfile.TemporaryDirectory() as tmp, patch('urllib.request.OpenerDirector.open', side_effect=self.api(tokens=300, reject=True)):
            rec = Recorder(Path(tmp)/'game', PUZZLE, config, prompts, echo=False)
            result = play(PUZZLE, config, rec, self.clients(config, rec, budget), prompts)
            self.assertFalse(result['success'])
            self.assertEqual(result['submissions'], 2)
            self.assertEqual(result['stop_reason'], 'solver_budget_exhausted')
            self.assertTrue(result['forced_final'])
            self.assertEqual(result['counted_questions'], 2)
            self.assertLessEqual(solver_usage(rec.calls)['output_tokens'], 2000)

    def test_format_retry_is_charged_and_uses_same_lane(self):
        config, prompts = self.config(), load_prompts()
        budget = {'generation_cap': 6, 'output_token_cap': 10000, 'submission_cap': 4}
        with tempfile.TemporaryDirectory() as tmp, patch('urllib.request.OpenerDirector.open', side_effect=self.api(invalid=True)):
            rec = Recorder(Path(tmp)/'game', PUZZLE, config, prompts, echo=False)
            result = play(PUZZLE, config, rec, self.clients(config, rec, budget), prompts)
            self.assertTrue(result['success'])
            actors = [c for c in rec.calls if c['role'] == 'player']
            self.assertEqual(len(actors), 6)
            self.assertEqual(len(submitted_review_actions(rec.calls)), 4)
            self.assertEqual(len({c['session_lane_id'] for c in actors}), 1)
            self.assertEqual(solver_usage(rec.calls)['output_tokens'], 60)

    def test_resume_does_not_repeat_observed_review_and_keeps_exact_pending_body(self):
        config, prompts = self.config(), load_prompts()
        budget = {'generation_cap': 6, 'output_token_cap': 10000, 'submission_cap': 4}
        with tempfile.TemporaryDirectory() as tmp, patch('urllib.request.OpenerDirector.open', side_effect=self.api(fail=True)):
            folder = Path(tmp)/'game'
            rec = Recorder(folder, PUZZLE, config, prompts, echo=False)
            result = play(PUZZLE, config, rec, self.clients(config, rec, budget), prompts)
            self.assertEqual(result['status'], 'error')
            self.assertEqual(result['submissions'], 1)
            raw = [json.loads(s) for s in (folder/'api_calls.jsonl').read_text().splitlines()]
            proof = saved_transport_recovery(result, raw, rec.turns, config, folder)
            self.assertIsNotNone(proof)
            (folder/'transport_recovery.json').write_text(json.dumps(proof))
            before = len(self.seen)
            saved = Recorder.restore(folder, PUZZLE, config, prompts, echo=False)
            result = play(PUZZLE, config, saved, self.clients(config, saved, budget), prompts)
            self.assertTrue(result['success'])
            self.assertEqual(self.seen[before][1], self.seen[before-1][1])
            self.assertEqual(len([c for c in saved.calls if c.get('self_review_key') == '2:0:review']), 1)
            self.assertEqual(solver_usage(saved.calls)['generations'], 6)

    def test_checked_local_recovery_reuses_last_observed_inline_correction(self):
        config, prompts = self.config(), load_prompts()
        budget = {'generation_cap': 6, 'output_token_cap': 10000, 'submission_cap': 4}
        base = self.api()
        def inline_api(req, **kw):
            response = base(req, **kw)
            message = response.data['choices'][0]['message']
            if json.loads(req.data)['model'] == 'player' and message['content'].startswith('QUESTION\n'):
                message['content'] = 'QUESTION '+('Last correction?' if 'format_correction' in self.previous['player'] else 'First proposal?')
            return response
        with tempfile.TemporaryDirectory() as tmp, patch('urllib.request.OpenerDirector.open', side_effect=inline_api):
            folder = Path(tmp)/'game'
            rec = Recorder(folder, PUZZLE, config, prompts, echo=False)
            # Reproduce the original strict parser that rejected inline headers.
            def legacy(raw, force=False, audit=None):
                if raw.startswith('QUESTION '):
                    raise ProtocolError('Legacy parser rejects inline header')
                parse_action(raw, force, audit)
                return raw
            with patch('turtle_loop.matched_self_review.action_text', side_effect=legacy):
                result = play(PUZZLE, config, rec, self.clients(config, rec, budget), prompts)
            self.assertEqual(result['status'], 'error')
            self.assertEqual(result['submissions'], 0)
            raw = [json.loads(s) for s in (folder/'api_calls.jsonl').read_text().splitlines()]
            proof = saved_action_recovery(result, raw, rec.turns, config, folder)
            self.assertIsNotNone(proof)
            (folder/'self_review_action_recovery.json').write_text(json.dumps(proof))
            before = len(self.seen)
            saved = Recorder.restore(folder, PUZZLE, config, prompts, echo=False)
            result = play(PUZZLE, config, saved, self.clients(config, saved, budget), prompts)
            self.assertTrue(result['success'])
            self.assertEqual(saved.turns[0]['text'], 'Last correction?')
            self.assertEqual(self.seen[before][0], 'host')
            self.assertEqual(len(submitted_review_actions(saved.calls)), 4)
            self.assertEqual(solver_usage(saved.calls)['generations'], 6)

    def test_preamble_inline_action_needs_no_additional_player_generation(self):
        config, prompts = self.config(), load_prompts()
        budget = {'generation_cap': 6, 'output_token_cap': 10000, 'submission_cap': 4}
        base = self.api()
        def prefaced(req, **kw):
            response = base(req, **kw)
            msg = response.data['choices'][0]['message']
            if json.loads(req.data)['model'] == 'player' and msg['content'].startswith('QUESTION\n'):
                msg['content'] = 'Some tentative notes.\nQUESTION '+msg['content'].partition('\n')[2]
            return response
        with tempfile.TemporaryDirectory() as tmp, patch('urllib.request.OpenerDirector.open', side_effect=prefaced):
            rec = Recorder(Path(tmp)/'game', PUZZLE, config, prompts, echo=False)
            result = play(PUZZLE, config, rec, self.clients(config, rec, budget), prompts)
            self.assertTrue(result['success'])
            self.assertEqual(solver_usage(rec.calls)['generations'], 6)
            self.assertEqual(len([c for c in rec.calls if c.get('self_review_phase') == 'action']), 4)
            self.assertEqual(rec.turns[0]['text'], 'One atomic question?')


if __name__ == '__main__':
    unittest.main()
