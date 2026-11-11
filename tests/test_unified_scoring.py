"""Score=100% and solved are the same contract, without changing legacy runs."""
import copy
import itertools
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from turtle_loop.coverage import UNIFIED_PROTOCOL, fact_specs
from turtle_loop.dataset import load_dataset, validate_dataset
from turtle_loop.engine import grade_final, play, Recorder, load_prompts
from turtle_loop.codex_client import output_contract
from test_loop import FakeClient, PUZZLE

ROOT=Path(__file__).resolve().parents[1]

class UnifiedScoringTests(unittest.TestCase):
    def setUp(self):
        self.rubric=[{'id':'C1','weight':0.4,'criterion':'crime','required_facts':['Killed wife.']},
                     {'id':'C2','weight':0.6,'criterion':'forgery','required_facts':['Forged letter.','Failed handwriting.']}]
        self.text='Killed wife. Forged letter. Failed handwriting.'
        self.value={'checkpoints':[{'id':p['id'],'credit':1,'evidence':self.text,'reason':'facts'} for p in self.rubric],
                    'full_solution':False,'completion_note':'Legacy independent veto.',
                    'material_contradiction':False,'irrelevant':False,'rubric_conflict':False,
                    'fact_coverage':[{'id':f['id'],'status':'covered','evidence':f['fact']} for f in fact_specs(self.rubric)],
                    'requirement_coverage':[],'contradictions':[]}

    def grade(self,v=None):
        return grade_final(json.dumps(v or self.value),self.rubric,[],self.text,UNIFIED_PROTOCOL)

    def test_full_score_ends_even_when_legacy_flag_says_no(self):
        g=self.grade();self.assertEqual(g['partial_score'],1);self.assertTrue(g['complete']);self.assertEqual(g['label'],'yes')
        self.assertTrue(g['full_solution']);self.assertTrue(g['controller_corrections'])

    def test_partial_missing_contradicted_never_full(self):
        for statuses in itertools.product(('covered','partial','missing','contradicted'),repeat=3):
            v=copy.deepcopy(self.value)
            for r,s in zip(v['fact_coverage'],statuses):
                r['status']=s
                if s=='missing':r['evidence']=''
            g=self.grade(v)
            self.assertEqual(g['partial_score']==1,g['complete'],statuses)
            self.assertEqual(g['complete'],all(s=='covered' for s in statuses))

    def test_stale_checkpoint_credits_cannot_override_fact_coverage(self):
        v=copy.deepcopy(self.value);v['checkpoints'][0]['credit']=0
        self.assertEqual(self.grade(v)['partial_score'],1)
        v['fact_coverage'][0].update(status='missing',evidence='');v['full_solution']=True
        self.assertEqual(self.grade(v)['partial_score'],0.6);self.assertFalse(self.grade(v)['complete'])

    def test_localized_contradiction_reduces_corresponding_score(self):
        v=copy.deepcopy(self.value);v['contradictions']=[{'quote':'Killed wife.','reference':'fictional example of a material conflict','checkpoint_ids':['C1']}]
        g=self.grade(v);self.assertEqual(g['partial_score'],0.6);self.assertFalse(g['complete'])

    def test_unlocalized_veto_or_rubric_conflict_needs_review_not_full_score(self):
        for key in ('material_contradiction','rubric_conflict','irrelevant'):
            v=copy.deepcopy(self.value);v[key]=True;g=self.grade(v)
            self.assertIsNone(g['partial_score']);self.assertTrue(g['rubric_conflict']);self.assertFalse(g['complete'])

    def test_no_unscored_requirements_allowed(self):
        with self.assertRaises(ValueError):
            grade_final(json.dumps(self.value),self.rubric,['unscored'],self.text,UNIFIED_PROTOCOL)

    def test_all_fifty_mappings_preserve_stories_weights_and_original_facts(self):
        old=load_dataset(ROOT/'data/annotations/turtle50_v4/private.json')['puzzles']
        new=load_dataset(ROOT/'data/annotations/turtle50_v5/private.json')['puzzles']
        mapping=json.loads((ROOT/'data/annotations/turtle50_v5/completion_mapping.json').read_text())['puzzles']
        self.assertEqual(len(new),50)
        for before,after,m in zip(old,new,mapping):
            self.assertEqual(before['id'],after['id']);self.assertEqual(before['answer'],after['answer']);self.assertEqual(before['opening'],after['opening'])
            self.assertEqual(after['completion_requirements'],[]);self.assertEqual(after['grading_protocol'],UNIFIED_PROTOCOL)
            self.assertEqual(len(m['requirements']),len(before['completion_requirements']))
            points={p['id']:p for p in after['rubric']}
            for b,a in zip(before['rubric'],after['rubric']):
                self.assertEqual(b['weight'],a['weight']);self.assertTrue(set(b['required_facts'])<=set(a['required_facts']))
            for i,r in enumerate(m['requirements']):
                self.assertEqual(r['source_text'],before['completion_requirements'][i])
                if r['checkpoint_id']:self.assertIn(r['scored_fact'],points[r['checkpoint_id']]['required_facts'])
                else:self.assertIn(r['source_text'],after['grading_notes'])

    def test_every_puzzle_full_coverage_and_every_mapped_omission(self):
        data=load_dataset(ROOT/'data/annotations/turtle50_v5/private.json')
        for puzzle in data['puzzles']:
            facts=fact_specs(puzzle['rubric']);submission=' '.join(f['fact'] for f in facts)
            value={'checkpoints':[{'id':p['id'],'credit':1,'evidence':submission,'reason':'fixture'} for p in puzzle['rubric']],
                   'full_solution':False,'completion_note':'Legacy veto',
                   'material_contradiction':False,'irrelevant':False,'rubric_conflict':False,
                   'fact_coverage':[{'id':f['id'],'status':'covered','evidence':f['fact']} for f in facts],
                   'requirement_coverage':[],'contradictions':[]}
            grade=lambda v:grade_final(json.dumps(v),puzzle['rubric'],[],submission,UNIFIED_PROTOCOL)
            self.assertTrue(grade(value)['complete'],puzzle['id'])
            self.assertEqual(grade(value)['partial_score'],1,puzzle['id'])
            for index in range(len(facts)):
                omitted=copy.deepcopy(value);omitted['fact_coverage'][index].update(status='missing',evidence='')
                self.assertFalse(grade(omitted)['complete'],(puzzle['id'],facts[index]['id']))
                self.assertLess(grade(omitted)['partial_score'],1)

    def test_transport_schema_includes_fact_evidence(self):
        schema,_,_=output_contract(json.dumps({'grading_protocol':UNIFIED_PROTOCOL,'submitted_explanation':self.text,'rubric':self.rubric}))
        self.assertIn('fact_coverage',schema['properties'])

    def test_loop_stops_after_one_full_final_and_conflicts_stop_for_review(self):
        for conflict in (False,True):
            v=copy.deepcopy(self.value);v['rubric_conflict']=conflict
            puzzle={**copy.deepcopy(PUZZLE),'rubric':self.rubric,'completion_requirements':[],'grading_protocol':UNIFIED_PROTOCOL}
            config={'max_questions':100,'player':{'provider':'mock'},'host':{'provider':'mock'},'grader':{'provider':'mock'}}
            clients={'player':FakeClient(lambda i,p:json.dumps({'type':'final','text':self.text})),'host':FakeClient(lambda i,p:None),'grader':FakeClient(lambda i,p:json.dumps(v))}
            with tempfile.TemporaryDirectory() as folder:
                rec=Recorder(Path(folder)/'game',puzzle,config,load_prompts(),echo=False)
                result=play(puzzle,config,rec,clients,load_prompts())
                self.assertEqual(result['submissions'],1)
                self.assertEqual(result['status'],'needs_review' if conflict else 'completed')
                self.assertEqual(result['stop_reason'],'rubric_conflict' if conflict else 'solved')
                self.assertEqual(result['final_partial_score'],None if conflict else 1)
