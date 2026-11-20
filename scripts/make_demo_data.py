"""Make demo data, so the other scripts and the notebooks run without lab data.

    uv run python scripts/make_demo_data.py            # both, under data/
    uv run python scripts/make_demo_data.py --processed-only

Writes:
    data/raw/demo/session0, session1     simulated Neuropixels recordings (raw)
    data/processed/M1/D1/OF1/            a processed session with behaviour
"""

import argparse
from pathlib import Path

from starter_project import demo


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--data', type=Path, default=Path('data'))
    p.add_argument('--processed-only', action='store_true')
    args = p.parse_args(argv)

    folder = demo.make_processed_session(args.data / 'processed')
    print(f'processed session -> {folder}')
    if not args.processed_only:
        for raw in demo.make_raw_day(args.data / 'raw' / 'demo'):
            print(f'raw recording     -> {raw}')


if __name__ == '__main__':
    main()
