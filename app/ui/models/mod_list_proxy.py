from __future__ import annotations

from enum import Enum

from PyQt6.QtCore import QModelIndex, QSortFilterProxyModel, Qt

from app.ui.models.installed_mod_list_model import InstalledModListModel, InstalledModRoles


class SortMode(Enum):
    NAME = "name"
    PRIORITY = "priority"
    INSTALLED = "installed"


class ModListFilterProxy(QSortFilterProxyModel):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._category_key: str | None = None
        self._search_text = ""
        self._sort_mode = SortMode.INSTALLED
        self._pinned: set[str] = set()
        self.setDynamicSortFilter(True)

    @property
    def search_text(self) -> str:
        return self._search_text

    @property
    def pinned_identities(self) -> frozenset[str]:
        return frozenset(self._pinned)

    def set_category(self, category_key: str | None) -> None:
        self._category_key = None if category_key in (None, "all") else category_key
        self._pinned.clear()
        self.invalidateFilter()

    def set_search_text(self, text: str) -> None:
        self._search_text = text.strip().casefold()
        self._pinned.clear()
        self.invalidateFilter()

    def pin(self, mod) -> None:
        """Keep a mod visible even once an edit makes it stop matching the filter.

        Editing a mod out of the active filter would otherwise delete the row the
        user is working in, clearing their selection mid-interaction. The pin is
        dropped the next time the filter itself changes.
        """
        self._pinned.add(mod.identity)
        self.invalidateFilter()

    def clear_pins(self) -> None:
        if self._pinned:
            self._pinned.clear()
            self.invalidateFilter()

    def matches_filters(self, mod) -> bool:
        """Whether a mod satisfies the filter on its own, ignoring any pin."""
        category_matches = self._category_key is None or mod.category_key == self._category_key
        searchable = f"{mod.name} {mod.description}".casefold()
        search_matches = not self._search_text or self._search_text in searchable
        return category_matches and search_matches

    def set_sort_mode(self, mode: SortMode, order: Qt.SortOrder) -> None:
        self._sort_mode = mode
        self.sort(0, order)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:  # noqa: N802
        source = self.sourceModel()
        if not isinstance(source, InstalledModListModel):
            return True
        mod = source.index(source_row, 0, source_parent).data(InstalledModRoles.MOD)
        if mod.identity in self._pinned:
            return True
        return self.matches_filters(mod)

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:  # noqa: N802
        left_mod = left.data(InstalledModRoles.MOD)
        right_mod = right.data(InstalledModRoles.MOD)
        if self._sort_mode == SortMode.NAME:
            return left_mod.name.casefold() < right_mod.name.casefold()
        if self._sort_mode == SortMode.PRIORITY:
            left_priority = -1 if left_mod.priority is None else left_mod.priority
            right_priority = -1 if right_mod.priority is None else right_mod.priority
            return left_priority < right_priority
        return left_mod.installed_on < right_mod.installed_on
