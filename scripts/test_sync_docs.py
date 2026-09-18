import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('sync_docs', Path(__file__).with_name('sync-docs.py'))
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.sources = {'version': 1, 'sources': {
            name: {'repository': repo, 'commit': 'a' * 40}
            for name, repo in sync.REPOS.items()}}

    def test_roundtrip_and_tamper_detection(self):
        outputs = {'dreamlake-notes/SKILL.md': b'original'}
        sync.synchronize(self.root, outputs, self.sources)
        sync.synchronize(self.root, outputs, self.sources, check=True)
        sync.verify_files(self.root)
        (self.root / 'dreamlake-notes/SKILL.md').write_bytes(b'edited')
        with self.assertRaisesRegex(ValueError, 'changed or missing'):
            sync.verify_files(self.root)
        with self.assertRaisesRegex(ValueError, 'propagation mismatch'):
            sync.synchronize(self.root, outputs, self.sources, check=True)

    def test_removed_output_preserves_unowned_peer(self):
        sync.synchronize(self.root, {'dreamlake-cli/reference/old.md': b'old'}, self.sources)
        peer = self.root / 'dreamlake-cli/reference/local.md'
        peer.write_bytes(b'hand authored')
        sync.synchronize(self.root, {'dreamlake-cli/SKILL.md': b'new'}, self.sources)
        self.assertFalse((peer.parent / 'old.md').exists())
        self.assertEqual(peer.read_bytes(), b'hand authored')

    def test_refuses_to_remove_edited_output(self):
        path = 'dreamlake-cli/reference/old.md'
        sync.synchronize(self.root, {path: b'old'}, self.sources)
        (self.root / path).write_bytes(b'local change')
        with self.assertRaisesRegex(ValueError, 'locally edited'):
            sync.synchronize(self.root, {'dreamlake-cli/SKILL.md': b'new'}, self.sources)
        self.assertEqual((self.root / path).read_bytes(), b'local change')

    def test_changed_source_revision_detected(self):
        outputs = {'dreamlake-notes/SKILL.md': b'same'}
        sync.synchronize(self.root, outputs, self.sources)
        self.sources['sources']['workspace']['commit'] = 'b' * 40
        with self.assertRaisesRegex(ValueError, 'sources.json'):
            sync.synchronize(self.root, outputs, self.sources, check=True)

    def test_links_preserve_fences_and_hyphenated_paths(self):
        pages = self.root / 'pages'
        path = pages / 'notes/linked-items/+Page.mdx'
        path.parent.mkdir(parents=True)
        path.write_text('guide')
        body = b'[guide](notes-linked-items.md#test)\n```md\n[example](unknown.md)\n```\n'
        result = sync.absolute_reference_links(body, pages)
        self.assertIn(b'https://docs.dreamlake.ai/notes/linked-items#test', result)
        self.assertIn(b'[example](unknown.md)', result)
        with self.assertRaisesRegex(ValueError, 'Unresolved'):
            sync.absolute_reference_links(b'[bad](unknown.md)', pages)

    def test_owned_paths_cannot_escape(self):
        for name in ('../outside', '/tmp/outside', 'README.md', 'dreamlake-cli/../../outside'):
            with self.assertRaises(ValueError):
                sync.owned_path(self.root, name)

    def test_snapshot_uses_commit_not_dirty_worktree(self):
        source = self.root / 'source'
        source.mkdir()
        def git(*args):
            return subprocess.check_output(['git', *args], cwd=source).decode().strip()
        git('init', '-q')
        docs = source / 'docs'
        (docs / 'scripts').mkdir(parents=True)
        (docs / 'value.txt').write_text('committed')
        (docs / 'scripts/gen-llms.mjs').write_text(
            "import fs from 'node:fs'; fs.mkdirSync('skills/dreamlake-cli', {recursive:true});"
            "fs.writeFileSync('skills/dreamlake-cli/SKILL.md', fs.readFileSync('docs/value.txt'));"
        )
        git('add', 'docs')
        git('-c', 'user.name=Test', '-c', 'user.email=test@example.com', 'commit', '-qm', 'fixture')
        revision = git('rev-parse', 'HEAD')
        (docs / 'value.txt').write_text('uncommitted')
        dest = self.root / 'export'
        dest.mkdir()
        self.assertEqual(sync.snapshot(source, revision, dest), revision)
        self.assertEqual((dest / 'skills/dreamlake-cli/SKILL.md').read_text(), 'committed')
        self.assertEqual((docs / 'value.txt').read_text(), 'uncommitted')


if __name__ == '__main__':
    unittest.main()
