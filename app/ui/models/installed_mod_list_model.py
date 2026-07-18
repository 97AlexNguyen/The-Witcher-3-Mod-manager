from __future__ import annotations

from enum import IntEnum

from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt

from app.domain import InstalledMod
from app.ui.theme.tokens import CATEGORY_COLORS, CATEGORY_KEY_COLORS


class InstalledModRoles(IntEnum):
    MOD = Qt.ItemDataRole.UserRole + 1
    ENABLED = Qt.ItemDataRole.UserRole + 2
    CATEGORY_COLOR = Qt.ItemDataRole.UserRole + 3
    DESCRIPTION = Qt.ItemDataRole.UserRole + 4
    THUMBNAIL_PATH = Qt.ItemDataRole.UserRole + 5


class InstalledModListModel(QAbstractListModel):
    def __init__(self, mods: list[InstalledMod], parent=None) -> None:
        super().__init__(parent)
        self._mods = mods

    def rowCount(self, parent=QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self._mods)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        mod = self._mods[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return mod.name
        if role == Qt.ItemDataRole.ToolTipRole:
            return f"{mod.name}\n\n{mod.description}"
        if role == InstalledModRoles.MOD:
            return mod
        if role == InstalledModRoles.ENABLED:
            return mod.enabled
        if role == InstalledModRoles.DESCRIPTION:
            return mod.description
        if role == InstalledModRoles.THUMBNAIL_PATH:
            return mod.thumbnail_path
        if role == InstalledModRoles.CATEGORY_COLOR:
            return CATEGORY_KEY_COLORS.get(mod.category_key, CATEGORY_COLORS["neutral"])
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable

    def setData(self, index: QModelIndex, value, role=Qt.ItemDataRole.EditRole) -> bool:  # noqa: N802
        if not index.isValid() or role != InstalledModRoles.ENABLED:
            return False
        self._mods[index.row()].enabled = bool(value)
        self.dataChanged.emit(index, index, [InstalledModRoles.ENABLED, InstalledModRoles.MOD])
        return True

    def add_mod(self, mod: InstalledMod) -> None:
        """Append a freshly installed mod, emitting the insert signals so the
        boxes and the debounced manifest save both react."""
        row = len(self._mods)
        self.beginInsertRows(QModelIndex(), row, row)
        self._mods.append(mod)
        self.endInsertRows()

    def has_identity(self, identity: str) -> bool:
        return any(mod.identity == identity for mod in self._mods)

    def mod_at(self, row: int) -> InstalledMod:
        return self._mods[row]

    def row_for(self, mod: InstalledMod) -> int:
        """Locate a mod by object identity.

        InstalledMod is a mutable dataclass with value equality, so list.index()
        would match the first field-identical mod rather than this exact one.
        """
        for row, candidate in enumerate(self._mods):
            if candidate is mod:
                return row
        return -1

    def set_category(self, mod: InstalledMod, category_key: str) -> bool:
        row = self.row_for(mod)
        if row < 0:
            return False
        mod.category_key = category_key
        index = self.index(row, 0)
        self.dataChanged.emit(index, index, [InstalledModRoles.MOD, InstalledModRoles.CATEGORY_COLOR])
        return True

    def set_priority(self, mod: InstalledMod, priority: int | None) -> bool:
        """Update the displayed priority.

        Priority belongs to game config (the game reads it at startup), not to the
        manifest, and the merge step is what writes it. Nothing in the UI edits it —
        this exists for whatever reads game config back in.
        """
        row = self.row_for(mod)
        if row < 0:
            return False
        mod.priority = priority
        index = self.index(row, 0)
        self.dataChanged.emit(index, index, [InstalledModRoles.MOD])
        return True

    @property
    def mods(self) -> tuple[InstalledMod, ...]:
        return tuple(self._mods)
