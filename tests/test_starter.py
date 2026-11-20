"""The starter project works against the pinned Raphael: analysis, its own
job stage, the scripts and the notebooks (on demo data)."""

import os
from pathlib import Path

import nbformat
import pandas as pd
import pytest
from nbclient import NotebookClient
from raphael.cluster import jobs

from starter_project import demo
from starter_project.analysis import rate_maps, score_session

ROOT = Path(__file__).resolve().parents[1]
SESSION = demo.DEMO_SESSION


@pytest.fixture(scope='module')
def processed(tmp_path_factory):
    root = tmp_path_factory.mktemp('processed')
    demo.make_processed_session(root, duration=600.0)
    return root


def test_place_cells_are_found(processed):
    table = score_session(processed, SESSION, n_shuffles=20).set_index('unit')
    assert len(table) == 6                                # the rejected unit is left out
    assert table.loc[[0, 1, 2, 3], 'si_sig'].all()
    assert not table.loc[[4, 5], 'si_sig'].any()
    assert set(rate_maps(processed, SESSION)) == set(table.index)


def test_project_stage_is_registered_and_runs(processed, tmp_path):
    assert 'starter_project' in jobs.load_project_stages()    # the installed entry point
    rel = SESSION.folder(processed).relative_to(processed.parent)
    job = jobs.make(tmp_path / 'scores', 'tuning_scores', [str(rel)], processed.parent,
                    resources={'gpu': False}, hash_inputs=False,
                    params={'mouse': 1, 'day': 1, 'session_type': 'OF1', 'n_shuffles': 10})
    jobs.run(job, processed.parent)
    out = pd.read_csv(job / 'outputs' / f'{SESSION.stem}_tuning_scores.csv')
    assert len(out) == 6


@pytest.mark.parametrize('name', ['01_process_raw_data.ipynb', '02_analyse_processed_data.ipynb'])
def test_notebook_runs(name, tmp_path, monkeypatch):
    """Each notebook, top to bottom, in a scratch copy of the repo layout
    (spike sorting stays off, as it is by default)."""
    for sub in ('pyproject.toml', 'configs'):
        os.symlink(ROOT / sub, tmp_path / sub)
    (tmp_path / 'notebooks').mkdir()
    nb = nbformat.read(ROOT / 'notebooks' / name, as_version=4)
    NotebookClient(nb, timeout=600, kernel_name='python3',
                   resources={'metadata': {'path': str(tmp_path / 'notebooks')}}).execute()
