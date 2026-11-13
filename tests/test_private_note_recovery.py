import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import test_budgeted_agents as fixtures
from test_loop import PUZZLE
from turtle_loop.engine import Recorder,load_prompts,play
from turtle_loop.private_note_recovery import saved_private_note_recovery
from turtle_loop.providers import APIError,Client


@patch.dict('os.environ',{'DEEPSEEK_API_KEY':'fixture'})
class PrivateNoteRecoveryTests(unittest.TestCase):
    def fixture(self):
        h=fixtures.BudgetedAgentsTests();base=h.api(mas=True)
        def api(req,**kw):
            response=base(req,**kw);role,body,payload=h.seen[-1]
            if role in ('player','partner') and payload['solver_phase']['slot']==2 and payload['solver_phase']['phase']=='review':
                response.data['choices'][0]['finish_reason']='length'
                response.data['choices'][0]['message']['content']='PRIVATE_INCOMPLETE_NOTE: verify the identity before'
            return response
        return h,api

    def test_fresh_private_truncation_continues_without_regenerating_note_or_leaking_to_partner(self):
        helper,api=self.fixture();config=helper.config();prompts=load_prompts()
        budget={'generation_cap':6,'output_token_cap':12000,'submission_cap':4}
        with tempfile.TemporaryDirectory() as tmp,patch('urllib.request.OpenerDirector.open',side_effect=api):
            rec=Recorder(Path(tmp)/'game',PUZZLE,config,prompts,echo=False)
            ledger,clients=helper.clients(config,rec,budget,True,True)
            result=play(PUZZLE,config,rec,clients,prompts)
            self.assertTrue(result['success']);self.assertEqual(result['submissions'],4)
            self.assertEqual(ledger.status()['generations'],6)
            truncated=[c for c in rec.calls if c.get('finish_reason')=='length']
            self.assertEqual(len(truncated),1);self.assertTrue(truncated[0]['accepted_incomplete_private_note'])
            next_action=next(p for _,_,p in helper.seen if p.get('solver_phase',{}).get('slot')==2 and p['solver_phase']['phase']=='action')
            self.assertEqual(len(next_action['solver_phase']['incomplete_private_notes']),1)
            shared=(rec.folder/'shared_dialogue.jsonl').read_text()
            self.assertNotIn('PRIVATE_INCOMPLETE_NOTE',shared)

    def test_saved_mas_note_resumes_original_actor_action_and_counts_paid_note_once(self):
        helper,api=self.fixture();config=helper.config();prompts=load_prompts()
        budget={'generation_cap':6,'output_token_cap':12000,'submission_cap':4}
        with tempfile.TemporaryDirectory() as tmp,patch('urllib.request.OpenerDirector.open',side_effect=api):
            rec=Recorder(Path(tmp)/'game',PUZZLE,config,prompts,echo=False)
            ledger,clients=helper.clients(config,rec,budget,True,True)
            with patch('turtle_loop.providers.private_note_truncation',return_value=False):
                stopped=play(PUZZLE,config,rec,clients,prompts)
            self.assertEqual(stopped['status'],'error');self.assertEqual(stopped['submissions'],1)
            raw=[json.loads(x) for x in (rec.folder/'api_calls.jsonl').read_text().splitlines()]
            proof=saved_private_note_recovery(stopped,raw,rec.turns,config,rec.folder)
            self.assertIsNotNone(proof)
            for mutation in ('action','refusal','changed_text','changed_usage'):
                calls=copy.deepcopy(raw)
                if mutation=='action':calls[-1]['reflection_phase']='action'
                elif mutation=='refusal':calls[-1]['finish_reason']='refusal'
                elif mutation=='changed_text':calls[-1]['text']=''
                else:calls[-1]['usage']={}
                self.assertIsNone(saved_private_note_recovery(stopped,calls,rec.turns,config,rec.folder),mutation)
            before=len(helper.seen);shared=(rec.folder/'shared_dialogue.jsonl').read_text()
            (rec.folder/'private_note_recovery.json').write_text(json.dumps(proof))
            rec=Recorder.restore(rec.folder,PUZZLE,config,prompts,echo=False)
            ledger,clients=helper.clients(config,rec,budget,True,True)
            result=play(PUZZLE,config,rec,clients,prompts)
            self.assertTrue(result['success']);self.assertEqual(result['submissions'],4)
            self.assertEqual(ledger.status()['generations'],6)
            self.assertEqual(helper.seen[before][0],'partner')
            self.assertEqual(helper.seen[before][2]['solver_phase']['phase'],'action')
            self.assertEqual(sum(c.get('finish_reason')=='length' for c in rec.calls),1)
            self.assertTrue((rec.folder/'shared_dialogue.jsonl').read_text().startswith(shared))
            self.assertFalse((rec.folder/'private_note_recovery.json').exists())

    def test_truncated_action_is_still_rejected_even_with_private_note_flag(self):
        records=[];client=Client({'provider':'deepseek','model':'test','max_retries':0},'player',records.append)
        client.accept_private_note_length=True
        response=fixtures.Response({'id':'r','choices':[{'message':{'content':'QUESTION\nPartial question'},'finish_reason':'length'}]})
        with patch.object(client.opener,'open',return_value=response),self.assertRaises(APIError):
            client.complete('system',json.dumps({'solver_phase':{'phase':'action','force_final':False}}))
        self.assertEqual(len(records),1)
        self.assertNotIn('accepted_incomplete_private_note',records[0])
