#!/usr/bin/env python3
"""Reproduce public Notes/CLI skills from committed, authorized source checkouts."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REPOS = {
    'workspace': 'https://github.com/dreamlake-ai/dreamlake-workspace',
    'cli': 'https://github.com/dreamlake-ai/dreamlake-cli',
}
SCOPES = ('dreamlake-notes/', 'dreamlake-cli/', 'dreamlake-scene-generation/')
SCENE_REFERENCES = ('scene-generation', 'libraries', 'envs', 'envs-layers')
NOTES_REFERENCES_FROM_CLI = ('notes-reading', 'notes-editing', 'notes-collaboration', 'notes-attachments', 'notes-legacy')
NOTES_REFERENCE_ROUTES = {
    '/notes/': 'notes.md',
    '/notes/reading/': 'notes-reading.md',
    '/notes/editing/': 'notes-editing.md',
    '/notes/collaboration/': 'notes-collaboration.md',
    '/notes/attachments/': 'notes-attachments.md',
    '/notes/legacy/': 'notes-legacy.md',
}


def run(*args, cwd=None, env=None):
    return subprocess.check_output(args, cwd=cwd, env=env)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text()) if path.exists() else {}


def action_guide_hashes(source_root, guide_name):
    guide_root = source_root / 'docs/skill-guides' / guide_name
    if not guide_root.is_dir():
        raise ValueError(f'missing action-guide source directory: {guide_root.relative_to(source_root)}')
    files = {
        path.relative_to(source_root).as_posix(): sha(path.read_bytes())
        for path in sorted(guide_root.rglob('*')) if path.is_file()
    }
    if not any(path.endswith('/SKILL.md') for path in files) or not any('/actions/' in path for path in files):
        raise ValueError(f'action-guide source needs SKILL.md and actions/*.md: {guide_root.relative_to(source_root)}')
    return files


def owned_path(root, name):
    p = Path(name)
    if p.is_absolute() or '..' in p.parts or not name.startswith(SCOPES):
        raise ValueError(f'Not a managed skill path: {name}')
    full = root / p
    if not full.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'Path escapes repository: {name}')
    return full


def verify_files(root):
    manifest = read_json(root / 'generated-files.json')
    if manifest.get('version') != 1 or not manifest.get('files'):
        raise ValueError('Missing generated-files.json; run source synchronization first')
    for name, digest in manifest['files'].items():
        path = owned_path(root, name)
        if not path.is_file() or sha(path.read_bytes()) != digest:
            raise ValueError(f'Generated file changed or missing: {name}')
    lock = read_json(root / 'sources.json')
    if sha((root / 'sources.json').read_bytes()) != manifest.get('sourcesSha256'):
        raise ValueError('Source provenance changed without synchronization')
    if lock.get('version') != 1 or set(lock.get('sources', {})) != set(REPOS):
        raise ValueError('Invalid source provenance')
    print(f"Verified {len(manifest['files'])} generated files (integrity only, not upstream freshness).")


def snapshot(source, revision, dest):
    revision = run('git', 'rev-parse', '--verify', revision + '^{commit}', cwd=source).decode().strip()
    archive = run('git', 'archive', revision, 'docs', cwd=source)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(dest, filter='data')
    # The upstream generator determines its output root using git rev-parse.
    run('git', 'init', '-q', str(dest))
    env = dict(os.environ)
    for key in ('URL', 'DEPLOY_PRIME_URL', 'GIT_DIR', 'GIT_WORK_TREE'):
        env.pop(key, None)
    log = run('node', 'docs/scripts/gen-llms.mjs', cwd=dest, env=env).decode()
    print(log.strip())
    return revision


def absolute_reference_links(body, pages, bundled=frozenset()):
    """Rewrite generated-reference sibling links: keep the ones bundled with
    the skill relative, resolve everything else to its canonical docs URL."""
    routes = {}
    for page in pages.rglob('+Page.mdx'):
        rel = page.parent.relative_to(pages).as_posix()
        route = '/' if rel == 'index' else '/' + rel
        filename = 'overview.md' if route == '/' else route[1:].replace('/', '-') + '.md'
        routes[filename] = 'https://docs.dreamlake.ai' + route
    chunks = re.split(r'(^```[^\n]*\n[\s\S]*?^```[^\n]*(?:\n|$))', body.decode(), flags=re.M)
    def replace(match):
        filename, anchor = match[1], match[2] or ''
        if filename in bundled:
            return '](' + filename + anchor + ')'
        if filename not in routes:
            raise ValueError(f'Unresolved docs reference: {filename}')
        return '](' + routes[filename] + anchor + ')'
    for i in range(0, len(chunks), 2):
        chunks[i] = re.sub(r'\]\((?:\./)?([^/:)#]+\.md)(#[^)]*)?\)', replace, chunks[i])
    return ''.join(chunks).encode()


def scene_generation_outputs(dest):
    """Assemble the dreamlake-scene-generation skill from a generated
    workspace snapshot: guide router + actions + tools from the committed
    guide source, plus the generated reference pages it routes to."""
    outputs = {}
    guide_root = dest / 'docs/skill-guides/scene-generation'
    for path in sorted(guide_root.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(guide_root).as_posix()
        if rel == 'SKILL.md' or rel.startswith(('actions/', 'tools/')):
            outputs['dreamlake-scene-generation/' + rel] = path.read_bytes()
    skill_md = outputs.get('dreamlake-scene-generation/SKILL.md', b'')
    front = re.match(rb'---\n(.*?)\n---\n', skill_md, re.S)
    if not front or not re.search(rb'^name: dreamlake-scene-generation$', front[1], re.M) \
            or not re.search(rb'^description: .{40,}', front[1], re.M):
        raise ValueError(
            'scene-generation SKILL.md needs frontmatter with name '
            'dreamlake-scene-generation and a substantive description')
    if not any(name.startswith('dreamlake-scene-generation/tools/') for name in outputs):
        raise ValueError('scene-generation guide source is missing its tools/')
    bundled = frozenset(f'{name}.md' for name in SCENE_REFERENCES)
    for name in SCENE_REFERENCES:
        page = dest / f'skills/dreamlake/reference/{name}.md'
        if not page.is_file():
            raise ValueError(f'workspace generator did not produce reference/{name}.md')
        outputs[f'dreamlake-scene-generation/reference/{name}.md'] = absolute_reference_links(
            page.read_bytes(), dest / 'docs/pages', bundled
        )
    return outputs


def notes_reference_links(body, docs_url):
    """Resolve CLI Notes routes to sibling bundled pages or canonical docs URLs."""
    chunks = re.split(r'(^```[^\n]*\n[\s\S]*?^```[^\n]*(?:\n|$))', body.decode(), flags=re.M)
    bundled_files = {'notes.md', *(name + '.md' for name in NOTES_REFERENCES_FROM_CLI)}
    def replace(match):
        path, anchor = match[1], match[2] or ''
        bundled = NOTES_REFERENCE_ROUTES.get(path)
        return '](' + (bundled if bundled else docs_url.rstrip('/') + path) + anchor + ')'
    for i in range(0, len(chunks), 2):
        chunks[i] = re.sub(r'\]\((/notes/[^)#\s]*)(#[^)]*)?\)', replace, chunks[i])
        def replace_sibling(match):
            filename, anchor = match[1], match[2] or ''
            if filename in bundled_files:
                return match[0]
            slug = filename.removeprefix('notes-')[:-3]
            return '](' + docs_url.rstrip('/') + '/notes/' + slug + '/' + anchor + ')'
        chunks[i] = re.sub(r'\]\((notes-[^/)#]+\.md)(#[^)]*)?\)', replace_sibling, chunks[i])
    return ''.join(chunks).encode()


def collect_sources(paths, locked=None):
    outputs, sources = {}, {}
    with tempfile.TemporaryDirectory(prefix='dreamlake-skills-sync-') as tmp:
        for name, repo in REPOS.items():
            source = paths[name].resolve()
            if not locked:
                dirty = run('git', 'status', '--porcelain', '--', 'docs', cwd=source).decode()
                if dirty.strip():
                    raise ValueError(f'{name}: commit docs changes before synchronizing; working-tree edits are not exported')
            revision = locked['sources'][name]['commit'] if locked else 'HEAD'
            dest = Path(tmp) / name
            dest.mkdir()
            commit = snapshot(source, revision, dest)
            generator = dest / 'docs/scripts/gen-llms.mjs'
            sources[name] = {'repository': repo, 'commit': commit, 'generatorSha256': sha(generator.read_bytes())}
            guide_name = 'notes' if name == 'workspace' else 'cli'
            sources[name]['actionGuides'] = action_guide_hashes(dest, guide_name)
            sources[name]['docsPages'] = (
                'docs/pages/{notes,scene-generation,libraries,envs,envs/layers}/+Page.mdx'
                if name == 'workspace' else 'docs/pages/**/+Page.mdx'
            )
            if name == 'cli':
                cli_skill = dest / 'skills/dreamlake-cli'
                for path in sorted(cli_skill.rglob('*')):
                    if path.is_file():
                        outputs['dreamlake-cli/' + path.relative_to(cli_skill).as_posix()] = path.read_bytes()
                # Notes' task-specific CLI references live in the CLI docs repo;
                # bundle only the pages the Notes action guides link to.
                for reference in NOTES_REFERENCES_FROM_CLI:
                    path = cli_skill / 'reference' / f'{reference}.md'
                    site_config = (dest / 'docs/site.config.ts').read_text()
                    docs_url = re.search(r"\burl:\s*['\"]([^'\"]+)", site_config).group(1)
                    outputs[f'dreamlake-notes/reference/{reference}.md'] = notes_reference_links(path.read_bytes(), docs_url)
            else:
                guide_root = dest / 'docs/skill-guides/notes'
                for path in sorted(guide_root.rglob('*')):
                    if path.is_file() and (path.name == 'SKILL.md' or path.relative_to(guide_root).parts[0] == 'actions'):
                        outputs['dreamlake-notes/' + path.relative_to(guide_root).as_posix()] = path.read_bytes()
                page = dest / 'docs/pages/notes/+Page.mdx'
                sources[name]['page'] = 'docs/pages/notes/+Page.mdx'
                sources[name]['pageSha256'] = sha(page.read_bytes())
                generated = dest / 'skills/dreamlake/reference/notes.md'
                outputs['dreamlake-notes/reference/notes.md'] = absolute_reference_links(
                    generated.read_bytes(), dest / 'docs/pages'
                )
                sources[name]['actionGuides'].update(
                    action_guide_hashes(dest, 'scene-generation'))
                scene_pages = {
                    'scene-generation': 'docs/pages/scene-generation/+Page.mdx',
                    'libraries': 'docs/pages/libraries/+Page.mdx',
                    'envs': 'docs/pages/envs/+Page.mdx',
                    'envs-layers': 'docs/pages/envs/layers/+Page.mdx',
                }
                sources[name]['scenePages'] = {
                    path: sha((dest / path).read_bytes()) for path in scene_pages.values()
                }
                outputs.update(scene_generation_outputs(dest))
    if not outputs.get('dreamlake-cli/SKILL.md'):
        raise ValueError('CLI generator did not produce its expected skill')
    if not outputs.get('dreamlake-scene-generation/SKILL.md'):
        raise ValueError('workspace source did not produce the scene-generation skill')
    return outputs, {'version': 1, 'sources': sources}


def synchronize(root, outputs, sources, check=False):
    old = read_json(root / 'generated-files.json').get('files', {})
    # Do not discard an edited generated file when its source removes that path.
    stale = set(old) - set(outputs)
    for name in stale:
        path = owned_path(root, name)
        if path.exists() and sha(path.read_bytes()) != old[name]:
            raise ValueError(f'Refusing to remove locally edited generated file: {name}')
    source_bytes = (json.dumps(sources, indent=2, ensure_ascii=False) + '\n').encode()
    manifest = {'version': 1, 'sourcesSha256': sha(source_bytes),
                'files': {name: sha(data) for name, data in sorted(outputs.items())}}
    desired = dict(outputs)
    desired['sources.json'] = source_bytes
    desired['generated-files.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    changed = [name for name, data in desired.items()
               if not (root / name).is_file() or (root / name).read_bytes() != data]
    changed += sorted(stale)
    if check:
        if changed:
            raise ValueError('Docs propagation mismatch:\n  ' + '\n  '.join(changed))
        print('Source revisions and generated public skills match.')
        return
    for name, data in outputs.items():
        path = owned_path(root, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    for name in stale:
        owned_path(root, name).unlink(missing_ok=True)
    for name in ('sources.json', 'generated-files.json'):
        (root / name).write_bytes(desired[name])
    print(f'Synchronized {len(outputs)} generated files. No publication or installation performed.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path)
    parser.add_argument('--cli', type=Path)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--locked', action='store_true', help='reproduce recorded commits, not current HEAD')
    parser.add_argument('--verify-files', action='store_true', help='offline integrity only; does not read upstream')
    args = parser.parse_args()
    if args.verify_files:
        verify_files(ROOT)
        return
    if not args.workspace or not args.cli:
        parser.error('--workspace and --cli are required for source synchronization')
    if args.locked and not args.check:
        parser.error('--locked requires --check; update from current source HEAD instead')
    locked = read_json(ROOT / 'sources.json') if args.locked else None
    if args.locked and not locked:
        parser.error('sources.json is required for --locked')
    outputs, sources = collect_sources({'workspace': args.workspace, 'cli': args.cli}, locked)
    synchronize(ROOT, outputs, sources, check=args.check)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error))
