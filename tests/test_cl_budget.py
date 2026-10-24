"""Exercise full 100-slot A/B episodes without billable requests."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from turtle_loop.experiments import main
from test_loop import FakeClient, PUZZLE, evaluated

class CLBudgetTests(unittest.TestCase):
    def test_answer_reveal_and_independent_100_slots_for_every_target(self):
        for source_succeeds in (False, True):
            with self.subTest(source_succeeds=source_succeeds), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp)
                puzzles=[]
                for pid in ('A','B'):
                    p=copy.deepcopy(PUZZLE)
                    p.update(id='CL_'+pid,opening='OPEN_'+pid,answer='FULL_'+pid+'\nSecond paragraph: complete explanation.')
                    puzzles.append(p)
                dataset=root/'data.json';dataset.write_text(json.dumps({'schema_version':1,'puzzles':puzzles}))
                config=root/'config.json';config.write_text(json.dumps({'max_questions':100,'host':{'provider':'openai','model':'fixture'},'player':{'provider':'openai','model':'fixture'}}))
                groups=root/'groups.json';groups.write_text(json.dumps({'groups':[{'id':'G','puzzles':['CL_A','CL_B'],'relation':'positive'}]}))
                player_calls=[];hosts=[];memory=[]
                def factory(profile,role,audit):
                    session=[]
                    if role=='player':player_calls.append(session)
                    def reply(i,payload):
                        if role=='player':
                            session.append(payload)
                            if i==1:
                                self.assertEqual(payload['visible_history'],[])
                                self.assertIn('Used question-equivalents: 0.',payload['turn_control'])
                            if i==100:self.assertIn('mandatory last turn',payload['turn_control'])
                            return json.dumps({'type':'final' if i in (1,100) else 'question','text':f'{payload["opening"]} attempt {i}'})
                        if role=='host':hosts.append(payload);return 'no'
                        if role=='memory':memory.append(payload);return 'Lossy summary intentionally omitting the answer.'
                        return evaluated() if source_succeeds and payload['opening']=='OPEN_A' else evaluated((0,0))
                    return FakeClient(reply)
                out=root/'out'
                with patch('turtle_loop.cli.validate_profile'),patch('turtle_loop.experiments.Client',side_effect=factory):
                    code=main(['continual','--dataset',str(dataset),'--config',str(config),'--groups',str(groups),
                               '--group','G','--pair','CL_A:CL_B','--memory','both','--repeat','1','--quiet','--out',str(out)])
                self.assertEqual(code,0)
                self.assertEqual(len(player_calls[0]),1 if source_succeeds else 100)
                self.assertNotIn('FULL_A',json.dumps(player_calls[0]))
                targets=player_calls[1:]
                self.assertEqual(len(targets),3)
                for session in targets:
                    self.assertEqual(len(session),100)
                    self.assertNotIn('FULL_B',json.dumps(session))
                    self.assertNotIn('SECRET_RUBRIC',json.dumps(session))
                    if 'prior_experience' in session[0]:
                        self.assertEqual(session[0]['prior_experience']['revealed_source_answer'],puzzles[0]['answer'])
                    else:self.assertNotIn('FULL_A',json.dumps(session))
                self.assertEqual(sum('prior_experience' in s[0] for s in targets),2)
                for f in out.glob('*_*/result.json'):
                    if f.parent.name.endswith('_source'):continue
                    r=json.loads(f.read_text())
                    self.assertEqual((r['submissions'],r['host_questions'],r['rejected_finals'],r['counted_questions']),(100,98,2,100))
                reveal=next(out.glob('*_source/source_answer_reveal.json'))
                self.assertFalse(json.loads(reveal.read_text())['counts_as_question'])
                self.assertEqual(memory[0]['revealed_source_answer'],puzzles[0]['answer'])
                self.assertNotIn('FULL_A',json.dumps([h for h in hosts if h['active_puzzle']['opening']=='OPEN_B']))
