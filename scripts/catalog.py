#!/usr/bin/env python3
"""Generate catalog.json from every <skill>/skill.json plus renamed.json.

catalog.json is the one small file the dreamlake CLI downloads to list skills
and resolve `requires`:

  {
    "schema": 1,
    "version": "<tag>",
    "skills": {"<name>": {"description": "...", "requires": [...], "tools": null | {...}, "files": <int>}},
    "renamed": {"<old name>": "<new name>"}
  }

`version` is --version (CI passes the release tag) or `git describe --tags --always`.
`files` counts a skill's files excluding reference/, dotfiles and Python caches.
_template/ and every other underscore- or dot-prefixed directory are not listed.
--check exits 1 when catalog.json differs from a fresh build; `version` is not compared.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CATALOG_FILE = 'catalog.json'
RENAMED_FILE = 'renamed.json'
SKILL_FILE = 'skill.json'
CATALOG_SCHEMA = 1
UNCOUNTED_DIRS = {'reference'}
FALLBACK_VERSION = 'untagged'
CATALOG_FIELDS = ('description', 'requires', 'tools')


class CatalogError(Exception):
    """A skill.json or renamed.json cannot be turned into a catalog."""


def skill_dirs(root):
    """Top-level directories with a skill.json, excluding dot- and underscore-prefixed names."""
    return sorted(d for d in root.iterdir()
                  if d.is_dir() and not d.name.startswith(('.', '_')) and (d / SKILL_FILE).is_file())


def iter_files(skill_dir, skip_reference=True):
    """Files shipped with a skill, sorted. Dotfiles, __pycache__ and *.pyc never count."""
    for path in sorted(skill_dir.rglob('*')):
        if not path.is_file():
            continue
        parts = path.relative_to(skill_dir).parts
        if any(part.startswith('.') or part == '__pycache__' for part in parts) or path.suffix == '.pyc':
            continue
        if skip_reference and parts[0] in UNCOUNTED_DIRS:
            continue
        yield path


def git_version(root):
    try:
        output = subprocess.run(['git', 'describe', '--tags', '--always'], cwd=root, check=True,
                                capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return FALLBACK_VERSION
    return output or FALLBACK_VERSION


def load_json(path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except OSError as error:
        raise CatalogError(f'{path.name}: {error.strerror}') from None
    except ValueError as error:
        raise CatalogError(f'{path.name}: invalid JSON ({error})') from None


def load_renamed(root):
    path = root / RENAMED_FILE
    if not path.is_file():
        raise CatalogError(f'{RENAMED_FILE} is missing; write {{}} when nothing was renamed')
    renamed = load_json(path)
    if not isinstance(renamed, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in renamed.items()):
        raise CatalogError(f'{RENAMED_FILE} must map old skill names to new skill names')
    return {old: renamed[old] for old in sorted(renamed)}


def build(root, version=None):
    skills = {}
    for skill_dir in skill_dirs(root):
        meta = load_json(skill_dir / SKILL_FILE)
        if not isinstance(meta, dict):
            raise CatalogError(f'{skill_dir.name}/{SKILL_FILE} must be a JSON object')
        missing = [key for key in ('name', *CATALOG_FIELDS) if key not in meta]
        if missing:
            raise CatalogError(f'{skill_dir.name}/{SKILL_FILE} lacks {", ".join(missing)}')
        if meta['name'] != skill_dir.name:
            raise CatalogError(f'{skill_dir.name}/{SKILL_FILE}: name {meta["name"]!r} differs from the directory name')
        skills[skill_dir.name] = {
            'description': meta['description'],
            'requires': list(meta['requires']),
            'tools': meta['tools'],
            'files': sum(1 for _ in iter_files(skill_dir)),
        }
    return {'schema': CATALOG_SCHEMA, 'version': version or git_version(root),
            'skills': skills, 'renamed': load_renamed(root)}


def dumps(catalog):
    return json.dumps(catalog, indent=2, ensure_ascii=False) + '\n'


def write(root, version=None):
    catalog = build(root, version)
    (root / CATALOG_FILE).write_text(dumps(catalog), encoding='utf-8')
    return catalog


def check(root):
    """Differences between catalog.json and a fresh build, ignoring `version`."""
    path = root / CATALOG_FILE
    if not path.is_file():
        return [f'{CATALOG_FILE} is missing; run scripts/catalog.py']
    text = path.read_text(encoding='utf-8')
    try:
        current = json.loads(text)
    except ValueError as error:
        return [f'{CATALOG_FILE}: invalid JSON ({error})']
    if not isinstance(current, dict):
        return [f'{CATALOG_FILE} must be a JSON object']
    expected = build(root, version='-')
    problems = []
    if current.get('schema') != CATALOG_SCHEMA:
        problems.append(f'{CATALOG_FILE}: schema must be {CATALOG_SCHEMA}')
    if not isinstance(current.get('version'), str) or not current['version']:
        problems.append(f'{CATALOG_FILE}: version must be a non-empty string')
    current_skills = current.get('skills')
    if not isinstance(current_skills, dict):
        problems.append(f'{CATALOG_FILE}: skills must be an object')
    else:
        for name in sorted(set(current_skills) | set(expected['skills'])):
            if name not in expected['skills']:
                problems.append(f'{CATALOG_FILE}: lists {name}, which has no {SKILL_FILE}')
            elif name not in current_skills:
                problems.append(f'{CATALOG_FILE}: does not list {name}')
            elif current_skills[name] != expected['skills'][name]:
                problems.append(f'{CATALOG_FILE}: entry for {name} is stale')
    if current.get('renamed') != expected['renamed']:
        problems.append(f'{CATALOG_FILE}: renamed differs from {RENAMED_FILE}')
    for key in sorted(set(current) - set(expected)):
        problems.append(f'{CATALOG_FILE}: unexpected key {key!r}')
    if not problems and text != dumps({**expected, 'version': current['version']}):
        problems.append(f'{CATALOG_FILE}: formatting differs from scripts/catalog.py output')
    if problems:
        problems.append('run scripts/catalog.py to regenerate')
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', type=Path, default=ROOT, help='repository root (default: this checkout)')
    parser.add_argument('--version', help='release tag to record (default: git describe --tags --always)')
    parser.add_argument('--check', action='store_true', help='exit 1 if catalog.json differs (version ignored)')
    args = parser.parse_args(argv)
    try:
        if args.check:
            problems = check(args.root)
            for line in problems:
                print(line)
            if problems:
                return 1
            print(f'{CATALOG_FILE} is up to date')
            return 0
        catalog = write(args.root, args.version)
    except CatalogError as error:
        print(f'error: {error}', file=sys.stderr)
        return 1
    print(f'{CATALOG_FILE}: {len(catalog["skills"])} skill(s), version {catalog["version"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
