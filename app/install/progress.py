"""Progress reporting for a running install.

Installing a heavy mod (extraction + copying tens of GB) takes real time, so the
install pipeline can emit :class:`InstallProgress` updates that the UI turns into
a progress bar. The install layer stays Qt-free: it just calls a plain callback,
and the UI adapts those callbacks into signals on its own thread.

``total_bytes == 0`` means the size is unknown for this phase (e.g. a .rar being
unpacked by an external tool that gives no per-file feedback) — the bar should
show an indeterminate/busy state rather than a stuck 0%.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum


class InstallPhase(Enum):
    EXTRACT = "Extracting archive"
    DEPLOY = "Copying into the game"
    VAULT = "Vaulting source archive"


@dataclass(frozen=True, slots=True)
class InstallProgress:
    phase: InstallPhase
    done_bytes: int
    total_bytes: int
    detail: str = ""  # the file or bundle currently being handled

    @property
    def indeterminate(self) -> bool:
        return self.total_bytes <= 0

    @property
    def fraction(self) -> float:
        if self.total_bytes <= 0:
            return 0.0
        return min(1.0, self.done_bytes / self.total_bytes)


# A sink the install pipeline pushes updates into. Runs on the worker thread, so
# implementations must be thread-safe with respect to whatever they touch (the Qt
# adapter only emits a queued signal, which is safe).
ProgressCallback = Callable[[InstallProgress], None]
