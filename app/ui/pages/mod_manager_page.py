from __future__ import annotations

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QStackedWidget, QVBoxLayout, QWidget

from app.data import make_mock_categories, make_mock_mods
from app.ui.models import InstalledModListModel, InstalledModRoles, ModListFilterProxy, SortMode
from app.ui.theme.tokens import SPACING_LG, SPACING_MD, SPACING_SM
from app.ui.widgets import ModCardList, ModFilterBar


class ModManagerPage(QWidget):
    def __init__(self, settings: QSettings, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("pageSurface")
        self._settings = settings
        self._categories = make_mock_categories()
        self._mods = make_mock_mods()

        self.mod_model = InstalledModListModel(self._mods, self)
        self.proxy = ModListFilterProxy(self)
        self.proxy.setSourceModel(self.mod_model)
        self.filter_bar = ModFilterBar(self._categories)
        self.card_list = ModCardList(self.proxy)
        self._build_ui()
        self._connect()
        self._restore_state()
        self._refresh_summary()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING_LG, SPACING_MD, SPACING_LG, SPACING_LG)
        layout.setSpacing(SPACING_MD)
        layout.addWidget(self.filter_bar)

        section = QHBoxLayout()
        section.setSpacing(SPACING_SM)
        title = QLabel("INSTALLED MODS")
        title.setProperty("class", "headline-sm")
        section.addWidget(title)
        self.result_label = QLabel()
        self.result_label.setProperty("class", "muted")
        section.addWidget(self.result_label)
        section.addStretch()
        drop_hint = QLabel("Drop .zip, .7z, or .rar files anywhere in this window")
        drop_hint.setProperty("class", "muted")
        section.addWidget(drop_hint)
        layout.addLayout(section)

        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(self.card_list)
        self.empty_state = self._make_empty_state()
        self.content_stack.addWidget(self.empty_state)
        layout.addWidget(self.content_stack, 1)

    def _make_empty_state(self) -> QWidget:
        empty = QWidget()
        empty.setObjectName("emptyState")
        box = QVBoxLayout(empty)
        box.addStretch()
        title = QLabel("No mods match these filters")
        title.setProperty("class", "headline-sm")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box.addWidget(title)
        message = QLabel("Try another category or clear the search field.")
        message.setProperty("class", "muted")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box.addWidget(message)
        clear = QPushButton("CLEAR FILTERS")
        clear.setProperty("class", "ghost")
        clear.clicked.connect(self._clear_filters)
        box.addWidget(clear, alignment=Qt.AlignmentFlag.AlignCenter)
        box.addStretch()
        return empty

    def _connect(self) -> None:
        self.filter_bar.search_changed.connect(self._set_search)
        self.filter_bar.category_changed.connect(self._set_category)
        self.filter_bar.sort_changed.connect(self._set_sort)
        self.mod_model.dataChanged.connect(self._refresh_summary)
        self.proxy.rowsInserted.connect(self._refresh_summary)
        self.proxy.rowsRemoved.connect(self._refresh_summary)
        self.proxy.modelReset.connect(self._refresh_summary)
        self.proxy.layoutChanged.connect(self._refresh_summary)

    def _restore_state(self) -> None:
        category_key = str(self._settings.value("mod_manager/category", "all"))
        sort_index = int(self._settings.value("mod_manager/sort", 0))
        self.filter_bar.restore(category_key, sort_index)
        self._set_category(category_key)
        mode, order = self.filter_bar.sort_combo.currentData()
        self._set_sort(mode, order)

    def _set_search(self, text: str) -> None:
        self.proxy.set_search_text(text)
        self._refresh_summary()

    def _set_category(self, category_key: str) -> None:
        self.proxy.set_category(category_key)
        self._settings.setValue("mod_manager/category", category_key)
        self._refresh_summary()

    def _set_sort(self, mode: SortMode, order: Qt.SortOrder) -> None:
        self.proxy.set_sort_mode(mode, order)
        self._settings.setValue("mod_manager/sort", self.filter_bar.sort_combo.currentIndex())

    def _clear_filters(self) -> None:
        self.filter_bar.search_input.clear()
        self.filter_bar.category_combo.setCurrentIndex(0)

    def _visible_mods(self):
        return [
            self.proxy.index(row, 0).data(InstalledModRoles.MOD)
            for row in range(self.proxy.rowCount())
        ]

    def _refresh_summary(self, *_args) -> None:
        visible = self._visible_mods()
        self.result_label.setText(f"{len(visible)} shown")
        self.content_stack.setCurrentWidget(self.card_list if visible else self.empty_state)

    def save_state(self) -> None:
        self._settings.setValue("mod_manager/category", self.filter_bar.category_combo.currentData())
        self._settings.setValue("mod_manager/sort", self.filter_bar.sort_combo.currentIndex())
