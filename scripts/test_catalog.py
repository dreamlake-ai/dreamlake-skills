"""Offline tests for scripts/catalog.py."""
import json
from pathlib import Path
import tempfile
import unittest

import catalog


def make_skill(root, name, requires=(), tools=None, docs=()):
    skill = root / name
    (skill / 'actions').mkdir(parents=True)
    (skill / 'skill.json').write_text(json.dumps({'name': name, 'description': f'{name} does things',
                                                  'requires': list(requires), 'docs': list(docs), 'tools': tools}))
    (skill / 'SKILL.md').write_text('skill')
    (skill / 'actions' / 'do.md').write_text('do')
    return skill


class CatalogTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.cli = make_skill(self.root, 'dreamlake-cli')
        self.notes = make_skill(self.root, 'dreamlake-notes', requires=['dreamlake-cli'],
                                tools={'python': '>=3.12', 'packages': ['mujoco']})
        (self.notes / 'reference').mkdir()
        (self.notes / 'reference' / 'cli-notes.md').write_text('generated')
        (self.notes / 'reference' / 'docs-notes.md').write_text('generated')
        (self.notes / 'tools').mkdir()
        (self.notes / 'tools' / 'x.py').write_text('')
        (self.notes / 'tools' / '__pycache__').mkdir()
        (self.notes / 'tools' / '__pycache__' / 'x.cpython-312.pyc').write_bytes(b'')
        (self.notes / '.DS_Store').write_bytes(b'')
        make_skill(self.root, '_template')
        (self.root / '.hidden').mkdir()
        (self.root / 'scripts').mkdir()
        (self.root / 'renamed.json').write_text(json.dumps({'workflow-publish': 'dreamlake-workflows',
                                                            'dreamlake-source': 'dreamlake-datasets'}))

    def test_build_shape(self):
        built = catalog.build(self.root, version='v2026.10.27')
        self.assertEqual(built, {
            'schema': 1,
            'version': 'v2026.10.27',
            'skills': {
                'dreamlake-cli': {'description': 'dreamlake-cli does things', 'requires': [], 'tools': None, 'files': 3},
                'dreamlake-notes': {'description': 'dreamlake-notes does things', 'requires': ['dreamlake-cli'],
                                    'tools': {'python': '>=3.12', 'packages': ['mujoco']}, 'files': 4},
            },
            'renamed': {'dreamlake-source': 'dreamlake-datasets', 'workflow-publish': 'dreamlake-workflows'},
        })
        self.assertEqual(list(built), ['schema', 'version', 'skills', 'renamed'])

    def test_version_falls_back_without_git(self):
        self.assertEqual(catalog.build(self.root)['version'], catalog.FALLBACK_VERSION)

    def test_write_then_check_ignores_version(self):
        catalog.write(self.root, version='v1')
        self.assertEqual(catalog.check(self.root), [])
        text = (self.root / 'catalog.json').read_text()
        self.assertTrue(text.endswith('}\n'))
        (self.root / 'catalog.json').write_text(text.replace('"v1"', '"v2"'))
        self.assertEqual(catalog.check(self.root), [])

    def test_check_detects_drift(self):
        catalog.write(self.root, version='v1')
        make_skill(self.root, 'dreamlake-new')
        problems = catalog.check(self.root)
        self.assertEqual(problems, ['catalog.json: does not list dreamlake-new', 'run scripts/catalog.py to regenerate'])
        catalog.write(self.root, version='v1')
        (self.notes / 'actions' / 'more.md').write_text('more')
        self.assertIn('catalog.json: entry for dreamlake-notes is stale', catalog.check(self.root))
        catalog.write(self.root, version='v1')
        (self.root / 'renamed.json').write_text('{}')
        self.assertIn('catalog.json: renamed differs from renamed.json', catalog.check(self.root))
        catalog.write(self.root, version='v1')
        data = json.loads((self.root / 'catalog.json').read_text())
        (self.root / 'catalog.json').write_text(json.dumps(data))
        self.assertIn('catalog.json: formatting differs from scripts/catalog.py output', catalog.check(self.root))
        (self.root / 'catalog.json').unlink()
        self.assertEqual(catalog.check(self.root), ['catalog.json is missing; run scripts/catalog.py'])

    def test_name_must_match_directory(self):
        (self.cli / 'skill.json').write_text(json.dumps({'name': 'other', 'description': 'd', 'requires': [],
                                                        'docs': [], 'tools': None}))
        with self.assertRaisesRegex(catalog.CatalogError, 'differs from the directory name'):
            catalog.build(self.root, version='v1')

    def test_renamed_is_required_and_must_be_a_mapping(self):
        (self.root / 'renamed.json').unlink()
        with self.assertRaisesRegex(catalog.CatalogError, 'renamed.json is missing'):
            catalog.build(self.root, version='v1')
        (self.root / 'renamed.json').write_text('[]')
        with self.assertRaisesRegex(catalog.CatalogError, 'must map'):
            catalog.build(self.root, version='v1')

    def test_main(self):
        self.assertEqual(catalog.main(['--root', str(self.root), '--check']), 1)
        self.assertEqual(catalog.main(['--root', str(self.root), '--version', 'v9']), 0)
        self.assertEqual(json.loads((self.root / 'catalog.json').read_text())['version'], 'v9')
        self.assertEqual(catalog.main(['--root', str(self.root), '--check']), 0)


if __name__ == '__main__':
    unittest.main()
