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
SCOPES = ('dreamlake-notes/', 'dreamlake-cli/')


def run(*args, cwd=None, env=None):
    return subprocess.check_output(args, cwd=cwd, env=env)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text()) if path.exists() else {}


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


def absolute_reference_links(body, pages):
    routes = {}
    for page in pages.rglob('+Page.mdx'):
        rel = page.parent.relative_to(pages).as_posix()
        route = '/' if rel == 'index' else '/' + rel
        filename = 'overview.md' if route == '/' else route[1:].replace('/', '-') + '.md'
        routes[filename] = 'https://docs.dreamlake.ai' + route
    chunks = re.split(r'(^```[^\n]*\n[\s\S]*?^```[^\n]*(?:\n|$))', body.decode(), flags=re.M)
    def replace(match):
        filename, anchor = match[1], match[2] or ''
        if filename not in routes:
            raise ValueError(f'Unresolved Notes reference: {filename}')
        return '](' + routes[filename] + anchor + ')'
    for i in range(0, len(chunks), 2):
        chunks[i] = re.sub(r'\]\((?:\./)?([^/:)#]+\.md)(#[^)]*)?\)', replace, chunks[i])
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
            if name == 'cli':
                for path in sorted((dest / 'skills/dreamlake-cli').rglob('*')):
                    if path.is_file():
                        outputs['dreamlake-cli/' + path.relative_to(dest / 'skills/dreamlake-cli').as_posix()] = path.read_bytes()
            else:
                page = dest / 'docs/pages/notes/+Page.mdx'
                description = re.search(r'^description: (.+)$', page.read_text(), re.M).group(1)
                sources[name]['page'] = 'docs/pages/notes/+Page.mdx'
                sources[name]['pageSha256'] = sha(page.read_bytes())
                body = (dest / 'skills/dreamlake/reference/notes.md').read_bytes()
                body = absolute_reference_links(body, dest / 'docs/pages')
                outputs['dreamlake-notes/reference/notes.md'] = body
                outputs['dreamlake-notes/SKILL.md'] = (
                    '---\nname: dreamlake-notes\ndescription: ' + json.dumps(description, ensure_ascii=False) + '\n---\n\n'
                    '# DreamLake Notes\n\n'
                    'Read [the Notes guide](reference/notes.md) before using the CLI or Python SDK\n'
                    'to create, read, edit, search or attach files to a collaborative note.\n\n'
                    'GENERATED from the [Notes docs](https://docs.dreamlake.ai/notes/).\n'
                    'Correct procedures and examples in the source docs, then run\n'
                    '`scripts/sync-docs.py`. Source revision and generator are recorded in\n'
                    '`sources.json` at the repository root. Do not maintain a second procedure here.\n'
                ).encode()
    if not outputs.get('dreamlake-cli/SKILL.md'):
        raise ValueError('CLI generator did not produce its expected skill')
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
