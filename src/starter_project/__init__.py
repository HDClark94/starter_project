"""starter_project: a template for a project that uses Raphael as its backend.

Raphael does the neural processing and the shared analysis; this package
holds what is specific to the project: the arena (`arena`), how behaviour
is loaded (`behaviour`), the downstream analysis (`analysis`), any project
job stages (`stages`) and demo data to try everything on (`demo`).

Importing the package applies the labs' figure style (`raphael.style`), so
every figure in the project looks the same. Change a setting afterwards
with `style.use({'font.size': 8})` or `plt.rcParams`; see Raphael's
docs/style.md.
"""

from raphael import style

style.use()
