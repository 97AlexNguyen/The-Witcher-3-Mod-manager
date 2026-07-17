from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLineEdit, QPushButton

from app.domain import Category
from app.ui.models import SortMode
from app.ui.theme.tokens import SPACING_MD, SPACING_SM


class ModFilterBar(QFrame):
    search_changed = pyqtSignal(str)
    category_changed = pyqtSignal(str)
    sort_changed = pyqtSignal(object, object)

    def __init__(self, categories: list[Category], parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("filterBar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACING_MD, SPACING_SM, SPACING_MD, SPACING_SM)
        layout.setSpacing(SPACING_SM)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by mod name or description...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.search_changed)
        layout.addWidget(self.search_input, 1)

        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(168)
        for category in categories:
            self.category_combo.addItem(category.name, category.key)
        self.category_combo.currentIndexChanged.connect(self._emit_category)
        layout.addWidget(self.category_combo)

        self.sort_combo = QComboBox()
        self.sort_combo.setMinimumWidth(168)
        self.sort_combo.addItem("Newest installed", (SortMode.INSTALLED, Qt.SortOrder.DescendingOrder))
        self.sort_combo.addItem("Name A–Z", (SortMode.NAME, Qt.SortOrder.AscendingOrder))
        self.sort_combo.addItem("Priority high", (SortMode.PRIORITY, Qt.SortOrder.DescendingOrder))
        self.sort_combo.currentIndexChanged.connect(self._emit_sort)
        layout.addWidget(self.sort_combo)

        check_button = QPushButton("CHECK UPDATES")
        check_button.setToolTip("Update checks will be connected when Nexus integration is implemented")
        layout.addWidget(check_button)

    def restore(self, category_key: str, sort_index: int) -> None:
        category_index = self.category_combo.findData(category_key)
        self.category_combo.setCurrentIndex(max(0, category_index))
        self.sort_combo.setCurrentIndex(max(0, min(sort_index, self.sort_combo.count() - 1)))

    def _emit_category(self, index: int) -> None:
        if index >= 0:
            self.category_changed.emit(self.category_combo.itemData(index))

    def _emit_sort(self, index: int) -> None:
        if index >= 0:
            mode, order = self.sort_combo.itemData(index)
            self.sort_changed.emit(mode, order)
