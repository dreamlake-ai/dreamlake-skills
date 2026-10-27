#!/usr/bin/env python3
"""Build the release assets: dist/skills.tar.gz and dist/catalog.json.

The tarball's top-level entries are the skill directories (every top-level
directory with a skill.json except _template/), including their generated
reference/. Dotfiles, __pycache__ and *.pyc are left out. The archive is
deterministic: entries are sorted, ownership is cleared, every mtime is
SOURCE_DATE_EPOCH (default 2024-01-01T00:00:00Z) and the gzip header carries
no timestamp or file name. catalog.json is copied unchanged, so run
`scripts/catalog.py --version <tag>` first.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tarfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catalog  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = 'dist'
ARCHIVE_NAME = 'skills.tar.gz'
DEFAULT_EPOCH = 1704067200  # 2024-01-01T00:00:00Z


class PackageError(Exception):
    """The repository is not in a packageable state."""


def entries(root):
    """Yield (archive name, path, is_dir) in a fixed order: each skill, its directories, its files."""
    for skill_dir in catalog.skill_dirs(root):
        yield skill_dir.name, skill_dir, True
        seen = set()
        for file in catalog.iter_files(skill_dir, skip_reference=False):
            rel = file.relative_to(skill_dir)
            for depth in range(1, len(rel.parts)):
                sub = Path(*rel.parts[:depth])
                if sub not in seen:
                    seen.add(sub)
                    yield f'{skill_dir.name}/{sub.as_posix()}', skill_dir / sub, True
            yield f'{skill_dir.name}/{rel.as_posix()}', file, False


def tar_info(name, path, is_dir, epoch):
    info = tarfile.TarInfo(name)
    info.mtime = epoch
    info.uid = info.gid = 0
    info.uname = info.gname = ''
    if is_dir:
        info.type = tarfile.DIRTYPE
        info.mode = 0o755
    else:
        info.type = tarfile.REGTYPE
        info.size = path.stat().st_size
        info.mode = 0o755 if os.access(path, os.X_OK) else 0o644
    return info


def build(root, out_dir, epoch=DEFAULT_EPOCH):
    names = [d.name for d in catalog.skill_dirs(root)]
    if not names:
        raise PackageError('no skill directory with a skill.json to package')
    catalog_path = root / catalog.CATALOG_FILE
    if not catalog_path.is_file():
        raise PackageError(f'{catalog.CATALOG_FILE} is missing; run scripts/catalog.py --version <tag>')
    listed = json.loads(catalog_path.read_text(encoding='utf-8')).get('skills', {})
    if set(listed) != set(names):
        raise PackageError(f'{catalog.CATALOG_FILE} lists {sorted(listed)} but the skill directories are {names}; '
                           f'run scripts/catalog.py --version <tag>')
    out_dir.mkdir(parents=True, exist_ok=True)
    archive = out_dir / ARCHIVE_NAME
    with open(archive, 'wb') as raw, gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as gz, \
            tarfile.open(fileobj=gz, mode='w', format=tarfile.GNU_FORMAT) as tar:
        for name, path, is_dir in entries(root):
            info = tar_info(name, path, is_dir, epoch)
            if is_dir:
                tar.addfile(info)
            else:
                with open(path, 'rb') as handle:
                    tar.addfile(info, handle)
    shutil.copyfile(catalog_path, out_dir / catalog.CATALOG_FILE)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    return archive, out_dir / catalog.CATALOG_FILE, digest, names


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', type=Path, default=ROOT, help='repository root (default: this checkout)')
    parser.add_argument('--out', type=Path, help=f'output directory (default: <root>/{DIST_DIR})')
    args = parser.parse_args(argv)
    out_dir = args.out or args.root / DIST_DIR
    epoch = int(os.environ.get('SOURCE_DATE_EPOCH', DEFAULT_EPOCH))
    try:
        archive, catalog_copy, digest, names = build(args.root, out_dir, epoch)
    except (PackageError, catalog.CatalogError, OSError, ValueError) as error:
        print(f'error: {error}', file=sys.stderr)
        return 1
    print(f'{archive}: {len(names)} skill(s) ({", ".join(names)})')
    print(f'sha256 {digest}')
    print(f'{catalog_copy}: copied')
    return 0


if __name__ == '__main__':
    sys.exit(main())
