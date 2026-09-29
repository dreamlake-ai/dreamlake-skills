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
        outputs = {
            'dreamlake-notes/SKILL.md': b'original',
            'dreamlake-notes/actions/read.md': b'generated action',
        }
        sync.synchronize(self.root, outputs, self.sources)
        sync.synchronize(self.root, outputs, self.sources, check=True)
        sync.verify_files(self.root)
        (self.root / 'dreamlake-notes/actions/read.md').write_bytes(b'edited')
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

    def test_action_guides_are_explicit_hashed_inputs(self):
        guide = self.root / 'docs/skill-guides/notes'
        (guide / 'actions').mkdir(parents=True)
        (guide / 'SKILL.md').write_text('router')
        action = guide / 'actions/read.md'
        action.write_text('read flow')
        hashes = sync.action_guide_hashes(self.root, 'notes')
        self.assertEqual(set(hashes), {
            'docs/skill-guides/notes/SKILL.md',
            'docs/skill-guides/notes/actions/read.md',
        })
        self.assertEqual(hashes['docs/skill-guides/notes/actions/read.md'], sync.sha(b'read flow'))
        (self.root / 'docs/skill-guides/empty').mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, 'SKILL.md and actions'):
            sync.action_guide_hashes(self.root, 'empty')

    def test_notes_reference_routes_resolve_bundled_and_external_links(self):
        body = (b'[edit](/notes/editing/#patch) [rich](/notes/rich-content/) '
                b'[other](notes-rich-content.md#tokens)\n'
                b'```md\n[example](/notes/editing/)\n```\n')
        result = sync.notes_reference_links(body, 'https://cli.dreamlake.ai')
        self.assertIn(b'[edit](notes-editing.md#patch)', result)
        self.assertIn(b'[rich](https://cli.dreamlake.ai/notes/rich-content/)', result)
        self.assertIn(b'[other](https://cli.dreamlake.ai/notes/rich-content/#tokens)', result)
        self.assertIn(b'[example](/notes/editing/)', result)

    def test_owned_paths_cannot_escape(self):
        for name in ('../outside', '/tmp/outside', 'README.md', 'dreamlake-cli/../../outside'):
            with self.assertRaises(ValueError):
                sync.owned_path(self.root, name)

    def _scene_snapshot(self, skill_md=None):
        guide = self.root / 'docs/skill-guides/scene-generation'
        (guide / 'actions').mkdir(parents=True)
        (guide / 'tools').mkdir()
        (guide / 'SKILL.md').write_text(skill_md if skill_md is not None else (
            '---\nname: dreamlake-scene-generation\ndescription: "Create or edit '
            'MuJoCo scenes with DreamLake libraries, layered envs and validation."\n---\n# S\n'
        ))
        (guide / 'actions/find-assets.md').write_text('search then pull')
        (guide / 'tools/scene_report.py').write_text('print("report")')
        (guide / 'tools/test_scene_tools.py').write_text('def test_ok(): pass')
        reference = self.root / 'skills/dreamlake/reference'
        reference.mkdir(parents=True)
        for name in sync.SCENE_REFERENCES:
            reference.mkdir(exist_ok=True)
            (reference / f'{name}.md').write_text(
                f'# {name}\nsee [layers](envs-layers.md#semantics-rules) and [cli](cli.md#envs)\n'
            )
        for route in ('scene-generation', 'libraries', 'envs', 'envs/layers', 'cli'):
            page = self.root / 'docs/pages' / route / '+Page.mdx'
            page.parent.mkdir(parents=True, exist_ok=True)
            page.write_text('page')
        return self.root

    def test_scene_generation_bundle_includes_every_helper_file(self):
        outputs = sync.scene_generation_outputs(self._scene_snapshot())
        self.assertEqual(set(outputs), {
            'dreamlake-scene-generation/SKILL.md',
            'dreamlake-scene-generation/actions/find-assets.md',
            'dreamlake-scene-generation/tools/scene_report.py',
            'dreamlake-scene-generation/tools/test_scene_tools.py',
            'dreamlake-scene-generation/reference/scene-generation.md',
            'dreamlake-scene-generation/reference/libraries.md',
            'dreamlake-scene-generation/reference/envs.md',
            'dreamlake-scene-generation/reference/envs-layers.md',
        })
        # bundled reference links stay relative; non-bundled resolve to docs
        body = outputs['dreamlake-scene-generation/reference/envs.md'].decode()
        self.assertIn('](envs-layers.md#semantics-rules)', body)
        self.assertIn('](https://docs.dreamlake.ai/cli#envs)', body)

    def test_scene_generation_requires_frontmatter_and_tools(self):
        root = self._scene_snapshot(skill_md='# no frontmatter\n')
        with self.assertRaisesRegex(ValueError, 'frontmatter'):
            sync.scene_generation_outputs(root)
        (root / 'docs/skill-guides/scene-generation/SKILL.md').write_text(
            '---\nname: dreamlake-scene-generation\ndescription: "Create or edit '
            'MuJoCo scenes with DreamLake libraries, layered envs and validation."\n---\n'
        )
        for tool in (root / 'docs/skill-guides/scene-generation/tools').iterdir():
            tool.unlink()
        with self.assertRaisesRegex(ValueError, 'missing its tools'):
            sync.scene_generation_outputs(root)

    def test_scene_generation_missing_reference_is_actionable(self):
        root = self._scene_snapshot()
        (root / 'skills/dreamlake/reference/envs-layers.md').unlink()
        with self.assertRaisesRegex(ValueError, 'reference/envs-layers.md'):
            sync.scene_generation_outputs(root)

    def test_scene_generation_outputs_roundtrip_through_manifest(self):
        outputs = sync.scene_generation_outputs(self._scene_snapshot())
        peer = self.root / 'dreamlake-envs/SKILL.md'
        peer.parent.mkdir()
        peer.write_text('hand-maintained peer skill')
        sync.synchronize(self.root, outputs, self.sources)
        sync.synchronize(self.root, outputs, self.sources, check=True)
        sync.verify_files(self.root)
        self.assertEqual(peer.read_text(), 'hand-maintained peer skill')
        (self.root / 'dreamlake-scene-generation/tools/scene_report.py').write_text('edited')
        with self.assertRaisesRegex(ValueError, 'changed or missing'):
            sync.verify_files(self.root)

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
