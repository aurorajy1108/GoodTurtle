import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path
import test_results_catalog as fixtures
from scripts.fetch_results import digest, restore_archive

class HFArchiveTests(unittest.TestCase):
    def bundle(self, base):
        source=base/'source';fixtures.ResultCatalogTests().fixture(source)
        files=[f for f in (source/'results').rglob('*') if f.is_file()]
        inventory={str(f.relative_to(source)):{'bytes':f.stat().st_size,'sha256':digest(f)} for f in files}
        manifest=base/'manifest.json';manifest.write_text(json.dumps(inventory))
        archive=base/'results.tar.gz'
        with tarfile.open(archive,'w:gz') as tar:
            for f in files:tar.add(f,arcname=str(f.relative_to(source)),recursive=False)
        return archive,manifest

    def test_original_records_round_trip_and_existing_conflicts_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);archive,manifest=self.bundle(base);target=base/'target'
            self.assertEqual(restore_archive(archive,manifest,target)['games'],1)
            self.assertEqual(restore_archive(archive,manifest,target)['restored_files'],0)
            p=target/'results/trajectories/cohort/game/result.json';p.write_text('changed')
            with self.assertRaisesRegex(ValueError,'Refusing to overwrite'):restore_archive(archive,manifest,target)
            self.assertEqual(p.read_text(),'changed')

    def test_traversal_and_missing_archive_entries_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);archive,manifest=self.bundle(base)
            with tarfile.open(archive,'w:gz') as tar:
                entry=tarfile.TarInfo('../escape');entry.size=1;tar.addfile(entry,io.BytesIO(b'x'))
            with self.assertRaisesRegex(ValueError,'Unsafe'):restore_archive(archive,manifest,base/'target')
            self.assertFalse((base/'escape').exists())
            with tarfile.open(archive,'w:gz'):pass
            with self.assertRaisesRegex(ValueError,'missing files'):restore_archive(archive,manifest,base/'target')

    def test_symlink_member_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);archive,manifest=self.bundle(base)
            with tarfile.open(archive,'w:gz') as tar:
                entry=tarfile.TarInfo('results/link');entry.type=tarfile.SYMTYPE;entry.linkname='/tmp';tar.addfile(entry)
            with self.assertRaisesRegex(ValueError,'Unsafe'):restore_archive(archive,manifest,base/'target')

    def test_export_keeps_original_submission_and_outcome(self):
        from scripts.export_hf_results import prepare
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);source=base/'source'
            fixtures.ResultCatalogTests().fixture(source)
            info=prepare(source,base/'bundle')
            self.assertEqual(info['counts'],{'games':1,'turns':1,'messages':0})
            turn=json.loads((base/'bundle/data/turns.jsonl').read_text())
            self.assertEqual(turn['text'],'attempt')
            game=json.loads((base/'bundle/data/games.jsonl').read_text())
            self.assertEqual(game['score'],.4)
            self.assertFalse(game['success'])
