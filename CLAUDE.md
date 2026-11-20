# starter_project

A project repository that uses **Raphael** (https://github.com/HDClark94/Raphael)
as its backend for neural data processing and shared analysis.

- Neural processing (spike sorting, LFP, imaging, NWB), loading spikes or
  dF/F (`raphael.population`), tuning scores and cluster jobs come from
  Raphael. Use those; do not reimplement them here. Raphael's source is
  installed in `.venv/lib/python3.11/site-packages/raphael/`, and its docs
  are in its repository.
- This repo holds only what is specific to the project: `arena.py`
  (apparatus, `bin_config`), `behaviour.py`, `analysis.py`, `stages.py`,
  scripts and notebooks.
- If something here would be useful to other projects, suggest moving it
  into Raphael (a pull request there) rather than copying it.
- Environment: `uv sync`; run things with `uv run ...`. Python 3.11 exactly.
- Processed files follow Raphael's tree:
  `{root}/M{mouse}/D{day}/{type}/sub-M{mouse}_ses-D{day}_typ-{type}_...`.
  Use `raphael.ephys.layout.Session` for paths, never build names by hand.
- Data never goes in git (`data/`, `jobs/`, `figures/` are ignored).
- Tests: `uv run pytest`.
