"""Demo data, so every script and notebook runs without lab data.

- `make_raw_day`: a simulated Neuropixels 2.0 day (two short sessions) with
  known spikes, as raw spikeinterface folders: the input to processing.
- `make_processed_session`: one session as Raphael's processed tree holds
  it (`_clusters.npz`), plus this project's behaviour file: the input to
  analysis. Some units are place cells, some are untuned, and one failed
  curation.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pynapple as nap
from raphael.ephys import nwb as ephys_nwb
from raphael.ephys.layout import Session

from starter_project.arena import ARENA_CM
from starter_project.behaviour import behaviour_path

DEMO_SESSION = Session(mouse='1', day='1', session_type='OF1')
PLACE_FIELDS_CM = [(25, 75), (70, 70), (50, 30), (80, 20)]


def make_raw_day(root, durations=(30.0, 30.0), num_units=20, per_shank=16, seed=0):
    """`root`/session0, `root`/session1 (raw recordings) and `root`/truth.
    Small by default (64 channels, 1 min), so processing takes minutes on a
    laptop CPU."""
    from raphael.ephys import benchmark

    root = Path(root)
    if not (root / 'session0').exists():
        benchmark.simulate(root, durations=durations, num_units=num_units, seed=seed,
                           per_shank=per_shank)
    return [root / f'session{i}' for i in range(len(durations))]


def _random_walk(rng, t, rate):
    xy = np.cumsum(rng.normal(0, 1.5, (len(t), 2)), axis=0) + np.array(ARENA_CM) / 2
    for i, size in enumerate(ARENA_CM):    # reflect at the walls
        xy[:, i] = size - np.abs(size - np.abs(xy[:, i]) % (2 * size))
    step = np.diff(xy, axis=0)
    speed = np.r_[0, np.hypot(*step.T) * rate]
    heading = np.r_[0, np.arctan2(step[:, 1], step[:, 0])]
    return xy, speed, heading


def make_processed_session(root, session=DEMO_SESSION, duration=900.0, seed=0):
    """Write a processed session under `root` and return its folder."""
    rng = np.random.default_rng(seed)
    rate = 50.0
    t = np.arange(0, duration, 1 / rate)
    xy, speed, heading = _random_walk(rng, t, rate)

    folder = session.folder(root)
    folder.mkdir(parents=True, exist_ok=True)
    nap.TsdFrame(t=t, d=np.c_[xy, speed, heading],
                 columns=['P_x', 'P_y', 'S', 'H']).save(str(behaviour_path(root, session)))

    spikes = {}
    for unit, (x, y) in enumerate(PLACE_FIELDS_CM):
        near = np.exp(-((xy[:, 0] - x) ** 2 + (xy[:, 1] - y) ** 2) / (2 * 10.0 ** 2))
        spikes[unit] = t[rng.random(len(t)) < 0.4 * near]
    for unit in range(len(PLACE_FIELDS_CM), len(PLACE_FIELDS_CM) + 3):   # untuned
        spikes[unit] = np.sort(rng.uniform(0, duration, int(4 * duration)))
    units = pd.DataFrame({'unit': list(spikes),
                          'accepted': [True] * (len(spikes) - 1) + [False]})
    ephys_nwb.export_clusters(units, spikes, duration, session.clusters(root, 'kilosort4'))
    return folder
