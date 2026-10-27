"""Offline tests for scripts/sync_references.py: fixture skills in a temp dir, a fake fetcher."""
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
import urllib.error

import sync_references as sync

DOCS = 'https://docs.dreamlake.ai'
CLI = 'https://cli.dreamlake.ai'
VIZ = 'https://viz.dreamlake.ai'


class FakeFetcher:
    """Maps fetch URLs to bytes; records every call; 404s anything unknown."""

    def __init__(self, pages):
        self.pages = {url: (body.encode('utf-8') if isinstance(body, str) else body) for url, body in pages.items()}
        self.calls = []

    def __call__(self, url):
        self.calls.append(url)
        if url not in self.pages:
            raise sync.FetchError(f'{url}: HTTP 404')
        return self.pages[url]


def make_skill(root, name, docs):
    skill = root / name
    (skill / 'actions').mkdir(parents=True)
    (skill / 'skill.json').write_text(json.dumps({'name': name, 'description': 'd', 'requires': [],
                                                  'docs': docs, 'tools': None}))
    (skill / 'SKILL.md').write_text(f'---\nname: {name}\ndescription: d\n---\n# {name}\n\n## Canonical source\n\nx\n')
    (skill / 'actions' / 'do.md').write_text('# Do\n')
    return skill


def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


class NamingTests(unittest.TestCase):
    def test_page_url_parsing(self):
        self.assertEqual(sync.parse_page_url(f'{CLI}/artifacts'), ('cli.dreamlake.ai', 'cli', '/artifacts'))
        self.assertEqual(sync.parse_page_url(f'{DOCS}/scenes/layers'), ('docs.dreamlake.ai', 'docs', '/scenes/layers'))
        self.assertEqual(sync.parse_page_url(f'{VIZ}/'), ('viz.dreamlake.ai', 'viz', '/'))
        self.assertEqual(sync.parse_page_url(VIZ), ('viz.dreamlake.ai', 'viz', '/'))
        for bad in ('https://example.com/x', f'{CLI}/artifacts.md', f'{DOCS}/notes/', f'{DOCS}/a?b=1',
                    f'{DOCS}/a#x', 'http://docs.dreamlake.ai/a'):
            with self.subTest(bad=bad), self.assertRaises(sync.SyncError):
                sync.parse_page_url(bad)

    def test_fetch_url_and_reference_names(self):
        cases = {
            f'{CLI}/artifacts': (f'{CLI}/artifacts.md', 'cli-artifacts.md'),
            f'{DOCS}/scenes/layers': (f'{DOCS}/scenes/layers.md', 'docs-scenes-layers.md'),
            f'{VIZ}/dataset-viz/spec': (f'{VIZ}/dataset-viz/spec.md', 'viz-dataset-viz-spec.md'),
            f'{CLI}/': (f'{CLI}/index.md', 'cli-index.md'),
        }
        for url, (fetch_url, name) in cases.items():
            with self.subTest(url=url):
                self.assertEqual(sync.fetch_url_for(url), fetch_url)
                _host, site, route = sync.parse_page_url(url)
                self.assertEqual(sync.reference_name(site, route), name)

    def test_duplicate_reference_names_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = make_skill(Path(tmp), 'dreamlake-x', [f'{DOCS}/scenes/layers', f'{DOCS}/scenes-layers'])
            with self.assertRaisesRegex(sync.SyncError, 'both map to docs-scenes-layers.md'):
                sync.load_docs(skill)


class LinkRewritingTests(unittest.TestCase):
    HOST = 'docs.dreamlake.ai'
    SIBLINGS = {'/projects': 'docs-projects.md', '/scenes/layers': 'docs-scenes-layers.md', '/': 'docs-index.md'}

    def rewrite(self, dest, siblings=None):
        return sync.rewrite_destination(dest, self.HOST, self.SIBLINGS if siblings is None else siblings)

    def test_live_site_link_forms(self):
        self.assertEqual(self.rewrite('/workspaces.md'), f'{DOCS}/workspaces')
        self.assertEqual(self.rewrite('/notes/#x'), f'{DOCS}/notes#x')
        self.assertEqual(self.rewrite('/projects.md#y'), 'docs-projects.md#y')
        self.assertEqual(self.rewrite('/api/external-mounts/'), f'{DOCS}/api/external-mounts')
        self.assertEqual(self.rewrite('/scenes/layers'), 'docs-scenes-layers.md')
        self.assertEqual(self.rewrite('/scenes/layers/#ops'), 'docs-scenes-layers.md#ops')

    def test_same_site_absolute_links(self):
        self.assertEqual(self.rewrite(f'{DOCS}/projects.md#y'), 'docs-projects.md#y')
        self.assertEqual(self.rewrite(f'{DOCS}/scenes/layers/'), 'docs-scenes-layers.md')
        self.assertEqual(self.rewrite(f'{DOCS}/other'), f'{DOCS}/other')
        self.assertEqual(self.rewrite(DOCS), 'docs-index.md')
        self.assertEqual(self.rewrite(f'{DOCS}/'), 'docs-index.md')

    def test_root_and_index(self):
        self.assertEqual(self.rewrite('/'), 'docs-index.md')
        self.assertEqual(self.rewrite('/index.md'), 'docs-index.md')
        self.assertEqual(self.rewrite('/', siblings={}), f'{DOCS}/')

    def test_untouched_forms(self):
        for dest in ('#anchor', f'{CLI}/artifacts#x', 'https://github.com/x/y', 'mailto:a@b.c',
                     'relative.md', '../up.md', '//cdn.example.com/x.js'):
            with self.subTest(dest=dest):
                self.assertEqual(self.rewrite(dest), dest)

    def test_unknown_paths_are_absolutised_without_md(self):
        self.assertEqual(self.rewrite('/img/diagram.png'), f'{DOCS}/img/diagram.png')
        self.assertEqual(self.rewrite('/downloads/skills.zip'), f'{DOCS}/downloads/skills.zip')

    def test_rewrite_links_in_text_skips_fenced_code(self):
        text = '\n'.join([
            'See [projects](/projects.md#y) and ![img](/img/a.png "title") and [a](#top).',
            '```bash',
            'curl [x](/projects.md)',
            '```',
            '~~~',
            '[y](/workspaces.md)',
            '~~~',
            '    ```',
            '[z](/workspaces.md) indented fence still counts',
            '    ```',
            'after [w](/workspaces/)',
        ])
        out = sync.rewrite_links(text, self.HOST, self.SIBLINGS)
        lines = out.split('\n')
        self.assertEqual(lines[0], f'See [projects](docs-projects.md#y) and ![img]({DOCS}/img/a.png "title") and [a](#top).')
        self.assertEqual(lines[2], 'curl [x](/projects.md)')
        self.assertEqual(lines[5], '[y](/workspaces.md)')
        self.assertEqual(lines[8], '[z](/workspaces.md) indented fence still counts')
        self.assertEqual(lines[10], f'after [w]({DOCS}/workspaces)')

    def test_longer_closing_fence_and_tilde_inside_backticks(self):
        text = '````\n```\n[x](/a.md)\n````\n[y](/a.md)'
        out = sync.rewrite_links(text, self.HOST, {})
        self.assertEqual(out.split('\n')[2], '[x](/a.md)')
        self.assertEqual(out.split('\n')[4], f'[y]({DOCS}/a)')


class RenderTests(unittest.TestCase):
    def test_source_line_gives_version_and_is_stripped(self):
        version, body = sync.split_source_line('<!-- source: https://x/y.md @ 0.1.43 abc123 -->\n# T\n')
        self.assertEqual(version, '0.1.43 abc123')
        self.assertEqual(body, '# T\n')
        self.assertEqual(sync.split_source_line('# T\n'), ('unknown', '# T\n'))
        self.assertEqual(sync.split_source_line('<!-- source: https://x/y.md -->\n# T')[0], 'unknown')
        self.assertEqual(sync.split_source_line('<!--source: https://x/y.md @  -->\nbody')[0], 'unknown')

    def test_render_header_and_body(self):
        raw = b'<!-- source: https://cli.dreamlake.ai/artifacts.md @ 1.2.3 deadbeef -->\r\n# A\r\n\r\n[p](/projects.md#x)\r\n'
        text, version = sync.render(f'{CLI}/artifacts', raw, {'/projects': 'cli-projects.md'})
        self.assertEqual(version, '1.2.3 deadbeef')
        self.assertEqual(text.split('\n')[0],
                         f'<!-- generated from {CLI}/artifacts.md at 1.2.3 deadbeef; do not edit -->')
        self.assertTrue(sync.HEADER_RE.match(text.split('\n')[0]))
        self.assertEqual(text, f'<!-- generated from {CLI}/artifacts.md at 1.2.3 deadbeef; do not edit -->\n\n'
                               '# A\n\n[p](cli-projects.md#x)\n')

    def test_render_root_page(self):
        text, version = sync.render(f'{DOCS}/', b'# Home\n', {})
        self.assertEqual(version, 'unknown')
        self.assertTrue(text.startswith(f'<!-- generated from {DOCS}/index.md at unknown; do not edit -->\n'))

    def test_non_utf8_is_an_error(self):
        with self.assertRaises(sync.FetchError):
            sync.render(f'{DOCS}/x', b'\xff\xfe', {})


class SyncTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.a = make_skill(self.root, 'dreamlake-a', [f'{CLI}/artifacts', f'{CLI}/projects', f'{DOCS}/'])
        self.b = make_skill(self.root, 'dreamlake-b', [f'{CLI}/projects'])
        (self.root / '.hidden').mkdir()
        (self.root / '.hidden' / 'skill.json').write_text('{}')
        self.fetcher = FakeFetcher({
            f'{CLI}/artifacts.md': '<!-- source: x @ 9.9 -->\n# Artifacts\n[p](/projects.md#move) [n](/notes/) [s](#self)\n',
            f'{CLI}/projects.md': '# Projects\n[a](/artifacts.md) [i](https://cli.dreamlake.ai/)\n',
            f'{DOCS}/index.md': '# Docs\n[c](/cli.md#collections)\n',
        })

    def read(self, skill, name):
        return (skill / 'reference' / name).read_text()

    def lock(self):
        return json.loads((self.root / 'references.lock').read_text())

    def test_sync_writes_files_and_lock_and_removes_orphans(self):
        (self.a / 'reference').mkdir()
        (self.a / 'reference' / 'stale.md').write_text('old')
        (self.a / 'reference' / 'render.py').write_text('print()')
        out = []
        differences = sync.sync(self.root, fetch=self.fetcher, out=out.append)
        self.assertEqual(sorted(p.name for p in (self.a / 'reference').iterdir()),
                         ['cli-artifacts.md', 'cli-projects.md', 'docs-index.md'])
        self.assertEqual([p.name for p in (self.b / 'reference').iterdir()], ['cli-projects.md'])
        self.assertIn('dreamlake-a: remove reference/stale.md (no docs[] entry produces it)', differences)
        self.assertIn('dreamlake-a: remove reference/render.py (no docs[] entry produces it)', differences)
        self.assertEqual(self.read(self.a, 'cli-artifacts.md'),
                         f'<!-- generated from {CLI}/artifacts.md at 9.9; do not edit -->\n\n'
                         f'# Artifacts\n[p](cli-projects.md#move) [n]({CLI}/notes) [s](#self)\n')
        # In skill b, /artifacts is not in docs[], so it becomes an absolute page URL; the root is not either.
        self.assertEqual(self.read(self.b, 'cli-projects.md'),
                         f'<!-- generated from {CLI}/projects.md at unknown; do not edit -->\n\n'
                         f'# Projects\n[a]({CLI}/artifacts) [i]({CLI}/)\n')
        # In skill a, /artifacts is a sibling; the CLI root is not in docs[] (the docs root is), so it stays absolute.
        self.assertIn(f'[a](cli-artifacts.md) [i]({CLI}/)', self.read(self.a, 'cli-projects.md'))
        self.assertIn(f'[c]({DOCS}/cli#collections)', self.read(self.a, 'docs-index.md'))
        lock = self.lock()
        self.assertEqual(lock['schema'], 1)
        self.assertEqual(list(lock['skills']), ['dreamlake-a', 'dreamlake-b'])
        entry = lock['skills']['dreamlake-a'][0]
        self.assertEqual(entry['url'], f'{CLI}/artifacts')
        self.assertEqual(entry['file'], 'reference/cli-artifacts.md')
        self.assertEqual(entry['version'], '9.9')
        self.assertEqual(entry['source_sha256'], hashlib.sha256(self.fetcher.pages[f'{CLI}/artifacts.md']).hexdigest())
        self.assertEqual(entry['sha256'], sha(self.read(self.a, 'cli-artifacts.md')))
        self.assertEqual(self.lock()['skills']['dreamlake-b'][0]['version'], 'unknown')
        # Requests are sequential, one per page, in docs[] order per skill.
        self.assertEqual(self.fetcher.calls, [f'{CLI}/artifacts.md', f'{CLI}/projects.md', f'{DOCS}/index.md',
                                              f'{CLI}/projects.md'])
        # A second run is a no-op.
        out.clear()
        self.assertEqual(sync.sync(self.root, fetch=self.fetcher, out=out.append), [])
        self.assertEqual(out, ['reference/ is up to date'])
        self.assertEqual(sync.offline_verify(self.root), [])

    def test_check_reports_and_writes_nothing(self):
        sync.sync(self.root, fetch=self.fetcher, out=lambda _: None)
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.fetcher.pages[f'{CLI}/projects.md'] = b'# Projects v2\n'
        (self.b / 'reference' / 'extra.md').write_text('x')
        out = []
        differences = sync.sync(self.root, fetch=self.fetcher, check=True, out=out.append)
        self.assertEqual(differences, [
            f'dreamlake-a: update reference/cli-projects.md ({CLI}/projects @ unknown)',
            'dreamlake-a: references.lock entry differs',
            f'dreamlake-b: update reference/cli-projects.md ({CLI}/projects @ unknown)',
            'dreamlake-b: remove reference/extra.md (no docs[] entry produces it)',
            'dreamlake-b: references.lock entry differs',
        ])
        self.assertTrue(all(line.startswith('would ') for line in out))
        after = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual({k: v for k, v in after.items() if k.name != 'extra.md'}, before)

    def test_skill_scope_limits_writes_and_keeps_other_lock_entries(self):
        sync.sync(self.root, fetch=self.fetcher, out=lambda _: None)
        self.fetcher.pages[f'{CLI}/projects.md'] = b'# Projects v2\n'
        self.fetcher.calls.clear()
        sync.sync(self.root, fetch=self.fetcher, skill='dreamlake-b', out=lambda _: None)
        self.assertEqual(self.fetcher.calls, [f'{CLI}/projects.md'])
        self.assertIn('v2', self.read(self.b, 'cli-projects.md'))
        self.assertNotIn('v2', self.read(self.a, 'cli-projects.md'))
        self.assertEqual(sorted(self.lock()['skills']), ['dreamlake-a', 'dreamlake-b'])
        with self.assertRaisesRegex(sync.SyncError, 'no skill directory named'):
            sync.sync(self.root, fetch=self.fetcher, skill='nope', out=lambda _: None)

    def test_stale_lock_entries_are_dropped_on_full_sync(self):
        sync.sync(self.root, fetch=self.fetcher, out=lambda _: None)
        self.assertIn('dreamlake-b: references.lock entry has no skill directory',
                      self.do_remove_b_and_verify())
        differences = sync.sync(self.root, fetch=self.fetcher, out=lambda _: None)
        self.assertIn('dreamlake-b: removed stale references.lock entry', differences)
        self.assertEqual(list(self.lock()['skills']), ['dreamlake-a'])

    def do_remove_b_and_verify(self):
        import shutil
        shutil.rmtree(self.b)
        return sync.offline_verify(self.root)

    def test_offline_verify_detects_every_drift(self):
        sync.sync(self.root, fetch=self.fetcher, out=lambda _: None)
        self.assertEqual(sync.offline_verify(self.root), [])
        self.assertEqual(sync.offline_verify(self.root, skill='dreamlake-b'), [])

        path = self.a / 'reference' / 'cli-projects.md'
        original = path.read_text()
        path.write_text(original + 'edited\n')
        self.assertEqual(sync.offline_verify(self.root, skill='dreamlake-a'),
                         ['dreamlake-a: reference/cli-projects.md was changed by hand; it is generated, so revert it '
                          'or run scripts/sync_references.py'])
        path.write_text(original)

        path.unlink()
        self.assertEqual(sync.offline_verify(self.root, skill='dreamlake-a'),
                         ['dreamlake-a: reference/cli-projects.md is missing'])
        path.write_text(original)

        (self.a / 'reference' / 'extra.md').write_text('x')
        self.assertEqual(sync.offline_verify(self.root, skill='dreamlake-a'),
                         ['dreamlake-a: reference/extra.md is not in references.lock'])
        (self.a / 'reference' / 'extra.md').unlink()

        meta = json.loads((self.a / 'skill.json').read_text())
        meta['docs'].append(f'{VIZ}/dataset-viz/spec')
        (self.a / 'skill.json').write_text(json.dumps(meta))
        problems = sync.offline_verify(self.root, skill='dreamlake-a')
        self.assertEqual(problems, ['dreamlake-a: docs[] differs from references.lock; '
                                    'run scripts/sync_references.py --skill dreamlake-a'])

        (self.root / 'references.lock').unlink()
        problems = sync.offline_verify(self.root)
        self.assertEqual(problems[0], 'references.lock is missing; run scripts/sync_references.py')

    def test_fetch_failure_names_skill_and_page_and_writes_nothing(self):
        del self.fetcher.pages[f'{DOCS}/index.md']
        with self.assertRaisesRegex(sync.FetchError, r'dreamlake-a: .*index\.md: HTTP 404'):
            sync.sync(self.root, fetch=self.fetcher, out=lambda _: None)
        self.assertFalse((self.a / 'reference').exists())
        self.assertFalse((self.root / 'references.lock').exists())

    def test_unknown_host_in_docs_is_an_error(self):
        make_skill(self.root, 'dreamlake-c', ['https://example.com/page'])
        with self.assertRaisesRegex(sync.SyncError, "dreamlake-c/skill.json: .*host 'example.com'"):
            sync.sync(self.root, fetch=self.fetcher, skill='dreamlake-c', out=lambda _: None)

    def test_empty_docs_leaves_no_reference_dir(self):
        c = make_skill(self.root, 'dreamlake-c', [])
        sync.sync(self.root, fetch=self.fetcher, skill='dreamlake-c', out=lambda _: None)
        self.assertFalse((c / 'reference').exists())
        self.assertEqual(self.lock()['skills']['dreamlake-c'], [])
        self.assertEqual(sync.offline_verify(self.root, skill='dreamlake-c'), [])

    def test_main_exit_codes(self):
        sync.sync(self.root, fetch=self.fetcher, out=lambda _: None)
        self.assertEqual(sync.main(['--root', str(self.root), '--offline-verify']), 0)
        (self.a / 'reference' / 'docs-index.md').write_text('tampered')
        self.assertEqual(sync.main(['--root', str(self.root), '--offline-verify']), 1)
        self.assertEqual(sync.main(['--root', str(self.root), '--offline-verify', '--skill', 'dreamlake-b']), 0)


class FakeResponse(io.BytesIO):
    def __init__(self, data, content_type='text/markdown; charset=utf-8'):
        super().__init__(data)
        self.headers = {'Content-Type': content_type}

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


class HttpFetchTests(unittest.TestCase):
    def opener(self, outcomes):
        requests = []

        def open_(request, timeout):
            requests.append((request.full_url, request.get_header('User-agent'), timeout))
            outcome = outcomes.pop(0)
            if isinstance(outcome, Exception):
                raise outcome
            return outcome
        return open_, requests

    def test_retries_once_on_5xx_then_succeeds(self):
        error = urllib.error.HTTPError('u', 503, 'down', None, None)
        opener, requests = self.opener([error, FakeResponse(b'# ok')])
        sleeps = []
        data = sync.http_fetch('https://cli.dreamlake.ai/x.md', sleep=sleeps.append, opener=opener)
        self.assertEqual(data, b'# ok')
        self.assertEqual(len(requests), 2)
        self.assertEqual(sleeps, [sync.RETRY_DELAY_SECONDS])
        self.assertEqual(requests[0][1], sync.USER_AGENT)
        self.assertEqual(requests[0][2], sync.TIMEOUT_SECONDS)

    def test_gives_up_after_second_5xx(self):
        opener, requests = self.opener([urllib.error.HTTPError('u', 502, 'bad', None, None)] * 2)
        with self.assertRaisesRegex(sync.FetchError, 'HTTP 502'):
            sync.http_fetch('https://cli.dreamlake.ai/x.md', sleep=lambda _: None, opener=opener)
        self.assertEqual(len(requests), 2)

    def test_404_is_not_retried(self):
        opener, requests = self.opener([urllib.error.HTTPError('u', 404, 'nope', None, None)])
        with self.assertRaisesRegex(sync.FetchError, 'HTTP 404'):
            sync.http_fetch('https://cli.dreamlake.ai/x.md', sleep=lambda _: None, opener=opener)
        self.assertEqual(len(requests), 1)

    def test_network_error_is_retried_once(self):
        opener, requests = self.opener([urllib.error.URLError('timed out'), urllib.error.URLError('timed out')])
        with self.assertRaisesRegex(sync.FetchError, 'timed out'):
            sync.http_fetch('https://cli.dreamlake.ai/x.md', sleep=lambda _: None, opener=opener)
        self.assertEqual(len(requests), 2)

    def test_html_body_is_rejected(self):
        opener, _ = self.opener([FakeResponse(b'<html>', 'text/html; charset=utf-8')])
        with self.assertRaisesRegex(sync.FetchError, 'text/html'):
            sync.http_fetch('https://cli.dreamlake.ai/x.md', sleep=lambda _: None, opener=opener)


if __name__ == '__main__':
    unittest.main()
