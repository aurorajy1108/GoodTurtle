import json
import subprocess
import unittest
from unittest.mock import patch
from turtle_loop.providers import Client,APIError

PROFILE={'provider':'codex_cli','model':'gpt-6-luna','reasoning_effort':'high'}

class CodexTests(unittest.TestCase):
    def test_cumulative_session_usage_is_differenced_and_raw_turn_mode_supported(self):
        from turtle_loop.codex_client import turn_usage
        from turtle_loop.costs import normalize_usage
        previous={'input_tokens':1934,'cached_input_tokens':0,'cache_write_input_tokens':0,
                  'output_tokens':16,'reasoning_output_tokens':0}
        raw={'input_tokens':3915,'cached_input_tokens':1792,'cache_write_input_tokens':0,
             'output_tokens':32,'reasoning_output_tokens':0}
        effective=turn_usage(raw,previous,'thread_total')
        self.assertEqual(effective['input_tokens'],1981)
        self.assertEqual(effective['output_tokens'],16)
        self.assertEqual(turn_usage(raw,previous,'turn'),raw)
        self.assertEqual(turn_usage(previous,raw,'thread_total'),{})
        normalized=normalize_usage('codex_cli',effective)
        self.assertEqual(normalized['reasoning_tokens'],0)
        self.assertEqual(normalized['total_tokens'],1997)
        self.assertEqual(normalize_usage('codex_cli',{'input_tokens':10,'cached_input_tokens':0,
                         'cache_write_input_tokens':3,'output_tokens':2,'reasoning_output_tokens':1})['cache_write_tokens'],3)

    @patch('turtle_loop.codex_client.shutil.which',return_value='/bin/codex')
    def test_official_cli_arguments_and_usage(self,_):
        output='\n'.join(json.dumps(x) for x in [
            {'type':'thread.started','thread_id':'test'},
            {'type':'item.completed','item':{'type':'agent_message','text':'{"text":"yes"}'}},
            {'type':'turn.completed','usage':{'input_tokens':100,'output_tokens':1}}])
        records=[]
        with patch('turtle_loop.codex_client.subprocess.run',return_value=subprocess.CompletedProcess([],0,output,'')) as call:
            result=Client(PROFILE,'host',records.append).complete('Host role','Question')
        self.assertEqual(result.text,'yes')
        self.assertEqual(result.usage['output_tokens'],1)
        args=call.call_args.args[0]
        self.assertIn('--ephemeral',args);self.assertIn('--ignore-user-config',args)
        self.assertIn('gpt-6-luna',args);self.assertIn('shell_tool',args)
        self.assertEqual(call.call_args.kwargs['input'],'Question')
        self.assertIsNone(records[0]['model_returned'])

    @patch('turtle_loop.codex_client.shutil.which',return_value='/bin/codex')
    def test_any_tool_use_invalidates_response(self,_):
        output='\n'.join(json.dumps(x) for x in [
            {'type':'item.started','item':{'type':'command_execution','command':'cat private.json'}},
            {'type':'item.completed','item':{'type':'agent_message','text':'{"text":"yes"}'}},
            {'type':'turn.completed','usage':{}}])
        records=[]
        with patch('turtle_loop.codex_client.subprocess.run',return_value=subprocess.CompletedProcess([],0,output,'')):
            with self.assertRaises(APIError):
                Client(PROFILE,'player',records.append).complete('Role','Puzzle')
        self.assertEqual(records[0]['status'],'invalid_response')

    @patch('turtle_loop.codex_client.shutil.which',return_value='/bin/codex')
    def test_no_unimplemented_token_limit_or_key_fields(self,_):
        with self.assertRaises(ValueError):
            Client({**PROFILE,'max_output_tokens':4096},'host',lambda x:None)


class StructuredCodexTests(unittest.TestCase):
    @patch('turtle_loop.codex_client.shutil.which',return_value='/bin/codex')
    def test_host_envelope_preserves_four_label_public_protocol(self,_):
        from turtle_loop.codex_client import output_contract
        user=json.dumps({'active_puzzle':{'answer':'private'},'current_question':'Question'})
        schema,key,override=output_contract(user)
        self.assertEqual(key,'label')
        self.assertEqual(set(schema['properties']['label']['enum']),{'yes','no','yes and no','irrelevant'})
        output='\n'.join(json.dumps(x) for x in [
            {'type':'item.completed','item':{'type':'agent_message','text':'{"label":"no"}'}},
            {'type':'turn.completed','usage':{}}])
        records=[]
        with patch('turtle_loop.codex_client.subprocess.run',return_value=subprocess.CompletedProcess([],0,output,'')):
            result=Client(PROFILE,'host',records.append).complete('Host',user)
        self.assertEqual(result.text,'no')
        self.assertEqual(records[0]['raw_text'],'{"label":"no"}')

    @patch('turtle_loop.codex_client.shutil.which',return_value='/bin/codex')
    def test_final_file_recovers_missing_event_without_second_call(self,_):
        from pathlib import Path
        def run(args,**kwargs):
            Path(args[args.index('--output-last-message')+1]).write_text('{"text":"recovered"}')
            return subprocess.CompletedProcess([],0,json.dumps({'type':'turn.completed','usage':{}}),'')
        records=[]
        with patch('turtle_loop.codex_client.subprocess.run',side_effect=run) as call:
            result=Client(PROFILE,'partner',records.append).complete('Review','Input')
        self.assertEqual(result.text,'recovered')
        self.assertEqual(call.call_count,1)
        self.assertEqual(records[0]['output_channel'],'last_message_file')
