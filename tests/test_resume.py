import json
import tempfile
import unittest
import copy
from unittest.mock import patch
from pathlib import Path
from turtle_loop.engine import Recorder, load_prompts, play
from turtle_loop.providers import APIError
from turtle_loop.experiments import TeamPlayer, main
from test_loop import PUZZLE, FakeClient, evaluated


class ResumeTests(unittest.TestCase):
    def test_batch_resume_reuses_completed_source_and_preserves_schedule(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);puzzles=[]
            for pid in ('FIXTURE_A','FIXTURE_B'):
                puzzle=copy.deepcopy(PUZZLE);puzzle.update(id=pid,opening=pid);puzzles.append(puzzle)
            (root/'data.json').write_text(json.dumps({'schema_version':1,'puzzles':puzzles}))
            (root/'config.json').write_text(json.dumps({'max_questions':3,'session_mode':'replay','host':{'provider':'openai','model':'fixture'},'player':{'provider':'openai','model':'fixture'}}))
            (root/'groups.json').write_text(json.dumps({'groups':[{'id':'G','puzzles':['FIXTURE_A','FIXTURE_B'],'directed_pairs':[['FIXTURE_A','FIXTURE_B']],'relation':'positive'}]}))
            argv=['continual','--dataset',str(root/'data.json'),'--config',str(root/'config.json'),
                  '--groups',str(root/'groups.json'),'--group','all','--memory','transcript','--repeat','1','--controls','answer_only',
                  '--on-error','stop','--quiet','--out',str(root/'out')]
            seen=[];fail=[True]
            def factory(profile,role,audit):
                def answer(i,payload):
                    if role=='player':
                        seen.append(payload['opening'])
                        if payload['opening']=='FIXTURE_B' and fail[0]:
                            audit({'role':role,'status':'invalid_response','raw_text':'',
                                   'diagnostics':[{'message':'usage limit'}]})
                            return APIError('quota')
                        return json.dumps({'type':'final','text':'guess'})
                    return evaluated()
                return FakeClient(answer)
            with patch('turtle_loop.cli.validate_profile'),patch('turtle_loop.experiments.Client',side_effect=factory):
                self.assertEqual(main(argv),1)
                fail[0]=False
                self.assertEqual(main(argv+['--resume']),0)
            self.assertEqual(seen.count('FIXTURE_A'),1)
            rows=json.loads((root/'out/experiment_runs.json').read_text())
            self.assertEqual(len(rows),4)
            self.assertTrue(all(r['status']=='completed' for r in rows))

    def test_pending_question_resumes_host_without_new_submission_or_quota_reset(self):
        with tempfile.TemporaryDirectory() as tmp:
            config={'max_questions':3};prompts=load_prompts()
            rec=Recorder(Path(tmp)/'game',PUZZLE,config,prompts,echo=False)
            def host(i,payload):
                if i==2:
                    rec.audit({'role':'host','status':'transport_error'})
                    return APIError('fixture interrupted transport')
                return 'no'
            before=play(PUZZLE,config,rec,{'player':FakeClient(lambda i,p:json.dumps({'type':'question','text':str(i)})),
                 'host':FakeClient(host),'grader':FakeClient(lambda i,p:evaluated())},prompts)
            self.assertEqual(before['submissions'],2)
            self.assertEqual(before['pending_feedback'],1)
            restored=Recorder.restore(rec.folder,PUZZLE,config,prompts,echo=False)
            seen=[]
            def player(i,payload):
                seen.append(payload)
                return json.dumps({'type':'final','text':'answer'})
            final=play(PUZZLE,config,restored,{'player':FakeClient(player),
                'host':FakeClient(lambda i,p:'no'),'grader':FakeClient(lambda i,p:evaluated((0,0)))},prompts)
            self.assertEqual(final['status'],'completed')
            self.assertEqual(final['counted_questions'],3)
            self.assertEqual(final['submissions'],3)
            self.assertEqual(len(seen),1)
            self.assertIn('Used question-equivalents: 2.',seen[0]['turn_control'])
            self.assertIn('mandatory last turn',seen[0]['turn_control'])
            self.assertEqual(len(seen[0]['visible_history']),2)

    def test_player_interruption_keeps_rejected_final_and_transfer_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            config={'max_questions':3};prompts=load_prompts()
            rec=Recorder(Path(tmp)/'game',PUZZLE,config,prompts,echo=False)
            context={'opening':'PREVIOUS','revealed_source_answer':'A ANSWER'}
            def player(i,payload):
                if i==2:
                    rec.audit({'role':'player','status':'invalid_response','raw_text':'',
                               'diagnostics':[{'message':"You've hit your usage limit"}]})
                    return APIError('quota')
                return json.dumps({'type':'final','text':'wrong'})
            play(PUZZLE,config,rec,{'player':FakeClient(player),'host':FakeClient(lambda i,p:'no'),
                'grader':FakeClient(lambda i,p:evaluated((0,0)))},prompts,context)
            restored=Recorder.restore(rec.folder,PUZZLE,config,prompts,echo=False)
            seen=[]
            def next_player(i,payload):
                seen.append(payload);return json.dumps({'type':'final','text':'correct'})
            result=play(PUZZLE,config,restored,{'player':FakeClient(next_player),'host':FakeClient(lambda i,p:'no'),
                'grader':FakeClient(lambda i,p:evaluated())},prompts,context)
            self.assertTrue(result['success'])
            self.assertEqual(result['submissions'],2)
            self.assertEqual(result['rejected_finals'],1)
            self.assertIn('Used question-equivalents: 1.',seen[0]['turn_control'])
            self.assertEqual(seen[0]['prior_experience'],context)
            with self.assertRaises(ValueError):Recorder.restore(rec.folder,PUZZLE,{'max_questions':100},prompts)

    def test_team_turn_order_restored_from_collaboration(self):
        with tempfile.TemporaryDirectory() as tmp:
            rec=Recorder(Path(tmp)/'game',PUZZLE,{'max_questions':100},load_prompts(),echo=False)
            rec.turns=[{'index':1,'type':'question','text':'x','forced':False,'label':'no'}]
            rec.append('collaboration.jsonl',{'turn':1,'strategy':'shared_buffer','actor':'A','published_turns':0})
            team=TeamPlayer(None,None,'shared_buffer',rec)
            self.assertEqual(team.turn,1)
            self.assertEqual(team.owners,[0])


if __name__=='__main__':unittest.main()
