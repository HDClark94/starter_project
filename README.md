# starter_project

A starting point for a new analysis project. Click **Use this template**
(it can be private), rename it, and build
your project on top of [Raphael](https://github.com/CogEmLab/Raphael), the
labs' shared core for neural data processing and analysis.

**New here? Follow [Getting started](https://github.com/CogEmLab/Raphael/blob/main/docs/getting_started.md)**:
VS Code and Claude Code set-up, then creating your project from this
template and installing it,
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
├── CHANGELOG.md, CITATION.cff           releases and how to cite them
└── CLAUDE.md                            tells Claude Code how this project is laid out
```

Importing the package applies Raphael's figure style, so your figures
share the labs' look from the start; Raphael's standard plots
(`raphael.plots`) cover rate maps, tuning curves, peri-event plots and more.

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
5. Edit `CITATION.cff` and `LICENSE` (your name), and start `CHANGELOG.md` afresh.

## Releasing (for a paper, or any result you share)

Each release is a GitHub Release, and with Zenodo connected it gets a DOI
to cite. Keep a line per notable change under `## [Unreleased]` in
`CHANGELOG.md`, then:

```bash
git switch -c release-1.0.0
uv run python .github/scripts/release_tools.py prepare 1.0.0
git commit -am "Release 1.0.0" && git push -u origin release-1.0.0
gh pr create --fill              # merge once CI passes, then tag main:
git switch main && git pull && git tag -a v1.0.0 -m "v1.0.0" && git push origin v1.0.0
```

Protect your project's `main` too (GitHub → Settings → Branches: require a pull
request and the `test` check), so nothing reaches it without passing CI.
Branch protection is free on public repositories; private ones need a paid
plan or a GitHub organization.

The release workflow publishes only if CI passes and Raphael is pinned to a
released tag in `uv.lock`, so the release always names the Raphael version
it ran on. In a paper, cite both: this project's release DOI and Raphael's.
Edit `CITATION.cff` (title, authors) when you make this project yours.
Details, Zenodo set-up and an example code-availability statement:
[Raphael's docs/releases.md](https://github.com/CogEmLab/Raphael/blob/main/docs/releases.md).

Moving to a newer Raphael:
`uv add "raphael @ git+https://github.com/CogEmLab/Raphael" --tag vX.Y.Z`,
then commit `pyproject.toml` and `uv.lock`.
