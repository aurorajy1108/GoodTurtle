import gzip
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.results_catalog import locate, summarize, validate


class ResultCatalogTests(unittest.TestCase):
    def row(self, **kw):
        return dict(dict(suite='cohort',puzzle='TS013',condition='direct',source=None,
                    role='target',primary=True,duplicate_of=None,status='completed',
                    score=.4,success=False,submissions=100),**kw)

    def test_summary_does_not_turn_incomplete_or_source_or_alias_into_samples(self):
        base=self.row()
        rows=[base,dict(base,score=.2),dict(base,status='error',score=None,success=None),
              dict(base,role='source',score=1,success=True),
              dict(base,primary=False,score=1,success=True),
              dict(base,duplicate_of='first',score=1,success=True)]
        s=summarize(rows)[0]
        self.assertEqual((s['n_completed'],s['n_incomplete'],s['solved']),(2,1,0))
        self.assertAlmostEqual(s['score_mean'],.3)

    def test_versions_and_sources_remain_separate_and_shared_direct_is_not_multiplied(self):
        b=self.row();rows=[b,dict(b,suite='other'),dict(b,condition='session',source='TS015'),
                          dict(b,condition='session',source='TS014')]
        self.assertEqual(len(summarize(rows)),4)
        self.assertEqual(sum(r['n_completed'] for r in summarize(rows)),4)

    def fixture(self, root):
        d=root/'results/trajectories/cohort/game';d.mkdir(parents=True)
        payload={'status':'completed','submissions':1,'success':False,'final_partial_score':.4}
        (d/'result.json').write_text(json.dumps(payload))
        (d/'trajectory.jsonl').write_text(json.dumps({'event':'submission','index':1,'type':'final','text':'attempt'})+'\n')
        hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in d.iterdir()}
        (d/'archive_metadata.json').write_text(json.dumps({'source_files_sha256':hashes}))
        row=dict(self.row(),id='game',path=str(d.relative_to(root)),submissions=1)
        (root/'results/catalog.json').write_text(json.dumps([row]))
        return d

    def test_validation_checks_frozen_bytes_and_original_outcomes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);d=self.fixture(root)
            self.assertEqual(validate(root)['games'],1)
            (d/'trajectory.jsonl').write_text('changed\n')
            with self.assertRaisesRegex(ValueError,'Frozen file changed'):validate(root)

    def test_catalog_path_cannot_escape_and_duplicate_id_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root);f=root/'results/catalog.json';rows=json.loads(f.read_text())
            f.write_text(json.dumps(rows+rows))
            with self.assertRaisesRegex(ValueError,'Duplicate catalog ID'):validate(root)
            rows[0]['path']='../outside';f.write_text(json.dumps(rows))
            with self.assertRaisesRegex(ValueError,'escapes'):validate(root)

    def test_locator_works_without_archive_git_objects_and_rejects_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);d=self.fixture(root)
            (root/'results/layout_migration.json').write_text(json.dumps({
                'archive_commit':'abcdef','file_moves':{'old.json':'results/trajectories/cohort/game/result.json'},
                'folder_moves':{},'archive_file_index':'results/archive_files.json.gz'}))
            with gzip.open(root/'results/archive_files.json.gz','wt') as f:json.dump({'old/index.html':{'bytes':5}},f)
            self.assertEqual(locate('old.json',root),'results/trajectories/cohort/game/result.json')
            self.assertIn('/abcdef/old/index.html',locate('old/index.html',root))
            with self.assertRaises(ValueError):locate('../outside',root)


if __name__=='__main__':unittest.main()
