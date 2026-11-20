"""This project's job stages. Named under `raphael.stages` in
pyproject.toml, so `raphael-jobs make --stage tuning_scores` finds it and
the job runs, is checked and records provenance like Raphael's own stages.

    uv run raphael-jobs make ~/jobs/scores-M25-D18 --stage tuning_scores --cpu \\
        --data-root DATA --input processed/M25/D18/OF1 \\
        --param mouse=25 --param day=18 --param session_type=OF1
"""

from raphael.cluster.jobs import JobError, stage
from raphael.ephys.layout import Session

from starter_project.analysis import score_session


def _check(params, inputs):
    for key in ('mouse', 'day', 'session_type'):
        if key not in params:
            raise JobError(f'tuning_scores needs --param {key}=...')
    if len(inputs) != 1:
        raise JobError('tuning_scores takes one input: the session folder')


@stage('tuning_scores', check=_check)
def tuning_scores_stage(ctx):
    p = ctx.params
    session = Session(str(p['mouse']), str(p['day']), str(p['session_type']))
    # The input is the session's folder; the processed root is three up
    # ({root}/M{mouse}/D{day}/{type}).
    root = ctx.inputs[0].parents[2]
    table = score_session(root, session, n_shuffles=int(p.get('n_shuffles', 100)))
    table.to_csv(ctx.outputs / f'{session.stem}_tuning_scores.csv', index=False)
