import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from turtle_loop.dataset import load_dataset, validate_dataset, overview, workbook_rows
from turtle_loop.engine import Recorder, ProtocolError, grade_final, load_prompts, parse_action, play, summarize_batch
from turtle_loop.providers import APIError, Client, Reply, build_request, parse_reply, resolve_env, validate_profile

PUZZLE = {'id': 'FIXTURE', 'opening': 'A person picked up an umbrella. Why?',
          'answer': 'SECRET_GOLD_SENTINEL', 'story_family': 'SECRET_FAMILY',
          'title': 'SECRET_TITLE', 'quality_status': 'SECRET_QUALITY',
          'rubric': [{'id': 'C1', 'weight': 0.6, 'criterion': 'SECRET_RUBRIC_1'},
                     {'id': 'C2', 'weight': 0.4, 'criterion': 'SECRET_RUBRIC_2'}]}


def evaluated(credits=(1, 1), contradiction=False, irrelevant=False, conflict=False):
    return json.dumps({'checkpoints': [{'id': f'C{i}', 'credit': c,
                                       'evidence': 'submitted explanation' if c else '', 'reason': 'test'}
                                      for i, c in enumerate(credits, 1)],
                       'material_contradiction': contradiction, 'irrelevant': irrelevant,
                       'rubric_conflict': conflict, 'full_solution': all(c == 1 for c in credits) and not contradiction,
                       'completion_note': 'Fixture narrative coverage'})


class FakeClient:
    def __init__(self, fn):
        self.fn, self.inputs = fn, []

    def complete(self, system, user):
        self.inputs.append((system, user))
        answer = self.fn(len(self.inputs), json.loads(user))
        if isinstance(answer, Exception):
            raise answer
        return Reply(answer, {})


class GameTests(unittest.TestCase):
    def game(self, player, host=lambda i, x: 'no', grader=lambda i, x: evaluated(), limit=100):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        folder = Path(temp.name)/'run'
        prompts = load_prompts()
        recorder = Recorder(folder, copy.deepcopy(PUZZLE), {'max_questions': limit}, prompts, echo=False)
        clients = {'player': FakeClient(player), 'host': FakeClient(host), 'grader': FakeClient(grader)}
        result = play(copy.deepcopy(PUZZLE), {'max_questions': limit}, recorder, clients, prompts)
        return result, recorder, clients

    def test_exact_100_boundary(self):
        def player(i, payload):
            if i == 100:
                self.assertIn('mandatory last turn', payload['turn_control'])
            return json.dumps({'type': 'final' if i == 100 else 'question', 'text': f'Attempt {i}'})
        result, rec, clients = self.game(player, grader=lambda i, x: evaluated((0, 0)))
        self.assertEqual((result['host_questions'], result['rejected_finals'], result['counted_questions']), (99, 1, 100))
        self.assertEqual(result['submissions'], 100)
        self.assertEqual(len(clients['host'].inputs), 99)
        self.assertEqual(result['stop_reason'], 'budget_exhausted')
        self.assertEqual(result['final_partial_score'], 0)

    def test_early_finals_consume_budget_and_host_sees_them(self):
        def player(i, payload):
            if i == 2:
                return json.dumps({'type': 'question', 'text': 'Does my last explanation have an error?'})
            return json.dumps({'type': 'final', 'text': f'Final explanation {i}'})
        result, rec, clients = self.game(player, grader=lambda i, x: evaluated((0.5, 0)), limit=4)
        self.assertEqual(result['counted_questions'], 4)
        self.assertEqual(result['submissions'], 4)
        self.assertEqual(result['rejected_finals'], 3)
        self.assertEqual(result['final_partial_score'], 0.3)
        h = json.loads(clients['host'].inputs[0][1])
        self.assertEqual(h['visible_history'][0]['type'], 'final')
        self.assertEqual(h['visible_history'][0]['feedback'], 'yes and no')
        self.assertNotIn('rubric', clients['host'].inputs[0][1])

    def test_player_context_has_no_hidden_fields_or_scores(self):
        self.game(lambda i, p: json.dumps({'type': 'final' if i == 3 else 'question', 'text': 'Guess'}), limit=3)
        result, rec, clients = self.game(
            lambda i, p: json.dumps({'type': 'final', 'text': 'Guess'}),
            grader=lambda i, p: evaluated((0.5, 0)) if i == 1 else evaluated(), limit=3)
        for system, user in clients['player'].inputs:
            self.assertNotIn('SECRET_', system+user)
            self.assertNotIn('partial_score', user)
            self.assertNotIn('credit', user)
            self.assertEqual(set(json.loads(user)), {'opening', 'visible_history', 'turn_control', 'action_protocol'})
        self.assertEqual(result['counted_questions'], 1)
        self.assertTrue(result['success'])

    def test_incomplete_and_irrelevant_finals_only_labels(self):
        result, rec, clients = self.game(
            lambda i, x: json.dumps({'type': 'final', 'text': 'Some explanation'}),
            grader=lambda i, x: evaluated((0, 0), irrelevant=True) if i == 1 else evaluated(), limit=2)
        self.assertEqual(rec.turns[0]['label'], 'irrelevant')
        self.assertEqual(result['counted_questions'], 1)
        self.assertEqual(result['submissions'], 2)

    def test_scores_do_not_accumulate(self):
        result, rec, _ = self.game(lambda i, x: json.dumps({'type': 'final', 'text': 'Guess'}),
                                   grader=lambda i, x: evaluated((1, 0)) if i == 1 else evaluated((0, 1)), limit=2)
        self.assertEqual(result['final_partial_score'], 0.4)
        self.assertEqual(result['best_partial_score'], 0.6)
        self.assertFalse(result['success'])

    def test_bad_host_label_is_not_coerced(self):
        result, rec, _ = self.game(lambda i, x: '{"type":"question","text":"Question?"}', host=lambda i, x: 'unknown')
        self.assertEqual(result['status'], 'error')
        self.assertIsNone(result['success'])
        self.assertIsNone(result['final_partial_score'])
        self.assertEqual(result['counted_questions'], 1)
        self.assertEqual(result['pending_feedback'], 1)

    def test_forced_final_violation_is_error_not_fake_answer(self):
        result, rec, clients = self.game(lambda i, x: '{"type":"question","text":"Question?"}', limit=1)
        self.assertEqual(result['status'], 'error')
        self.assertFalse(clients['host'].inputs)
        self.assertEqual(result['submissions'], 0)

    def test_immediate_success_counts_no_wrong_submission(self):
        result, rec, _ = self.game(lambda i, x: '{"type":"final","text":"Complete answer"}', limit=1)
        self.assertTrue(result['success'])
        self.assertEqual(result['counted_questions'], 0)
        self.assertEqual(result['submissions'], 1)

    def test_api_error_preserves_submitted_question(self):
        result, rec, _ = self.game(lambda i, x: '{"type":"question","text":"Question?"}',
                                   host=lambda i, x: APIError('unavailable'))
        self.assertEqual(result['counted_questions'], 1)
        self.assertEqual(result['status'], 'error')
        self.assertTrue((rec.folder/'trajectory.jsonl').exists())
        self.assertTrue((rec.folder/'human_review.csv').exists())

    def test_invalid_or_missing_host_pack_is_recorded_before_model_calls(self):
        for error in (ValueError('host fingerprint mismatch'), FileNotFoundError('missing host pack')):
            with self.subTest(error=type(error).__name__), patch(
                    'turtle_loop.engine.build_story_context', side_effect=error):
                result, rec, clients = self.game(lambda i, x: '{"type":"final","text":"Guess"}')
            self.assertEqual(result['status'], 'error')
            self.assertEqual(result['stop_reason'], 'host_context_error')
            self.assertIsNone(result['success'])
            self.assertEqual(result['counted_questions'], 0)
            self.assertEqual(result['submissions'], 0)
            self.assertTrue(all(not client.inputs for client in clients.values()))
            self.assertEqual(json.loads((rec.folder/'result.json').read_text())['status'], 'error')
            self.assertIn('host_context', (rec.folder/'trajectory.jsonl').read_text())

    def test_rubric_conflict_marks_review_not_success(self):
        result, _, _ = self.game(lambda i, x: '{"type":"final","text":"Answer"}',
                                 grader=lambda i, x: evaluated(conflict=True))
        self.assertEqual(result['status'], 'needs_review')
        self.assertIsNone(result['success'])

    def test_html_escapes_model_text(self):
        result, rec, _ = self.game(lambda i, x: '{"type":"final","text":"<script>alert(1)</script>"}')
        output = (rec.folder/'trajectory.html').read_text()
        self.assertNotIn('<script>', output)
        self.assertIn('&lt;script&gt;', output)

    def test_non_completed_runs_not_in_success_denominator(self):
        result, rec, _ = self.game(lambda i, x: '{"type":"final","text":"Answer"}')
        entries = [dict(result, puzzle_id='P', repeat=1, run_dir='r1'),
                   dict(result, puzzle_id='P', repeat=2, run_dir='r2', status='error', success=None)]
        summary = summarize_batch(rec.folder.parent, entries)
        self.assertEqual(summary['completed_games'], 1)
        self.assertEqual(summary['success_rate_completed'], 1)


class ScoreTests(unittest.TestCase):
    def test_weighted_score(self):
        self.assertEqual(grade_final(evaluated((0.5, 1)), PUZZLE['rubric'])['partial_score'], 0.7)

    def test_contradiction_prevents_success_at_full_partial_score(self):
        g = grade_final(evaluated(contradiction=True), PUZZLE['rubric'])
        self.assertEqual(g['partial_score'], 1)
        self.assertFalse(g['complete'])
        self.assertEqual(g['label'], 'yes and no')

    def test_bad_credits_ids_flags(self):
        for change in ('credit', 'id', 'flag', 'missing', 'irrelevant'):
            value = json.loads(evaluated())
            if change == 'credit': value['checkpoints'][0]['credit'] = True
            if change == 'id': value['checkpoints'][0]['id'] = 'C2'
            if change == 'flag': value['irrelevant'] = 'false'
            if change == 'missing': value['checkpoints'].pop()
            if change == 'irrelevant': value['irrelevant'] = True
            with self.subTest(change=change), self.assertRaises(ProtocolError):
                grade_final(json.dumps(value), PUZZLE['rubric'])

    def test_markdown_json_not_silently_repaired(self):
        with self.assertRaises(ProtocolError):
            parse_action('```json\n{"type":"final","text":"x"}\n```')


class ProviderTests(unittest.TestCase):
    def test_api_shapes(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY':'fixture-key','ANTHROPIC_API_KEY':'fixture-key','DEEPSEEK_API_KEY':'fixture-key'}):
            for provider, suffix in [('openai','/responses'), ('openai_chat','/chat/completions'),
                                     ('deepseek','/chat/completions'), ('anthropic','/messages')]:
                with self.subTest(provider=provider):
                    cfg = {'provider': provider, 'model':'chosen-model'}
                    url, headers, body, kind = build_request(cfg, 'sys', 'user')
                    self.assertTrue(url.endswith(suffix))
                    self.assertEqual(body['model'], 'chosen-model')
                    self.assertFalse(body['stream'])
                    if provider == 'anthropic':
                        self.assertEqual(body['system'], 'sys')
                        self.assertEqual(body['messages'], [{'role':'user','content':'user'}])
                    elif provider == 'openai':
                        self.assertFalse(body['store'])
                        self.assertEqual(body['input'][0]['role'], 'system')
                    self.assertNotIn('fixture-key', json.dumps(body))

    def test_configurable_endpoint_and_reasoning(self):
        cfg = {'provider':'openai', 'model':'custom', 'base_url':'https://gateway.example/v1',
               'api_key_env':'MY_KEY', 'extra_body':{'reasoning':{'effort':'high'}}}
        url, _, body, _ = build_request(cfg, 'sys', 'user')
        self.assertEqual(url,'https://gateway.example/v1/responses')
        self.assertEqual(body['reasoning']['effort'], 'high')

    def test_extract_text_not_reasoning(self):
        reply = parse_reply('responses', {'output':[{'type':'reasoning','content':'hidden'},
                            {'type':'message','content':[{'type':'output_text','text':'yes'}]}], 'usage':{'output_tokens':4}})
        self.assertEqual(reply.text, 'yes')
        reply = parse_reply('anthropic', {'content':[{'type':'thinking','thinking':'hidden'},{'type':'text','text':'no'}]})
        self.assertEqual(reply.text, 'no')
        self.assertEqual(parse_reply('chat', {'choices':[{'message':{'content':'irrelevant','reasoning_content':'hidden'}}]}).text, 'irrelevant')

    def test_reject_secret_or_prompt_overrides(self):
        for patch_value in [{'api_key':'bad'}, {'base_url':'https://secret@host.example/v1'},
                            {'extra_body':{'messages':[]}}, {'extra_body':{'tools':[]}}]:
            with self.subTest(patch_value=patch_value), self.assertRaises(ValueError):
                validate_profile({'provider':'openai','model':'test',**patch_value}, require_key=False)

    def test_env_model_resolution(self):
        with patch.dict(os.environ, {'MODEL_FIXTURE':'exact-id'}):
            self.assertEqual(resolve_env({'model':'${MODEL_FIXTURE}'}),{'model':'exact-id'})
        with self.assertRaises(ValueError): resolve_env('${MISSING_FIXTURE_VARIABLE}')


class DatasetTests(unittest.TestCase):
    def test_invalid_weight_total(self):
        puzzle = copy.deepcopy(PUZZLE);puzzle['rubric'][0]['weight'] = 0.7
        with self.assertRaises(ValueError):validate_dataset({'schema_version':1,'puzzles':[puzzle]})

    def test_duplicate_ids(self):
        with self.assertRaises(ValueError):validate_dataset({'schema_version':1,'puzzles':[PUZZLE,PUZZLE]})

    def test_empty_score_not_zero_and_duplicate_groups(self):
        p = copy.deepcopy(PUZZLE);p['observed_score'] = None
        other = copy.deepcopy(p);other['id'] = 'OTHER'
        data = validate_dataset({'schema_version':1,'puzzles':[p,other]})
        self.assertIsNone(data['puzzles'][0]['observed_score'])
        self.assertEqual(overview(data)['identical_opening_groups'],[['FIXTURE','OTHER']])


class FullNarrativeTests(unittest.TestCase):
    def test_full_checkpoint_score_not_automatically_complete(self):
        value = json.loads(evaluated())
        value['full_solution'] = False
        value['completion_note'] = 'Some reference events are still missing'
        grade = grade_final(json.dumps(value), PUZZLE['rubric'])
        self.assertEqual(grade['partial_score'], 1)
        self.assertFalse(grade['complete'])
        self.assertEqual(grade['label'], 'yes and no')


class TransportTests(unittest.TestCase):
    def test_actual_client_paths_and_credentials_not_in_logs(self):
        import io
        responses = {
            'openai': {'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':'yes'}]}]},
            'deepseek': {'choices':[{'message':{'content':'no'},'finish_reason':'stop'}]},
            'anthropic': {'content':[{'type':'text','text':'irrelevant'}],'stop_reason':'end_turn'},
        }
        with patch.dict(os.environ, {'OPENAI_API_KEY':'SECRET_TEST_KEY','DEEPSEEK_API_KEY':'SECRET_TEST_KEY','ANTHROPIC_API_KEY':'SECRET_TEST_KEY'}):
            for provider, payload in responses.items():
                with self.subTest(provider=provider):
                    logs = []
                    client = Client({'provider':provider, 'model':'test'},'host',logs.append)
                    with patch.object(client.opener, 'open', return_value=io.BytesIO(json.dumps(payload).encode())) as http:
                        reply = client.complete('system','question')
                    self.assertTrue(reply.text)
                    self.assertEqual(http.call_count,1)
                    self.assertNotIn('SECRET_TEST_KEY',json.dumps(logs))
                    self.assertEqual(logs[0]['status'],'ok')

    def test_retry_is_transport_only_and_recorded(self):
        import io
        import urllib.error
        with patch.dict(os.environ, {'OPENAI_API_KEY':'test'}):
            logs=[];client=Client({'provider':'openai','model':'test','max_retries':1},'host',logs.append)
            payload={'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':'yes'}]}]}
            error=urllib.error.HTTPError('https://api.openai.com/v1/responses',429,'rate',{},None)
            with patch.object(client.opener,'open',side_effect=[error,io.BytesIO(json.dumps(payload).encode())]), patch('turtle_loop.providers.time.sleep'):
                self.assertEqual(client.complete('s','u').text,'yes')
            self.assertEqual([r['status'] for r in logs],['http_error','ok'])

    def test_truncation_keeps_output_without_resampling(self):
        import io
        with patch.dict(os.environ, {'OPENAI_API_KEY':'test'}):
            logs=[];client=Client({'provider':'openai','model':'test'},'player',logs.append)
            payload={'status':'incomplete','output':[{'type':'message','content':[{'type':'output_text','text':'partial'}]}]}
            with patch.object(client.opener,'open',return_value=io.BytesIO(json.dumps(payload).encode())) as http:
                with self.assertRaises(APIError):client.complete('s','u')
            self.assertEqual(http.call_count,1)
            self.assertEqual(logs[0]['text'],'partial')

    def test_invalid_provider_json_is_logged(self):
        import io
        with patch.dict(os.environ, {'OPENAI_API_KEY':'test'}):
            logs=[];client=Client({'provider':'openai','model':'test'},'host',logs.append)
            with patch.object(client.opener,'open',return_value=io.BytesIO(b'not json')):
                with self.assertRaises(APIError):client.complete('s','u')
            self.assertEqual(logs[0]['status'],'invalid_response')

if __name__ == '__main__':
    unittest.main()
