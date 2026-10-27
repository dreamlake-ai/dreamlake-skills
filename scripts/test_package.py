"""Offline tests for scripts/package.py."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

import catalog
import package


def make_skill(root, name, requires=()):
    skill = root / name
    (skill / 'actions').mkdir(parents=True)
    (skill / 'reference').mkdir()
    (skill / 'skill.json').write_text(json.dumps({'name': name, 'description': 'd', 'requires': list(requires),
                                                  'docs': [], 'tools': None}))
    (skill / 'SKILL.md').write_text('skill')
    (skill / 'actions' / 'do.md').write_text('do')
    (skill / 'reference' / 'cli-x.md').write_text('generated')
    return skill


class PackageTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        make_skill(self.root, 'dreamlake-cli')
        notes = make_skill(self.root, 'dreamlake-notes', requires=['dreamlake-cli'])
        (notes / '.hidden').write_text('')
        (notes / 'tools').mkdir()
        (notes / 'tools' / 'run.py').write_text('')
        (notes / 'tools' / 'run.py').chmod(0o755)
        (notes / 'tools' / '__pycache__').mkdir()
        (notes / 'tools' / '__pycache__' / 'run.pyc').write_bytes(b'')
        make_skill(self.root, '_template')
        (self.root / 'scripts').mkdir()
        (self.root / 'renamed.json').write_text('{}')
        catalog.write(self.root, version='v2026.10.27')

    def test_archive_contents_and_determinism(self):
        out = self.root / 'dist'
        archive, catalog_copy, digest, names = package.build(self.root, out)
        self.assertEqual(names, ['dreamlake-cli', 'dreamlake-notes'])
        first = archive.read_bytes()
        with tarfile.open(archive) as tar:
            members = tar.getmembers()
        self.assertEqual([m.name for m in members], [
            'dreamlake-cli', 'dreamlake-cli/SKILL.md', 'dreamlake-cli/actions', 'dreamlake-cli/actions/do.md',
            'dreamlake-cli/reference', 'dreamlake-cli/reference/cli-x.md', 'dreamlake-cli/skill.json',
            'dreamlake-notes', 'dreamlake-notes/SKILL.md', 'dreamlake-notes/actions', 'dreamlake-notes/actions/do.md',
            'dreamlake-notes/reference', 'dreamlake-notes/reference/cli-x.md', 'dreamlake-notes/skill.json',
            'dreamlake-notes/tools', 'dreamlake-notes/tools/run.py',
        ])
        by_name = {m.name: m for m in members}
        self.assertTrue(by_name['dreamlake-cli'].isdir())
        self.assertEqual(by_name['dreamlake-notes/tools/run.py'].mode, 0o755)
        self.assertEqual(by_name['dreamlake-cli/SKILL.md'].mode, 0o644)
        self.assertTrue(all(m.mtime == package.DEFAULT_EPOCH and m.uid == 0 and m.uname == '' for m in members))
        committed = json.loads((self.root / 'catalog.json').read_text())
        release = json.loads(catalog_copy.read_text())
        self.assertNotIn('assets', committed)
        self.assertEqual(release.pop('assets'), {'skills.tar.gz': {'sha256': digest, 'bytes': len(first)}})
        self.assertEqual(release, committed)
        self.assertEqual(list(json.loads(catalog_copy.read_text())), ['schema', 'version', 'skills', 'renamed', 'assets'])
        # gzip header carries no timestamp or name
        self.assertEqual(first[4:8], b'\x00\x00\x00\x00')
        with gzip.open(io.BytesIO(first)) as gz:
            self.assertEqual(getattr(gz, 'name', ''), '')
        (self.root / 'dreamlake-cli' / 'SKILL.md').touch()
        archive2, _, digest2, _ = package.build(self.root, out)
        self.assertEqual(archive2.read_bytes(), first)
        self.assertEqual(digest2, digest)

    def test_release_catalog_hash_matches_archive(self):
        archive, catalog_copy, digest, _ = package.build(self.root, self.root / 'dist')
        assets = json.loads(catalog_copy.read_text())['assets']['skills.tar.gz']
        self.assertEqual(assets['sha256'], hashlib.sha256(archive.read_bytes()).hexdigest())
        self.assertEqual(assets['bytes'], archive.stat().st_size)
        self.assertEqual(digest, assets['sha256'])
        # The committed catalog.json must stay release-key free.
        committed = json.loads((self.root / 'catalog.json').read_text())
        (self.root / 'catalog.json').write_text(json.dumps({**committed, 'assets': {}}))
        with self.assertRaisesRegex(package.PackageError, "carries 'assets'"):
            package.build(self.root, self.root / 'dist')

    def test_catalog_must_match_directories(self):
        make_skill(self.root, 'dreamlake-extra')
        with self.assertRaisesRegex(package.PackageError, 'run scripts/catalog.py'):
            package.build(self.root, self.root / 'dist')
        (self.root / 'catalog.json').unlink()
        with self.assertRaisesRegex(package.PackageError, 'catalog.json is missing'):
            package.build(self.root, self.root / 'dist')

    def test_main(self):
        self.assertEqual(package.main(['--root', str(self.root), '--out', str(self.root / 'out')]), 0)
        self.assertTrue((self.root / 'out' / 'skills.tar.gz').is_file())
        self.assertTrue((self.root / 'out' / 'catalog.json').is_file())


if __name__ == '__main__':
    unittest.main()
