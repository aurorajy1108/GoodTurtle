import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from test_loop import PUZZLE, FakeClient, evaluated
from turtle_loop.engine import Recorder, load_prompts, play
from turtle_loop.host import answer_question, POLICY
from turtle_loop.providers import APIError


class HostVerificationTests(unittest.TestCase):
    def test_one_call_even_when_archived_pack_requests_verification(self):
        client=FakeClient(lambda i,p:['no','yes and no','no'][i-1])
        payload={'active_puzzle':{'verification_policy':'independent_then_adjudicate_v1'},'visible_history':[], 'current_question':'Q'}
        reviews=[]
        response=answer_question(client,'system',payload,'verify',reviews.append)
        self.assertEqual(response.text,'no')
        self.assertEqual(len(client.inputs),1)
        self.assertEqual(reviews[0]['calls'],1)
        self.assertEqual(reviews[0]['policy'],'single')
        self.assertNotIn('candidate_labels',payload)

    def test_invalid_response_stops_without_answer_fishing(self):
        client=FakeClient(lambda i,p:'unknown')
        with self.assertRaises(APIError):
            answer_question(client,'system',{'active_puzzle':{'verification_policy':POLICY}},'verify')
        self.assertEqual(len(client.inputs),1)

    def test_single_host_call_has_one_public_feedback_and_one_question(self):
        prompts=load_prompts()
        with tempfile.TemporaryDirectory() as tmp:
            recorder=Recorder(Path(tmp)/'run',PUZZLE,{'max_questions':2},prompts,echo=False)
            clients={'player':FakeClient(lambda i,p:json.dumps({'type':'question' if i==1 else 'final','text':'Guess'})),
                     'host':FakeClient(lambda i,p:'no'), 'grader':FakeClient(lambda i,p:evaluated())}
            with patch('turtle_loop.engine.build_story_context',return_value={'verification_policy':POLICY,'context_sha256':'test'}):
                result=play(copy.deepcopy(PUZZLE),{'max_questions':2},recorder,clients,prompts)
            self.assertEqual(len(clients['host'].inputs),1)
            self.assertEqual(result['counted_questions'],1)
            history=json.loads(clients['player'].inputs[1][1])['visible_history']
            self.assertEqual(history,[{'type':'question','text':'Guess','feedback':'no'}])
