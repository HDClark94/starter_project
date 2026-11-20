"""Analyse a processed session: which units are tuned to position, head
direction and speed, and their rate maps.

    uv run python scripts/analyse_tuning.py                 # the demo session
    uv run python scripts/analyse_tuning.py /data/processed --mouse 25 --day 18 --session-type OF1

Writes figures/{session}_tuning.pdf and the scores as a CSV beside it.
"""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from raphael.ephys.layout import Session

from starter_project.analysis import rate_maps, score_session


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('root', type=Path, nargs='?', default=Path('data/processed'))
    p.add_argument('--mouse', default='1')
    p.add_argument('--day', default='1')
    p.add_argument('--session-type', default='OF1')
    p.add_argument('--n-shuffles', type=int, default=100)
    p.add_argument('--out', type=Path, default=Path('figures'))
    args = p.parse_args(argv)

    session = Session(args.mouse, args.day, args.session_type)
    table = score_session(args.root, session, n_shuffles=args.n_shuffles)
    maps = rate_maps(args.root, session)

    n = len(table)
    fig, axes = plt.subplots(1, n + 1, figsize=(2.2 * (n + 1), 2.4))
    fractions = table[['si_sig', 'hd_sig', 'speed_sig']].mean()
    axes[0].bar(['place', 'HD', 'speed'], fractions.values, color='0.3')
    axes[0].set(ylim=(0, 1), ylabel='fraction of units')
    for ax, row in zip(axes[1:], table.itertuples(), strict=True):
        ax.imshow(maps[row.unit].T, origin='lower', cmap='viridis')
        ax.set_title(f'unit {row.unit}\nSI {row.spatial_information:.2f}'
                     + (' *' if row.si_sig else ''), fontsize=8)
        ax.axis('off')
    fig.suptitle(session.stem, fontsize=8)
    fig.tight_layout()

    args.out.mkdir(parents=True, exist_ok=True)
    path = args.out / f'{session.stem}_tuning.pdf'
    fig.savefig(path)
    table.to_csv(path.with_suffix('.csv'), index=False)
    print(table.to_string(index=False))
    print(f'-> {path}')
    return path


if __name__ == '__main__':
    main()
