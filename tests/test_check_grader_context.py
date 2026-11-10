import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


class GraderReplayContextTests(unittest.TestCase):
    def test_dry_run_uses_runtime_grader_reference_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); cases=root/'cases.json';out=root/'out'
            cases.write_text(json.dumps([{'id':'context','puzzle_id':'TS034',
                'submission':'The father is the hostage and the daughter is free.',
                'expected':{'complete':False}}]))
            subprocess.run([sys.executable,str(ROOT/'scripts/check_grader.py'),
                '--dataset',str(ROOT/'data/studies/ts034_v5.json'),
                '--config',str(ROOT/'configs/loop.deepseek.solo-json.json'),
                '--cases',str(cases),'--out',str(out),'--dry-run'],cwd=ROOT,check=True)
            context=json.loads((out/'inputs.json').read_text())[0]['story_context']
            self.assertLessEqual(len(context['host_examples']),3)
            self.assertTrue(context['canonical_solution'])
            self.assertTrue(context['completion_requirements'])

if __name__=='__main__':unittest.main()
