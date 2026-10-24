import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from scripts.experiment_bundle import export, verify


class BundleTests(unittest.TestCase):
    def test_export_contains_only_inputs_and_requires_matching_bindings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'configs').mkdir()
            (root/'configs/host_bindings.json').write_text('{}')
            (root/'.env').write_text('SECRET=never export')
            data = root/'dataset.json'
            data.write_text(json.dumps({'schema_version':1, 'puzzles':[{
                'id':'FIXTURE', 'opening':'Public', 'answer':'Private',
                'rubric':[{'id':'C1','weight':1,'criterion':'Private'}]}]}))
            out = root/'bundle.zip'
            result = export(data, out, root)
            self.assertEqual(result['puzzles'],1)
            self.assertTrue(verify(out,root)['verified'])
            with ZipFile(out) as archive:
                self.assertEqual(set(archive.namelist()), {
                    'data/annotations/turtle50_v4/private.json', 'data/experiment_bundle_manifest.json'})
            (root/'configs/host_bindings.json').write_text('{"changed":true}')
            with self.assertRaisesRegex(ValueError,'bindings differ'):
                verify(out,root)

    def test_rejects_path_traversal_before_reading_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory)/'bad.zip'
            with ZipFile(out,'w') as archive:
                archive.writestr('data/../../outside','bad')
            with self.assertRaisesRegex(ValueError,'path'):
                verify(out,Path(directory))
