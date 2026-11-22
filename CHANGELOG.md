# Changelog

Notable changes to this project. Each release is a GitHub Release (and,
with Zenodo connected, gets a DOI); see "Releasing" in the README.

## [Unreleased]

### Changed
- starter_project is a GitHub template: start a project with **Use this
  template** (which allows private repositories) instead of forking.

### Changed
- Raphael pinned to v0.3.0. Importing `starter_project` applies Raphael's
  figure style (`raphael.style.use()`), so every figure in a project built
  from this template shares the labs' look.
- `scripts/analyse_tuning.py` and the analysis notebook draw with
  `raphael.plots` (rate maps against the arena's size, raster, score
  against its shuffled null) and save with `style.save` (PDF and PNG).

## [0.1.0] - 2026-11-21

### Added
- Template for a project built on Raphael (pinned to v0.2.0): notebooks
  and scripts for processing raw data and analysing processed data on
  generated demo data, a small project package, VS Code settings and a
  CLAUDE.md.
- CI, and a release workflow that publishes a GitHub Release only if CI
  passes and Raphael is pinned to a released tag.

[Unreleased]: https://github.com/HDClark94/starter_project/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/HDClark94/starter_project/releases/tag/v0.1.0
