import json
import tempfile
import unittest
from pathlib import Path
import test_results_catalog as fixtures
from scripts.results_catalog import validate


class ReleasePresentationTests(unittest.TestCase):
    def fixture(self, root):
        folder = fixtures.ResultCatalogTests().fixture(root)
        (folder/'trajectory.md').write_text('Original question and answer\n')
        path = folder/'archive_metadata.json'
        meta = json.loads(path.read_text())
        meta['source_files_sha256']['trajectory.html'] = 'historical-rendered-page'
        meta['release_omitted_presentations'] = {
            'trajectory.html': {'replacement':'trajectory.md'}}
        path.write_text(json.dumps(meta))
        return folder

    def test_presentation_may_be_omitted_with_existing_text_replacement(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            self.assertEqual(validate(root)['games'], 1)

    def test_missing_replacement_and_attempt_to_omit_data_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = self.fixture(root)
            (folder/'trajectory.md').unlink()
            with self.assertRaisesRegex(ValueError, 'replacement missing'):
                validate(root)
            (folder/'trajectory.md').write_text('restored')
            path = folder/'archive_metadata.json'
            meta = json.loads(path.read_text())
            meta['release_omitted_presentations']['trajectory.jsonl'] = {'replacement':'trajectory.md'}
            path.write_text(json.dumps(meta))
            with self.assertRaisesRegex(ValueError, 'Invalid presentation omission'):
                validate(root)

    def test_lightweight_release_requires_a_verified_pinned_remote(self):
        from scripts.release_check import check
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'docs/release').mkdir(parents=True)
            (root/'docs/release/html_inventory.json').write_text('[]')
            (root/'results').mkdir()
            remote={'revision':'a'*40,'download_verified':True,'counts':{'games':206,'turns':20076}}
            path=root/'results/remote.json';path.write_text(json.dumps(remote))
            self.assertFalse(check(root)['local_full_archive'])
            remote['download_verified']=False;path.write_text(json.dumps(remote))
            with self.assertRaisesRegex(ValueError,'not verified'):check(root)
