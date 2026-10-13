import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('catalog', Path(__file__).with_name('catalog.py'))
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.skills = {
            'product': {'maintenance': 'generated', 'source_repos': ['cli'],
                        'edit': 'https://github.com/example/cli/tree/main/docs',
                        'review_docs': [], 'overlaps': ['utility']},
            'utility': {'maintenance': 'standalone', 'edit': 'utility/',
                        'review_docs': [], 'overlaps': []},
        }
        for name in self.skills:
            (self.root / name).mkdir()
            (self.root / name / 'SKILL.md').write_text('skill')
        (self.root / 'README.md').write_text('\n'.join(f'[skill](./{name}/SKILL.md)' for name in self.skills))
        self.sources = {'cli': {'repository': 'https://github.com/example/cli', 'commit': 'a' * 40}}
        self.write('sources.json', {'sources': self.sources})
        self.write('generated-files.json', {'files': {'product/SKILL.md': 'hash'}})
        (self.root / 'MAINTENANCE.md').write_text('Before\n' + catalog.START + '\n' + catalog.END + '\nAfter\n')
        self.save()

    def write(self, name, value):
        (self.root / name).write_text(json.dumps(value))

    def save(self):
        self.write('catalog.json', {'version': 1, 'skills': self.skills})

    def test_inventory_and_source_revision_drift(self):
        catalog.update(self.root)
        catalog.update(self.root, check=True)
        page = (self.root / 'MAINTENANCE.md').read_text()
        self.assertTrue(page.startswith('Before\n'))
        self.assertTrue(page.endswith('\nAfter\n'))
        self.assertIn('not checked by this report', page)
        self.sources['cli']['commit'] = 'b' * 40
        self.write('sources.json', {'sources': self.sources})
        with self.assertRaisesRegex(ValueError, 'stale'):
            catalog.update(self.root, check=True)

    def test_new_skill_cannot_bypass_registration(self):
        (self.root / 'unregistered').mkdir()
        (self.root / 'unregistered/SKILL.md').write_text('skill')
        with self.assertRaisesRegex(ValueError, 'coverage mismatch'):
            catalog.load(self.root)

    def test_generated_owner_cannot_be_relabeled_standalone(self):
        self.skills['product']['maintenance'] = 'standalone'
        self.save()
        with self.assertRaisesRegex(ValueError, 'no generated catalog owner'):
            catalog.load(self.root)

    def test_manual_skill_cannot_claim_generation_without_manifest(self):
        self.skills['utility'].update(maintenance='generated', source_repos=['cli'],
                                     edit='https://github.com/example/cli/tree/main/docs')
        self.save()
        with self.assertRaisesRegex(ValueError, 'generated SKILL.md'):
            catalog.load(self.root)

    def test_manual_product_requires_docs(self):
        self.skills['utility']['maintenance'] = 'manual-product'
        self.save()
        with self.assertRaisesRegex(ValueError, 'paired review'):
            catalog.load(self.root)

    def test_unknown_overlap_and_missing_discovery(self):
        self.skills['utility']['overlaps'] = ['missing']
        self.save()
        with self.assertRaisesRegex(ValueError, 'unknown or self overlap'):
            catalog.load(self.root)
        self.skills['utility']['overlaps'] = []
        self.save()
        (self.root / 'README.md').write_text('[skill](./product/SKILL.md)')
        with self.assertRaisesRegex(ValueError, 'README discovery'):
            catalog.load(self.root)


if __name__ == '__main__':
    unittest.main()
