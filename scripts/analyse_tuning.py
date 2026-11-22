"""Analyse a processed session: which units are tuned to position, head
direction and speed, and their rate maps.

    uv run python scripts/analyse_tuning.py                 # the demo session
    uv run python scripts/analyse_tuning.py /data/processed --mouse 25 --day 18 --session-type OF1

Writes figures/{session}_tuning.pdf and .png, and the scores as a CSV beside them.
"""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from raphael import plots, population, style
from raphael.ephys.layout import Session

from starter_project.analysis import score_session  # importing applies the style
from starter_project.arena import ARENA_CM, bin_config
from starter_project.behaviour import load_behaviour


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('root', type=Path, nargs='?', default=Path('data/processed'))
    p.add_argument('--mouse', default='1')
    p.add_argument('--day', default='1')
    p.add_argument('--session-type', default='OF1')
    p.add_argument('--sorter', default='kilosort4')
    p.add_argument('--n-shuffles', type=int, default=100)
    p.add_argument('--out', type=Path, default=Path('figures'))
    args = p.parse_args(argv)

    session = Session(args.mouse, args.day, args.session_type)
    table = score_session(args.root, session, sorter=args.sorter, n_shuffles=args.n_shuffles)
    pop = population.load(session.folder(args.root)
                          / f'{session.stem}_srt-{args.sorter}').accepted()
    beh = load_behaviour(args.root, session)
    config = bin_config()[('P_x', 'P_y')]

    n = len(table)
    fig, axes = plt.subplots(1, n + 1, figsize=style.figsize('double', height_mm=40),
                             gridspec_kw={'width_ratios': [1.3] + [1] * n})
    fractions = table[['si_sig', 'hd_sig', 'speed_sig']].mean()
    axes[0].bar(['place', 'HD', 'speed'], fractions.values, color=style.GREYS['dark'])
    axes[0].set(ylim=(0, 1), ylabel='Fraction of units')
    style.panel_label(axes[0], 'a')
    for ax, row in zip(axes[1:], table.itertuples(), strict=True):
        plots.rate_map(ax, pop.data[row.unit], beh, bounds=(0, ARENA_CM[0], 0, ARENA_CM[1]),
                       bins=config['num_bins'], smooth=config['smooth_sigma'])
        ax.set_title(f'Unit {row.unit}\nSI {row.spatial_information:.2f}'
                     + (' *' if row.si_sig else ''))
    style.panel_label(axes[1], 'b', x=-0.1)
    fig.suptitle(session.stem)

    path = args.out / f'{session.stem}_tuning'
    written = style.save(fig, path, close=True)
    table.to_csv(path.with_suffix('.csv'), index=False)
    print(table.to_string(index=False))
    print('->', ', '.join(map(str, written)))
    return written[0]


if __name__ == '__main__':
    main()
