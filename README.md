# starter_project

A starting point for a new analysis project. Fork it, rename it, and build
your project on top of [Raphael](https://github.com/HDClark94/Raphael), the
labs' shared core for neural data processing and analysis.

**New here? Follow [Getting started](https://github.com/HDClark94/Raphael/blob/main/docs/getting_started.md)**:
VS Code and Claude Code set-up, then forking and installing this repository,
step by step.

## What's inside

```
starter_project/
├── notebooks/
│   ├── 01_process_raw_data.ipynb        raw Neuropixels → LFP and sorted units (Raphael jobs)
│   └── 02_analyse_processed_data.ipynb  load units, rate maps, tuning scores
├── scripts/
│   ├── make_demo_data.py                demo raw and processed data, so everything runs now
│   ├── process_raw_ephys.py             the processing notebook as a script (lfp | kilosort4)
│   └── analyse_tuning.py                the analysis notebook as a figure script
├── src/starter_project/                 your project's code
│   ├── arena.py                         apparatus: arena size and bin_config()
│   ├── behaviour.py                     loads behaviour into pynapple objects
│   ├── analysis.py                      downstream analysis, calling Raphael
│   ├── stages.py                        a project job stage (tuning_scores)
│   └── demo.py                          the demo data
├── configs/                             your copies of Raphael's settings
├── tests/                               uv run pytest
└── CLAUDE.md                            tells Claude Code how this project is laid out
```

The rule: **neural processing and shared analysis come from Raphael;
this repo holds only what is specific to your project.** If you write
something other projects would use, suggest it for Raphael.

## Try it

```bash
uv sync
uv run python scripts/make_demo_data.py
uv run python scripts/analyse_tuning.py               # -> figures/
uv run python scripts/process_raw_ephys.py lfp --demo # -> jobs/
```

or open the notebooks in VS Code and run them top to bottom. Spike sorting
needs the `gpu` extra (`uv sync --extra gpu`); without an NVIDIA GPU it runs
on the CPU (about 2 minutes on the demo).

## Making it yours

1. Rename the package: `src/starter_project` → `src/my_project`, and the
   `name` and entry point in `pyproject.toml`.
2. Fill in the NWB metadata in `configs/ephys.yaml` and `configs/imaging.yaml`
   (lab, experimenters, procedures).
3. Replace `arena.py` and `behaviour.py` with your apparatus and behaviour.
4. Delete the demo data and the parts you do not need.

Moving to a newer Raphael:
`uv add "raphael @ git+https://github.com/HDClark94/Raphael" --tag vX.Y.Z`,
then commit `pyproject.toml` and `uv.lock`.
