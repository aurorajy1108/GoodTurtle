import json
import tempfile
import unittest
from pathlib import Path
from scripts.render_trajectories import render


class TrajectoryHTMLTests(unittest.TestCase):
    def test_embeds_all_turns_discussion_and_escapes_script_end(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root/'team/TS031_r01_discuss'
            folder.mkdir(parents=True)
            malicious = '</script><script>alert("untrusted model text")</script>'
            (folder/'puzzle_private.json').write_text(json.dumps({'id':'TS031','opening':'Puzzle','answer':'Private answer'}))
            (folder/'result.json').write_text(json.dumps({'status':'completed','counted_questions':1}))
            (root/'audit_notice.json').write_text(json.dumps({'note':malicious,'raw_results_modified':False}))
            events = [{'event':'submission','index':1,'type':'question','text':malicious},
                      {'event':'host_feedback','submission':1,'label':'no'},
                      {'event':'host_review','submission':1,'candidate_labels':['no','no'],'calls':2},
                      {'event':'submission','index':2,'type':'final','text':'Final'}]
            (folder/'trajectory.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in events))
            (folder/'collaboration.jsonl').write_text(json.dumps({'advice':'Private discussion'})+'\n')
            out = root/'all.html'
            summary = render(root,out)
            self.assertEqual(summary['submissions'],2)
            self.assertEqual(summary['collaboration_records'],1)
            content = out.read_text()
            self.assertNotIn(malicious,content)
            data = content.split('<script id="data" type="application/json">')[1].split('</script>')[0]
            restored = json.loads(data)
            self.assertEqual(restored[0]['events'][0]['text'],malicious)
            self.assertEqual(restored[0]['collaboration'][0]['advice'],'Private discussion')
            self.assertEqual(restored[0]['audit_notice']['note'],malicious)
            self.assertEqual(restored[0]['events'][2]['calls'],2)

    def test_live_partial_last_line_is_ignored(self):
        from scripts.render_trajectories import jsonl
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'live.jsonl'
            p.write_text('{"event":"start"}\n{"event":')
            self.assertEqual(jsonl(p),[{'event':'start'}])

    def test_discovers_direct_and_nested_batches_without_snapshot_duplicates(self):
        from scripts.render_trajectories import collect
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('TS023_r01_solo', 'batches/TS032/TS032_r02_independent',
                         'runtime_snapshot/example'):
                folder = root / name
                folder.mkdir(parents=True)
                (folder / 'trajectory.jsonl').write_text('{"event":"start"}\n')
            self.assertEqual({g['name'] for g in collect(root)},
                             {'TS023_r01_solo', 'batches/TS032/TS032_r02_independent'})
