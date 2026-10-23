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
    def test_independence_and_adjudication(self):
        client=FakeClient(lambda i,p:['no','yes and no','no'][i-1])
        payload={'active_puzzle':{'verification_policy':POLICY},'visible_history':[], 'current_question':'Q'}
        reviews=[]
        response=answer_question(client,'system',payload,'verify',reviews.append)
        self.assertEqual(response.text,'no')
        self.assertEqual(client.inputs[0][1], client.inputs[1][1])
        self.assertEqual(json.loads(client.inputs[2][1])['candidate_labels'],['no','yes and no'])
        self.assertEqual(reviews[0]['calls'],3)
        self.assertNotIn('candidate_labels',payload)

    def test_invalid_response_stops_without_answer_fishing(self):
        client=FakeClient(lambda i,p:'unknown')
        with self.assertRaises(APIError):
            answer_question(client,'system',{'active_puzzle':{'verification_policy':POLICY}},'verify')
        self.assertEqual(len(client.inputs),1)

    def test_extra_host_calls_are_not_questions_or_public_feedback(self):
        prompts=load_prompts()
        with tempfile.TemporaryDirectory() as tmp:
            recorder=Recorder(Path(tmp)/'run',PUZZLE,{'max_questions':2},prompts,echo=False)
            clients={'player':FakeClient(lambda i,p:json.dumps({'type':'question' if i==1 else 'final','text':'Guess'})),
                     'host':FakeClient(lambda i,p:'no'), 'grader':FakeClient(lambda i,p:evaluated())}
            with patch('turtle_loop.engine.build_story_context',return_value={'verification_policy':POLICY,'context_sha256':'test'}):
                result=play(copy.deepcopy(PUZZLE),{'max_questions':2},recorder,clients,prompts)
            self.assertEqual(len(clients['host'].inputs),2)
            self.assertEqual(result['counted_questions'],1)
            history=json.loads(clients['player'].inputs[1][1])['visible_history']
            self.assertEqual(history,[{'type':'question','text':'Guess','feedback':'no'}])
