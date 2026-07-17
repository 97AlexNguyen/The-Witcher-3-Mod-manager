from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QAbstractItemView, QListView

from app.domain import InstalledMod
from app.ui.delegates import InstalledModCardDelegate
from app.ui.models import InstalledModRoles, ModListFilterProxy


class ModCardList(QListView):
    selection_changed = pyqtSignal(list)
    focus_details_requested = pyqtSignal(object)
    remove_requested = pyqtSignal(object)

    def __init__(self, proxy: ModListFilterProxy, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("modCardList")
        self.setModel(proxy)
        self._delegate = InstalledModCardDelegate(self)
        self.setItemDelegate(self._delegate)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setUniformItemSizes(True)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._delegate.remove_requested.connect(self.remove_requested)
        self.selectionModel().selectionChanged.connect(self._emit_selection)

    def toggle_enabled(self, index) -> bool:
        if not index.isValid():
            return False
        return self.model().setData(
            index,
            not bool(index.data(InstalledModRoles.ENABLED)),
            InstalledModRoles.ENABLED,
        )

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        index = self.currentIndex()
        if index.isValid():
            mod = index.data(InstalledModRoles.MOD)
            if event.key() == Qt.Key.Key_Space:
                self.toggle_enabled(index)
                event.accept()
                return
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and mod is not None:
                self.focus_details_requested.emit(mod)
                event.accept()
                return
            if event.key() == Qt.Key.Key_Delete and mod is not None:
                self.remove_requested.emit(mod)
                event.accept()
                return
        super().keyPressEvent(event)

    def _emit_selection(self, *_args) -> None:
        mods: list[InstalledMod] = []
        for index in self.selectionModel().selectedIndexes():
            mod = index.data(InstalledModRoles.MOD)
            if mod is not None:
                mods.append(mod)
        self.selection_changed.emit(mods)
