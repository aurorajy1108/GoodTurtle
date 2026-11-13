import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from turtle_loop.grader import evaluate_final,missing_coverage_fields
from turtle_loop.engine import Recorder,ProtocolError,load_prompts,play,saved_grader_reason_recovery
from turtle_loop.providers import Client
from turtle_loop.coverage import UNIFIED_PROTOCOL,fact_specs
from turtle_loop.codex_client import output_contract
from test_loop import FakeClient,PUZZLE
from test_sessions import Response

class MissingCoverageTests(unittest.TestCase):
    def setUp(self):
        self.rubric=[{'id':'C1','weight':1,'criterion':'Elevator to underground garage.',
                      'required_facts':['He used an elevator.','The garage was underground.']}]
        self.raw={'checkpoints':[{'id':'C1','credit':0.5,'evidence':'He used an elevator.','reason':'Garage location omitted.'}],
                  'full_solution':False,'completion_note':'Location missing.','material_contradiction':False,
                  'irrelevant':False,'rubric_conflict':False}
        self.payload={'submitted_explanation':'He used an elevator.','reference_answer':'He used an elevator to an underground garage.',
                      'rubric':self.rubric,'grading_protocol':UNIFIED_PROTOCOL,'completion_requirements':[],
                      'required_facts':fact_specs(self.rubric),'required_completion':[]}
        self.addition={'fact_coverage':[{'id':'C1.F1','status':'covered','evidence':'He used an elevator.'},
                                       {'id':'C1.F2','status':'missing','evidence':''}],
                       'requirement_coverage':[],'contradictions':[], 'consistent_with_existing_judgment':True}

    def test_missing_arrays_completed_once_without_changing_original_credits(self):
        client=FakeClient(lambda i,p:json.dumps(self.raw if i==1 else self.addition))
        grade,raw=evaluate_final(client,'grade',self.payload)
        self.assertEqual(grade['partial_score'],0.5);self.assertFalse(grade['complete']);self.assertEqual(len(client.inputs),2)
        merged=json.loads(raw)
        for k,v in self.raw.items():self.assertEqual(merged[k],v)
        self.assertFalse(grade['coverage_completion']['judgments_changed'])
        self.assertTrue(json.loads(client.inputs[1][1])['coverage_completion'])

    def test_conflicting_coverage_is_rejected_without_resampling(self):
        addition=copy.deepcopy(self.addition);addition['fact_coverage'][1].update(status='covered',evidence='He used an elevator.')
        client=FakeClient(lambda i,p:json.dumps(self.raw if i==1 else addition))
        with self.assertRaisesRegex(ProtocolError,'conflicts with the original judgment'):evaluate_final(client,'grade',self.payload)
        self.assertEqual(len(client.inputs),2)
        addition['consistent_with_existing_judgment']=False
        client=FakeClient(lambda i,p:json.dumps(self.raw if i==1 else addition))
        with self.assertRaises(ProtocolError):evaluate_final(client,'grade',self.payload)
        self.assertEqual(len(client.inputs),2)

    def test_unknown_legacy_field_is_not_silently_dropped(self):
        raw={**self.raw,'extra_judgment':'new verdict'}
        self.assertIsNone(missing_coverage_fields(json.dumps(raw),self.payload))
        client=FakeClient(lambda i,p:json.dumps(raw))
        with self.assertRaises(ProtocolError):evaluate_final(client,'grade',self.payload)
        self.assertEqual(len(client.inputs),1)

    def test_present_arrays_are_preserved_and_cannot_be_replaced(self):
        raw={**self.raw,'fact_coverage':self.addition['fact_coverage']}
        addition={k:v for k,v in self.addition.items() if k!='fact_coverage'}
        client=FakeClient(lambda i,p:json.dumps(raw if i==1 else addition))
        grade,merged=evaluate_final(client,'grade',self.payload)
        self.assertEqual(json.loads(merged)['fact_coverage'],raw['fact_coverage'])
        client=FakeClient(lambda i,p:json.dumps(raw if i==1 else self.addition))
        with self.assertRaises(ProtocolError):evaluate_final(client,'grade',self.payload)

    def test_output_contract_has_only_missing_arrays_and_consistency_flag(self):
        schema,_,_=output_contract(json.dumps({'coverage_completion':True,'missing_fields':['fact_coverage']}))
        self.assertEqual(set(schema['properties']),{'fact_coverage','consistent_with_existing_judgment'})

    @patch.dict('os.environ',{'DEEPSEEK_API_KEY':'fixture'})
    def test_saved_judgment_recovers_with_no_player_host_or_full_grading_call(self):
        config={'max_questions':1,'session_mode':'persistent',**{r:{'provider':'deepseek','model':r} for r in ('player','host','grader')}}
        puzzle={**copy.deepcopy(PUZZLE),'rubric':self.rubric,'completion_requirements':[],'grading_protocol':UNIFIED_PROTOCOL}
        prompts=load_prompts();counts={'player':0,'host':0,'grader':0};requests=[]
        def api(req,**kw):
            body=json.loads(req.data);role=body['model'];counts[role]+=1;requests.append(body)
            text='FINAL\nHe used an elevator.' if role=='player' else json.dumps(self.raw if counts['grader']==1 else self.addition)
            return Response({'id':role+str(counts[role]),'choices':[{'message':{'content':text},'finish_reason':'stop'}]})
        def legacy(client,system,payload,audit=None):
            client.complete(system,json.dumps(payload));raise ProtocolError('Invalid evaluator fields')
        with tempfile.TemporaryDirectory() as tmp,patch('urllib.request.OpenerDirector.open',side_effect=api):
            rec=Recorder(Path(tmp)/'game',puzzle,config,prompts,echo=False)
            clients=lambda record:{r:Client(config[r],r,record.audit) for r in counts}
            with patch('turtle_loop.engine.evaluate_final',side_effect=legacy):stopped=play(puzzle,config,rec,clients(rec),prompts)
            calls=[json.loads(l) for l in (rec.folder/'api_calls.jsonl').read_text().splitlines()]
            proof=saved_grader_reason_recovery(stopped,calls,rec.turns,config,puzzle,missing_coverage=True)
            self.assertIsNotNone(proof)
            marker=rec.folder/'grader_coverage_completion.json';marker.write_text(json.dumps(proof))
            restored=Recorder.restore(rec.folder,puzzle,config,prompts,echo=False)
            result=play(puzzle,config,restored,clients(restored),prompts)
            self.assertEqual(result['status'],'completed');self.assertEqual(result['submissions'],1)
            self.assertEqual(result['final_partial_score'],0.5);self.assertEqual(result['counted_questions'],1)
            self.assertEqual(counts,{'player':1,'host':0,'grader':2});self.assertFalse(marker.exists())

    def test_field_aliases_preserve_values_and_parent_ids_must_match(self):
        from turtle_loop.coverage import normalize_coverage_metadata
        row={'fact_id':'C1.F1','coverage':'partial','evidence':'He used an elevator.','checkpoint_id':'C1'}
        fixed,changes=normalize_coverage_metadata({'fact_coverage':[row]},self.rubric,[])
        self.assertEqual(fixed['fact_coverage'],[{'id':'C1.F1','status':'partial','evidence':'He used an elevator.'}])
        self.assertEqual(len(changes),3)
        for extra in ({'id':'C2.F1'},{'status':'covered'},{'checkpoint_id':'C2'}):
            with self.assertRaises(ValueError):normalize_coverage_metadata({'fact_coverage':[{**row,**extra}]},self.rubric,[])

    @patch.dict('os.environ',{'DEEPSEEK_API_KEY':'fixture'})
    def test_saved_supplement_is_recovered_offline_without_another_model_call(self):
        from turtle_loop.grader import COVERAGE_COMPLETION_PROMPT
        config={'max_questions':1,'session_mode':'persistent',**{r:{'provider':'deepseek','model':r} for r in ('player','host','grader')}}
        puzzle={**copy.deepcopy(PUZZLE),'rubric':self.rubric,'completion_requirements':[],'grading_protocol':UNIFIED_PROTOCOL}
        addition=copy.deepcopy(self.addition)
        for row in addition['fact_coverage']:
            row['fact_id']=row.pop('id');row['coverage']=row.pop('status');row['checkpoint_id']='C1'
        prompts=load_prompts();counts={'player':0,'host':0,'grader':0}
        def api(req,**kw):
            body=json.loads(req.data);role=body['model'];counts[role]+=1
            text='FINAL\nHe used an elevator.' if role=='player' else json.dumps(self.raw if counts['grader']==1 else addition)
            return Response({'id':role+str(counts[role]),'choices':[{'message':{'content':text},'finish_reason':'stop'}]})
        def old_controller(client,system,payload,audit=None):
            client.complete(system,json.dumps(payload))
            client.complete(COVERAGE_COMPLETION_PROMPT,json.dumps({'coverage_completion':True,
                'original_evaluation':self.raw,'missing_fields':['fact_coverage','requirement_coverage','contradictions']}))
            raise ProtocolError('fact_coverage: invalid or duplicate coverage row')
        with tempfile.TemporaryDirectory() as tmp,patch('urllib.request.OpenerDirector.open',side_effect=api):
            rec=Recorder(Path(tmp)/'game',puzzle,config,prompts,echo=False)
            clients=lambda record:{r:Client(config[r],r,record.audit) for r in counts}
            with patch('turtle_loop.engine.evaluate_final',side_effect=old_controller):stopped=play(puzzle,config,rec,clients(rec),prompts)
            calls=[json.loads(l) for l in (rec.folder/'api_calls.jsonl').read_text().splitlines()]
            proof=saved_grader_reason_recovery(stopped,calls,rec.turns,config,puzzle,missing_coverage=True)
            self.assertIsNotNone(proof);self.assertIn('grade',proof)
            marker=rec.folder/'grader_coverage_completion.json';marker.write_text(json.dumps(proof))
            restored=Recorder.restore(rec.folder,puzzle,config,prompts,echo=False)
            result=play(puzzle,config,restored,clients(restored),prompts)
            self.assertEqual(result['final_partial_score'],0.5);self.assertEqual(result['counted_questions'],1)
            self.assertEqual(counts,{'player':1,'host':0,'grader':2});self.assertFalse(marker.exists())
