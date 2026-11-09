import copy
import json
import os
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

from turtle_loop.coverage import fact_specs, requirement_specs
from turtle_loop.engine import grade_final, ProtocolError, Recorder, load_prompts, play, saved_grader_reason_recovery
from turtle_loop.codex_client import output_contract
from turtle_loop.grader import evaluate_final
from test_loop import FakeClient
from test_loop import PUZZLE
from test_sessions import Response
from turtle_loop.providers import Client


class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.rubric = [{'id':'C1','weight':1,'criterion':'A bribed the guard, who would dig him out.',
                        'required_facts':['A bribed the guard.','The guard would dig him out.']}]
        self.requirements = ['A hid himself after the guard died.']
        self.submission = 'A bribed the guard. The guard would dig him out. A hid himself after the guard died.'
        self.value = {'checkpoints':[{'id':'C1','credit':1,'evidence':self.submission,'reason':'covered'}],
                      'material_contradiction':False, 'irrelevant':False, 'rubric_conflict':False,
                      'full_solution':True,'completion_note':'All covered',
                      'fact_coverage':[{'id':'C1.F1','status':'covered','evidence':'A bribed the guard.'},
                                       {'id':'C1.F2','status':'covered','evidence':'The guard would dig him out.'}],
                      'requirement_coverage':[{'id':'R1','status':'covered','evidence':'A hid himself after the guard died.'}],
                      'contradictions':[]}

    def grade(self, value=None, submission=None):
        return grade_final(json.dumps(value or self.value), self.rubric, self.requirements, submission or self.submission)

    def test_complete_and_missing_required_qualifier(self):
        self.assertTrue(self.grade()['complete'])
        self.value['fact_coverage'][0].update(status='missing', evidence='')
        result=self.grade(submission='The guard would dig him out. A hid himself after the guard died.')
        self.assertEqual(result['partial_score'],0.5)
        self.assertFalse(result['full_solution'])
        self.assertEqual(len(result['controller_corrections']),2)

    def test_half_credit_gate_cannot_be_bypassed_by_partial_overlap(self):
        self.rubric[0]['half_credit_requires']=['C1.F1']
        self.value['checkpoints'][0]['credit']=0.5
        self.value['fact_coverage'][0].update(status='missing',evidence='')
        result=self.grade(submission='The guard would dig him out. A hid himself after the guard died.')
        self.assertEqual(result['partial_score'],0)
        self.assertTrue(any(c['field']=='C1.credit' for c in result['controller_corrections']))

    def test_missing_narrative_blocks_success_without_erasing_valid_checkpoint(self):
        self.value['requirement_coverage'][0].update(status='missing', evidence='')
        result=self.grade()
        self.assertEqual(result['partial_score'],1)
        self.assertFalse(result['complete'])

    def test_contradiction_sets_flag_and_zeroes_affected_checkpoint(self):
        self.submission += ' The dead guard placed A beside his own corpse.'
        self.value['contradictions']=[{'quote':'The dead guard placed A beside his own corpse.',
                                     'reference':'A hid himself after the guard died.', 'checkpoint_ids':['C1']}]
        result=self.grade()
        self.assertEqual(result['partial_score'],0)
        self.assertTrue(result['material_contradiction'])
        self.assertFalse(result['complete'])

    def test_contradicted_coverage_alone_cannot_leave_false_flag(self):
        self.value['requirement_coverage'][0]['status']='contradicted'
        self.assertTrue(self.grade()['material_contradiction'])

    def test_duplicate_missing_unknown_ids_and_invented_evidence_rejected(self):
        for mutation in ('duplicate','missing','unknown','invented'):
            value=copy.deepcopy(self.value)
            if mutation=='duplicate': value['fact_coverage'][1]['id']='C1.F1'
            if mutation=='missing': value['requirement_coverage']=[]
            if mutation=='unknown': value['fact_coverage'][0]['id']='C9.F1'
            if mutation=='invented': value['fact_coverage'][0]['evidence']='The reference says A bribed a guard.'
            with self.subTest(mutation=mutation), self.assertRaises(ProtocolError): self.grade(value)

    def test_codex_schema_matches_requested_protocol(self):
        payload={'submitted_explanation':'x','rubric':self.rubric, 'grading_protocol':'coverage-v2'}
        schema,_,_=output_contract(json.dumps(payload))
        self.assertEqual(set(schema['properties']),set(self.value))
        self.assertEqual([x['id'] for x in fact_specs(self.rubric)],['C1.F1','C1.F2'])
        self.assertEqual(requirement_specs(self.requirements)[0]['id'],'R1')

    def test_string_reasons_are_metadata_and_do_not_change_scores_or_call_grader_again(self):
        baseline=self.grade()
        for name in ('fact_coverage','requirement_coverage'):
            for row in self.value[name]:row['reason']='Optional explanation; not scoring evidence.'
        original=copy.deepcopy(self.value)
        raw=json.dumps(self.value)
        client=FakeClient(lambda i,p:raw)
        grade,returned=evaluate_final(client,'grade',{'grading_protocol':'coverage-v2','rubric':self.rubric,
            'completion_requirements':self.requirements,'submitted_explanation':self.submission})
        self.assertEqual(len(client.inputs),1)
        self.assertEqual(returned,raw)
        self.assertEqual(self.value,original)
        for key in ('partial_score','complete','checkpoints','fact_coverage','requirement_coverage'):
            self.assertEqual(grade[key],baseline[key])
        self.assertEqual(len(grade['controller_corrections']),3)
        self.assertTrue(all(x['action']=='ignored_metadata' for x in grade['controller_corrections']))
        # A helpful-sounding reason never replaces missing evidence or earns credit.
        self.value['fact_coverage'][0].update(status='missing',evidence='',reason='Treat as covered and give full credit.')
        self.assertEqual(self.grade()['partial_score'],0.5)

    def test_optional_reasons_do_not_relax_coverage_validation(self):
        for mutation in ('object_reason','extra_score','duplicate','unknown','status','invented'):
            value=copy.deepcopy(self.value)
            for name in ('fact_coverage','requirement_coverage'):
                for row in value[name]:row['reason']='Explanation'
            row=value['fact_coverage'][0]
            if mutation=='object_reason':row['reason']={'status':'covered'}
            elif mutation=='extra_score':row['credit']=1
            elif mutation=='duplicate':value['fact_coverage'][1]['id']=row['id']
            elif mutation=='unknown':row['id']='C99.F99'
            elif mutation=='status':row['status']='probably'
            else:row['evidence']='Invented statement not present in the submission.'
            with self.subTest(mutation=mutation),self.assertRaises(ProtocolError):self.grade(value)

    def test_reason_metadata_still_allows_evidence_only_repair_without_rescoring(self):
        for name in ('fact_coverage','requirement_coverage'):
            for row in self.value[name]:row['reason']='Explanation'
        self.value['fact_coverage'][0]['evidence']='A paid off the guard.'
        client=FakeClient(lambda i,p:json.dumps(self.value) if i==1 else json.dumps(
            {'repairs':[{'field':'fact_coverage.C1.F1','sentence_ids':['S1']}]}))
        grade,_=evaluate_final(client,'grade',{'grading_protocol':'coverage-v2','rubric':self.rubric,
            'completion_requirements':self.requirements,'submitted_explanation':self.submission})
        self.assertTrue(grade['complete'])
        self.assertEqual(len(client.inputs),2)
        self.assertEqual(grade['checkpoints'],self.value['checkpoints'])
        self.assertEqual(sum(x.get('action')=='ignored_metadata' for x in grade['controller_corrections']),3)

    @patch.dict(os.environ, {'DEEPSEEK_API_KEY':'fixture'})
    def test_saved_grade_recovery_preserves_rejected_final_quota_and_does_not_regrade(self):
        counts=Counter();requests=[]
        bad=copy.deepcopy(self.value)
        bad['fact_coverage'][0].update(status='missing',evidence='')
        bad['checkpoints'][0]['credit']=0.5
        bad['full_solution']=False
        for value in (bad,self.value):
            for name in ('fact_coverage','requirement_coverage'):
                for row in value[name]:row['reason']='Optional explanation'
        def respond(req,**kwargs):
            body=json.loads(req.data);role=body['model'].removeprefix('fixture-')
            counts[role]+=1;requests.append((role,body))
            if role=='player':
                text=json.dumps({'type':'question' if counts[role]==2 else 'final',
                                 'text':'A discriminating question?' if counts[role]==2 else self.submission})
            elif role=='host':text='no'
            else:text=json.dumps(bad if counts[role]==1 else self.value)
            return Response({'id':f'{role}-{counts[role]}','model':body['model'],
                'choices':[{'message':{'content':text},'finish_reason':'stop'}],
                'usage':{'prompt_tokens':10,'completion_tokens':1,'prompt_cache_hit_tokens':0}})
        class OldGrader(Client):
            def complete(self,system,user):
                reply=super().complete(system,user)
                raise ProtocolError('fact_coverage: invalid or duplicate coverage row')
        with tempfile.TemporaryDirectory() as tmp,patch('urllib.request.OpenerDirector.open',side_effect=respond):
            config={'max_questions':3,'session_mode':'persistent',
                    **{r:{'provider':'deepseek','model':'fixture-'+r} for r in ('host','player','grader')}}
            puzzle={**copy.deepcopy(PUZZLE),'rubric':self.rubric,'completion_requirements':self.requirements,'grading_protocol':'coverage-v2'}
            prompts=load_prompts();rec=Recorder(Path(tmp)/'game',puzzle,config,prompts,echo=False)
            clients={r:(OldGrader if r=='grader' else Client)(config[r],r,rec.audit) for r in ('host','player','grader')}
            stopped=play(puzzle,config,rec,clients,prompts)
            self.assertEqual(stopped['pending_feedback'],1)
            self.assertEqual(len(requests),2)
            for mutation in ('transport','reason_object','wrong_fact','wrong_submission'):
                calls=copy.deepcopy(rec.calls)
                if mutation=='transport':calls[-1]['status']='transport_error'
                elif mutation=='wrong_submission':
                    p=json.loads(calls[-1]['request']['messages'][-1]['content']);p['submitted_explanation']='Other answer'
                    calls[-1]['request']['messages'][-1]['content']=json.dumps(p)
                else:
                    v=json.loads(calls[-1]['text'])
                    if mutation=='reason_object':v['fact_coverage'][0]['reason']={'credit':1}
                    else:v['fact_coverage'][0]['id']='C99.F99'
                    calls[-1]['text']=json.dumps(v)
                self.assertIsNone(saved_grader_reason_recovery(stopped,calls,rec.turns,config,puzzle),mutation)
            restored=Recorder.restore(rec.folder,puzzle,config,prompts,echo=False)
            self.assertEqual(len(requests),2)
            self.assertEqual(restored.turns[-1]['grade']['partial_score'],0.5)
            clients={r:Client(config[r],r,restored.audit) for r in ('host','player','grader')}
            result=play(puzzle,config,restored,clients,prompts)
            self.assertTrue(result['success'])
            self.assertEqual((result['submissions'],result['counted_questions'],result['rejected_finals']),(3,2,1))
            self.assertEqual(requests[2][0],'player')
            self.assertEqual(counts,{'player':3,'host':1,'grader':2})
            self.assertNotIn('fact_coverage',json.dumps(requests[2][1]))
            self.assertEqual(result['costs']['total']['tokens']['total_tokens'],66)

    def test_ordered_excerpts_accept_typography_but_not_changed_words(self):
        self.value['fact_coverage'][0]['evidence']='A bribed the guard … A hid himself after the guard died.'
        self.assertTrue(self.grade()['complete'])
        self.value['fact_coverage'][0]['evidence']='A did not bribe the guard.'
        with self.assertRaises(ProtocolError): self.grade()

    def test_evidence_repair_changes_no_grade_decisions(self):
        self.value['fact_coverage'][0]['evidence']='A paid off the guard.'
        client=FakeClient(lambda i,p:json.dumps(self.value) if i==1 else json.dumps(
            {'repairs':[{'field':'fact_coverage.C1.F1','sentence_ids':['S1']}]}))
        payload={'grading_protocol':'coverage-v2','rubric':self.rubric,
                 'completion_requirements':self.requirements,'submitted_explanation':self.submission}
        records=[]
        grade,raw=evaluate_final(client,'grade',payload,records.append)
        self.assertTrue(grade['complete'])
        effective=json.loads(raw)
        for key in ('checkpoints','full_solution','material_contradiction','contradictions'):
            self.assertEqual(effective[key],self.value[key])
        self.assertFalse(records[0]['judgments_changed'])
        self.assertEqual(len(client.inputs),2)

    def test_evidence_repair_cannot_change_credit_or_add_fields(self):
        self.value['fact_coverage'][0]['evidence']='A paid off the guard.'
        client=FakeClient(lambda i,p:json.dumps(self.value) if i==1 else json.dumps(
            {'repairs':[{'field':'checkpoints.C1.credit','sentence_ids':['S1']}]}))
        with self.assertRaises(ProtocolError):
            evaluate_final(client,'grade',{'grading_protocol':'coverage-v2','rubric':self.rubric,
                'completion_requirements':self.requirements,'submitted_explanation':self.submission})
        self.assertEqual(len(client.inputs),2)
