import http.client
import json
import unittest
from unittest.mock import patch

from turtle_loop.providers import APIError, Client


class BrokenFraming:
    def __init__(self, body): self.body=body
    def __enter__(self): return self
    def __exit__(self,*args): pass
    def read(self): raise http.client.IncompleteRead(self.body)


@patch.dict('os.environ',{'DEEPSEEK_API_KEY':'fixture'})
class HttpReadRecoveryTests(unittest.TestCase):
    def run_call(self,body):
        calls=[]
        client=Client({'provider':'deepseek','model':'test','max_retries':2},'host',calls.append)
        with patch.object(client.opener,'open',return_value=BrokenFraming(body)) as opened:
            try: reply=client.complete('system','{}')
            except APIError: reply=None
        self.assertEqual(opened.call_count,1)
        return reply,calls

    def test_complete_json_missing_http_terminator_preserves_answer_and_usage_once(self):
        reply,calls=self.run_call(b'\n'+json.dumps({'id':'original','model':'test',
            'choices':[{'message':{'content':'no'},'finish_reason':'stop'}],
            'usage':{'prompt_tokens':10,'completion_tokens':2,'total_tokens':12}}).encode())
        self.assertEqual(reply.text,'no');self.assertEqual(reply.response_id,'original')
        self.assertEqual(len(calls),1);self.assertEqual(calls[0]['status'],'ok')
        self.assertEqual(calls[0]['usage']['total_tokens'],12)
        self.assertTrue(calls[0]['http_read_diagnostic']['framing_recovered'])

    def test_truncated_json_and_whitespace_never_become_an_answer(self):
        for body in [b'\n\n',b'{"id":"partial","choices":[',b'{"secret":"sensitive-fragment',b'[]']:
            with self.subTest(body=body):
                reply,calls=self.run_call(body)
                self.assertIsNone(reply);self.assertEqual(calls[0]['status'],'transport_error')
                self.assertEqual(calls[0]['http_read_diagnostic']['partial_bytes'],len(body))
                self.assertNotIn('sensitive-fragment',json.dumps(calls))

    def test_complete_refusal_truncation_or_empty_body_still_fails_normal_checks(self):
        for reason,content in [('length','no'),('refusal',''),('stop','')]:
            with self.subTest(reason=reason):
                # Disable ordinary empty-response retries for this fixture.
                calls=[];client=Client({'provider':'deepseek','model':'test','max_retries':0},'host',calls.append)
                body=json.dumps({'id':'r','choices':[{'message':{'content':content},'finish_reason':reason}]}).encode()
                with patch.object(client.opener,'open',return_value=BrokenFraming(body)),self.assertRaises(APIError):
                    client.complete('system','{}')
                self.assertEqual(len(calls),1)
                self.assertTrue(calls[0]['http_read_diagnostic']['framing_recovered'])
