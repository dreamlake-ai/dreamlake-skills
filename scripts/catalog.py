#!/usr/bin/env python3
"""Validate skill ownership and render the maintenance inventory (offline)."""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- catalog:start -->'
END = '<!-- catalog:end -->'
MODES = {'generated': 'Generated', 'manual-product': 'Manual product', 'standalone': 'Standalone'}


def load(root):
    catalog = json.loads((root / 'catalog.json').read_text())
    if catalog.get('version') != 1 or not isinstance(catalog.get('skills'), dict):
        raise ValueError('Invalid catalog.json')
    skills = catalog['skills']
    actual = {p.parent.name for p in root.glob('*/SKILL.md')}
    if set(skills) != actual:
        raise ValueError(f'Catalog coverage mismatch: unregistered={sorted(actual - set(skills))}, '
                         f'missing={sorted(set(skills) - actual)}')
    generated = json.loads((root / 'generated-files.json').read_text())['files']
    sources = json.loads((root / 'sources.json').read_text())['sources']
    for path in generated:
        name = path.split('/')[0]
        if name not in skills or skills[name].get('maintenance') != 'generated':
            raise ValueError(f'Generated file has no generated catalog owner: {path}')
    readme = (root / 'README.md').read_text()
    for name, item in skills.items():
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
            raise ValueError(f'Invalid skill name: {name}')
        mode = item.get('maintenance')
        if mode not in MODES:
            raise ValueError(f'{name}: unknown maintenance mode')
        edit = item.get('edit', '')
        if not isinstance(edit, str) or not edit or any(c in edit for c in '\n|[]()'):
            raise ValueError(f'{name}: missing or invalid edit location')
        for key in ('review_docs', 'overlaps'):
            if not isinstance(item.get(key), list) or not all(isinstance(v, str) for v in item[key]):
                raise ValueError(f'{name}: {key} must be a list of strings')
        if mode == 'generated':
            if f'{name}/SKILL.md' not in generated or not edit.startswith('https://github.com/'):
                raise ValueError(f'{name}: generated entry needs upstream source and generated SKILL.md')
            keys = item.get('source_repos', [])
            if not keys or any(key not in sources for key in keys):
                raise ValueError(f'{name}: unknown or missing source repositories')
        else:
            if edit != f'{name}/' or item.get('source_repos'):
                raise ValueError(f'{name}: hand-maintained entry must point to its own directory')
            if mode == 'manual-product' and not item['review_docs']:
                raise ValueError(f'{name}: manual product skill needs docs for paired review')
        for url in item['review_docs']:
            if not url.startswith('https://') or any(c in url for c in '\n|[]() '):
                raise ValueError(f'{name}: invalid review docs URL')
        for related in item['overlaps']:
            if related == name or related not in skills:
                raise ValueError(f'{name}: unknown or self overlap {related}')
        if f'](./{name}/SKILL.md)' not in readme:
            raise ValueError(f'{name}: missing README discovery link')
    return skills, sources


def render(skills, sources):
    counts = {mode: sum(item['maintenance'] == mode for item in skills.values()) for mode in MODES}
    lines = [f"{len(skills)} skills: {counts['generated']} generated, "
             f"{counts['manual-product']} manual product, {counts['standalone']} standalone.", '',
             '| Skill | Maintenance | Edit location | Docs to review | Related skills |',
             '|---|---|---|---|---|']
    for name, item in sorted(skills.items()):
        docs = ', '.join(f'[docs {i + 1}]({url})' for i, url in enumerate(item['review_docs'])) or 'Source docs'
        related = ', '.join(f'[{s}]({s}/SKILL.md)' for s in item['overlaps']) or 'None recorded'
        lines.append(f'| [{name}]({name}/SKILL.md) | {MODES[item["maintenance"]]} | '
                     f'[edit]({item["edit"]}) | {docs} | {related} |')
    lines += ['', 'Recorded generated-source snapshots (not a freshness assertion):', '']
    for key, source in sorted(sources.items()):
        lines.append(f'- `{key}`: [{source["commit"][:12]}]({source["repository"]}/commit/{source["commit"]})')
    lines += ['', 'Upstream freshness: **not checked by this report**.']
    return '\n'.join(lines)


def update(root, check=False):
    skills, sources = load(root)
    path = root / 'MAINTENANCE.md'
    text = path.read_text()
    if text.count(START) != 1 or text.count(END) != 1 or text.index(START) >= text.index(END):
        raise ValueError('MAINTENANCE.md needs one ordered pair of catalog markers')
    before, rest = text.split(START)
    _, after = rest.split(END)
    expected = before + START + '\n' + render(skills, sources) + '\n' + END + after
    if check and text != expected:
        raise ValueError('Maintenance inventory is stale; run python3 scripts/catalog.py')
    if not check:
        path.write_text(expected)
    print(f'Catalog covers {len(skills)} skills. Ownership and inventory checked; upstream freshness not checked.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail on incomplete metadata or stale inventory')
    args = parser.parse_args()
    try:
        update(ROOT, args.check)
    except (ValueError, KeyError, TypeError, OSError) as error:
        raise SystemExit(str(error))
