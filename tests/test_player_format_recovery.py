import json
import unittest
from turtle_loop.engine import parse_action, ProtocolError


class PlayerFormatRecoveryTests(unittest.TestCase):
    def test_one_unescaped_inner_quote_pair_preserves_question_words(self):
        events=[]
        raw='{"type":"question","text":"Did you click "confirm before deadline," and lose the dishes?"}'
        self.assertEqual(parse_action(raw,audit=events.append),
                         {'type':'question','text':'Did you click "confirm before deadline," and lose the dishes?'})
        self.assertEqual(events[0]['method'],'unescaped_question_inner_quotes')
        self.assertEqual(events[0]['characters_added'],2)
        for invalid in (
            '{"type":"final","text":"A "quoted" guess?"}',
            '{"type":"question","text":"Q?","extra":"value?"}',
            '{"type":"question","text":"Q?","type":"final"}',
            '{"type":"question","text":"Did {you} click "confirm"?"}',
            '{"type":"question","text":"Did "A" or "B" do it?"}',
            'Prose {"type":"question","text":"Did you click "confirm"?"}',
        ):
            # Valid JSON with forbidden extra fields is still rejected too.
            with self.subTest(raw=invalid),self.assertRaises(ProtocolError):parse_action(invalid)
        with self.assertRaises(ProtocolError):parse_action(raw,force_final=True)

    def test_exact_missing_question_quote_inserts_only_one_character(self):
        events=[]
        raw='{"type":"question","text":"Were the courses taken by someone else?}'
        self.assertEqual(parse_action(raw,audit=events.append),
                         {'type':'question','text':'Were the courses taken by someone else?'})
        self.assertEqual(events[0]['method'],'missing_question_text_closing_quote')
        self.assertEqual(events[0]['characters_added'],1)
        at=events[0]['insert_offset']
        self.assertEqual(raw[:at]+'"'+raw[at:],'{"type":"question","text":"Were the courses taken by someone else?"}')
        for invalid in (
            '{"type":"question","text":"Truncated text}',
            '{"type":"final","text":"A guess?}',
            '{"type":"question","text":"Q?} {"type":"question","text":"Other?"}',
            '{"type":"question","text":"Nested {text}?}',
            'Prose {"type":"question","text":"Q?}',
        ):
            with self.subTest(raw=invalid),self.assertRaises(ProtocolError):parse_action(invalid)
        with self.assertRaises(ProtocolError):parse_action(raw,force_final=True)

    def test_prose_and_json_preserves_action_and_records_recovery(self):
        events = []
        raw = 'Let me refocus.\n\n{"type":"question","text":"Is she already dead?"}'
        self.assertEqual(parse_action(raw, audit=events.append),
                         {'type': 'question', 'text': 'Is she already dead?'})
        self.assertEqual(events[0]['method'], 'single_embedded_json')

    def test_ambiguous_or_truncated_objects_stop(self):
        for raw in ['{"type":"question","text":"A?"} {"type":"question","text":"B?"}',
                    '{"type":"question","text":"A?"} {"type":']:
            with self.subTest(raw=raw), self.assertRaises(ProtocolError):
                parse_action(raw)

    def test_recovery_does_not_bypass_final_or_schema(self):
        for raw, forced in [('Thoughts: {"type":"question","text":"A?"}', True),
                            ('Thoughts: {"type":"question","text":"A?","extra":1}', False)]:
            with self.subTest(raw=raw), self.assertRaises(ProtocolError):
                parse_action(raw, force_final=forced)

    def test_strict_json_remains_unchanged(self):
        events = []
        action = {'type': 'final', 'text': 'The answer'}
        self.assertEqual(parse_action(json.dumps(action), audit=events.append), action)
        self.assertEqual(events, [])

    def test_embedded_json_and_string_note_compose_without_changing_action(self):
        events=[]
        raw='Let me refocus. {"type":"question","text":"Is she already dead?","text_note":"rephrase"}'
        self.assertEqual(parse_action(raw,audit=events.append),
                         {'type':'question','text':'Is she already dead?'})
        self.assertEqual(events[0]['method'],'single_embedded_json')
