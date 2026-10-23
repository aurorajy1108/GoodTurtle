import copy
import json
import unittest

from turtle_loop.coverage import fact_specs, requirement_specs
from turtle_loop.engine import grade_final, ProtocolError
from turtle_loop.codex_client import output_contract
from turtle_loop.grader import evaluate_final
from test_loop import FakeClient


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
