import argparse
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.team_campaign import ROOT, catalogue, select_tasks, prepare, execute, report, main
from turtle_loop.costs import cost_summary


class CampaignTests(unittest.TestCase):
    def test_report_reads_live_game_counts_instead_of_stale_batch_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);folder=out/'task/continual';game=folder/'game';game.mkdir(parents=True)
            stale={'condition':'session','target':'TS013','source':'TS015','repeat':1,'run_dir':'game',
                   'status':'running','success':None,'submissions':0,'counted_questions':0,'costs':cost_summary([])}
            (folder/'experiment_runs.json').write_text(json.dumps([stale]))
            (game/'result.json').write_text(json.dumps({**stale,'submissions':17,'counted_questions':17}))
            job={'id':'cl-set1-a','folder':'task','kind':'continual','set':1,'slot':'a','repeat_offset':0,'planned_games':1}
            manifest={'runner':'reviewer','preset':'full','jobs':[job],'planned_games':1,'catalogue':[job],'source_policy':'fixed'}
            (out/'campaign.json').write_text(json.dumps(manifest))
            rows=report(out)
            self.assertEqual(rows[0]['counted_questions'],17)
            self.assertEqual(rows[0]['submissions'],17)

    def args(self,out,**kw):
        return argparse.Namespace(command='start',preset='full',runner='reviewer',tasks='cl-set1-a',workers=2,
            set1_positive='15',config=str(ROOT/'configs/loop.deepseek.json'),
            dataset=str(ROOT/'data/annotations/turtle50_v5/private.json'),seed=20261111,host_gate='auto',
            on_error='stop',poll_seconds=1,mode='plan',out=str(out),**kw)

    def test_assignment_and_repetition_counts_match_screenshots(self):
        tasks=catalogue();self.assertEqual(len(tasks),12)
        self.assertEqual(sum(t['planned_games'] for t in tasks if t['kind']=='continual'),126)
        self.assertEqual(sum(t['planned_games'] for t in tasks if t['kind']=='team'),24)
        self.assertEqual({t['target'] for t in tasks if t['kind']=='team'},{'TS038','TS002','TS014'})
        for t in tasks:
            self.assertEqual(t['repeat'],2)
            self.assertEqual(t['repeat_offset'],0 if t['slot']=='a' else 2)
        self.assertEqual(tasks[0]['sources'],{'TS015':'positive','TS014':'negative','TS028':'neutral'})
        self.assertEqual(tasks[4]['suggested_runners'],['shirley'])
        self.assertEqual(tasks[5]['suggested_runners'],['jiayang','zhenqi'])
        self.assertEqual(sum(t['planned_games'] for t in catalogue(positive='both')),164)
        self.assertEqual(list(catalogue(positive='16')[0]['sources'])[0],'TS016')
        with self.assertRaises(ValueError):select_tasks(tasks,'cl-set1-a,cl-set1-a')
        with self.assertRaises(ValueError):select_tasks(tasks,'set4')

    def test_smoke_is_six_games_with_full_quota_and_frozen_protocol(self):
        with tempfile.TemporaryDirectory() as tmp:
            args=self.args(Path(tmp)/'pilot');args.preset='smoke';args.tasks='cl-set1-a,mas-ts038-a'
            out,manifest=prepare(args)
            self.assertEqual(manifest['planned_games'],6)
            self.assertEqual(manifest['host_gate']['checks'],20)
            self.assertEqual(len({j['protocol_hash'] for j in manifest['jobs']}),1)
            for job in manifest['jobs']:
                config=json.loads((out/job['folder']/'runtime_snapshot/configs/run.json').read_text())
                data=json.loads((out/job['folder']/'runtime_snapshot/data/dataset.json').read_text())
                self.assertTrue(data['puzzles'])
                self.assertEqual({p['grading_protocol'] for p in data['puzzles']},{'coverage-v3-unified'})
                self.assertEqual(config['max_questions'],100)
                self.assertEqual(config['player']['extra_body']['thinking']['type'],'disabled')
                plan=json.loads((out/job['folder']/'study_plan.json').read_text())
                if job['kind']=='continual':
                    self.assertEqual({b['source'] for b in plan['blocks']['continual']},{'TS015'})
                    self.assertTrue(all(set(b['conditions'])=={'direct','session','answer_only'} for b in plan['blocks']['continual']))
                else:self.assertTrue(all(set(b['conditions'])=={'solo','free_dialogue'} for b in plan['blocks']['team']))

    def test_two_slots_have_disjoint_global_repeat_ids_and_costs_are_not_duplicated(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);jobs=[]
            for slot,offset in [('a',0),('b',2)]:
                task={'id':'cl-set1-'+slot,'folder':slot,'kind':'continual','set':1,'slot':slot,
                      'repeat_offset':offset,'planned_games':2}
                jobs.append(task);folder=out/slot/'continual';folder.mkdir(parents=True)
                rows=[{'condition':'session','target':'TS013','source':'TS015','repeat':n,'run_dir':'r'+str(n),
                       'status':'completed','success':True,'counted_questions':40+10*n,'submissions':41+10*n,
                       'final_partial_score':1,'costs':cost_summary([]),'source_context_sha256':'prefix-'+slot} for n in (1,2)]
                (folder/'experiment_runs.json').write_text(json.dumps(rows))
            m={'runner':'coordinator','preset':'full','jobs':jobs,'planned_games':4,'catalogue':jobs,'source_policy':'fixed within slot'}
            (out/'campaign.json').write_text(json.dumps(m))
            rows=report(out);self.assertEqual(sorted(r['global_repeat'] for r in rows),[1,2,3,4])
            score=json.loads((out/'performance.json').read_text())[0]
            self.assertEqual(score['completed'],4)
            self.assertEqual(score['question_consumption']['mean'],55)
            self.assertEqual(score['source_prefix_hashes'],['prefix-a','prefix-b'])
            self.assertEqual(json.loads((out/'cost_summary.json').read_text())['total']['calls'],0)
            with self.assertRaises(ValueError):report(out,[(out,m),(out,m)])

    def test_fail_fast_cancels_only_owned_workers_and_never_starts_pending_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);jobs=[];started=[];closed=[]
            for i in range(3):
                folder=out/str(i);(folder/'runtime_snapshot').mkdir(parents=True)
                jobs.append({'id':str(i),'folder':str(i),'kind':'team','hashes':{},'argv':['fixture'],
                             'planned_games':1,'repeat_offset':0,'slot':'a'})
            manifest={'jobs':jobs,'runner':'fixture','preset':'full','host_gate':None,'arguments':{
                'workers':2,'mode':'run','on_error':'stop','poll_seconds':1}}
            class Process:
                def __init__(self,*a,**kw):
                    self.id=len(started);self.pid=100+self.id;started.append(self)
                    self.assert_group=kw['start_new_session']
                def poll(self):return 1 if self.id==0 else None
            def stop(active,exited):
                for key,(_,log) in active.items():closed.append(key);log.close()
                active.clear()
            with patch('scripts.team_campaign.subprocess.Popen',Process),patch('scripts.team_campaign.report'),\
                 patch('scripts.team_campaign.rows_for',return_value=[]),patch('scripts.team_campaign.stop_owned_workers',side_effect=stop):
                code=execute(out,manifest)
            self.assertEqual(code,1);self.assertEqual(len(started),2)
            self.assertTrue(all(p.assert_group for p in started))
            self.assertEqual(closed,['1'])
            state=json.loads((out/'status.json').read_text())
            self.assertEqual(state['tasks'],{'0':'error','1':'cancelled','2':'planned'})

    def test_collect_rejects_duplicate_slots_and_pilot_formal_mix_before_creating_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);inputs=[]
            for n in ('one','two'):
                folder=root/n;folder.mkdir();inputs.append(str(folder))
                (folder/'campaign.json').write_text(json.dumps({'preset':'full','protocol_hash':'same',
                    'jobs':[{'id':'cl-set1-a'}]}))
            self.assertEqual(main(['collect','--inputs',*inputs,'--out',str(root/'merge')]),2)
            self.assertFalse((root/'merge').exists())
            (root/'two/campaign.json').write_text(json.dumps({'preset':'smoke','protocol_hash':'same','jobs':[]}))
            self.assertEqual(main(['collect','--inputs',*inputs,'--out',str(root/'merge')]),2)
            self.assertFalse((root/'merge').exists())

    def test_failed_host_gate_starts_no_slot_workers(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);(out/'task/runtime_snapshot').mkdir(parents=True)
            manifest={'runner':'fixture','preset':'full',
                'jobs':[{'id':'cl-set1-a','folder':'task','hashes':{}}],
                'host_gate':{'snapshot':'task/runtime_snapshot','argv':['fixture-gate'],'checks':20},
                'arguments':{'mode':'run','workers':2,'on_error':'stop','poll_seconds':1}}
            class Process:
                pid=123
                def wait(self):return 1
            with patch('scripts.team_campaign.subprocess.Popen',return_value=Process()) as called,\
                 patch('scripts.team_campaign.report'):
                self.assertEqual(execute(out,manifest),1)
            self.assertEqual(called.call_count,1)
            state=json.loads((out/'status.json').read_text())
            self.assertEqual(state['status'],'stopped_on_host_gate')
            self.assertEqual(state['tasks'],{'cl-set1-a':'planned'})


if __name__=='__main__':unittest.main()
