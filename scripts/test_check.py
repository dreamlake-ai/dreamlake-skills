"""Offline tests for scripts/check.py: a fixture repository in a temp dir, a fake fetcher."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import catalog
import check
import sync_references as sync

REPO = Path(__file__).resolve().parents[1]
CLI = 'https://cli.dreamlake.ai'
DOCS = 'https://docs.dreamlake.ai'
PAGES = {
    f'{CLI}/artifacts.md': b'# Artifacts\n[p](/projects.md#x)\n',
    f'{CLI}/projects.md': b'# Projects\n',
    f'{DOCS}/notes.md': b'# Notes\n',
}


def fake_fetch(url):
    if url not in PAGES:
        raise sync.FetchError(f'{url}: HTTP 404')
    return PAGES[url]


def write_skill(root, name, docs, requires=(), tools=None, dirname=None):
    skill = root / (dirname or name)
    (skill / 'actions').mkdir(parents=True, exist_ok=True)
    (skill / 'skill.json').write_text(json.dumps({'name': name, 'description': f'{name} owns a goal.',
                                                  'requires': list(requires), 'docs': list(docs), 'tools': tools}))
    (skill / 'SKILL.md').write_text(
        f'---\nname: {name}\ndescription: Use for the {name} goal.\n---\n\n# {name}\n\n'
        f'## Route\n\n| Request | Open |\n|---|---|\n| do it | [actions/do.md](actions/do.md) |\n\n'
        f'## Canonical source\n\nhttps://docs.dreamlake.ai, fetchable as `<page-url>.md`.\n')
    (skill / 'actions' / 'do.md').write_text('# Do\n\nSee [SKILL.md](../SKILL.md) and [flags](../reference/cli-artifacts.md).\n'
                                             if docs else '# Do\n\nSee [SKILL.md](../SKILL.md).\n')
    return skill


class CheckTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        shutil.copyfile(REPO / 'skill.schema.json', self.root / 'skill.schema.json')
        self.cli = write_skill(self.root, 'dreamlake-cli', [f'{CLI}/artifacts', f'{CLI}/projects'])
        self.notes = write_skill(self.root, 'dreamlake-notes', [f'{DOCS}/notes', f'{CLI}/artifacts'],
                                 requires=['dreamlake-cli'], tools={'python': '>=3.12', 'packages': []})
        self.template = write_skill(self.root, 'dreamlake-example', [f'{CLI}/artifacts'], dirname='_template')
        (self.root / 'renamed.json').write_text(json.dumps({'dreamlake-tasks': 'dreamlake-cli'}))
        (self.root / 'scripts').mkdir()
        (self.root / 'docs').mkdir()
        (self.root / 'evidence').mkdir()
        (self.root / '.github').mkdir()
        self.regenerate()

    def regenerate(self):
        sync.sync(self.root, fetch=fake_fetch, out=lambda _: None)
        catalog.write(self.root, version='v1')

    def failures(self, **kwargs):
        kwargs.setdefault('offline', True)
        kwargs.setdefault('run_tool_tests', False)
        return check.check_repo(self.root, **kwargs).failures

    def assertFailure(self, needle, failures=None):
        failures = self.failures() if failures is None else failures
        self.assertTrue(any(needle in f for f in failures), f'{needle!r} not in {failures}')

    def test_fixture_passes(self):
        report = check.check_repo(self.root, offline=True, run_tool_tests=False)
        self.assertEqual(report.failures, [])
        self.assertEqual(report.warnings, [])
        self.assertEqual(check.main(['--root', str(self.root), '--offline', '--skip-tool-tests']), 0)

    def test_missing_skill_json_and_legacy_references(self):
        (self.cli / 'skill.json').unlink()
        (self.cli / 'references').mkdir()
        failures = self.failures()
        self.assertFailure('dreamlake-cli: missing skill.json', failures)
        self.assertFailure('dreamlake-cli: references/ is a legacy hand-written directory', failures)
        # A directory without skill.json is reported for those two things only.
        self.assertEqual(len([f for f in failures if f.startswith('dreamlake-cli:')]), 2)
        # Downstream, notes can no longer resolve its requirement and the catalog is stale.
        self.assertFailure("dreamlake-notes: skill.json: requires 'dreamlake-cli', which is not a skill", failures)
        self.assertFailure('catalog.json: lists dreamlake-cli', failures)
        self.assertEqual(check.main(['--root', str(self.root), '--offline', '--skip-tool-tests']), 1)

    def test_schema_violations(self):
        meta = json.loads((self.cli / 'skill.json').read_text())
        cases = {
            'name': ('Bad_Name', 'skill.json.name'),
            'description': ('', 'skill.json.description'),
            'docs': ([f'{CLI}/artifacts.md'], 'skill.json.docs[0]'),
            'tools': ({'packages': []}, "skill.json.tools: missing required key 'python'"),
            'extra': (1, "skill.json: unexpected key 'extra'"),
        }
        for key, (value, needle) in cases.items():
            with self.subTest(key=key):
                broken = {**meta, key: value}
                (self.cli / 'skill.json').write_text(json.dumps(broken))
                self.assertFailure(needle)
        for url in (f'{DOCS}/notes/', 'https://example.com/x', f'{DOCS}/a?b', 'http://docs.dreamlake.ai/a'):
            with self.subTest(url=url):
                (self.cli / 'skill.json').write_text(json.dumps({**meta, 'docs': [url]}))
                self.assertFailure('skill.json.docs[0]')
        (self.cli / 'skill.json').write_text(json.dumps({**meta, 'docs': [f'{DOCS}/', f'{DOCS}/a.b/c-d_e']}))
        self.assertFalse([f for f in self.failures() if 'skill.json.docs' in f])
        (self.cli / 'skill.json').write_text('{not json')
        self.assertFailure('dreamlake-cli: skill.json: invalid JSON')

    def test_name_must_equal_directory_except_for_template(self):
        meta = json.loads((self.cli / 'skill.json').read_text())
        (self.cli / 'skill.json').write_text(json.dumps({**meta, 'name': 'dreamlake-other'}))
        failures = self.failures()
        self.assertFailure("dreamlake-cli: skill.json: name 'dreamlake-other' must equal the directory name", failures)
        self.assertFailure("frontmatter name 'dreamlake-cli' differs from skill.json name 'dreamlake-other'", failures)
        self.assertFalse([f for f in failures if f.startswith('_template:')])

    def test_skill_md_rules(self):
        path = self.cli / 'SKILL.md'
        original = path.read_text()
        path.write_text(original + '\n'.join(['filler'] * 80) + '\n')
        self.assertFailure('SKILL.md has 96 lines; the limit is 80')
        path.write_text(original.replace('## Canonical source', '## Sources'))
        self.assertFailure("SKILL.md must end with a '## Canonical source' section")
        path.write_text(original.replace('## Canonical source', '## Canonical source\n\n## Later'))
        self.assertFailure("SKILL.md must end with a '## Canonical source' section")
        path.write_text(original.split('## Canonical source')[0] + '## Canonical source\n')
        self.assertFailure("the '## Canonical source' section of SKILL.md is empty")
        path.write_text(original.split('---\n\n', 1)[1])
        self.assertFailure('SKILL.md must start with YAML frontmatter')
        path.write_text(original.replace('description: Use for the dreamlake-cli goal.', 'description: ""'))
        self.assertFailure('frontmatter needs a non-empty description')
        path.write_text(original.replace('description: Use for the dreamlake-cli goal.',
                                         'description: >\n  Folded block\n  scalar.'))
        self.assertFalse([f for f in self.failures() if 'frontmatter' in f])
        path.unlink()
        self.assertFailure('dreamlake-cli: missing SKILL.md')

    def test_actions_and_reference_dir_rules(self):
        (self.cli / 'actions' / 'do.md').unlink()
        self.assertFailure('dreamlake-cli: actions/ must hold at least one .md page')
        (self.cli / 'actions' / 'do.md').write_text('# Do\n')
        (self.cli / 'reference' / 'notes.md').write_text('# hand written\n')
        failures = self.failures()
        self.assertFailure('dreamlake-cli: reference/notes.md lacks the generated header', failures)
        self.assertFailure('references.lock: dreamlake-cli: reference/notes.md is not in references.lock', failures)
        (self.cli / 'reference' / 'notes.md').unlink()
        (self.cli / 'reference' / 'render.py').write_text('')
        self.assertFailure('dreamlake-cli: reference/render.py is not a generated .md page')
        (self.cli / 'reference' / 'render.py').unlink()
        (self.cli / 'reference' / 'sub').mkdir()
        self.assertFailure('dreamlake-cli: reference/sub/ is a directory')

    def test_relative_links(self):
        page = self.cli / 'actions' / 'do.md'
        page.write_text('[gone](../reference/nope.md) [abs](/notes) [out](../../dreamlake-notes/SKILL.md) '
                        '[ok](../SKILL.md#route) [web](https://docs.dreamlake.ai/x) [anchor](#here)\n'
                        '```\n[code](missing.md)\n```\n')
        failures = [f for f in self.failures() if 'actions/do.md' in f]
        self.assertEqual(failures, [
            'dreamlake-cli: actions/do.md:1: link ../reference/nope.md does not resolve to a file',
            'dreamlake-cli: actions/do.md:1: link /notes is root-absolute; use a full URL or a path relative to this file',
            'dreamlake-cli: actions/do.md:1: link ../../dreamlake-notes/SKILL.md leaves the skill; refer to other skills by name',
        ])

    def test_requires_closure_and_cycles(self):
        meta = json.loads((self.cli / 'skill.json').read_text())
        (self.cli / 'skill.json').write_text(json.dumps({**meta, 'requires': ['dreamlake-missing']}))
        self.assertFailure("dreamlake-cli: skill.json: requires 'dreamlake-missing', which is not a skill in this repository")
        (self.cli / 'skill.json').write_text(json.dumps({**meta, 'requires': ['dreamlake-cli']}))
        self.assertFailure('dreamlake-cli: skill.json: requires itself')
        (self.cli / 'skill.json').write_text(json.dumps({**meta, 'requires': ['dreamlake-notes']}))
        self.assertFailure('requires cycle: dreamlake-cli -> dreamlake-notes -> dreamlake-cli')
        # The schema's name pattern rejects _template before the graph is built.
        (self.cli / 'skill.json').write_text(json.dumps({**meta, 'requires': ['_template']}))
        self.assertFailure("dreamlake-cli: skill.json.requires[0]: '_template' does not match")

    def test_renamed_rules(self):
        (self.root / 'renamed.json').write_text(json.dumps({'old-name': 'dreamlake-nope'}))
        self.assertFailure('renamed.json: old-name -> dreamlake-nope, but dreamlake-nope is not a skill')
        (self.root / 'renamed.json').write_text(json.dumps({'dreamlake-notes': 'dreamlake-cli'}))
        self.assertFailure('renamed.json: dreamlake-notes is listed as renamed but still exists')
        (self.root / 'renamed.json').write_text(json.dumps({'dreamlake-x': 'dreamlake-x'}))
        failures = self.failures()
        self.assertFailure('renamed.json: dreamlake-x maps to itself', failures)
        (self.root / 'renamed.json').unlink()
        self.assertFailure('renamed.json: missing')

    def test_catalog_and_lock_drift(self):
        text = (self.root / 'catalog.json').read_text()
        (self.root / 'catalog.json').write_text(text.replace('"files": 3', '"files": 9'))
        self.assertFailure('catalog.json: catalog.json: entry for')
        (self.root / 'catalog.json').write_text(text)
        page = self.cli / 'reference' / 'cli-projects.md'
        page.write_text(page.read_text() + 'hand edit\n')
        self.assertFailure('references.lock: dreamlake-cli: reference/cli-projects.md was changed by hand')

    def test_live_url_check_skips_template_and_reports_404(self):
        calls = []

        def fetch(url):
            calls.append(url)
            return fake_fetch(url)
        self.assertEqual(self.failures(offline=False, fetch=fetch), [])
        self.assertEqual(calls, [f'{CLI}/artifacts.md', f'{CLI}/projects.md', f'{DOCS}/notes.md'])
        for skill in (self.template, self.notes):
            meta = json.loads((skill / 'skill.json').read_text())
            (skill / 'skill.json').write_text(json.dumps({**meta, 'docs': [f'{DOCS}/missing']}))
            (skill / 'actions' / 'do.md').write_text('# Do\n')
            sync.sync(self.root, fetch=lambda u: b'# any', skill=skill.name, out=lambda _: None)
            catalog.write(self.root, version='v1')
            if skill is self.template:
                self.assertEqual(self.failures(offline=False, fetch=fetch), [])
        self.assertFailure(f'dreamlake-notes: docs[] page is not served as Markdown: {DOCS}/missing.md: HTTP 404',
                           self.failures(offline=False, fetch=fetch))

    def test_tools_tests_run_or_warn(self):
        tools = self.notes / 'tools'
        tools.mkdir()
        (tools / 'test_tools.py').write_text('def test_fails():\n    assert False\n')
        catalog.write(self.root, version='v1')
        report = check.check_repo(self.root, offline=True, run_tool_tests=True)
        if importlib.util.find_spec('pytest') is None:
            self.assertEqual(report.failures, [])
            self.assertIn('dreamlake-notes: pytest is not installed; tools tests skipped', report.warnings)
        else:
            self.assertTrue(any(f.startswith('dreamlake-notes: tools tests failed') for f in report.failures), report.failures)
        report = check.check_repo(self.root, offline=True, run_tool_tests=False)
        self.assertEqual(report.failures, [])
        self.assertIn('dreamlake-notes: tools tests skipped (--skip-tool-tests)', report.warnings)

    def test_missing_template_is_only_a_warning(self):
        shutil.rmtree(self.template)
        self.regenerate()
        report = check.check_repo(self.root, offline=True, run_tool_tests=False)
        self.assertEqual(report.failures, [])
        self.assertEqual(report.warnings, ['_template: missing; contributors copy it to start a skill'])


class SchemaValidatorTests(unittest.TestCase):
    def test_subset_semantics(self):
        schema = {'type': 'object', 'required': ['a'], 'additionalProperties': False,
                  'properties': {'a': {'type': ['string', 'null'], 'pattern': '^x'},
                                 'b': {'type': 'array', 'uniqueItems': True, 'minItems': 1,
                                       'items': {'enum': [1, 2]}},
                                 'c': {'oneOf': [{'type': 'null'}, {'type': 'integer'}]}}}
        self.assertEqual(check.validate({'a': 'xy', 'b': [1, 2], 'c': None}, schema), [])
        self.assertEqual(check.validate({'a': None}, schema), [])
        self.assertEqual(check.validate({'b': [3, 3], 'c': 'no', 'd': 1}, schema), [
            "$: missing required key 'a'",
            '$.b[0]: must be one of [1, 2]',
            '$.b[1]: must be one of [1, 2]',
            '$.b: duplicate item 3',
            '$.c: must match exactly one alternative',
            "$: unexpected key 'd'",
        ])
        self.assertEqual(check.validate({'a': 'y', 'b': []}, schema),
                         ["$.a: 'y' does not match ^x", '$.b: needs at least 1 item(s)'])
        self.assertEqual(check.validate(True, {'type': 'integer'}), ['$: expected integer'])


if __name__ == '__main__':
    unittest.main()
