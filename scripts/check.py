#!/usr/bin/env python3
"""Validate the whole dreamlake-skills repository; exit 1 on any failure.

Per skill directory (every top-level directory except scripts/, docs/, evidence/,
dist/ and dot-prefixed ones; _template/ included):
  - skill.json exists and is valid against skill.schema.json; name equals the directory name
  - requires names existing skills, never itself, and the graph has no cycles
  - top-level entries are only skill.json, SKILL.md, actions/, tools/, assets/, reference/
    and agents/ (optional Codex UI metadata: openai.yaml or other *.yaml files, nothing else)
  - SKILL.md has frontmatter with the same name, at most 80 lines, and ends with '## Canonical source'
  - actions/ holds at least one .md page
  - no legacy references/ directory; reference/ holds only generated files
  - every relative link in SKILL.md, actions/*.md and assets/**/*.md is resolved from the
    file that holds it (standard Markdown) and lands on a file inside the skill
  - tools/test_*.py pass under pytest (a warning if pytest is not installed)
Repository-wide:
  - renamed.json maps retired names to existing skills
  - catalog.json equals what scripts/catalog.py generates (version ignored)
  - reference/ matches references.lock (scripts/sync_references.py --offline-verify)
  - unless --offline: every docs[] page is served as Markdown (HTTP 200 on <url>.md)
_template/ is excluded from catalog.json and from the live URL check.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catalog  # noqa: E402
import sync_references as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_FILE = 'skill.schema.json'
RENAMED_FILE = 'renamed.json'
TEMPLATE_DIR = '_template'
NON_SKILL_DIRS = {'scripts', 'docs', 'evidence', 'dist', 'node_modules', '__pycache__'}
LEGACY_DIRS = ('references',)
SKILL_FILES = {sync.SKILL_FILE, 'SKILL.md'}
SKILL_DIRS = {'actions', 'tools', 'assets', sync.REFERENCE_DIR, 'agents'}
AGENTS_DIR = 'agents'
AGENT_META_SUFFIXES = ('.yaml', '.yml')
MAX_SKILL_LINES = 80
CANONICAL_HEADING = '## Canonical source'
NAME_RE = re.compile(r'^[a-z][a-z0-9-]*$')
FRONTMATTER_RE = re.compile(r'\A---\n(.*?)\n---(?:\n|\Z)', re.S)
EXTERNAL_SCHEMES = ('http://', 'https://', 'mailto:')

TYPE_CHECKS = {
    'string': lambda v: isinstance(v, str),
    'integer': lambda v: isinstance(v, int) and not isinstance(v, bool),
    'number': lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    'boolean': lambda v: isinstance(v, bool),
    'null': lambda v: v is None,
    'array': lambda v: isinstance(v, list),
    'object': lambda v: isinstance(v, dict),
}


class Report:
    def __init__(self):
        self.failures = []
        self.warnings = []

    def fail(self, scope, message):
        self.failures.append(f'{scope}: {message}')

    def warn(self, scope, message):
        self.warnings.append(f'{scope}: {message}')


# --- A small JSON Schema evaluator for skill.schema.json -----------------------

def validate(instance, schema, path='$'):
    """Return the list of violations of the JSON Schema subset used by skill.schema.json."""
    errors = []
    types = schema.get('type')
    if types is not None:
        types = [types] if isinstance(types, str) else list(types)
        if not any(TYPE_CHECKS[t](instance) for t in types):
            return [f'{path}: expected {" or ".join(types)}']
    if 'const' in schema and instance != schema['const']:
        errors.append(f'{path}: must be {schema["const"]!r}')
    if 'enum' in schema and instance not in schema['enum']:
        errors.append(f'{path}: must be one of {schema["enum"]!r}')
    for keyword in ('oneOf', 'anyOf'):
        alternatives = schema.get(keyword)
        if alternatives is None:
            continue
        results = [validate(instance, alt, path) for alt in alternatives]
        matching = [r for r in results if not r]
        if (keyword == 'oneOf' and len(matching) != 1) or (keyword == 'anyOf' and not matching):
            # When exactly one alternative has the instance's type, its own errors are the useful message.
            typed = [r for alt, r in zip(alternatives, results)
                     if isinstance(alt.get('type'), str) and TYPE_CHECKS[alt['type']](instance)]
            if len(typed) == 1 and typed[0]:
                errors.extend(typed[0])
            else:
                errors.append(f'{path}: must match {"exactly" if keyword == "oneOf" else "at least"} one alternative')
    if isinstance(instance, str):
        if 'pattern' in schema and not re.search(schema['pattern'], instance):
            errors.append(f'{path}: {instance!r} does not match {schema["pattern"]}')
        if 'minLength' in schema and len(instance) < schema['minLength']:
            errors.append(f'{path}: must be at least {schema["minLength"]} character(s)')
        if 'maxLength' in schema and len(instance) > schema['maxLength']:
            errors.append(f'{path}: must be at most {schema["maxLength"]} characters')
    if isinstance(instance, list):
        if 'minItems' in schema and len(instance) < schema['minItems']:
            errors.append(f'{path}: needs at least {schema["minItems"]} item(s)')
        if 'maxItems' in schema and len(instance) > schema['maxItems']:
            errors.append(f'{path}: allows at most {schema["maxItems"]} item(s)')
        if 'items' in schema:
            for index, item in enumerate(instance):
                errors.extend(validate(item, schema['items'], f'{path}[{index}]'))
        if schema.get('uniqueItems'):
            seen = set()
            for item in instance:
                key = json.dumps(item, sort_keys=True)
                if key in seen:
                    errors.append(f'{path}: duplicate item {item!r}')
                seen.add(key)
    if isinstance(instance, dict):
        for key in schema.get('required', []):
            if key not in instance:
                errors.append(f'{path}: missing required key {key!r}')
        for key, sub in schema.get('properties', {}).items():
            if key in instance:
                errors.extend(validate(instance[key], sub, f'{path}.{key}'))
        if schema.get('additionalProperties') is False:
            for key in sorted(set(instance) - set(schema.get('properties', {}))):
                errors.append(f'{path}: unexpected key {key!r}')
    return errors


# --- Per-skill checks ---------------------------------------------------------

def skill_dirs(root):
    return sorted(d for d in root.iterdir()
                  if d.is_dir() and not d.name.startswith('.') and d.name not in NON_SKILL_DIRS)


def parse_frontmatter(block):
    """Flatten `key: value` lines (block scalars folded) into a dict of strings."""
    fields, key = {}, None
    for line in block.split('\n'):
        match = re.match(r'^([A-Za-z_][\w-]*):\s*(.*)$', line)
        if match and not line.startswith((' ', '\t')):
            key, value = match.group(1), match.group(2).strip()
            fields[key] = '' if value in ('', '>', '|', '>-', '|-') else value.strip('"\'')
        elif key and line.startswith((' ', '\t')):
            fields[key] = (fields[key] + ' ' + line.strip()).strip()
    return fields


def check_skill_md(skill_dir, meta, report):
    name = skill_dir.name
    path = skill_dir / 'SKILL.md'
    if not path.is_file():
        report.fail(name, 'missing SKILL.md')
        return
    text = path.read_text(encoding='utf-8')
    lines = text.split('\n')
    if lines and lines[-1] == '':
        lines.pop()
    if len(lines) > MAX_SKILL_LINES:
        report.fail(name, f'SKILL.md has {len(lines)} lines; the limit is {MAX_SKILL_LINES}. Move detail into actions/')
    frontmatter = FRONTMATTER_RE.match(text)
    if not frontmatter:
        report.fail(name, 'SKILL.md must start with YAML frontmatter carrying name and description')
    else:
        fields = parse_frontmatter(frontmatter.group(1))
        if meta is not None and fields.get('name') != meta.get('name'):
            report.fail(name, f'SKILL.md frontmatter name {fields.get("name")!r} differs from skill.json name {meta.get("name")!r}')
        if not fields.get('description'):
            report.fail(name, 'SKILL.md frontmatter needs a non-empty description')
    heading_lines = [index for index, line in enumerate(lines) if line.startswith('## ')]
    if not heading_lines or lines[heading_lines[-1]].rstrip() != CANONICAL_HEADING:
        report.fail(name, f"SKILL.md must end with a '{CANONICAL_HEADING}' section")
    elif not any(line.strip() for line in lines[heading_lines[-1] + 1:]):
        report.fail(name, f"the '{CANONICAL_HEADING}' section of SKILL.md is empty")


def check_layout(skill_dir, report):
    """Only the sanctioned entries at the top of a skill; agents/ holds Codex metadata (*.yaml) only."""
    name = skill_dir.name
    for entry in sorted(skill_dir.iterdir()):
        if entry.name.startswith('.') or entry.name == '__pycache__' or entry.name in LEGACY_DIRS:
            continue
        if entry.is_dir():
            if entry.name not in SKILL_DIRS:
                report.fail(name, f'{entry.name}/ is not part of a skill; allowed directories are '
                                  f'{", ".join(sorted(SKILL_DIRS))}')
        elif entry.name not in SKILL_FILES:
            report.fail(name, f'{entry.name} is not part of a skill; top-level files are '
                              f'{" and ".join(sorted(SKILL_FILES))}')
    agents = skill_dir / AGENTS_DIR
    if agents.is_dir():
        for entry in sorted(agents.iterdir()):
            if entry.name.startswith('.'):
                continue
            if entry.is_dir() or entry.suffix not in AGENT_META_SUFFIXES:
                report.fail(name, f'{AGENTS_DIR}/{entry.name}: {AGENTS_DIR}/ holds only Codex UI metadata '
                                  f'(openai.yaml); put other material in actions/, assets/ or tools/')


def check_actions(skill_dir, report):
    actions = skill_dir / 'actions'
    if not actions.is_dir() or not any(actions.glob('*.md')):
        report.fail(skill_dir.name, 'actions/ must hold at least one .md page')


def check_reference_dir(skill_dir, report):
    name = skill_dir.name
    ref_dir = skill_dir / sync.REFERENCE_DIR
    if not ref_dir.is_dir():
        return
    for path in sorted(ref_dir.iterdir()):
        rel = f'{sync.REFERENCE_DIR}/{path.name}'
        if path.is_dir():
            report.fail(name, f'{rel}/ is a directory; reference/ holds only generated .md files')
        elif path.suffix != '.md':
            report.fail(name, f'{rel} is not a generated .md page; hand-written material belongs in actions/, assets/ or tools/')
        elif not sync.HEADER_RE.match(path.read_text(encoding='utf-8', errors='replace').split('\n', 1)[0]):
            report.fail(name, f'{rel} lacks the generated header; reference/ is written only by scripts/sync_references.py')


def check_links(skill_dir, report):
    name = skill_dir.name
    pages = [skill_dir / 'SKILL.md', *sorted((skill_dir / 'actions').glob('*.md')),
             *sorted((skill_dir / 'assets').rglob('*.md'))]
    skill_root = skill_dir.resolve()
    for page in pages:
        if not page.is_file():
            continue
        rel_page = page.relative_to(skill_dir).as_posix()
        lines = page.read_text(encoding='utf-8').split('\n')
        for index, line, in_code in sync.outside_fences(lines):
            if in_code or '](' not in line:
                continue
            for match in sync.LINK_RE.finditer(line):
                dest = match.group(2)
                if dest.startswith('#') or dest.startswith(EXTERNAL_SCHEMES):
                    continue
                where = f'{rel_page}:{index + 1}'
                if dest.startswith('/'):
                    report.fail(name, f'{where}: link {dest} is root-absolute; use a full URL or a path relative to this file')
                    continue
                target = dest.split('#', 1)[0].split('?', 1)[0]
                if not target:
                    continue
                resolved = (page.parent / target).resolve()
                if not resolved.is_relative_to(skill_root):
                    report.fail(name, f'{where}: link {dest} leaves the skill; refer to other skills by name')
                elif not resolved.exists():
                    report.fail(name, f'{where}: link {dest} does not resolve to a file')


def check_tools(skill_dir, report, run_tests=True):
    name = skill_dir.name
    tools = skill_dir / 'tools'
    if not tools.is_dir() or not any(tools.glob('test_*.py')):
        return
    if not run_tests:
        report.warn(name, 'tools tests skipped (--skip-tool-tests)')
        return
    if importlib.util.find_spec('pytest') is None:
        report.warn(name, 'pytest is not installed; tools tests skipped')
        return
    proc = subprocess.run([sys.executable, '-m', 'pytest', '-q'], cwd=tools, capture_output=True, text=True)
    if proc.returncode != 0:
        tail = '\n'.join((proc.stdout + proc.stderr).strip().split('\n')[-15:])
        report.fail(name, f'tools tests failed (python -m pytest -q in {name}/tools):\n{tail}')


def check_skill(skill_dir, schema, report, run_tests=True):
    """Run the per-directory checks; return the parsed skill.json when it is valid."""
    name = skill_dir.name
    for legacy in LEGACY_DIRS:
        if (skill_dir / legacy).is_dir():
            report.fail(name, f'{legacy}/ is a legacy hand-written directory; move task pages to actions/ '
                              f'and let docs[] fetch product pages into reference/')
    meta_path = skill_dir / sync.SKILL_FILE
    if not meta_path.is_file():
        report.fail(name, f'missing {sync.SKILL_FILE}')
        return None
    try:
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
    except ValueError as error:
        report.fail(name, f'{sync.SKILL_FILE}: invalid JSON ({error})')
        meta = None
    if meta is not None:
        errors = validate(meta, schema, sync.SKILL_FILE)
        for error in errors:
            report.fail(name, error)
        if errors:
            meta = None
    if meta is not None and name != TEMPLATE_DIR and meta['name'] != name:
        report.fail(name, f'{sync.SKILL_FILE}: name {meta["name"]!r} must equal the directory name')
    check_layout(skill_dir, report)
    check_skill_md(skill_dir, meta, report)
    check_actions(skill_dir, report)
    check_reference_dir(skill_dir, report)
    check_links(skill_dir, report)
    check_tools(skill_dir, report, run_tests)
    return meta


# --- Repository-wide checks ---------------------------------------------------

def check_graph(metas, report):
    names = set(metas) - {TEMPLATE_DIR}
    for dirname, meta in sorted(metas.items()):
        for required in meta['requires']:
            if required == meta['name']:
                report.fail(dirname, f'{sync.SKILL_FILE}: requires itself')
            elif required not in names:
                report.fail(dirname, f'{sync.SKILL_FILE}: requires {required!r}, which is not a skill in this repository')
    graph = {n: [r for r in metas[n]['requires'] if r in names] for n in names}
    state = {}

    def visit(node, trail):
        state[node] = 'active'
        for nxt in graph[node]:
            if state.get(nxt) == 'active':
                cycle = trail[trail.index(nxt):] + [nxt]
                report.fail(node, 'requires cycle: ' + ' -> '.join(cycle))
            elif nxt not in state:
                visit(nxt, trail + [nxt])
        state[node] = 'done'

    for node in sorted(graph):
        if node not in state:
            visit(node, [node])


def check_renamed(root, names, report):
    path = root / RENAMED_FILE
    if not path.is_file():
        report.fail(RENAMED_FILE, 'missing; write {} when nothing was renamed')
        return
    try:
        renamed = json.loads(path.read_text(encoding='utf-8'))
    except ValueError as error:
        report.fail(RENAMED_FILE, f'invalid JSON ({error})')
        return
    if not isinstance(renamed, dict):
        report.fail(RENAMED_FILE, 'must be an object mapping old names to new names')
        return
    for old, new in renamed.items():
        if not isinstance(new, str) or not NAME_RE.match(old) or not NAME_RE.match(new):
            report.fail(RENAMED_FILE, f'{old!r} -> {new!r}: names must match {NAME_RE.pattern}')
            continue
        if old == new:
            report.fail(RENAMED_FILE, f'{old} maps to itself')
        if new not in names:
            report.fail(RENAMED_FILE, f'{old} -> {new}, but {new} is not a skill in this repository')
        if old in names:
            report.fail(RENAMED_FILE, f'{old} is listed as renamed but still exists as a skill directory')


def check_live_urls(metas, report, fetch):
    results = {}
    for dirname, meta in sorted(metas.items()):
        if dirname == TEMPLATE_DIR:
            continue
        for url in meta['docs']:
            if url not in results:
                try:
                    fetch(sync.fetch_url_for(url))
                    results[url] = None
                except sync.SyncError as error:
                    results[url] = str(error)
            if results[url]:
                report.fail(dirname, f'docs[] page is not served as Markdown: {results[url]}')


def check_repo(root, offline=False, fetch=sync.http_fetch, run_tool_tests=True):
    report = Report()
    schema_path = root / SCHEMA_FILE
    if not schema_path.is_file():
        report.fail(SCHEMA_FILE, 'missing')
        return report
    schema = json.loads(schema_path.read_text(encoding='utf-8'))
    dirs = skill_dirs(root)
    if not any(d.name == TEMPLATE_DIR for d in dirs):
        report.warn(TEMPLATE_DIR, 'missing; contributors copy it to start a skill')
    metas = {}
    for skill_dir in dirs:
        meta = check_skill(skill_dir, schema, report, run_tool_tests)
        if meta is not None:
            metas[skill_dir.name] = meta
    names = set(metas) - {TEMPLATE_DIR}
    check_graph(metas, report)
    check_renamed(root, names, report)
    try:
        for problem in catalog.check(root):
            report.fail(catalog.CATALOG_FILE, problem)
    except catalog.CatalogError as error:
        report.fail(catalog.CATALOG_FILE, str(error))
    try:
        for problem in sync.offline_verify(root):
            report.fail(sync.LOCK_FILE, problem)
    except sync.SyncError as error:
        report.fail(sync.LOCK_FILE, str(error))
    if not offline:
        check_live_urls(metas, report, fetch)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', type=Path, default=ROOT, help='repository root (default: this checkout)')
    parser.add_argument('--offline', action='store_true', help='skip the live docs[] URL check')
    parser.add_argument('--skip-tool-tests', action='store_true', help='do not run tools/test_*.py')
    args = parser.parse_args(argv)
    report = check_repo(args.root, offline=args.offline, run_tool_tests=not args.skip_tool_tests)
    for line in report.warnings:
        print(f'WARN {line}')
    for line in report.failures:
        print(f'FAIL {line}')
    dirs = skill_dirs(args.root)
    skills = len([d for d in dirs if d.name != TEMPLATE_DIR])
    scope = f'{skills} skill dir(s)' + (f' plus {TEMPLATE_DIR}/' if len(dirs) > skills else '')
    mode = 'offline' if args.offline else 'online'
    if report.failures:
        print(f'check ({mode}): {len(report.failures)} failure(s), {len(report.warnings)} warning(s) across {scope}')
        return 1
    print(f'check ({mode}): ok, {scope}, {len(report.warnings)} warning(s)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
