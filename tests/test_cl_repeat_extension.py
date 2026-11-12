import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts.extend_cl_repeats import prepare
from turtle_loop.experiments import main,fixed_source_checkpoint,same_player_prefix
from test_loop import PUZZLE,evaluated
from test_cl_session import response


@patch.dict('os.environ',{'DEEPSEEK_API_KEY':'fixture'})
class RepeatExtensionTests(unittest.TestCase):
    def test_recovery_never_reenables_a_disabled_auxiliary_formatter(self):
        from scripts.resume_study import format_overlay_policy
        current={'max_codex_calls_per_game':3,'enabled':True}
        self.assertEqual(format_overlay_policy(current,{'max_codex_calls_per_game':0})['max_codex_calls_per_game'],0)
        self.assertEqual(current['max_codex_calls_per_game'],3)

    def test_fixed_checkpoint_selection_does_not_depend_on_current_repeat(self):
        original={'condition':'source','puzzle_id':'A','block':'G_A_B_r02','repeat':2}
        self.assertEqual(fixed_source_checkpoint([original],'source','A'),original)
        self.assertIsNone(fixed_source_checkpoint([original],'source','C'))
        with self.assertRaises(ValueError):fixed_source_checkpoint([original,original],'source','A')

    def test_extension_runs_only_new_b_and_reuses_original_a_messages(self):
        repo=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            old=Path(tmp)/'old';snap=old/'runtime_snapshot'
            for directory in ('turtle_loop','prompts'):
                shutil.copytree(repo/directory,snap/directory,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
            (snap/'configs').mkdir();(snap/'data').mkdir();(snap/'scripts').mkdir()
            shutil.copy2(repo/'configs/player_format_repair.json',snap/'configs/player_format_repair.json')
            shutil.copy2(repo/'scripts/experiment.py',snap/'scripts/experiment.py')
            config={'session_mode':'persistent','max_questions':2,**{
                r:{'provider':'deepseek','model':r} for r in ('host','player','grader')}}
            puzzles=[{**copy.deepcopy(PUZZLE),'id':p,'opening':p+' opening','answer':p+' SECRET'} for p in ('A','B')]
            (snap/'data/dataset.json').write_text(json.dumps({'schema_version':1,'puzzles':puzzles}))
            (snap/'configs/study_groups.json').write_text(json.dumps({'groups':[{
                'id':'G','puzzles':['A','B'],'relation':'positive','directed_pairs':[['A','B']]}]}))
            (snap/'configs/run.json').write_text(json.dumps(config))
            args=['continual','--dataset',str(snap/'data/dataset.json'),'--config',str(snap/'configs/run.json'),
                  '--groups',str(snap/'configs/study_groups.json'),'--group','G','--repeat','2','--seed','3',
                  '--controls','answer_only','--quiet','--out',str(old/'continual')]
            requests=[]
            def api(req,**kw):
                body=json.loads(req.data);requests.append(body)
                text='Notes that are not the submitted action.\nFINAL submitted explanation' if body['model']=='player' else evaluated()
                return response('deepseek',len(requests),text)
            with patch('urllib.request.OpenerDirector.open',side_effect=api):
                self.assertEqual(main(args),0)
            rows=json.loads((old/'continual/experiment_runs.json').read_text())
            self.assertEqual(len(rows),7)
            original_source=next(r for r in rows if r['condition']=='source')
            source_calls=(old/'continual'/original_source['run_dir']/'api_calls.jsonl').read_bytes()
            hashes={str(p.relative_to(snap)):hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in snap.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
            (old/'snapshot_hashes.json').write_text(json.dumps(hashes))
            (old/'study_plan.json').write_text(json.dumps({'arguments':{'repeat':2},'jobs':[{
                'name':'continual','argv':[sys.executable,str(snap/'scripts/experiment.py'),*args]}]}))
            out=Path(tmp)/'extension'
            manifest=prepare(old,out,4)
            self.assertEqual(manifest['extension']['preserved_games'],7)
            self.assertEqual(manifest['extension']['new_games'],6)
            self.assertEqual(manifest['planned_games'],13)
            self.assertEqual(json.loads((out/'study/runtime_snapshot/configs/player_format_repair.json').read_text())['max_codex_calls_per_game'],0)
            self.assertEqual((out/'study/runtime_snapshot/configs/run.json').read_bytes(),
                             (snap/'configs/run.json').read_bytes())
            before=len(requests)
            with patch('urllib.request.OpenerDirector.open',side_effect=api):
                self.assertEqual(main(manifest['jobs'][0]['argv'][2:]),0)
            self.assertEqual(len(requests)-before,12)  # Six new B games, not A or old B.
            batch=out/'study/continual'
            updated=json.loads((batch/'experiment_runs.json').read_text())
            self.assertEqual(len(updated),13)
            self.assertEqual(sum(r['condition']=='source' for r in updated),1)
            self.assertEqual((old/'continual'/original_source['run_dir']/'api_calls.jsonl').read_bytes(),source_calls)
            self.assertEqual((batch/original_source['run_dir']/'api_calls.jsonl').read_bytes(),source_calls)
            branches=[json.loads((batch/r['run_dir']/'player_continuation.json').read_text())
                      for r in updated if r['condition']=='session']
            self.assertEqual(len(branches),4)
            self.assertTrue(all(same_player_prefix(branches[0],p) for p in branches[1:]))
            for row in rows:
                self.assertEqual((old/'continual'/row['run_dir']/'api_calls.jsonl').read_bytes(),
                                 (batch/row['run_dir']/'api_calls.jsonl').read_bytes())


if __name__=='__main__':unittest.main()
