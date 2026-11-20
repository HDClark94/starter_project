"""What is specific to this project's apparatus: the arena and its binning.

Raphael's tuning scores take a `bin_config`, so this is where a project says
how big its arena is and how finely to bin it.
"""

import numpy as np

ARENA_CM = (100.0, 100.0)


def bin_config():
    return {
        ('P_x', 'P_y'): {'dim': '2d', 'bounds': (0.0, ARENA_CM[0], 0.0, ARENA_CM[1]),
                         'num_bins': 40, 'smooth_sigma': 1.5},
        'H': {'dim': '1dc', 'bounds': (-np.pi, np.pi), 'num_bins': 20},
        'S': {'dim': '1d', 'bounds': (1.0, 50.0), 'num_bins': 12},
    }
