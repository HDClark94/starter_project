"""Downstream analysis: Raphael's loaders and scores, this project's
behaviour and arena."""

import pandas as pd
from raphael import population
from raphael.ephys.layout import Session
from raphael.tuning_scores import (
    compute_hd_mean_vector_length,
    compute_spatial_information,
    compute_speed_correlation,
)

from starter_project.arena import bin_config
from starter_project.behaviour import load_behaviour


def score_session(root, session: Session, sorter='kilosort4', n_shuffles=100, alpha=0.05):
    """One row per accepted unit: spatial information, HD tuning and speed
    correlation, each with whether it beats its shuffled null."""
    # Raphael: spikes, whatever sorted them, in the shared processed tree.
    pop = population.load(session.folder(root) / f'{session.stem}_srt-{sorter}').accepted()
    # The project: behaviour and arena.
    beh = load_behaviour(root, session)
    bins = bin_config()

    rows = []
    for unit in pop.ids:
        spikes = pop.data[unit]
        si, = compute_spatial_information(beh, bins, spikes, unit, alpha, n_shuffles)
        hd, = compute_hd_mean_vector_length(beh, bins, spikes, unit, alpha, n_shuffles)
        sc, = compute_speed_correlation(beh, spikes, unit, alpha, n_shuffles)
        rows.append({'unit': unit,
                     'spatial_information': si['spatial_information'], 'si_sig': si['sig'],
                     'hd_mvl': hd['hd_mean_vector_length'], 'hd_sig': hd['sig'],
                     'speed_corr': sc['speed_correlation'], 'speed_sig': sc['sig']})
    return pd.DataFrame(rows)


def rate_maps(root, session: Session, sorter='kilosort4'):
    """{unit: 2D rate map (Hz)} of the accepted units, while moving, binned
    and smoothed as this project's arena says."""
    import numpy as np
    import pynapple as nap
    from raphael.util import gaussian_filter_nan

    pop = population.load(session.folder(root) / f'{session.stem}_srt-{sorter}').accepted()
    beh = load_behaviour(root, session)
    config = bin_config()[('P_x', 'P_y')]
    features = np.stack([beh['P_x'], beh['P_y']], axis=1)
    maps, _ = nap.compute_2d_tuning_curves(pop.data, features, nb_bins=config['num_bins'],
                                           minmax=config['bounds'], ep=beh['moving'])
    s = config['smooth_sigma']
    return {unit: gaussian_filter_nan(m, sigma=(s, s)) for unit, m in maps.items()}
