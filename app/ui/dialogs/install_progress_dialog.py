"""Threaded install with a live progress dialog.

Extraction and copying a large mod can take minutes; doing it on the UI thread
freezes the window. :class:`InstallWorker` runs the confirmed install on Qt's
thread pool and emits progress, and :class:`InstallProgressDialog` shows it as a
phase label plus a progress bar (determinate when the size is known, a busy
indicator when it isn't). The dialog runs its own modal event loop, so the page's
install loop can stay simple and synchronous while the UI stays responsive.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QObject, QRunnable, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from app.install import (
    InstallProgress,
    InstallResult,
    install_package,
    prepare_archive,
)
from app.ui.theme.tokens import SPACING_LG, SPACING_MD, SPACING_SM

_BAR_STEPS = 1000


class InstallSignals(QObject):
    progress = pyqtSignal(object)  # InstallProgress
    finished = pyqtSignal(object)  # InstallResult
    failed = pyqtSignal(object)  # Exception


class InstallWorker(QRunnable):
    """Runs the (already confirmed) extract + install off the UI thread."""

    def __init__(
        self,
        *,
        archive_path: str,
        game_path: str,
        vault_path: str | None,
        nexus_metadata: dict | None,
        name_override: str,
    ) -> None:
        super().__init__()
        self._archive_path = archive_path
        self._game_path = game_path
        self._vault_path = vault_path
        self._nexus_metadata = nexus_metadata
        self._name_override = name_override
        self.signals = InstallSignals()

    def run(self) -> None:  # noqa: D401 - QRunnable entry point
        emit = self.signals.progress.emit
        try:
            with prepare_archive(self._archive_path, progress=emit) as package:
                result = install_package(
                    package,
                    self._game_path,
                    self._vault_path,
                    nexus_metadata=self._nexus_metadata,
                    name_override=self._name_override,
                    progress=emit,
                )
        except Exception as exc:  # noqa: BLE001 - reported to the UI, not swallowed
            self.signals.failed.emit(exc)
            return
        self.signals.finished.emit(result)


class InstallProgressDialog(QDialog):
    """Modal progress readout shown while :class:`InstallWorker` runs.

    The page drives it: connect the worker signals, ``exec()`` to block on the
    modal loop, then call :meth:`finish` from the finished/failed handlers to end
    it. It cannot be dismissed by the user while the install is running."""

    def __init__(self, mod_name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._done = False
        self.setObjectName("installProgressDialog")
        self.setWindowTitle("Installing")
        self.setModal(True)
        self.setMinimumWidth(460)
        # No close button and no context-help — the install must not be abandoned
        # part-way, which would leave a half-copied mod in the game folder.
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self._build_ui(mod_name)

    def _build_ui(self, mod_name: str) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        layout.setSpacing(SPACING_SM)

        heading = QLabel("INSTALLING")
        heading.setProperty("class", "label-md")
        layout.addWidget(heading)

        name = QLabel(mod_name)
        name.setProperty("class", "headline-sm")
        name.setWordWrap(True)
        layout.addWidget(name)

        layout.addSpacing(SPACING_SM)
        self._phase_label = QLabel("Preparing…")
        layout.addWidget(self._phase_label)

        self._bar = QProgressBar()
        self._bar.setObjectName("installProgressBar")
        self._bar.setTextVisible(False)
        self._bar.setRange(0, 0)  # busy until the first determinate update
        layout.addWidget(self._bar)

        self._detail_label = QLabel("")
        self._detail_label.setProperty("class", "muted")
        self._detail_label.setWordWrap(False)
        layout.addWidget(self._detail_label)

    # -- worker signal slots ---------------------------------------------- #

    def update_progress(self, progress: InstallProgress) -> None:
        self._phase_label.setText(progress.phase.value + "…")
        if progress.indeterminate:
            self._bar.setRange(0, 0)
        else:
            self._bar.setRange(0, _BAR_STEPS)
            self._bar.setValue(int(progress.fraction * _BAR_STEPS))
        self._detail_label.setText(_elide(progress.detail))

    def finish(self, result: InstallResult | None, error: Exception | None) -> None:
        """End the modal loop once the worker reports done (success or failure)."""
        self._done = True
        if error is None:
            self.accept()
        else:
            self.reject()

    # -- keep the dialog up until the worker is done ---------------------- #

    def reject(self) -> None:  # noqa: D401 - Qt override
        # Ignore Esc / programmatic reject until the install actually finished.
        if self._done:
            super().reject()

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt override
        if self._done:
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt override
        if event.key() == Qt.Key.Key_Escape and not self._done:
            event.ignore()
            return
        super().keyPressEvent(event)


def _elide(text: str, limit: int = 56) -> str:
    if len(text) <= limit:
        return text
    return "…" + text[-(limit - 1):]
