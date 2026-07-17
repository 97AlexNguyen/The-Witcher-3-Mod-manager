from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QAbstractItemView, QListView

from app.domain import InstalledMod
from app.ui.delegates import InstalledModCardDelegate
from app.ui.models import InstalledModRoles, ModListFilterProxy


class ModCardList(QListView):
    selection_changed = pyqtSignal(list)

    def __init__(self, proxy: ModListFilterProxy, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("modCardList")
        self.setModel(proxy)
        self.setItemDelegate(InstalledModCardDelegate(self))
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setUniformItemSizes(True)
        self.setMouseTracking(True)
        self.selectionModel().selectionChanged.connect(self._emit_selection)

    def _emit_selection(self, *_args) -> None:
        mods: list[InstalledMod] = []
        for index in self.selectionModel().selectedIndexes():
            mod = index.data(InstalledModRoles.MOD)
            if mod is not None:
                mods.append(mod)
        self.selection_changed.emit(mods)
