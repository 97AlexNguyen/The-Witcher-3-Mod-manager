from __future__ import annotations

from PyQt6.QtGui import QDragEnterEvent, QDragLeaveEvent, QDragMoveEvent, QDropEvent

from app.ui.widgets.mod_card import MIME_MOD_IDENTITY


class ModDropTargetMixin:
    """Accepts a dragged mod card and reports where it was dropped.

    Mixed into both the shelf tile and the open box so a mod can be dropped onto
    either to change its category. The concrete widget must:
      * define a ``mod_dropped`` pyqtSignal(str, str)  (mod identity, target key),
      * set ``self._target_category_key``,
      * implement ``_set_drop_active(bool)`` for hover feedback.
    """

    _target_category_key: str

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:  # noqa: N802
        if event.mimeData().hasFormat(MIME_MOD_IDENTITY):
            event.acceptProposedAction()
            self._set_drop_active(True)
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:  # noqa: N802
        if event.mimeData().hasFormat(MIME_MOD_IDENTITY):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event: QDragLeaveEvent) -> None:  # noqa: N802
        self._set_drop_active(False)

    def dropEvent(self, event: QDropEvent) -> None:  # noqa: N802
        self._set_drop_active(False)
        if not event.mimeData().hasFormat(MIME_MOD_IDENTITY):
            event.ignore()
            return
        identity = bytes(event.mimeData().data(MIME_MOD_IDENTITY)).decode("utf-8")
        event.acceptProposedAction()
        self.mod_dropped.emit(identity, self._target_category_key)

    def _set_drop_active(self, active: bool) -> None:  # pragma: no cover - overridden
        raise NotImplementedError
