#!/usr/bin/env python3
"""Fetch each skill's docs pages into <skill>/reference/ and record them in references.lock.

For every top-level directory that has a skill.json, each URL in its docs[] is
fetched as Markdown (<url>.md, or index.md for a site root) and written to
reference/<site>-<slug>.md with a provenance header. Links between pages of the
same skill become sibling file names; every other same-site link becomes an
absolute page URL. references.lock records, per skill and page, the source URL,
the docs-site version, the sha256 of the fetched bytes and of the written file.

Modes:
  (default)          fetch, write reference/ files, remove orphans, update references.lock
  --check            fetch and compare with the files on disk; print differences; write nothing
  --offline-verify   no network; verify reference/ matches references.lock exactly
  --skill NAME       limit any mode to one skill

Standard library only. Requests are sequential, identified by a User-Agent,
time out, and are retried once on a 5xx or network error.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SITES = {'docs.dreamlake.ai': 'docs', 'cli.dreamlake.ai': 'cli', 'viz.dreamlake.ai': 'viz'}
LOCK_FILE = 'references.lock'
LOCK_SCHEMA = 1
REFERENCE_DIR = 'reference'
SKILL_FILE = 'skill.json'
USER_AGENT = 'dreamlake-skills-sync/1 (+https://github.com/dreamlake-ai/dreamlake-skills)'
TIMEOUT_SECONDS = 30
RETRY_DELAY_SECONDS = 2
UNKNOWN_VERSION = 'unknown'

HEADER_RE = re.compile(r'^<!-- generated from (\S+) at (.*?); do not edit -->$')
SOURCE_RE = re.compile(r'^<!--\s*source:\s*(\S+)(?:\s*@\s*(.*?))?\s*-->\s*$')
PAGE_URL_RE = re.compile(r'^https://([a-z0-9.-]+)(/[^?#]*)?$')
# Inline link or image destination: ](dest) or ](dest "title"). Destinations with
# spaces or parentheses are left alone.
LINK_RE = re.compile(r'(\]\()([^()\s]+)((?:\s+"[^"]*")?\))')
# Any indentation counts: docs pages nest fences inside list items.
FENCE_RE = re.compile(r'^\s*(`{3,}|~{3,})')


class SyncError(Exception):
    """Configuration or consistency problem that stops the run."""


class FetchError(SyncError):
    """A page could not be fetched as Markdown."""


# --- URL and file naming ------------------------------------------------------

def parse_page_url(url):
    """Return (host, site, route) for a docs[] entry, or raise SyncError."""
    match = PAGE_URL_RE.match(url)
    if not match:
        raise SyncError(f'{url}: not an https page URL without query or fragment')
    host, path = match.group(1), match.group(2) or '/'
    if host not in SITES:
        raise SyncError(f'{url}: host {host!r} is not one of {", ".join(sorted(SITES))}')
    if path.endswith('.md'):
        raise SyncError(f'{url}: list the page URL, not its .md endpoint')
    if path != '/' and path.endswith('/'):
        raise SyncError(f'{url}: no trailing slash except on the site root')
    return host, SITES[host], path


def fetch_url_for(url):
    """The Markdown endpoint for a page URL: <url>.md, or index.md for a site root."""
    _host, _site, route = parse_page_url(url)
    return url + 'index.md' if route == '/' else url + '.md'


def reference_name(site, route):
    """reference/ file name: <site>-<slug>.md; the site root is <site>-index.md."""
    slug = route.strip('/').replace('/', '-') or 'index'
    return f'{site}-{slug}.md'


def normalise_route(path):
    """Collapse /path.md, /path/ and /path (with or without /index) to a route."""
    route = path
    if route.endswith('.md'):
        route = route[:-3]
    route = route.rstrip('/') or '/'
    if route == '/index':
        route = '/'
    if not route.startswith('/'):
        route = '/' + route
    return route


# --- Link rewriting -----------------------------------------------------------

def rewrite_destination(dest, host, siblings):
    """Rewrite one link destination found on a page served by `host`.

    siblings maps a route to the reference file name of another page of the same
    skill on the same site. Anchors are kept. Pure-anchor links and links to
    other hosts are returned unchanged.
    """
    if dest.startswith('#'):
        return dest
    prefix = f'https://{host}'
    if dest == prefix or dest.startswith(prefix + '/'):
        path = dest[len(prefix):] or '/'
    elif dest.startswith('/') and not dest.startswith('//'):
        path = dest
    else:
        return dest
    anchor = ''
    if '#' in path:
        path, fragment = path.split('#', 1)
        anchor = '#' + fragment
    route = normalise_route(path)
    if route in siblings:
        return siblings[route] + anchor
    return prefix + route + anchor


def outside_fences(lines):
    """Yield (index, line, in_code) for each line, tracking fenced code blocks."""
    fence = None
    for index, line in enumerate(lines):
        match = FENCE_RE.match(line)
        if fence is None:
            if match:
                fence = match.group(1)
                yield index, line, True
                continue
            yield index, line, False
        else:
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence) \
                    and line.strip() == match.group(1):
                fence = None
            yield index, line, True


def rewrite_links(text, host, siblings):
    lines = text.split('\n')
    for index, line, in_code in outside_fences(lines):
        if in_code or '](' not in line:
            continue
        lines[index] = LINK_RE.sub(
            lambda m: m.group(1) + rewrite_destination(m.group(2), host, siblings) + m.group(3), line)
    return '\n'.join(lines)


# --- Rendering ----------------------------------------------------------------

def split_source_line(text):
    """Return (version, body). The version comes from a leading <!-- source: ... --> line."""
    first, sep, rest = text.partition('\n')
    match = SOURCE_RE.match(first)
    if not match:
        return UNKNOWN_VERSION, text
    version = (match.group(2) or '').strip() or UNKNOWN_VERSION
    return version, rest if sep else ''


def render(url, raw, siblings):
    """Turn fetched bytes into the reference file text. Returns (text, version)."""
    host, _site, _route = parse_page_url(url)
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError as error:
        raise FetchError(f'{url}: response is not UTF-8 text ({error})') from None
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    version, body = split_source_line(text)
    body = rewrite_links(body, host, siblings).strip('\n')
    header = f'<!-- generated from {fetch_url_for(url)} at {version}; do not edit -->'
    return header + '\n\n' + body + '\n' if body else header + '\n', version


def sha256(data):
    return hashlib.sha256(data).hexdigest()


@dataclass
class Page:
    url: str
    file: str
    version: str
    source_sha256: str
    sha256: str
    text: str

    def lock_entry(self):
        return {'url': self.url, 'file': self.file, 'version': self.version,
                'source_sha256': self.source_sha256, 'sha256': self.sha256}


# --- Repository access --------------------------------------------------------

def skill_dirs(root):
    """Top-level directories with a skill.json, sorted; dot-prefixed names are skipped."""
    return sorted(d for d in root.iterdir()
                  if d.is_dir() and not d.name.startswith('.') and (d / SKILL_FILE).is_file())


def select_skills(root, skill=None):
    dirs = skill_dirs(root)
    if skill is None:
        return dirs
    chosen = [d for d in dirs if d.name == skill]
    if not chosen:
        raise SyncError(f'no skill directory named {skill!r} with a {SKILL_FILE}')
    return chosen


def load_docs(skill_dir):
    """The docs[] list of a skill, validated for host, shape and name collisions."""
    try:
        meta = json.loads((skill_dir / SKILL_FILE).read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        raise SyncError(f'{skill_dir.name}/{SKILL_FILE}: {error}') from None
    docs = meta.get('docs') if isinstance(meta, dict) else None
    if not isinstance(docs, list) or not all(isinstance(u, str) for u in docs):
        raise SyncError(f'{skill_dir.name}/{SKILL_FILE}: "docs" must be a list of URLs')
    files = {}
    for url in docs:
        try:
            _host, site, route = parse_page_url(url)
        except SyncError as error:
            raise SyncError(f'{skill_dir.name}/{SKILL_FILE}: {error}') from None
        name = reference_name(site, route)
        if name in files:
            raise SyncError(f'{skill_dir.name}/{SKILL_FILE}: {url} and {files[name]} both map to {name}')
        files[name] = url
    if len(set(docs)) != len(docs):
        raise SyncError(f'{skill_dir.name}/{SKILL_FILE}: duplicate docs[] entries')
    return docs


def load_lock(root):
    path = root / LOCK_FILE
    if not path.is_file():
        return {'schema': LOCK_SCHEMA, 'skills': {}}
    try:
        lock = json.loads(path.read_text(encoding='utf-8'))
    except ValueError as error:
        raise SyncError(f'{LOCK_FILE}: {error}') from None
    if not isinstance(lock, dict) or lock.get('schema') != LOCK_SCHEMA or not isinstance(lock.get('skills'), dict):
        raise SyncError(f'{LOCK_FILE}: expected {{"schema": {LOCK_SCHEMA}, "skills": {{...}}}}')
    return lock


def dump_lock(lock):
    ordered = {'schema': LOCK_SCHEMA, 'skills': {name: lock['skills'][name] for name in sorted(lock['skills'])}}
    return json.dumps(ordered, indent=2, ensure_ascii=False) + '\n'


def reference_files(skill_dir):
    ref_dir = skill_dir / REFERENCE_DIR
    if not ref_dir.is_dir():
        return {}
    return {p.name: p for p in sorted(ref_dir.iterdir()) if p.is_file()}


# --- Fetching -----------------------------------------------------------------

def http_fetch(url, timeout=TIMEOUT_SECONDS, sleep=time.sleep, opener=urllib.request.urlopen):
    """GET a Markdown endpoint; retry once on 5xx or a network error."""
    request = urllib.request.Request(url, headers={
        'User-Agent': USER_AGENT,
        'Accept': 'text/markdown, text/plain;q=0.9, */*;q=0.1',
    })
    last = None
    for attempt in range(2):
        try:
            with opener(request, timeout=timeout) as response:
                content_type = response.headers.get('Content-Type', '')
                data = response.read()
            if content_type.split(';')[0].strip().lower() == 'text/html':
                raise FetchError(f'{url}: served text/html, not Markdown')
            return data
        except urllib.error.HTTPError as error:
            if error.code >= 500 and attempt == 0:
                last = f'HTTP {error.code}'
                sleep(RETRY_DELAY_SECONDS)
                continue
            raise FetchError(f'{url}: HTTP {error.code}') from None
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            if attempt == 0:
                last = str(error)
                sleep(RETRY_DELAY_SECONDS)
                continue
            raise FetchError(f'{url}: {error}') from None
    raise FetchError(f'{url}: {last}')


def plan_skill(skill_dir, fetch):
    """Fetch every page of one skill and return the list of rendered Pages."""
    docs = load_docs(skill_dir)
    siblings = {}
    for url in docs:
        host, site, route = parse_page_url(url)
        siblings.setdefault(host, {})[route] = reference_name(site, route)
    pages, failures = [], []
    for url in docs:
        host, site, route = parse_page_url(url)
        try:
            raw = fetch(fetch_url_for(url))
            text, version = render(url, raw, siblings[host])
        except FetchError as error:
            failures.append(str(error))
            continue
        pages.append(Page(url=url, file=f'{REFERENCE_DIR}/{reference_name(site, route)}', version=version,
                          source_sha256=sha256(raw), sha256=sha256(text.encode('utf-8')), text=text))
    if failures:
        raise FetchError(f'{skill_dir.name}: ' + '; '.join(failures))
    return pages


# --- Modes --------------------------------------------------------------------

def sync(root, fetch=http_fetch, skill=None, check=False, out=print):
    """Fetch and write (or, with check=True, only compare). Returns the list of differences."""
    lock = load_lock(root)
    differences = []
    for skill_dir in select_skills(root, skill):
        name = skill_dir.name
        pages = plan_skill(skill_dir, fetch)
        existing = reference_files(skill_dir)
        produced = {page.file.split('/', 1)[1] for page in pages}
        for page in pages:
            path = skill_dir / page.file
            current = path.read_text(encoding='utf-8') if path.is_file() else None
            if current != page.text:
                verb = 'update' if current is not None else 'add'
                differences.append(f'{name}: {verb} {page.file} ({page.url} @ {page.version})')
        for orphan in sorted(set(existing) - produced):
            differences.append(f'{name}: remove {REFERENCE_DIR}/{orphan} (no docs[] entry produces it)')
        entries = [page.lock_entry() for page in pages]
        if lock['skills'].get(name) != entries:
            differences.append(f'{name}: {LOCK_FILE} entry differs')
        if check:
            continue
        ref_dir = skill_dir / REFERENCE_DIR
        if pages:
            ref_dir.mkdir(exist_ok=True)
        for page in pages:
            (skill_dir / page.file).write_text(page.text, encoding='utf-8')
        for orphan in sorted(set(existing) - produced):
            existing[orphan].unlink()
        if ref_dir.is_dir() and not any(ref_dir.iterdir()):
            ref_dir.rmdir()
        lock['skills'][name] = entries
    if not check:
        if skill is None:
            present = {d.name for d in skill_dirs(root)}
            for stale in [n for n in lock['skills'] if n not in present]:
                differences.append(f'{stale}: removed stale {LOCK_FILE} entry')
                del lock['skills'][stale]
        (root / LOCK_FILE).write_text(dump_lock(lock), encoding='utf-8')
    for line in differences:
        out(('would ' if check else '') + line)
    if not differences:
        out('reference/ is up to date')
    return differences


def offline_verify(root, skill=None):
    """Compare reference/ files against references.lock without network. Returns problems."""
    problems = []
    try:
        lock = load_lock(root)
    except SyncError as error:
        return [str(error)]
    if not (root / LOCK_FILE).is_file():
        problems.append(f'{LOCK_FILE} is missing; run scripts/sync_references.py')
    dirs = select_skills(root, skill)
    for skill_dir in dirs:
        name = skill_dir.name
        try:
            docs = load_docs(skill_dir)
        except SyncError as error:
            problems.append(str(error))
            continue
        entries = lock['skills'].get(name)
        if entries is None:
            problems.append(f'{name}: no {LOCK_FILE} entry; run scripts/sync_references.py --skill {name}')
            continue
        locked_urls = [e.get('url') for e in entries]
        if locked_urls != docs:
            problems.append(f'{name}: docs[] differs from {LOCK_FILE}; run scripts/sync_references.py --skill {name}')
        expected = {}
        for entry in entries:
            file = entry.get('file', '')
            if not file.startswith(REFERENCE_DIR + '/') or '/' in file[len(REFERENCE_DIR) + 1:]:
                problems.append(f'{name}: {LOCK_FILE} entry {entry.get("url")} has an invalid file {file!r}')
                continue
            try:
                _host, site, route = parse_page_url(entry['url'])
                if file != f'{REFERENCE_DIR}/{reference_name(site, route)}':
                    problems.append(f'{name}: {file} is not the file name derived from {entry["url"]}')
            except (SyncError, KeyError) as error:
                problems.append(f'{name}: {LOCK_FILE} entry invalid: {error}')
            expected[file.split('/', 1)[1]] = entry
        actual = reference_files(skill_dir)
        ref_dir = skill_dir / REFERENCE_DIR
        if ref_dir.is_dir():
            for extra_dir in sorted(p for p in ref_dir.iterdir() if p.is_dir()):
                problems.append(f'{name}: {REFERENCE_DIR}/{extra_dir.name}/ is a directory; reference/ holds files only')
        for missing in sorted(set(expected) - set(actual)):
            problems.append(f'{name}: {REFERENCE_DIR}/{missing} is missing')
        for extra in sorted(set(actual) - set(expected)):
            problems.append(f'{name}: {REFERENCE_DIR}/{extra} is not in {LOCK_FILE}')
        for file in sorted(set(expected) & set(actual)):
            data = actual[file].read_bytes()
            if sha256(data) != expected[file].get('sha256'):
                problems.append(f'{name}: {REFERENCE_DIR}/{file} was changed by hand; it is generated, so revert it '
                                f'or run scripts/sync_references.py')
            elif not HEADER_RE.match(data.decode('utf-8', 'replace').split('\n', 1)[0]):
                problems.append(f'{name}: {REFERENCE_DIR}/{file} lacks the generated header')
    if skill is None:
        present = {d.name for d in dirs}
        for stale in sorted(set(lock['skills']) - present):
            problems.append(f'{stale}: {LOCK_FILE} entry has no skill directory')
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', type=Path, default=ROOT, help='repository root (default: this checkout)')
    parser.add_argument('--skill', help='limit to one skill directory')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true', help='fetch and compare; write nothing; exit 1 on differences')
    mode.add_argument('--offline-verify', action='store_true',
                      help='no network; verify reference/ against references.lock; exit 1 on mismatch')
    args = parser.parse_args(argv)
    try:
        if args.offline_verify:
            problems = offline_verify(args.root, args.skill)
            for line in problems:
                print(line)
            if problems:
                print(f'{len(problems)} problem(s)')
                return 1
            print(f'{REFERENCE_DIR}/ matches {LOCK_FILE}')
            return 0
        differences = sync(args.root, skill=args.skill, check=args.check)
        if args.check and differences:
            print(f'{len(differences)} difference(s); run scripts/sync_references.py to apply')
            return 1
        return 0
    except SyncError as error:
        print(f'error: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
