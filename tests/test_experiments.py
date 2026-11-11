import copy
import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

from turtle_loop.experiments import TeamPlayer, experience, make_plan, write_reports, main
from turtle_loop.engine import Recorder, load_prompts, play
from test_loop import PUZZLE, FakeClient, evaluated


class ExperimentTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)

    def recorder(self):
        return Recorder(self.root/'game',PUZZLE,{'max_questions':3},load_prompts(),echo=False)

    def test_context_only_reaches_player_requirements_only_grader(self):
        puzzle=copy.deepcopy(PUZZLE)
        puzzle['completion_requirements']=['SECRET_REQUIRED']
        rec=self.recorder()
        players=FakeClient(lambda i,p:json.dumps({'type':'question' if i==1 else 'final','text':'attempt'}))
        host=FakeClient(lambda i,p:'no');grader=FakeClient(lambda i,p:evaluated())
        result=play(puzzle,{'max_questions':3},rec,{'player':players,'host':host,'grader':grader},load_prompts(),{'memory':'SOURCE_ONLY'})
        self.assertTrue(result['success'])
        self.assertIn('SOURCE_ONLY',str(players.inputs))
        self.assertNotIn('SECRET',str(players.inputs))
        self.assertNotIn('SOURCE_ONLY',str(host.inputs)+str(grader.inputs))
        self.assertIn('SECRET_REQUIRED',str(grader.inputs))

    def test_transfer_excludes_grades_and_gold_by_default(self):
        rec=self.recorder()
        rec.turns=[{'type':'final','text':'guess','label':'yes and no','grade':{'reason':'SECRET_RUBRIC'}}]
        value=experience(PUZZLE,rec,{'stop_reason':'budget_exhausted'},'none')
        self.assertNotIn('SECRET',json.dumps(value))
        gold=experience(PUZZLE,rec,{'stop_reason':'solved'},'answer')
        self.assertEqual(gold['revealed_source_answer'],PUZZLE['answer'])

    def test_alternating_shared_public_history(self):
        rec=self.recorder()
        a=FakeClient(lambda i,p:json.dumps({'type':'question','text':'leader'}))
        b=FakeClient(lambda i,p:json.dumps({'type':'final','text':'partner'}))
        team=TeamPlayer(a,b,'alternating',rec)
        team.complete('system',json.dumps({'visible_history':[]}))
        team.complete('system',json.dumps({'visible_history':[{'text':'leader','feedback':'no'}]}))
        self.assertEqual(len(a.inputs),1);self.assertEqual(len(b.inputs),1)
        self.assertIn('leader',str(b.inputs))
        self.assertTrue((rec.folder/'collaboration.html').exists())

    def test_discussion_counts_one_host_action_not_three(self):
        rec=self.recorder()
        leader=FakeClient(lambda i,p:json.dumps({'type':'final','text':'draft' if i%2 else 'revised'}))
        partner=FakeClient(lambda i,p:'Check the causal mechanism.')
        team=TeamPlayer(leader,partner,'discuss',rec)
        result=play(PUZZLE,{'max_questions':3},rec,{'player':team,'host':FakeClient(lambda i,p:'no'),'grader':FakeClient(lambda i,p:evaluated())},load_prompts())
        self.assertEqual(result['submissions'],1)
        self.assertEqual(len(leader.inputs),2);self.assertEqual(len(partner.inputs),1)
        self.assertEqual(rec.turns[0]['text'],'revised')
        self.assertNotIn('SECRET',str(partner.inputs))

    def test_same_agent_reflection_uses_no_partner_calls(self):
        rec=self.recorder()
        leader=FakeClient(lambda i,p:'Review.' if i==2 else json.dumps({'type':'final','text':'answer'}))
        partner=FakeClient(lambda i,p: self.fail('partner called'))
        TeamPlayer(leader,partner,'solo_reflect',rec).complete('system','{}')
        self.assertEqual(len(leader.inputs),3)

    def test_independent_partner_never_sees_draft_and_only_synthesis_is_hosted(self):
        rec=self.recorder()
        leader=FakeClient(lambda i,p:json.dumps({'type':'final','text':'PRIVATE_DRAFT' if i == 1 else 'synthesis'}))
        partner=FakeClient(lambda i,p:json.dumps({'type':'final','text':'alternative'}))
        team=TeamPlayer(leader,partner,'independent',rec)
        result=play(PUZZLE,{'max_questions':3},rec,
                    {'player':team,'host':FakeClient(lambda i,p:'no'),
                     'grader':FakeClient(lambda i,p:evaluated())},load_prompts())
        self.assertTrue(result['success'])
        self.assertEqual(result['submissions'],1)
        self.assertEqual(rec.turns[0]['text'],'PRIVATE_DRAFT')
        self.assertTrue(team.discussions[0]['selection_override'])
        self.assertEqual(leader.inputs[0],partner.inputs[0])
        self.assertNotIn('PRIVATE_DRAFT',str(partner.inputs))
        self.assertNotIn('SECRET',str(partner.inputs))
        self.assertEqual(json.loads(leader.inputs[1][1])['independent_action']['text'],'alternative')
        self.assertEqual(len(leader.inputs),2)
        self.assertEqual(len(partner.inputs),1)

    def test_team_cyclic_order_balances_complete_and_partial_cycles(self):
        args=Namespace(command='team',puzzle='all',repeat=4,seed=7,
                       strategies='solo,solo_reflect,discuss,independent')
        bank={'A':{'id':'A'},'B':{'id':'B'}}
        plan=make_plan(args,bank)
        self.assertEqual(plan,make_plan(args,bank))
        for pid in bank:
            local=sorted([x for x in plan if x['target']==pid],key=lambda x:x['repeat'])
            for position in range(4):
                self.assertEqual(len({x['conditions'][position] for x in local}),4)
                self.assertEqual(len({x['conditions'][position] for x in local[:3]}),3)

    def test_reports_stratify_puzzles_and_compare_reflection_control(self):
        blocks=[{'block':p,'target':p,'repeat':1,'conditions':['solo','solo_reflect','discuss','independent']} for p in ['A','B']]
        rows=[]
        for block in blocks:
            for cond in block['conditions']:
                rows.append({'block':block['block'],'puzzle_id':block['target'],'repeat':1,
                             'run_dir':'test','status':'completed','success':False,
                             'counted_questions':100,'submissions':100,'condition':cond,
                             'final_partial_score':.75 if block['target']=='A' else .25,
                             'usage':{'player':{'http_attempts':200,'provider_reported_usage':{'input_tokens':10}},
                                      'partner':{'http_attempts':100,'provider_reported_usage':{'input_tokens':5}}}})
        write_reports(self.root,rows,blocks,'team')
        data=json.loads((self.root/'condition_summary_by_puzzle.json').read_text())
        self.assertEqual(data['A/discuss']['final_partial_score']['mean'],.75)
        self.assertEqual(data['B/discuss']['final_partial_score']['mean'],.25)
        self.assertEqual(data['A/discuss']['solver_attempts']['mean'],300)
        self.assertEqual(data['A/discuss']['solver_input_tokens']['mean'],15)
        self.assertEqual(data['A/discuss']['solver_output_tokens']['n'],0)
        contrasts=json.loads((self.root/'reflection_contrasts.json').read_text())
        self.assertEqual(len(contrasts),4)
        self.assertTrue(all(c['valid_pair'] and c['score_gain']==0 for c in contrasts))
        rows[-1]['status']='error'
        write_reports(self.root,rows,blocks,'team')
        contrasts=json.loads((self.root/'reflection_contrasts.json').read_text())
        self.assertFalse(contrasts[-1]['valid_pair'])
        self.assertIsNone(contrasts[-1]['score_gain'])

    def test_plan_directions_overlaps_seed(self):
        args=Namespace(command='continual',groups=str(Path(__file__).resolve().parents[1]/'configs/transfer_groups.json'),group='G02,G04',pair=None,repeat=2,memory='both',seed=3)
        bank={f'TS{x:03d}':{} for x in (13,15,16)}
        plan=make_plan(args,bank)
        self.assertEqual(len(plan),16)
        self.assertEqual(plan,make_plan(args,bank))
        overlap=[x for x in plan if x['source']=='TS015' and x['target']=='TS016']
        self.assertEqual({x['relation_hypothesis'] for x in overlap},{'positive','negative'})
        args.pair='TS015:TS016'
        self.assertEqual(len(make_plan(args,bank)),4)

    def test_failed_pairs_not_question_savings_and_no_score_imputation(self):
        block={'block':'b','source':'A','target':'B','repeat':1,'group':'G','conditions':['direct','transcript']}
        base={'block':'b','puzzle_id':'B','repeat':1,'run_dir':'test','status':'completed','success':True,'counted_questions':4,'submissions':5,'final_partial_score':1}
        rows=[{**base,'condition':'direct'},{**base,'condition':'transcript','success':False,'counted_questions':100,'final_partial_score':.5}]
        write_reports(self.root,rows,[block],'continual')
        contrast=json.loads((self.root/'contrasts.json').read_text())[0]
        self.assertEqual(contrast['score_gain'],-.5)
        self.assertIsNone(contrast['question_saving_both_solved'])
        rows[1]['status']='error'
        write_reports(self.root,rows,[block],'continual')
        contrast=json.loads((self.root/'contrasts.json').read_text())[0]
        self.assertFalse(contrast['valid_pair']);self.assertIsNone(contrast['score_gain'])

    def test_cli_dry_run_all_team_modes_no_network(self):
        puzzle=copy.deepcopy(PUZZLE);puzzle['id']='TS002'
        data=self.root/'dataset.json';data.write_text(json.dumps({'schema_version':1,'puzzles':[puzzle]}))
        config=self.root/'config.json';config.write_text(json.dumps({'max_questions':3,'host':{'provider':'openai','model':'test'},'player':{'provider':'openai','model':'test'}}))
        out=self.root/'out'
        with patch('turtle_loop.experiments.Client',side_effect=AssertionError('API in dry-run')):
            result=main(['team','--dataset',str(data),'--config',str(config),'--repeat','1','--out',str(out),'--dry-run','--quiet'])
        self.assertEqual(result,0)
        rows=json.loads((out/'experiment_runs.json').read_text())
        self.assertEqual(len(rows),4)
        self.assertTrue(all(r['final_partial_score'] is None for r in rows))

    def test_full_continual_run_with_scripted_clients(self):
        puzzles=[]
        for pid in ('FIXTURE_A','FIXTURE_B'):
            puzzle=copy.deepcopy(PUZZLE)
            puzzle.update(id=pid,opening='PUBLIC_'+pid,answer='PRIVATE_'+pid)
            puzzles.append(puzzle)
        dataset=self.root/'data.json'
        dataset.write_text(json.dumps({'schema_version':1,'puzzles':puzzles}))
        config=self.root/'config.json'
        config.write_text(json.dumps({'max_questions':1,'host':{'provider':'openai','model':'fixture'},'player':{'provider':'openai','model':'fixture'}}))
        groups=self.root/'groups.json'
        groups.write_text(json.dumps({'groups':[{'id':'G','puzzles':['FIXTURE_A','FIXTURE_B'],'relation':'positive'}]}))
        seen=[]
        def factory(profile,role,audit):
            def answer(i,payload):
                if role=='player':
                    seen.append(payload)
                    return json.dumps({'type':'final','text':'PUBLIC_GUESS'})
                return evaluated()
            return FakeClient(answer)
        out=self.root/'actual'
        with patch('turtle_loop.cli.validate_profile'), patch('turtle_loop.experiments.Client',side_effect=factory):
            result=main(['continual','--dataset',str(dataset),'--config',str(config),'--groups',str(groups),
                         '--group','G','--pair','FIXTURE_A:FIXTURE_B','--memory','transcript','--repeat','1','--out',str(out),'--quiet'])
        self.assertEqual(result,0)
        self.assertEqual(len(seen),3)
        targets=[x for x in seen if x['opening']=='PUBLIC_FIXTURE_B']
        self.assertEqual(sum('prior_experience' in x for x in targets),1)
        transferred=next(x['prior_experience'] for x in targets if 'prior_experience' in x)
        self.assertEqual(transferred['history'][0]['text'],'PUBLIC_GUESS')
        self.assertEqual(transferred['revealed_source_answer'],'PRIVATE_FIXTURE_A')
        self.assertNotIn('PRIVATE_FIXTURE_B',json.dumps(seen))
        self.assertNotIn('PRIVATE_',json.dumps(next(x for x in targets if 'prior_experience' not in x)))
        self.assertNotIn('SECRET_',json.dumps(seen))
        contrasts=json.loads((out/'contrasts.json').read_text())
        self.assertTrue(contrasts[0]['valid_pair'])
        self.assertTrue(contrasts[0]['source_success'])
        self.assertEqual(contrasts[0]['score_gain'],0)
        folder=next(out.glob('*_transcript'))
        self.assertIn('PREVIOUS',json.loads((folder/'prompts.json').read_text())['player'])


if __name__=='__main__':
    unittest.main()
