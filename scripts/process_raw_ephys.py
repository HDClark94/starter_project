"""Process raw Neuropixels recordings with Raphael: LFP, or spike sorting.

Each run is a Raphael job bundle (a folder under jobs/) that records its
inputs, settings and environment, so a result can always be traced back.

    # the demo day from make_demo_data.py: LFP runs on any laptop
    uv run python scripts/process_raw_ephys.py lfp --demo

    # spike sorting needs the gpu extra (uv sync --extra gpu); CPU works, slowly
    uv run python scripts/process_raw_ephys.py kilosort4 --demo

    # your own recordings: inputs are relative to --data-root, one per session
    uv run python scripts/process_raw_ephys.py kilosort4 --data-root /data \\
        --input raw/M25_D18_OF1 --input raw/M25_D18_OF2 \\
        --mouse 25 --day 18 --session-type OF1 --session-type OF2 \\
        --session-start 2026-11-03T14:05 --session-start 2026-11-03T14:50

    # for the cluster: make the bundle here, copy it there, sbatch it
    uv run python scripts/process_raw_ephys.py kilosort4 ... --make-only

The same jobs from the command line: `uv run raphael-jobs make ... / run ...`.
"""

import argparse
from datetime import datetime
from pathlib import Path

from raphael.cluster import jobs

CONFIG = Path('configs/ephys.yaml')


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('stage', choices=['lfp', 'kilosort4'])
    p.add_argument('--demo', action='store_true', help='the simulated day under data/raw/demo')
    p.add_argument('--data-root', type=Path, default=Path('data'))
    p.add_argument('--input', dest='inputs', action='append', default=[])
    p.add_argument('--mouse', default='1')
    p.add_argument('--day', default='1')
    p.add_argument('--session-type', dest='types', action='append', default=[])
    p.add_argument('--session-start', dest='starts', action='append', default=[])
    p.add_argument('--jobs', type=Path, default=Path('jobs'))
    p.add_argument('--make-only', action='store_true', help='make the bundle, do not run it')
    args = p.parse_args(argv)

    if args.demo:
        from starter_project.demo import make_raw_day
        make_raw_day(args.data_root / 'raw' / 'demo')
        args.inputs = ['raw/demo/session0', 'raw/demo/session1']
        args.types, args.starts = ['OF1', 'OF2'], ['2026-01-01T10:00', '2026-01-01T10:30']
    if not args.inputs or len(args.types) != len(args.inputs) or len(args.starts) != len(args.inputs):
        p.error('give --input, --session-type and --session-start once per session (or --demo)')

    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    job_dir = args.jobs / f'{args.stage}-M{args.mouse}-D{args.day}-{stamp}'
    params = {'mouse': args.mouse, 'day': args.day,
              'session_type': args.types, 'session_start': args.starts}
    if args.demo:
        # The simulated probe has independent noise per channel, which the
        # bad-channel detector (built for real probes) mistakes for bad channels.
        params['preprocessing'] = {'remove_bad_channels': False}
    job = jobs.make(job_dir, args.stage, args.inputs, args.data_root, params=params,
                    resources={'gpu': args.stage == 'kilosort4', 'gpu_backend': 'cuda'},
                    configs=[CONFIG], hash_inputs=not args.demo)
    print(f'job bundle -> {job}')
    if args.make_only:
        print('copy it to the cluster and run: sbatch JOB/submit.slurm (docs/msc_cluster.md)')
        return job

    if args.stage == 'kilosort4':
        # No NVIDIA GPU here (e.g. a Mac: Kilosort 4.0.16 cannot use Apple
        # GPUs)? It also runs on the CPU, just slowly.
        from raphael.cluster import gpu
        try:
            gpu.check('cuda')
        except gpu.GpuUnavailable:
            spec = jobs.load(job)
            spec['resources']['gpu'] = False
            (job / 'job.yaml').write_text(jobs.yaml.safe_dump(spec, sort_keys=False))
            print('no GPU here: sorting on the CPU (slow)')
    jobs.run(job, args.data_root)
    print(f'done: processed files under {job / "outputs"}')
    for f in sorted((job / 'outputs').rglob('sub-*')):
        print('   ', f.relative_to(job / 'outputs'))
    return job


if __name__ == '__main__':
    main()
