"""Structural migration preserves live context and source evidence; uploads are inert."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from scripts.host_reference import init_source, validate_inbox
from turtle_loop.dataset import load_dataset
from turtle_loop.host_context import build_story_context
from turtle_loop.repository import resolve_historical_path
ROOT=Path(__file__).resolve().parents[1]

class RepositoryLayoutTests(unittest.TestCase):
    def test_ts002_study_dataset_binds_updated_host(self):
        bank=load_dataset(ROOT/'data/studies/ts002_v7.json')['puzzles']
        self.assertEqual([p['id'] for p in bank],['TS002'])
        self.assertEqual(build_story_context(bank[0])['binding_version'],'host-v11-unknown-wordplay-alternatives-20261109')
        first=bank[0]['rubric'][0]
        self.assertEqual(first['weight'],0.4)
        self.assertIn('boyfriend or romantic partner',first['required_facts'][0])
        self.assertIn('same boyfriend or romantic partner',bank[0]['completion_requirements'][4])

    def test_all_fifty_contexts_preserve_migration_or_explicit_review(self):
        manifest=json.loads((ROOT/'configs/repository_layout.json').read_text())
        bank=load_dataset(ROOT/'data/annotations/turtle50_v4/private.json')['puzzles']
        bindings=json.loads((ROOT/'configs/host_bindings.json').read_text())
        review=json.loads((ROOT/'data/host_reference/reviews/audit_20261030/activation.json').read_text())
        latest=json.loads((ROOT/'data/host_reference/reviews/recheck_20261031/resolution.json').read_text())
        human=json.loads((ROOT/'data/host_reference/reviews/human_20261102/manifest.json').read_text())
        correction=json.loads((ROOT/'data/host_reference/reviews/ts013_20261108_causal_fix.json').read_text())
        ts034=json.loads((ROOT/'data/host_reference/reviews/ts034_20261109_fear_boundary.json').read_text())
        pillow=json.loads((ROOT/'data/host_reference/reviews/ts002_20261109_pillow_boundaries.json').read_text())
        clarification=json.loads((ROOT/'data/host_reference/reviews/ts002_20261109_unknown_wordplay.json').read_text())
        self.assertEqual(review['context_sha256_before'],manifest['context_sha256_before'])
        self.assertEqual(latest['context_sha256_before'],review['context_sha256_after'])
        self.assertEqual(human['context_sha256_before'],latest['context_sha256_after'])
        self.assertEqual(correction['context_sha256_before'],{'TS013':human['context_sha256_after']['TS013']})
        self.assertEqual(set(correction['context_sha256_after']),{'TS013'})
        self.assertEqual(pillow['context_sha256_before'],{'TS002':human['context_sha256_after']['TS002']})
        self.assertEqual(set(pillow['context_sha256_after']),{'TS002'})
        self.assertEqual(clarification['context_sha256_before'],pillow['context_sha256_after'])
        self.assertEqual(set(clarification['context_sha256_after']),{'TS002'})
        self.assertEqual(ts034['context_sha256_before'],{'TS034':human['context_sha256_after']['TS034']})
        self.assertEqual(len(bank),50)
        self.assertEqual({p.stem for p in (ROOT/'data/host_packs/active').glob('*.json')},{p['id'] for p in bank})
        for p in bank:
            expected=ts034['context_sha256_after'].get(p['id'],clarification['context_sha256_after'].get(p['id'],pillow['context_sha256_after'].get(p['id'],correction['context_sha256_after'].get(p['id'],human['context_sha256_after'][p['id']]))))
            self.assertEqual(build_story_context(p)['context_sha256'],expected)
            if p['id'] not in human['packs']:
                self.assertEqual(human['context_sha256_after'][p['id']],latest['context_sha256_after'][p['id']])
            if p['id'] not in latest['packs']:
                self.assertEqual(latest['context_sha256_after'][p['id']],review['context_sha256_after'][p['id']])
            if p['id'] not in review['packs']:
                self.assertEqual(review['context_sha256_after'][p['id']],manifest['context_sha256_before'][p['id']])
            self.assertEqual(bindings[p['id']]['overlay_pack'],f"data/host_packs/active/{p['id']}.json")

    def test_published_originals_preserve_bytes_and_old_paths_resolve(self):
        manifest=json.loads((ROOT/'configs/repository_layout.json').read_text())
        for old,new in manifest['published_moves'].items():
            with self.subTest(path=old):
                self.assertFalse((ROOT/old).exists())
                self.assertEqual(resolve_historical_path(old),ROOT/new)
                self.assertEqual(hashlib.sha256((ROOT/new).read_bytes()).hexdigest(),manifest['original_sha256'][old])
        with self.assertRaises(ValueError):resolve_historical_path('../outside')

    def root_fixture(self,folder):
        root=Path(folder);p=root/'data/annotations/turtle50_v4/private.json';p.parent.mkdir(parents=True)
        p.write_text(json.dumps({'puzzles':[{'id':'TS032'},{'id':'TS034'}]}))
        (root/'configs').mkdir();(root/'configs/host_bindings.json').write_text('{}')
        return root

    def test_import_is_lossless_pending_and_cannot_overwrite_or_activate(self):
        with tempfile.TemporaryDirectory() as folder:
            root=self.root_fixture(folder);original=root/'chat.txt';blob=b'Question?\nmo\nCorrection: no\n';original.write_bytes(blob)
            dest=init_source(['TS032'],'20261028_chat01',input_file=original,root=root)
            self.assertEqual((dest/'trajectory.txt').read_bytes(),blob)
            self.assertEqual(json.loads((dest/'source.json').read_text())['review_status'],'pending')
            self.assertEqual((root/'configs/host_bindings.json').read_text(),'{}')
            self.assertFalse((root/'data/host_packs').exists())
            self.assertEqual(validate_inbox(root)[0]['status'],'valid')
            with self.assertRaises(FileExistsError):init_source(['TS032'],'20261028_chat01',input_file=original,root=root)
            self.assertEqual((dest/'trajectory.txt').read_bytes(),blob)
            (dest/'trajectory.txt').write_text('modified')
            self.assertEqual(validate_inbox(root)[0]['status'],'invalid')

    def test_multi_template_and_unknown_ids(self):
        with tempfile.TemporaryDirectory() as folder:
            root=self.root_fixture(folder)
            dest=init_source(['TS032','TS034'],'multi01',root=root)
            self.assertEqual(dest.parent.name,'multi');self.assertEqual(validate_inbox(root)[0]['status'],'draft')
            for ids,name in [(['TS999'],'unknown'),(['TS032','TS032'],'duplicate'),(['TS032'],'../bad')]:
                with self.assertRaises(ValueError):init_source(ids,name,root=root)
            m=json.loads((dest/'source.json').read_text());m['trajectory_file']='../../private.json';(dest/'source.json').write_text(json.dumps(m))
            self.assertEqual(validate_inbox(root)[0]['status'],'invalid')

if __name__=='__main__':unittest.main()
