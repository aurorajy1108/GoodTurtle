import http.client
import errno
import json
import socket
import ssl
import tempfile
import unittest
import urllib.error
from unittest.mock import patch

from turtle_loop.providers import APIError, Client, PreSendTLSFailure


class Response:
    def __init__(self, data=b''): self.data = data
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self): return self.data


class TransportDiagnosticsTests(unittest.TestCase):
    def make_client(self, records, retries=2):
        return Client({'provider':'deepseek', 'model':'test', 'max_retries':retries}, 'player', records.append)

    @patch.dict('os.environ', {'DEEPSEEK_API_KEY':'fixture'})
    @patch('turtle_loop.providers.time.sleep')
    def test_unreachable_during_connect_retries_before_http_bytes(self, sleep):
        for code in (errno.EHOSTUNREACH, errno.ENETUNREACH):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as tmp:
                calls=[];client=self.make_client(calls, retries=1);client.begin_game(tmp,lambda *a,**kw:None)
                with patch.object(http.client.HTTPSConnection,'connect',side_effect=OSError(code,'sensitive-network-detail')) as connect, \
                     patch.object(socket.socket,'sendall') as sent, self.assertRaises(APIError):
                    client.complete('system','{}')
                self.assertEqual(connect.call_count,2)
                sent.assert_not_called()
                self.assertTrue(all(c['safe_pre_send_retry'] for c in calls))
                self.assertTrue(all(c['reason_errno']==code for c in calls))
                self.assertNotIn('sensitive-network-detail',str(calls))
                client.close_game()

    @patch.dict('os.environ', {'DEEPSEEK_API_KEY':'fixture'})
    @patch('turtle_loop.providers.time.sleep')
    def test_untracked_unreachable_does_not_retry(self, sleep):
        calls=[];client=self.make_client(calls)
        with tempfile.TemporaryDirectory() as tmp:
            client.begin_game(tmp,lambda *a,**kw:None)
            with patch.object(client.opener,'open',side_effect=urllib.error.URLError(OSError(errno.EHOSTUNREACH,'x'))) as opened, self.assertRaises(APIError):
                client.complete('system','{}')
            self.assertEqual(opened.call_count,1)
            self.assertFalse(calls[0]['safe_pre_send_retry'])
            client.close_game()

    @patch.dict('os.environ', {'DEEPSEEK_API_KEY':'fixture'})
    @patch('turtle_loop.providers.time.sleep')
    def test_tls_eof_in_connect_retries_before_any_http_bytes(self, sleep):
        calls=[];client=self.make_client(calls, retries=2)
        with tempfile.TemporaryDirectory() as tmp:
            client.begin_game(tmp,lambda *a,**kw:None)
            with patch.object(http.client.HTTPSConnection,'connect',side_effect=ssl.SSLEOFError(8,'private detail')) as connect, \
                 patch.object(socket.socket,'sendall') as sent, self.assertRaises(APIError):
                client.complete('system','{}')
            self.assertEqual(connect.call_count,3)
            sent.assert_not_called()
            self.assertEqual([c['transport_category'] for c in calls],['tls_handshake_eof']*3)
            self.assertTrue(all(c['safe_pre_send_retry'] for c in calls))
            self.assertTrue(all(c['reason_type']=='SSLEOFError' for c in calls))
            self.assertNotIn('private detail',str(calls))
            self.assertEqual(sleep.call_count,2)
            client.close_game()

    @patch.dict('os.environ', {'DEEPSEEK_API_KEY':'fixture'})
    @patch('turtle_loop.providers.time.sleep')
    def test_untracked_tls_eof_does_not_retry(self, sleep):
        calls=[];client=self.make_client(calls)
        with tempfile.TemporaryDirectory() as tmp:
            client.begin_game(tmp,lambda *a,**kw:None)
            with patch.object(client.opener,'open',side_effect=urllib.error.URLError(ssl.SSLEOFError(8,'x'))) as opened, self.assertRaises(APIError):
                client.complete('system','{}')
            self.assertEqual(opened.call_count,1)
            self.assertEqual(calls[0]['transport_category'],'tls')
            self.assertFalse(calls[0]['safe_pre_send_retry'])
            client.close_game()

    @patch.dict('os.environ', {'DEEPSEEK_API_KEY':'fixture'})
    @patch('turtle_loop.providers.time.sleep')
    def test_pre_send_tls_failure_then_success_advances_session_once(self, sleep):
        calls=[];client=self.make_client(calls)
        answer=Response(json.dumps({'id':'r1','model':'test','choices':[{'message':{'content':'ok'},'finish_reason':'stop'}]}).encode())
        error=urllib.error.URLError(PreSendTLSFailure(ssl.SSLEOFError(8,'x')))
        with tempfile.TemporaryDirectory() as tmp:
            client.begin_game(tmp,lambda *a,**kw:None)
            with patch.object(client.opener,'open',side_effect=[error,answer]) as opened:
                self.assertEqual(client.complete('system','{}').text,'ok')
            self.assertEqual(opened.call_count,2)
            self.assertEqual(opened.call_args_list[0].args[0].data,opened.call_args_list[1].args[0].data)
            lane=next(iter(client.session.lanes.values()))
            self.assertEqual(lane['turn'],1)
            self.assertEqual(len(lane['messages']),2)
            self.assertFalse(client.session.failed)
            client.close_game()

    @patch.dict('os.environ', {'DEEPSEEK_API_KEY':'sensitive-key'})
    @patch('turtle_loop.providers.time.sleep')
    def test_dns_failure_retries_same_persistent_request_once(self, sleep):
        calls = []
        client = self.make_client(calls)
        answer = Response(json.dumps({'id':'r1', 'model':'test', 'choices':[{'message':{'content':'ok'}, 'finish_reason':'stop'}]}).encode())
        failure = urllib.error.URLError(socket.gaierror(socket.EAI_AGAIN, 'secret-server-detail'))
        with tempfile.TemporaryDirectory() as tmp:
            client.begin_game(tmp, lambda *a, **kw:None)
            with patch.object(client.opener, 'open', side_effect=[failure, answer]) as opened:
                result = client.complete('system', json.dumps({'opening':'puzzle'}))
            self.assertEqual(result.text, 'ok')
            self.assertEqual(opened.call_count, 2)
            self.assertEqual(opened.call_args_list[0].args[0].data, opened.call_args_list[1].args[0].data)
            self.assertEqual(calls[0]['transport_category'], 'dns_resolution')
            self.assertEqual(calls[0]['reason_errno'], socket.EAI_AGAIN)
            self.assertTrue(calls[0]['safe_pre_send_retry'])
            self.assertEqual(calls[0]['session_lane_id'], calls[1]['session_lane_id'])
            self.assertEqual(client.session.lanes[next(iter(client.session.lanes))]['turn'], 1)
            self.assertNotIn('secret-server-detail', str(calls))
            self.assertNotIn('sensitive-key', str(calls))
            client.close_game()

    @patch.dict('os.environ', {'DEEPSEEK_API_KEY':'fixture'})
    @patch('turtle_loop.providers.time.sleep')
    def test_ambiguous_failures_do_not_retry(self, sleep):
        failures = [urllib.error.URLError('private detail'), urllib.error.URLError(socket.timeout('timeout')),
                    urllib.error.URLError(ConnectionResetError('reset')), ConnectionResetError('reset')]
        for failure in failures:
            with self.subTest(failure=type(failure).__name__), tempfile.TemporaryDirectory() as tmp:
                calls=[]; client=self.make_client(calls);client.begin_game(tmp,lambda *a,**kw:None)
                with patch.object(client.opener,'open',side_effect=failure) as opened, self.assertRaises(APIError):
                    client.complete('system','{}')
                self.assertEqual(opened.call_count,1)
                self.assertFalse(calls[0]['safe_pre_send_retry'])
                self.assertNotIn('private detail', str(calls))
                self.assertTrue(client.session.failed)
                client.close_game()

    @patch.dict('os.environ', {'DEEPSEEK_API_KEY':'fixture'})
    @patch('turtle_loop.providers.time.sleep')
    def test_dns_exception_during_read_is_not_retried(self, sleep):
        calls=[];client=self.make_client(calls)
        response=Response()
        with tempfile.TemporaryDirectory() as tmp:
            client.begin_game(tmp,lambda *a,**kw:None)
            with patch.object(client.opener,'open',return_value=response) as opened, \
                 patch.object(response,'read',side_effect=urllib.error.URLError(socket.gaierror(socket.EAI_AGAIN,'x'))), \
                 self.assertRaises(APIError):
                client.complete('system','{}')
            self.assertEqual(opened.call_count,1)
            self.assertEqual(calls[0]['transport_phase'],'read')
            self.assertFalse(calls[0]['safe_pre_send_retry'])
            client.close_game()

    @patch.dict('os.environ', {'DEEPSEEK_API_KEY':'fixture'})
    @patch('turtle_loop.providers.time.sleep')
    def test_dns_retry_limit(self, sleep):
        calls=[];client=self.make_client(calls, retries=2)
        with tempfile.TemporaryDirectory() as tmp:
            client.begin_game(tmp,lambda *a,**kw:None)
            with patch.object(client.opener,'open',side_effect=urllib.error.URLError(socket.gaierror(socket.EAI_AGAIN,'x'))) as opened, self.assertRaises(APIError):
                client.complete('system','{}')
            self.assertEqual(opened.call_count,3)
            self.assertEqual([c['attempt'] for c in calls],[1,2,3])
            self.assertEqual(sleep.call_count,2)
            client.close_game()

if __name__ == '__main__': unittest.main()
