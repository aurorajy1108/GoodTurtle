import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

from turtle_loop.codex_client import output_contract
from turtle_loop.dialogue import FreeDialoguePlayer, dialogue_settings
from turtle_loop.engine import Recorder, ProtocolError, load_prompts, play
from turtle_loop.sessions import GameSession, delta
from turtle_loop.providers import Reply
from test_loop import FakeClient, PUZZLE, evaluated


def action(kind, text, next_speaker='B'):
    return json.dumps(dict(type=kind, text=text, next_speaker=next_speaker))


class DialogueTests(unittest.TestCase):
    def test_prose_and_note_metadata_compose_in_shared_dialogue(self):
        team,rec=self.team(lambda i,p:'A thought. {"type":"question","text":"Q?","next_speaker":"B","text_note":"rephrase"}',
                           lambda i,p:'{}',max_discussion=0)
        reply=team.complete('system','{}')
        self.assertEqual(json.loads(reply.text),{'type':'question','text':'Q?'})
        self.assertNotIn('text_note',team.transcript[0])
        events=[json.loads(x) for x in (rec.folder/'trajectory.jsonl').read_text().splitlines()]
        self.assertTrue(any(e['event']=='player_format_recovery' for e in events))
        self.assertTrue(any(e['event']=='player_action_normalized' for e in events))

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.prompts = load_prompts()

    def team(self, a, b, **options):
        rec = Recorder(self.root/'game', PUZZLE, {'max_questions':3}, self.prompts, echo=False)
        settings = dialogue_settings(Namespace(**{'dialogue_'+k:v for k,v in options.items()}))
        return FreeDialoguePlayer(FakeClient(a), FakeClient(b), rec, settings), rec

    def test_recovers_one_action_with_prose_and_records_actor(self):
        team, rec = self.team(lambda i,p: 'Let me check.\n' + action('question', 'Is it alive?'),
                              lambda i,p: action('question', 'Other?'))
        reply = team.complete('system', '{}')
        self.assertEqual(json.loads(reply.text), {'type':'question', 'text':'Is it alive?'})
        events = [json.loads(line) for line in (rec.folder/'trajectory.jsonl').read_text().splitlines()]
        recovery = [e for e in events if e['event'] == 'player_format_recovery']
        self.assertEqual(len(recovery), 1)
        self.assertEqual(recovery[0]['actor'], 'A')

    def test_recovery_rejects_ambiguous_or_disallowed_actions(self):
        team, rec = self.team(lambda i,p: 'Note: '+action('question','A?')+' '+action('question','B?'),
                              lambda i,p: action('question','Other?'))
        with self.assertRaises(ProtocolError):
            team.complete('system', '{}')
        self.assertEqual(team.transcript, [])

    def test_shared_chat_discussion_and_private_grade_isolation(self):
        def a(i, p):
            return action('discuss', 'Could it be a mistaken identity?') if i == 1 else action('final', 'Complete explanation', 'A')
        def b(i, p):
            if i == 1:
                self.assertEqual(p['shared_dialogue'][0]['speaker'], 'A')
                return action('question', 'Is identity important?', 'B')
            self.assertEqual(p['shared_dialogue'][-1]['text'], 'no')
            return action('final', 'Incomplete explanation', 'A')
        team, rec = self.team(a, b)
        host = FakeClient(lambda i,p:'no')
        grader = FakeClient(lambda i,p: evaluated((.5,0)) if i == 1 else evaluated())
        result = play(PUZZLE, {'max_questions':3}, rec,
                      dict(player=team, host=host, grader=grader), self.prompts)
        self.assertTrue(result['success'])
        self.assertEqual(result['submissions'], 3)
        self.assertEqual(result['counted_questions'], 2)  # successful final is logged, not an unsuccessful question
        self.assertEqual(result['rejected_finals'], 1)
        self.assertEqual(len(host.inputs), 1)
        last = json.loads(team.leader.inputs[-1][1])
        self.assertEqual(last['shared_dialogue'][-1]['text'], 'yes and no')
        self.assertEqual(last['dialogue_control']['allowed_actions'], ['final'])
        for system, user in team.leader.inputs + team.partner.inputs:
            self.assertNotIn('SECRET', system+user)
            self.assertNotIn('partial_score', user)
            self.assertNotIn('completion_note', user)
            self.assertNotIn('visible_history', json.loads(user))
        self.assertEqual(team.transcript[-1]['text'], 'yes')
        self.assertEqual(result['dialogue_metrics']['internal_messages'], 1)
        self.assertEqual(result['dialogue_metrics']['counts_by_actor']['B'], {'question':1, 'final':1})
        self.assertTrue((rec.folder/'shared_dialogue.html').exists())

    def test_alternating_overrides_self_selection_and_discussion_is_bounded(self):
        team, rec = self.team(lambda i,p:action('pass', 'Please test this.', 'A'),
                              lambda i,p:action('question', 'A direct test?', 'B'),
                              scheduling='alternating', max_discussion=1)
        reply = team.complete('system', json.dumps({'visible_history':[], 'turn_control':'normal'}))
        self.assertEqual(json.loads(reply.text)['type'], 'question')
        self.assertEqual(json.loads(team.partner.inputs[0][1])['dialogue_control']['allowed_actions'], ['question','final'])
        self.assertEqual(team.speaker, 'A')
        self.assertEqual(team.transcript[0]['requested_next_speaker'], 'A')
        self.assertEqual(team.transcript[0]['effective_next_speaker'], 'B')
        with self.assertRaises(ProtocolError):
            team.complete('system', '{}')
        with self.assertRaises(ProtocolError):
            team.observe_feedback(2, json.loads(reply.text), 'no')
        team.observe_feedback(1, json.loads(reply.text), 'no')

    def test_no_discussion_and_mandatory_final_reject_invalid_actions_without_retry(self):
        team, rec = self.team(lambda i,p:action('discuss', 'More discussion'),
                              lambda i,p:action('question', 'Q'), max_discussion=0)
        with self.assertRaises(ProtocolError):
            team.complete('system', '{}')
        self.assertEqual(len(team.leader.inputs), 1)
        self.assertEqual(team.transcript, [])
        # A final-only call must not admit either questions or internal discussion.
        with self.assertRaises(ProtocolError):
            team.complete('system', json.dumps({'turn_control':'This is the mandatory last turn.'}))
        self.assertEqual(json.loads(team.leader.inputs[-1][1])['dialogue_control']['allowed_actions'], ['final'])

    def test_role_presets_start_and_validation(self):
        for preset, expected in [('complementary', ['investigator','critic']),
                                 ('symmetric',['generalist','generalist']), ('swapped',['critic','investigator'])]:
            settings=dialogue_settings(Namespace(dialogue_roles=preset))
            self.assertEqual([x['specialty'] for x in settings['role_assignment'].values()], expected)
        for bad in (-1,11,True,1.5):
            with self.assertRaises(ValueError):
                dialogue_settings(Namespace(dialogue_max_discussion=bad))
        team, rec = self.team(lambda i,p:action('question','A'), lambda i,p:action('question','B'), start='B')
        self.assertEqual(json.loads(team.complete('system','{}').text)['text'], 'B')
        self.assertEqual(len(team.leader.inputs), 0)

    def test_persistent_agent_lanes_resume_own_context_and_append_peer_messages(self):
        a=GameSession('player',self.root,lambda *a,**k:None)
        b=GameSession('partner',self.root,lambda *a,**k:None)
        self.addCleanup(a.close); self.addCleanup(b.close)
        first={'active_speaker':'A','shared_dialogue':[], 'dialogue_control':{'allowed_actions':['question','final']}}
        lane, payload, system, wire, metadata = a.prepare('same system',json.dumps(first))
        a.accept(lane,payload,wire,Reply('{"type":"question","text":"Q","next_speaker":"B"}', {}, response_id='thread-A'))
        messages=[{'speaker':'A','type':'question','text':'Q'}, {'speaker':'Host','type':'feedback','text':'yes'}]
        lb,pb,sb,wb,mb=b.prepare('same system',json.dumps({**first,'active_speaker':'B','shared_dialogue':messages}))
        b.accept(lb,pb,wb,Reply('{"type":"question","text":"Q2","next_speaker":"A"}', {}, response_id='thread-B'))
        messages += [{'speaker':'B','type':'question','text':'Q2'}, {'speaker':'Host','type':'feedback','text':'no'}]
        la,pa,sa,wa,ma=a.prepare('same system',json.dumps({**first,'shared_dialogue':messages}))
        self.assertIs(la,lane)
        self.assertNotEqual(la['id'],lb['id'])
        self.assertEqual(ma['previous_response_id'],'thread-A')
        self.assertEqual(json.loads(wa)['context_update']['append_shared_dialogue'],messages)
        self.assertNotIn('active_speaker',json.loads(wa)['context_update']['set'])
        self.assertEqual(delta({'shared_dialogue':messages},{'shared_dialogue':messages[:1]})['context_update']['set']['shared_dialogue'], messages[:1])

    def test_schema_and_resumed_game_guard(self):
        schema, _, _=output_contract(json.dumps({'dialogue_control':{'allowed_actions':['final']}}))
        self.assertEqual(schema['properties']['type']['enum'], ['final'])
        self.assertFalse(schema['additionalProperties'])
        team, rec=self.team(lambda i,p:'{}', lambda i,p:'{}')
        rec.resumed=True; rec.turns=[{'type':'question'}]
        with self.assertRaises(ValueError):
            FreeDialoguePlayer(team.leader,team.partner,rec,team.settings)


if __name__ == '__main__':
    unittest.main()
