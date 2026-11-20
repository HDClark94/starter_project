"""Load this project's behaviour into the session dict Raphael's tuning
scores read: pynapple objects keyed P_x, P_y, S (cm/s), H (rad), moving.

How behaviour is stored is the project's choice. Here it is one TsdFrame
per session, `{stem}_behaviour.npz`, next to Raphael's processed files.
"""

import pynapple as nap
from raphael.ephys.layout import Session

MOVING_CM_S = 5.0


def behaviour_path(root, session):
    return session.folder(root) / f'{session.stem}_behaviour.npz'


def load_behaviour(root, session: Session):
    beh = nap.load_file(str(behaviour_path(root, session)))
    out = {name: beh[name] for name in ('P_x', 'P_y', 'S', 'H')}
    out['moving'] = out['S'].threshold(MOVING_CM_S).time_support
    return out
