"""Releases: one version everywhere, and Raphael pinned to a released tag
(a release of this project must name a Raphael version that exists)."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('release_tools',
                                              ROOT / '.github' / 'scripts' / 'release_tools.py')
rt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rt)


def test_versions_agree():
    found = rt.versions(ROOT)
    assert len(set(found.values())) == 1, found


def test_raphael_is_pinned_to_a_release():
    """Fails while Raphael is installed from a local checkout (uv add --editable):
    switch back to a release before committing."""
    assert rt.pinned_tag('raphael', ROOT).startswith('v')
