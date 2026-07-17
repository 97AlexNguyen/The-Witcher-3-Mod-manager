from __future__ import annotations

from PyQt6.QtCore import QByteArray, QItemSelectionModel, QSettings, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSplitter, QStackedWidget, QVBoxLayout, QWidget

from app.data import make_mock_categories, make_mock_mods
from app.ui.models import InstalledModListModel, InstalledModRoles, ModListFilterProxy, SortMode
from app.ui.theme.tokens import SPACING_LG, SPACING_MD, SPACING_SM
from app.ui.widgets import ModCardList, ModDetailPanel, ModFilterBar


class ModManagerPage(QWidget):
    archives_dropped = pyqtSignal(list)

    ARCHIVE_SUFFIXES = (".zip", ".7z", ".rar")
    NOTICE_TIMEOUT_MS = 6000

    def __init__(self, settings: QSettings, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("pageSurface")
        self.setAcceptDrops(True)
        self._settings = settings
        self._categories = make_mock_categories()
        self._mods = make_mock_mods()

        self.mod_model = InstalledModListModel(self._mods, self)
        self.proxy = ModListFilterProxy(self)
        self.proxy.setSourceModel(self.mod_model)
        self.filter_bar = ModFilterBar(self._categories)
        self.card_list = ModCardList(self.proxy)
        self.detail_panel = ModDetailPanel(self._categories)
        self._notice_timer = QTimer(self)
        self._notice_timer.setSingleShot(True)
        self._notice_timer.setInterval(self.NOTICE_TIMEOUT_MS)
        self._notice_timer.timeout.connect(self._hide_notice)
        self._build_ui()
        self._connect()
        self._restore_state()
        self._refresh_summary()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING_LG, SPACING_MD, SPACING_LG, SPACING_LG)
        layout.setSpacing(SPACING_MD)
        layout.addWidget(self.filter_bar)

        self.notice_label = QLabel()
        self.notice_label.setObjectName("noticeBar")
        self.notice_label.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.notice_label.setWordWrap(True)
        self.notice_label.hide()
        layout.addWidget(self.notice_label)

        section = QHBoxLayout()
        section.setSpacing(SPACING_SM)
        title = QLabel("INSTALLED MODS")
        title.setProperty("class", "headline-sm")
        section.addWidget(title)
        self.result_label = QLabel()
        self.result_label.setProperty("class", "muted")
        section.addWidget(self.result_label)
        section.addStretch()
        drop_hint = QLabel("Drop .zip, .7z, or .rar files here to install")
        drop_hint.setProperty("class", "muted")
        section.addWidget(drop_hint)
        layout.addLayout(section)

        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(self.card_list)
        self.empty_filtered = self._make_filtered_empty_state()
        self.empty_library = self._make_library_empty_state()
        self.content_stack.addWidget(self.empty_filtered)
        self.content_stack.addWidget(self.empty_library)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setObjectName("modWorkspaceSplitter")
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(1)
        self.splitter.addWidget(self.content_stack)
        self.splitter.addWidget(self.detail_panel)
        # The card list must always stay visible; the detail panel may be collapsed away
        # by users who want the full width for browsing.
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, True)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 0)
        self.splitter.setSizes([1000, 360])
        layout.addWidget(self.splitter, 1)

    @staticmethod
    def _empty_shell(title_text: str, message_text: str) -> tuple[QWidget, QVBoxLayout]:
        empty = QWidget()
        empty.setObjectName("emptyState")
        box = QVBoxLayout(empty)
        box.addStretch()
        title = QLabel(title_text)
        title.setProperty("class", "headline-sm")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box.addWidget(title)
        message = QLabel(message_text)
        message.setProperty("class", "muted")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box.addWidget(message)
        return empty, box

    def _make_filtered_empty_state(self) -> QWidget:
        empty, box = self._empty_shell(
            "No mods match these filters",
            "Try another category or clear the search field.",
        )
        clear = QPushButton("CLEAR FILTERS")
        clear.setProperty("class", "ghost")
        clear.clicked.connect(self._clear_filters)
        box.addWidget(clear, alignment=Qt.AlignmentFlag.AlignCenter)
        box.addStretch()
        return empty

    def _make_library_empty_state(self) -> QWidget:
        empty, box = self._empty_shell(
            "No mods installed yet",
            "Drop a .zip, .7z, or .rar archive here, or use INSTALL MOD in the header to get started.",
        )
        box.addStretch()
        return empty

    def _connect(self) -> None:
        self.filter_bar.search_changed.connect(self._set_search)
        self.filter_bar.category_changed.connect(self._set_category)
        self.filter_bar.sort_changed.connect(self._set_sort)
        # Re-picking the category already selected emits no currentIndexChanged, but the
        # user did just "change the filter" as far as they are concerned — drop the pins.
        self.filter_bar.category_combo.activated.connect(self._reapply_category_filter)
        self.card_list.selection_changed.connect(self.detail_panel.show_selection)
        self.card_list.focus_details_requested.connect(self._focus_details)
        self.card_list.remove_requested.connect(self._request_remove)
        self.detail_panel.category_changed.connect(self._set_mod_category)
        self.mod_model.dataChanged.connect(self._on_data_changed)
        self.mod_model.modelReset.connect(self._refresh_summary)
        self.proxy.rowsInserted.connect(self._refresh_summary)
        self.proxy.rowsRemoved.connect(self._refresh_summary)
        self.proxy.modelReset.connect(self._refresh_summary)
        self.proxy.layoutChanged.connect(self._refresh_summary)

    def _read_int(self, key: str, default: int) -> int:
        try:
            return int(self._settings.value(key, default))
        except (TypeError, ValueError):
            return default

    def _restore_state(self) -> None:
        category_key = str(self._settings.value("mod_manager/category", "all"))
        sort_index = self._read_int("mod_manager/sort", 0)
        self.filter_bar.restore(category_key, sort_index)
        self._set_category(category_key)
        mode, order = self.filter_bar.sort_combo.currentData()
        self._set_sort(mode, order)
        splitter_state = self._settings.value("mod_manager/detail_splitter")
        if isinstance(splitter_state, QByteArray):
            self.splitter.restoreState(splitter_state)

    def _category_name(self, category_key: str) -> str:
        for category in self._categories:
            if category.key == category_key:
                return category.name
        return category_key

    def _show_notice(self, text: str) -> None:
        self.notice_label.setText(text)
        self.notice_label.show()
        self._notice_timer.start()

    def _hide_notice(self) -> None:
        self._notice_timer.stop()
        self.notice_label.hide()

    def _set_search(self, text: str) -> None:
        self._hide_notice()
        self.proxy.set_search_text(text)
        self._refresh_summary()

    def _set_category(self, category_key: str) -> None:
        self._hide_notice()
        self.proxy.set_category(category_key)
        self._settings.setValue("mod_manager/category", category_key)
        self._refresh_summary()

    def _reapply_category_filter(self, _index: int) -> None:
        self._hide_notice()
        self.proxy.clear_pins()
        self._refresh_summary()

    def _set_sort(self, mode: SortMode, order: Qt.SortOrder) -> None:
        self.proxy.set_sort_mode(mode, order)
        self._settings.setValue("mod_manager/sort", self.filter_bar.sort_combo.currentIndex())

    def _set_mod_category(self, mod, category_key: str) -> None:
        if mod.category_key == category_key:
            return
        # Pin first: the edit re-runs the filter, which would otherwise drop the row
        # the user is editing and clear their selection.
        self.proxy.pin(mod)
        if not self.mod_model.set_category(mod, category_key):
            return
        if not self.proxy.matches_filters(mod):
            self._show_notice(
                f"'{mod.name}' moved to {self._category_name(category_key)} and no longer matches "
                "the current filter. It stays visible until you change the filter."
            )

    def _focus_details(self, mod) -> None:
        for row in range(self.proxy.rowCount()):
            index = self.proxy.index(row, 0)
            if index.data(InstalledModRoles.MOD) is mod:
                self.card_list.selectionModel().select(
                    index, QItemSelectionModel.SelectionFlag.ClearAndSelect
                )
                self.card_list.setCurrentIndex(index)
                break
        # Shown directly rather than via selectionChanged: asking for details on the
        # already-selected card emits no selection signal.
        self.detail_panel.show_selection([mod])
        self.detail_panel.setFocus()

    def _request_remove(self, mod) -> None:
        self._show_notice(f"Removing '{mod.name}' will be connected in a later phase.")

    def _clear_filters(self) -> None:
        self.filter_bar.search_input.clear()
        self.filter_bar.category_combo.setCurrentIndex(0)

    def _on_data_changed(self, top_left, bottom_right, _roles=None) -> None:
        self._refresh_summary()
        mod = self.detail_panel.current_mod
        if mod is None:
            return
        for row in range(top_left.row(), bottom_right.row() + 1):
            if self.mod_model.mod_at(row) is mod:
                self.detail_panel.show_selection([mod])
                return

    def _refresh_summary(self, *_args) -> None:
        visible = self.proxy.rowCount()
        total = self.mod_model.rowCount()
        self.result_label.setText(f"{visible} shown" if visible == total else f"{visible} of {total} shown")
        if total == 0:
            self.content_stack.setCurrentWidget(self.empty_library)
        elif visible == 0:
            self.content_stack.setCurrentWidget(self.empty_filtered)
        else:
            self.content_stack.setCurrentWidget(self.card_list)

    def _archive_paths(self, event) -> list[str]:
        mime = event.mimeData()
        if not mime.hasUrls():
            return []
        return [
            url.toLocalFile()
            for url in mime.urls()
            if url.isLocalFile() and url.toLocalFile().lower().endswith(self.ARCHIVE_SUFFIXES)
        ]

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:  # noqa: N802
        if self._archive_paths(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event) -> None:  # noqa: N802
        if self._archive_paths(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:  # noqa: N802
        paths = self._archive_paths(event)
        if not paths:
            event.ignore()
            return
        event.acceptProposedAction()
        self.archives_dropped.emit(paths)
        count = len(paths)
        self._show_notice(
            f"{count} archive{'s' if count != 1 else ''} received. "
            "The install flow will be connected in a later phase."
        )

    def save_state(self) -> None:
        self._settings.setValue("mod_manager/category", self.filter_bar.category_combo.currentData())
        self._settings.setValue("mod_manager/sort", self.filter_bar.sort_combo.currentIndex())
        self._settings.setValue("mod_manager/detail_splitter", self.splitter.saveState())
