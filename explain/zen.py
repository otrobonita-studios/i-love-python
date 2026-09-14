"""The Zen of Python, decoded from CPython's own module.

Do not hand-author the English. `this.s` is rot13; we decode it.
"""

from __future__ import annotations

import codecs
import contextlib
import io

EXECUTE_LABEL = "Execute"
HIDE_LABEL = "Hide"


def after_press(showing: bool) -> tuple[bool, str]:
    """Execute reveals the Zen; Hide puts the card away and restores Execute."""
    now = not showing
    return now, HIDE_LABEL if now else EXECUTE_LABEL


def zen_of_python() -> str:
    """Return the Zen as plain English, from `this.s`."""
    # Importing `this` prints the Zen to stdout. The letter UI prints it
    # only after Execute, so swallow the import side-effect.
    with contextlib.redirect_stdout(io.StringIO()):
        import this as this_mod
    return codecs.decode(this_mod.s, "rot_13")
