"""Release helper: one version number everywhere, and release notes from the changelog.

    python .github/scripts/release_tools.py prepare 0.3.0   # bump versions, date the changelog
    python .github/scripts/release_tools.py check v0.3.0    # everything agrees with the tag
    python .github/scripts/release_tools.py notes 0.3.0     # that version's changelog section

Works on a repository with pyproject.toml, CHANGELOG.md (Keep a Changelog
style: `## [Unreleased]`, `## [0.3.0] - 2026-11-21`) and CITATION.cff, and
optionally `__version__` in src/<package>/__init__.py. The same file is used
by Raphael and by projects built on it (starter_project), where
`check --require-pinned raphael` also insists that Raphael is pinned to a
released tag in uv.lock, so a published analysis never depends on an
unreleased Raphael.
"""

import argparse
import re
import subprocess
import sys
import tomllib
from datetime import date
from pathlib import Path

ROOT = Path.cwd()
VERSION = r'\d+\.\d+\.\d+'


class ReleaseError(RuntimeError):
    pass


def _init_files(root):
    return [p for p in sorted((root / 'src').glob('*/__init__.py'))
            if re.search(r"^__version__\s*=", p.read_text(), re.MULTILINE)]


def versions(root=ROOT):
    """{where: version} for every place the version is written."""
    root = Path(root)
    found = {'pyproject.toml': tomllib.loads((root / 'pyproject.toml').read_text())
             ['project']['version']}
    cff = root / 'CITATION.cff'
    if cff.exists():
        m = re.search(rf'^version:\s*["\']?({VERSION})', cff.read_text(), re.MULTILINE)
        found['CITATION.cff'] = m.group(1) if m else None
    for init in _init_files(root):
        m = re.search(rf"^__version__\s*=\s*['\"]({VERSION})['\"]", init.read_text(), re.MULTILINE)
        found[str(init.relative_to(root))] = m.group(1) if m else None
    return found


def changelog_sections(root=ROOT):
    """[(heading version or 'Unreleased', date or None, body)] in file order."""
    text = (Path(root) / 'CHANGELOG.md').read_text()
    heads = list(re.finditer(rf'^## \[(Unreleased|{VERSION})\](?: - (\d{{4}}-\d{{2}}-\d{{2}}))?\s*$',
                             text, re.MULTILINE))
    out = []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        body = text[m.end():end]
        body = re.split(r'^\[[^\]]+\]: ', body, maxsplit=1, flags=re.MULTILINE)[0]   # drop link refs
        out.append((m.group(1), m.group(2), body.strip()))
    return out


def notes(version, root=ROOT):
    for v, _, body in changelog_sections(root):
        if v == version:
            if not body:
                raise ReleaseError(f'CHANGELOG.md has no entries under [{version}]')
            return body
    raise ReleaseError(f'CHANGELOG.md has no section for [{version}]')


def pinned_tag(package, root=ROOT):
    """The git tag `package` is locked to in uv.lock, or raise."""
    lock = tomllib.loads((Path(root) / 'uv.lock').read_text())
    for pkg in lock.get('package', []):
        if pkg['name'] == package:
            source = pkg.get('source', {})
            git = source.get('git')
            if not git:
                raise ReleaseError(f'{package} is not installed from a git release in uv.lock '
                                   f'(source {source}); pin a tag: uv add "{package} @ git+...'
                                   f'" --tag vX.Y.Z')
            m = re.search(r'[?&]tag=([^&#]+)', git)
            if not m:
                raise ReleaseError(f'{package} is locked to a branch or commit, not a release '
                                   f'tag ({git}); pin a tag: uv add "... --tag vX.Y.Z"')
            return m.group(1)
    raise ReleaseError(f'{package} is not in uv.lock')


def check(tag, root=ROOT, require_pinned=()):
    """Raise unless the tag, every written version and the changelog agree."""
    m = re.fullmatch(rf'v({VERSION})', tag)
    if not m:
        raise ReleaseError(f'tag {tag!r} must look like v1.2.3')
    version = m.group(1)
    wrong = {where: v for where, v in versions(root).items() if v != version}
    if wrong:
        raise ReleaseError(f'tag {tag} but ' + ', '.join(f'{w} says {v}' for w, v in wrong.items())
                           + f'; run: release_tools.py prepare {version}')
    sections = {v: d for v, d, _ in changelog_sections(root)}
    if version not in sections:
        raise ReleaseError(f'CHANGELOG.md has no section [{version}]')
    if not sections[version]:
        raise ReleaseError(f'CHANGELOG.md section [{version}] has no date')
    cff = Path(root) / 'CITATION.cff'
    if cff.exists():
        m = re.search(r'^date-released:\s*["\']?(\d{4}-\d{2}-\d{2})', cff.read_text(), re.MULTILINE)
        if not m or m.group(1) != sections[version]:
            raise ReleaseError(f'CITATION.cff date-released ({m and m.group(1)}) differs from '
                               f'the changelog date ({sections[version]})')
    notes(version, root)
    pins = {p: pinned_tag(p, root) for p in require_pinned}
    return version, pins


def _replace(path, pattern, repl, what):
    text = path.read_text()
    new, n = re.subn(pattern, repl, text, count=1, flags=re.MULTILINE)
    if not n:
        raise ReleaseError(f'could not find {what} in {path.name}')
    path.write_text(new)


def prepare(version, root=ROOT, today=None, lock=True):
    """Write `version` everywhere and turn [Unreleased] into a dated section."""
    root = Path(root)
    if not re.fullmatch(VERSION, version):
        raise ReleaseError(f'version {version!r} must look like 1.2.3')
    current = versions(root)['pyproject.toml']
    if tuple(map(int, version.split('.'))) <= tuple(map(int, current.split('.'))):
        raise ReleaseError(f'{version} is not after the current version {current}')
    unreleased = next((b for v, _, b in changelog_sections(root) if v == 'Unreleased'), None)
    if not unreleased:
        raise ReleaseError('nothing under ## [Unreleased] in CHANGELOG.md: say what changed first')
    day = (today or date.today()).isoformat()

    _replace(root / 'pyproject.toml', rf'^version = "{VERSION}"', f'version = "{version}"',
             'version = "..."')
    for init in _init_files(root):
        _replace(init, rf"^__version__ = ['\"]{VERSION}['\"]", f"__version__ = '{version}'",
                 '__version__')
    cff = root / 'CITATION.cff'
    if cff.exists():
        _replace(cff, r'^version: .*$', f'version: {version}', 'version:')
        _replace(cff, r'^date-released: .*$', f'date-released: "{day}"', 'date-released:')
    log = root / 'CHANGELOG.md'
    _replace(log, r'^## \[Unreleased\]\s*$', f'## [Unreleased]\n\n## [{version}] - {day}',
             '## [Unreleased]')
    text = log.read_text()
    m = re.search(r'^\[Unreleased\]: (\S+)/compare/v(\S+)\.\.\.HEAD$', text, re.MULTILINE)
    if m:                                            # keep the comparison links current
        base, previous = m.group(1), m.group(2)
        text = text.replace(m.group(0), f'[Unreleased]: {base}/compare/v{version}...HEAD\n'
                                        f'[{version}]: {base}/compare/v{previous}...v{version}')
        log.write_text(text)
    if lock and (root / 'uv.lock').exists():
        subprocess.run(['uv', 'lock', '--quiet'], cwd=root, check=True)
    return version


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='command', required=True)
    s = sub.add_parser('prepare', help='bump the version everywhere and date the changelog')
    s.add_argument('version')
    s = sub.add_parser('check', help='the tag, versions and changelog agree')
    s.add_argument('tag')
    s.add_argument('--require-pinned', action='append', default=[], metavar='PACKAGE',
                   help='also require PACKAGE to be pinned to a git tag in uv.lock')
    s = sub.add_parser('notes', help="print a version's changelog section")
    s.add_argument('version')
    args = p.parse_args(argv)
    try:
        if args.command == 'prepare':
            v = prepare(args.version)
            print(f'Prepared {v}. Check the diff, then (main is protected, so by pull request):\n'
                  f'  git commit -am "Release {v}" && git push -u origin HEAD\n'
                  f'  gh pr create --fill                   # merge once CI passes, then:\n'
                  f'  git switch main && git pull\n'
                  f'  git tag -a v{v} -m "v{v}" && git push origin v{v}   # the release workflow does the rest')
        elif args.command == 'check':
            v, pins = check(args.tag, require_pinned=args.require_pinned)
            print(f'{args.tag}: versions, changelog and citation agree'
                  + ''.join(f'; {p} pinned to {t}' for p, t in pins.items()))
        else:
            print(notes(args.version))
    except ReleaseError as e:
        print(f'::error::{e}' if 'GITHUB_ACTIONS' in __import__('os').environ else f'error: {e}',
              file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
